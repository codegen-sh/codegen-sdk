"""Slack chatbot for answering questions about FastAPI using Codegen's VectorIndex."""

import os
from typing import Any

import modal
from codegen import Codebase
from codegen.extensions import VectorIndex
from fastapi import FastAPI, Request
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from tokens import OPENAI_API_KEY, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


########################################################
# Modal & Slack Setup
########################################################

volume = modal.Volume.from_name("repo-cache", create_if_missing=True)
# Create image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.13")
    .apt_install("git")
    .pip_install(
        "slack-bolt>=1.18.0",
        "codegen>=0.6.1",
        "openai>=1.1.0",
    )
)

# Create Modal app and stub
app = modal.App("codegen-slack-demo")
web_app = FastAPI()

# Initialize Slack app with signing secret
slack_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)

# Create FastAPI app
handler = SlackRequestHandler(slack_app)

########################################################
# Slackbot Verification Endpoint
########################################################


@web_app.post("/slack/verify")  # you will need to rename this to do proper verification
async def verify(request: Request):
    """Handle Slack URL verification challenge."""
    data = await request.json()

    # Handle the URL verification challenge
    if data["type"] == "url_verification":
        return {"challenge": data["challenge"]}

    # For other event types, pass to the Slack handler
    return await handler.handle(request)


@web_app.post("/")
async def endpoint(request: Request):
    """Handle Slack events and verify requests."""
    return await handler.handle(request)


@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return web_app


########################################################
# LLM Processing
########################################################


def format_response(answer: str, context: list[dict[str, str]]) -> str:
    """Format the response for Slack with file links."""
    response = f"*Answer:*\n{answer}\n\n*Relevant Files:*\n"

    # Add file links
    for ctx in context:
        # Create GitHub link to the file
        github_link = f"https://github.com/tiangolo/fastapi/blob/master/{ctx['filepath']}"
        response += f"• <{github_link}|`{ctx['filepath']}`>\n"

    return response


def answer_question(query: str) -> tuple[str, list[dict[str, str]]]:
    """Use RAG to answer a question about FastAPI."""
    # Initialize codebase
    codebase = Codebase.from_repo("fastapi/fastapi", tmp_dir="/root")

    # Initialize vector index
    index = VectorIndex(codebase)

    # Try to load existing index or create new one
    index_path = "/root/fastapi_index.pkl"
    try:
        index.load(index_path)
    except FileNotFoundError:
        # Create new index if none exists
        index.create()
        index.save(index_path)

    # Find relevant files
    results = index.similarity_search(query, k=10)

    # Collect context from relevant files
    context = []
    for filepath, score in results:
        if "#chunk" in filepath:
            filepath = filepath.split("#chunk")[0]
        file = codebase.get_file(filepath)
        context.append(
            {
                "filepath": file.filepath,
                "snippet": file.content[:1000],  # First 1000 chars as preview
            }
        )

    # Format context for prompt
    context_str = "\n\n".join([f"File: {c['filepath']}\n```\n{c['snippet']}\n```" for c in context])

    # Create prompt for OpenAI
    prompt = f"""You are an expert on FastAPI. Given the following code context and question, provide a clear and accurate answer.
Focus on the specific code shown in the context and FastAPI's implementation details.

Question: {query}

Relevant FastAPI code:
{context_str}

Answer:"""

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a FastAPI expert. Answer questions about FastAPI's implementation accurately and concisely based on the provided code context."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    return response.choices[0].message.content, [{"filepath": c["filepath"], "snippet": c["snippet"]} for c in context]


responded = {}

########################################################
# Main Event Handler
########################################################


@slack_app.event("app_mention")
def handle_mention(event: dict[str, Any], say: Any) -> None:
    """Handle mentions of the bot in channels."""
    print("event", event)

    # Skip if we've already answered this question
    if event["ts"] in responded:
        return
    else:
        responded[event["ts"]] = True

    # Get message text without the bot mention
    query = event["text"].split(">", 1)[1].strip()
    if not query:
        say("Please ask a question about FastAPI!")
        return

    if "!" not in event["text"]:
        say("include `!` in your message to ask a question")
        return

    try:
        # Add typing indicator emoji
        slack_app.client.reactions_add(
            channel=event["channel"],
            timestamp=event["ts"],
            name="writing_hand",
        )

        if not query:
            say("Please ask a question about FastAPI!")
            return

        # Get answer using RAG
        answer, context = answer_question(query)

        # Format and send response in thread
        response = format_response(answer, context)
        say(text=response, thread_ts=event["ts"])

        # Remove typing indicator emoji
        slack_app.client.reactions_remove(
            channel=event["channel"],
            timestamp=event["ts"],
            name="writing_hand",
        )

    except Exception as e:
        # Send error message in thread
        say(text=f"Error: {str(e)}", thread_ts=event["ts"])

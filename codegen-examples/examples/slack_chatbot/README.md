# FastAPI Slack Bot

<p align="center">
  <a href="https://docs.codegen.com">
    <img src="https://i.imgur.com/6RF9W0z.jpeg" />
  </a>
</p>

<h2 align="center">
  A Slack bot for answering questions about FastAPI's implementation
</h2>

<div align="center">

[![Documentation](https://img.shields.io/badge/Docs-docs.codegen.com-purple?style=flat-square)](https://docs.codegen.com)
[![License](https://img.shields.io/badge/Code%20License-Apache%202.0-gray?&color=gray)](https://github.com/codegen-sh/codegen-sdk/tree/develop?tab=Apache-2.0-1-ov-file)

</div>

This example demonstrates how to build a Slack chatbot that can answer questions about FastAPI's implementation using Codegen's VectorIndex for RAG. The bot:

1. Maintains an up-to-date index of FastAPI's source code
1. Uses semantic search to find relevant code snippets
1. Generates detailed answers about FastAPI's internals using GPT-4

## Quick Start

1. Install dependencies:

```bash
pip install modal-client codegen slack-bolt openai
```

2. Create a Slack app and get tokens:

   - Create a new Slack app at https://api.slack.com/apps
   - Enable Socket Mode
   - Add bot token scopes:
     - `app_mentions:read`
     - `chat:write`
     - `reactions:write`
   - Install the app to your workspace
   - Copy the Bot User OAuth Token and App-Level Token

1. Create a Modal secret for Slack tokens:

```bash
modal secret create slack-tokens \
  SLACK_BOT_TOKEN="xoxb-your-bot-token" \
  SLACK_APP_TOKEN="xapp-your-app-token"
```

4. Start the bot:

```bash
modal serve api.py
```

## Usage

Just mention the bot in any channel and ask your question about FastAPI:

```
@fastapi-bot How does FastAPI handle dependency injection?
@fastapi-bot What's the implementation of path parameters?
@fastapi-bot How does FastAPI validate request bodies?
```

The bot will:

1. Find the most relevant FastAPI source code
1. Generate a detailed explanation
1. Show you the actual implementation

## Response Format

The bot responds with:

1. A detailed answer about FastAPI's implementation
1. Relevant code snippets with file paths
1. Error messages if something goes wrong

Example response:

````
*Answer:*
FastAPI handles dependency injection through its Depends class, which creates
a dependency that can be injected into path operation functions...

*Relevant Code:*
*File:* `fastapi/dependencies/utils.py`
```python
def get_dependant(
    path: str,
    call: Callable,
    name: str,
    security_scopes: List[str] = None,
    use_cache: bool = True,
) -> Dependant:
    ...
````

## Environment Variables

Required environment variables (set through Modal secrets):

- `SLACK_BOT_TOKEN`: Slack Bot User OAuth Token
- `SLACK_APP_TOKEN`: Slack App-Level Token
- `OPENAI_API_KEY`: OpenAI API key

## Development

The bot is built using:

- Modal for serverless deployment
- Codegen for FastAPI code analysis
- Slack Bolt for the Slack integration
- OpenAI for embeddings and Q&A

To deploy changes:

```bash
modal deploy api.py
```

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Codegen Documentation](https://docs.codegen.com)
- [Slack Bolt Python](https://slack.dev/bolt-python/concepts)
- [Modal Documentation](https://modal.com/docs)

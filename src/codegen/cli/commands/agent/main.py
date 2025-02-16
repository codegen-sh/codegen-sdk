import uuid

import rich_click as click
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from codegen import Codebase
from codegen.extensions.langchain.agent import create_agent_with_tools
from codegen.extensions.langchain.tools import (
    CreateFileTool,
    DeleteFileTool,
    EditFileTool,
    ListDirectoryTool,
    MoveSymbolTool,
    RenameFileTool,
    RevealSymbolTool,
    SearchTool,
    ViewFileTool,
)

console = Console()


@click.command(name="agent")
@click.option("--query", "-q", default=None, help="Initial query for the agent.")
def agent_command(query: str):
    """Start an interactive chat session with the Codegen AI agent."""
    # Initialize codebase from current directory
    with console.status("[bold green]Initializing codebase...[/bold green]"):
        codebase = Codebase("./")

    # Helper function for agent to print messages
    def say(message: str):
        markdown = Markdown(message)
        console.print(markdown)

    # Initialize tools
    tools = [
        ViewFileTool(codebase),
        ListDirectoryTool(codebase),
        SearchTool(codebase),
        CreateFileTool(codebase),
        DeleteFileTool(codebase),
        RenameFileTool(codebase),
        MoveSymbolTool(codebase),
        RevealSymbolTool(codebase),
        EditFileTool(codebase),
    ]

    # Initialize chat history with system message
    chat_history = [
        SystemMessage(
            content="""You are a helpful AI assistant with access to the local codebase.
You can help with code exploration, editing, and general programming tasks.
Always explain what you're planning to do before taking actions."""
        )
    ]

    # Get initial query if not provided via command line
    if not query:
        console.print("[bold]Welcome to the Codegen AI Agent! What can I help you with?[/bold]")
        query = Prompt.ask(":speech_balloon: [bold]Your message[/bold]")

    # Create the agent
    agent = create_agent_with_tools(codebase, tools, chat_history=chat_history)

    # Main chat loop
    while True:
        if not query:  # Only prompt for subsequent messages
            user_input = Prompt.ask(":speech_balloon: [bold]Your message[/bold]")
        else:
            user_input = query
            query = None  # Clear the initial query so we enter the prompt flow

        if user_input.lower() in ["exit", "quit"]:
            break

        # Add user message to chat history
        chat_history.append(HumanMessage(content=user_input))

        # Invoke the agent
        with console.status("[bold green]Agent is thinking...") as status:
            try:
                session_id = str(uuid.uuid4())
                result = agent.invoke(
                    {"input": user_input},
                    config={"configurable": {"session_id": session_id}},
                )
                # Update chat history with AI's response
                if result.get("output"):
                    say(result["output"])
                    chat_history.append(AIMessage(content=result["output"]))
            except Exception as e:
                console.print(f"[bold red]Error during agent execution:[/bold red] {e}")
                break

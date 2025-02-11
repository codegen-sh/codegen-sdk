"""Demo implementation of an agent with Codegen tools."""

from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from codegen import Codebase

from .tools import (
    CommitTool,
    CreateFileTool,
    DeleteFileTool,
    EditFileTool,
    ListDirectoryTool,
    MoveSymbolTool,
    RenameFileTool,
    RevealSymbolTool,
    SearchTool,
    SemanticEditTool,
    SemanticSearchTool,
    ViewFileTool,
)


def create_codebase_agent(
    codebase: Codebase,
    model_name: str = "gpt-4o",
    temperature: float = 0,
    verbose: bool = True,
) -> RunnableWithMessageHistory:
    """Create an agent with all codebase tools.

    Args:
        codebase: The codebase to operate on
        model_name: Name of the model to use (default: gpt-4)
        temperature: Model temperature (default: 0)
        verbose: Whether to print agent's thought process (default: True)

    Returns:
        Initialized agent with message history
    """
    # Initialize language model
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
    )

    # Get all codebase tools
    tools = [
        ViewFileTool(codebase),
        ListDirectoryTool(codebase),
        SearchTool(codebase),
        EditFileTool(codebase),
        CreateFileTool(codebase),
        DeleteFileTool(codebase),
        RenameFileTool(codebase),
        MoveSymbolTool(codebase),
        RevealSymbolTool(codebase),
        SemanticEditTool(codebase),
        SemanticSearchTool(codebase),
        CommitTool(codebase),
    ]

    # Get the prompt to use
    prompt = hub.pull("hwchase17/openai-functions-agent")

    # Create the agent
    agent = OpenAIFunctionsAgent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
    )

    # Create message history handler
    message_history = ChatMessageHistory()

    # Wrap with message history
    return RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: message_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

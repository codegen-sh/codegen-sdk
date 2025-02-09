"""Demo implementation of an agent with workspace tools."""

from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain_core.chat_history import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from codegen import Codebase
from codegen.sdk.enums import ProgrammingLanguage

from . import get_workspace_tools


def create_workspace_agent(
    codebase: Codebase,
    model_name: str = "gpt-4o",
    temperature: float = 0,
    verbose: bool = True,
) -> RunnableWithMessageHistory:
    """Create an agent with all workspace tools.

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

    # Get all workspace tools
    tools = get_workspace_tools(codebase)

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


if __name__ == "__main__":
    # Initialize codebase
    codebase = Codebase("./", programming_language=ProgrammingLanguage.PYTHON)

    # Create agent with history
    agent = create_workspace_agent(codebase)

    # Example interactions
    print("\nAsking agent to explore the codebase...")
    result = agent.invoke(
        {"input": "List all Python files in the src directory"},
        config={"configurable": {"session_id": "demo"}},
    )
    print("Messages:", result["messages"])

    print("\nAsking agent to analyze a specific file...")
    result = agent.invoke(
        {"input": "Show me the contents of src/codegen/workspace/tools/reveal_symbol.py"},
        config={"configurable": {"session_id": "demo"}},
    )
    print("Messages:", result["messages"])

    print("\nAsking agent to analyze symbol relationships...")
    result = agent.invoke(
        {"input": "What are the dependencies of the reveal_symbol function?"},
        config={"configurable": {"session_id": "demo"}},
    )
    print("Messages:", result["messages"])

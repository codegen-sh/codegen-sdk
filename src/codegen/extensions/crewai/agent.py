from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

from codegen import Codebase
from codegen.extensions.crewai.tools import ViewFileTool

load_dotenv()

codebase = Codebase.from_repo("codegen-sh/codegen-sdk")

# Add tools to agent
agent = Agent(
    role="codegen-agi, an AGI generalist SWE agent",
    goal="Answer user queries about codebases",
    backstory="You are built by the codegen team to help answer user queries about codebases",
    tools=[ViewFileTool(codebase)],
    verbose=True,
    function_calling_llm="gpt-4o",  # Cheaper model for tool calls
)

task = Task(description="Explain to me the scripts/profiling/apis.py file - what does it do?", agent=agent, expected_output="An english answer for the user")

my_crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)


result = my_crew.kickoff()
print(result)

output = task.output
print(output)

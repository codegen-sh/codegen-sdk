from codegen.extensions.mcp.reveal_symbol_tool import mcp
from codegen.extensions.mcp.search_codebase_tool import mcp
import json
from typing import Annotated, Any, Literal, Optional
from codegen.extensions.tools import reveal_symbol
from codegen.extensions.tools.search import search
from codegen.extensions.vector_index import VectorIndex
from codegen.sdk.core.codebase import Codebase
from mcp.server.fastmcp import FastMCP
from codegen.sdk.enums import ProgrammingLanguage

mcp = FastMCP("codebase-tools-mcp", instructions="Use this server to access any information from your codebase. This tool can provide information ranging from AST Symbol details and information from across the codebase. Use this tool for all questions, queries regarding your codebase.")

@mcp.tool(name="reveal_symbol", description="Reveal the dependencies and usages of a symbol up to N degrees")
def reveal_symbol_tool(
    symbol_name: Annotated[str, "Name of the symbol to inspect"],
    target_file: Annotated[Optional[str], "The file path of the file containing the symbol to inspect"],
    codebase_dir: Annotated[str, "The root directory of your codebase"],
    codebase_language: Annotated[ProgrammingLanguage, "The language the codebase is written in"],
    degree: Annotated[Optional[int], "depth do which symbol information is retrieved"],
    collect_dependencies: Annotated[Optional[bool], "includes dependencies of symbol"],
    collect_usages: Annotated[Optional[bool], "includes usages of symbol"]
):
    codebase = Codebase(repo_path=codebase_dir, programming_language=codebase_language)
    found_symbol = None
    if target_file:
        file = codebase.get_file(target_file)
        found_symbol = file.get_symbol(symbol_name)
    else:
        found_symbol = codebase.get_symbol(symbol_name)

    result = reveal_symbol(
        found_symbol,
        degree,
        collect_dependencies=collect_dependencies,
        collect_usages=collect_usages,
    )
    return json.dumps(result, indent=2)

@mcp.tool(name="search_codebase", description="Search the codebase using text search or regex pattern matching")
def search_codebase_tool(
    query: str, 
    target_directories: Annotated[Optional[list[str]], "list of directories to search within"],     
    codebase_dir: Annotated[str, "The root directory of your codebase"],
    codebase_language: Annotated[ProgrammingLanguage, "The language the codebase is written in"],
    use_regex: Annotated[bool, "use regex for the search query"]
):
    codebase = Codebase(repo_path=codebase_dir, programming_language=codebase_language)
    result = search(codebase, query, target_directories, use_regex=use_regex)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Initialize and run the server
    print("Starting codebase toolsen server...")
    mcp.run(transport="stdio")

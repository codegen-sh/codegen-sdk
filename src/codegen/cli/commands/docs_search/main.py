import asyncio
import json

import rich
import rich_click as click
from algoliasearch.search.client import SearchClient
from rich import box
from rich.panel import Panel

from codegen.cli.env.global_env import global_env

ALGOLIA_APP_ID = "Q48PJS245N"
ALGOLIA_SEARCH_KEY = global_env.ALGOLIA_SEARCH_KEY
ALGOLIA_INDEX_NAME = "prod_knowledge"


@click.command(name="docs-search")
@click.argument("query")
@click.option(
    "--page",
    "-p",
    help="Page number (starts at 0)",
    default=0,
    type=int,
)
@click.option(
    "--hits",
    "-n",
    help="Number of results per page",
    default=5,
    type=int,
)
@click.option(
    "--doctype",
    "-d",
    help="Filter by documentation type (api or example)",
    type=click.Choice(["api", "example"], case_sensitive=False),
)
def docs_search_command(query: str, page: int, hits: int, doctype: str | None):
    """Search Codegen documentation."""
    try:
        # Run the async search in the event loop
        results = asyncio.run(async_docs_search(query, page, hits, doctype))
        results = json.loads(results)
        results = results["results"][0]
        hits_list = results["hits"]

        # Print search stats
        total_hits = results.get("nbHits", 0)
        total_pages = results.get("nbPages", 0)
        doctype_str = f" ({doctype} only)" if doctype else ""
        rich.print(f"\nFound {total_hits} results for '{query}'{doctype_str} ({total_pages} pages)")
        rich.print(f"Showing page {page + 1} of {total_pages}\n")

        # Print each hit with appropriate formatting
        for i, hit in enumerate(hits_list, 1):
            if hit.get("type") == "doc":
                format_api_doc(hit, i)
            else:
                format_example(hit, i)

        if hits_list:
            rich.print("─" * 80)  # Final separator

            # Navigation help with doctype if specified
            doctype_param = f" -d {doctype}" if doctype else ""
            if page > 0:
                rich.print(f"\nPrevious page: codegen docs-search -p {page - 1}{doctype_param} '{query}'")
            if page + 1 < total_pages:
                rich.print(f"Next page: codegen docs-search -p {page + 1}{doctype_param} '{query}'")

    except Exception as e:
        rich.print(
            Panel(
                f"[bold red]🔴 Error:[/bold red] {e!s}",
                title="Error searching docs",
                border_style="red",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        return 1


async def async_docs_search(query: str, page: int, hits_per_page: int, doctype: str | None):
    """Async function to perform the actual search."""
    client = SearchClient(ALGOLIA_APP_ID, ALGOLIA_SEARCH_KEY)

    try:
        # Build the search params
        search_params = {
            "indexName": ALGOLIA_INDEX_NAME,
            "query": query,
            "hitsPerPage": hits_per_page,
            "page": page,
        }

        # Add filters based on doctype
        if doctype == "api":
            search_params["filters"] = "type:doc"
        elif doctype == "example":
            search_params["filters"] = "type:skill_implementation"

        response = await client.search(
            search_method_params={
                "requests": [search_params],
            },
        )
        return response.to_json()

    finally:
        await client.close()


def format_api_doc(hit: dict, index: int) -> None:
    """Format and print an API documentation entry."""
    rich.print("─" * 80)  # Separator line
    rich.print(f"\n[{index}] {hit['fullname']}")

    if hit.get("description"):
        rich.print("\nDescription:")
        rich.print(hit["description"].strip())

    # Print additional API-specific details
    rich.print("\nDetails:")
    rich.print(f"Type: {hit.get('level', 'N/A')} ({hit.get('docType', 'N/A')})")
    rich.print(f"Language: {hit.get('language', 'N/A')}")
    if hit.get("className"):
        rich.print(f"Class: {hit['className']}")
    rich.print(f"Path: {hit.get('path', 'N/A')}")
    rich.print()


def format_example(hit: dict, index: int) -> None:
    """Format and print an example entry."""
    rich.print("─" * 80)  # Separator line

    # Title with emoji if available
    title = f"\n[{index}] {hit['name']}"
    if hit.get("emoji"):
        title = f"{title} {hit['emoji']}"
    rich.print(title)

    if hit.get("docstring"):
        rich.print("\nDescription:")
        rich.print(hit["docstring"].strip())

    if hit.get("source"):
        rich.print("\nSource:")
        rich.print("```")
        rich.print(hit["source"].strip())
        rich.print("```")

    # Additional metadata
    if hit.get("language") or hit.get("user_name"):
        rich.print("\nMetadata:")
        if hit.get("language"):
            rich.print(f"Language: {hit['language']}")
        if hit.get("user_name"):
            rich.print(f"Author: {hit['user_name']}")

    rich.print()

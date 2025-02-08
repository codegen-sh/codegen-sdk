from itertools import groupby

import rich
import rich_click as click
from rich.table import Table


@click.group(name="config")
def config_command():
    """Manage codegen configuration."""
    pass


@config_command.command(name="list")
def list_command():
    """List current configuration values."""
    from codegen.shared.configs.config import config

    table = Table(title="Configuration Values", border_style="blue", show_header=True)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="magenta")

    def flatten_dict(data: dict, prefix: str = "") -> dict:
        items = {}
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                items.update(flatten_dict(value, f"{full_key}."))
            else:
                items[full_key] = value
        return items

    # Get flattened config and sort by keys
    flat_config = flatten_dict(config.model_dump())
    sorted_items = sorted(flat_config.items(), key=lambda x: x[0])

    # Group by top-level prefix
    def get_prefix(item):
        return item[0].split(".")[0]

    for prefix, group in groupby(sorted_items, key=get_prefix):
        table.add_section()
        table.add_row(f"[bold blue]{prefix}[/bold blue]", "")
        for key, value in group:
            # Remove the prefix from the displayed key
            display_key = key[len(prefix) + 1 :] if "." in key else key
            table.add_row(f"  {display_key}", str(value))

    rich.print(table)


@config_command.command(name="get")
@click.argument("key")
def get_command(key: str):
    """Get a configuration value."""
    # TODO: Implement configuration get logic
    rich.print(f"[yellow]Getting configuration value for: {key}[/yellow]")


@config_command.command(name="set")
@click.argument("key")
@click.argument("value")
def set_command(key: str, value: str):
    """Set a configuration value."""
    # TODO: Implement configuration set logic
    rich.print(f"[green]Setting {key}={value}[/green]")

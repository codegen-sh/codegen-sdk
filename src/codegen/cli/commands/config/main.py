import logging
from itertools import groupby

import rich
import rich_click as click
from rich.table import Table

from codegen.shared.configs.config import config


@click.group(name="config")
def config_command():
    """Manage codegen configuration."""
    pass


@config_command.command(name="list")
def list_command():
    """List current configuration values."""
    table = Table(title="Configuration Values", border_style="blue", show_header=True)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    def flatten_dict(data: dict, prefix: str = "") -> dict:
        items = {}
        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key
            if isinstance(value, dict):
                # Always include dictionary fields, even if empty
                if not value:
                    items[full_key] = "{}"
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
        table.add_row(f"[bold yellow]{prefix}[/bold yellow]", "")
        for key, value in group:
            # Remove the prefix from the displayed key
            display_key = key[len(prefix) + 1 :] if "." in key else key
            table.add_row(f"  {display_key}", str(value))

    rich.print(table)


@config_command.command(name="get")
@click.argument("key")
def get_command(key: str):
    """Get a configuration value."""
    value = config.get(key)
    if value is None:
        rich.print(f"[red]Error: Configuration key '{key}' not found[/red]")
        return

    rich.print(f"[cyan]{key}[/cyan] = [magenta]{value}[/magenta]")


@config_command.command(name="set")
@click.argument("key")
@click.argument("value")
def set_command(key: str, value: str):
    """Set a configuration value and write to config.toml."""
    cur_value = config.get(key)
    if cur_value is None:
        rich.print(f"[red]Error: Configuration key '{key}' not found[/red]")
        return

    if cur_value.lower() != value.lower():
        try:
            config.set(key, value)
        except Exception as e:
            logging.exception(e)
            rich.print(f"[red]{e}[/red]")
            return

    rich.print(f"[green]Successfully set {key}=[magenta]{value}[/magenta] and saved to config.toml[/green]")

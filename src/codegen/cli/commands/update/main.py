import subprocess
import sys
from importlib.metadata import distribution

import requests
import rich
import rich_click as click
from packaging.version import Version

from codegen.cli.auth.session import CodegenSession


def fetch_pypi_releases(package: str) -> list[str]:
    response = requests.get(f"https://pypi.org/pypi/{package}/json")
    response.raise_for_status()
    return response.json()["releases"].keys()


def filter_versions(versions: list[Version], current_version: Version) -> list[Version]:
    # Filter out versions that are less than the previous minor version
    if current_version.minor == 0:
        if current_version.major == 0:
            return versions
        compare_tuple = (current_version.major - 1, 9, 0)
    else:
        compare_tuple = (current_version.major, current_version.minor - 1, 0)

    return [v for v in versions if v > v.release > compare_tuple]


def install_package(package: str, *args: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, *args])


@click.command(name="update")
@click.option("--list", "-l", "list_", is_flag=True, help="List all supported versions of the codegen")
@click.option("--version", "-v", type=str, help="Update to a specific version of the codegen")
def update_command(session: CodegenSession, list_: bool = False, version: str | None = None):
    """Update the codegen SDK to the latest version.

    --list: List all supported versions of the codegen
    --version: Update to a specific version of the codegen
    """
    if list_ and version:
        msg = "Cannot specify both --list and --version"
        raise click.ClickException(msg)

    package_info = distribution(__package__)
    version = package_info.version

    if list_:
        releases = fetch_pypi_releases(package_info.name)
        filtered_releases = filter_versions([Version(r) for r in releases], Version(version))
        for release in filtered_releases:
            if release == version:
                release = f"[bold]{release}(current)[/bold]"
            rich.print(release)
    elif version:
        install_package(f"{package_info.name}=={version}")
    else:
        # Update to latest version
        install_package(package_info.name, "--upgrade")

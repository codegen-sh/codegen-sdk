import os
import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from codegen.cli.commands.init.main import init_command


@pytest.fixture
def sample_repository(tmp_path: Path):
    os.chdir(tmp_path)
    subprocess.run(["git", "init", str(tmp_path)], check=True)
    subprocess.run(["git", "config", "--local", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "config", "--local", "user.name", "Test User"], check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/test/test.git"], check=True)
    yield tmp_path
    try:
        shutil.rmtree(tmp_path)
    except FileNotFoundError:
        pass


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


@pytest.fixture
def initialized_repo(sample_repository: Path, runner: CliRunner):
    os.chdir(sample_repository)
    runner.invoke(init_command)
    subprocess.run(["git", "add", "."], cwd=sample_repository, check=True)
    subprocess.run(["git", "commit", "-m", "Initialize codegen"], cwd=sample_repository, check=True)
    return sample_repository

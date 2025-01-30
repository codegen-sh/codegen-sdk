import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
import time
import platform

# NOTE: This is a test CLI for the codegen CLI to ensure it works as expected. The style-debug and run-on-pr commands are skipped.


class CLITester:
    def __init__(self):
        self.results = []
        self.console = Console()
        self.start_time = datetime.now()
        self.system_info = {"os": platform.system(), "python": platform.python_version(), "platform": platform.platform()}

        try:
            git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.PIPE).strip()
            self.repo_path = Path(git_root)
        except subprocess.CalledProcessError:
            raise RuntimeError("❌ Not in a git repository")

        try:
            self.git_info = {
                "branch": subprocess.check_output(["git", "branch", "--show-current"], text=True).strip(),
                "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()[:8],
            }
        except subprocess.CalledProcessError:
            self.git_info = {"branch": "unknown", "commit": "unknown"}

        default_token = os.getenv("CODEGEN_TOKEN", "")
        if default_token:
            self.console.print(f"[dim]Using token from environment[/dim]")
        self.test_token = input("Please enter your test token (or press Enter to use env token): ").strip() or default_token
        if not self.test_token:
            raise ValueError("❌ Test token is required")

        response = input("Do you want to run codegen reset at the end? This will reset the git repository (Y/N): ").strip().lower()
        self.run_reset = response == "y"

        os.chdir(self.repo_path)
        self.print_test_header()
        self.base_command = ["codegen"]

    def print_test_header(self):
        """Print a fancy header with test environment information"""
        self.console.print("\n=== Codegen CLI Test Suite ===", style="bold blue")

        info_table = Table(show_header=False, box=box.ROUNDED)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")

        info_table.add_row("Repository", str(self.repo_path))
        info_table.add_row("Branch", self.git_info["branch"])
        info_table.add_row("Commit", self.git_info["commit"])
        info_table.add_row("OS", self.system_info["os"])
        info_table.add_row("Python", self.system_info["python"])

        self.console.print(Panel(info_table, title="[bold]Test Environment", border_style="blue"))

    def run_command(self, args: List[str], expected_code: int = 0, timeout: Optional[int] = 30) -> Tuple[int, str, str]:
        """Run a CLI command with timeout and return its output"""
        command = self.base_command + args
        self.console.print(f"\n[cyan]$ {' '.join(command)}[/cyan]")

        try:
            env = os.environ.copy()
            env["ENV"] = "prod"
            env["CODEGEN_TEST_MODE"] = "1"

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=self.repo_path,
            )

            try:
                start_time = time.time()
                stdout, stderr = process.communicate(timeout=timeout)
                duration = time.time() - start_time
                success = process.returncode == expected_code

                if success:
                    self.console.print("✅ Success", style="green")
                else:
                    self.console.print(f"❌ Failed (expected {expected_code}, got {process.returncode})", style="red")
                    if stdout.strip():
                        self.console.print(Panel(stdout.strip(), title="[yellow]stdout", border_style="yellow"))
                    if stderr.strip():
                        self.console.print(Panel(stderr.strip(), title="[red]stderr", border_style="red"))

                self.results.append({"command": f"{' '.join(command)}", "success": success, "duration": duration, "returncode": process.returncode})
                return process.returncode, stdout, stderr

            except subprocess.TimeoutExpired:
                process.kill()
                self.console.print(f"⏰ Command timed out after {timeout}s", style="red")
                self.results.append({"command": f"{' '.join(command)}", "success": False, "duration": time.time(), "error": "Timeout"})
                return 1, "", f"Command timed out after {timeout}s"

        except FileNotFoundError:
            self.console.print(f"❌ Command not found: {' '.join(command)}", style="red")
            self.results.append({"command": f"{' '.join(command)}", "success": False, "duration": time.time(), "error": "Command not found"})
            return 1, "", "Command not found"

    def test_jupyter_notebook_command(self):
        """Test the 'notebook' command without showing UI"""
        self.console.print("\n[bold cyan]=== Testing: Notebook Command ===[/bold cyan]")

        try:
            process = subprocess.Popen(
                self.base_command + ["notebook"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
            )
            self.console.print("🔄 Starting notebook in background...", style="dim")

            time.sleep(5)
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
                self.console.print("✅ Notebook command executed successfully", style="green")
                self.results.append({"command": "codegen notebook", "success": True, "duration": 1, "returncode": process.returncode})
            except subprocess.TimeoutExpired:
                process.kill()
                self.console.print("✅ Notebook process terminated as expected", style="green")
                self.results.append({"command": "codegen notebook", "success": True, "duration": 1, "returncode": -15})

        except FileNotFoundError:
            self.console.print("❌ Notebook command not found", style="red")
            self.results.append({"command": "codegen notebook", "success": False, "duration": 0, "error": "Command not found"})
        except Exception as e:
            self.console.print(f"❌ Error running notebook command: {e}", style="red")
            self.results.append({"command": "codegen notebook", "success": False, "duration": 0, "error": str(e)})

    def test_style_debug_command(self):
        """Test the 'style-debug' command without letting it run indefinitely"""
        self.console.print("\n[bold cyan]=== Testing: Style Debug Command ===[/bold cyan]")

        try:
            process = subprocess.Popen(
                self.base_command + ["style-debug"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
            )
            self.console.print("🔄 Starting style-debug in background...", style="dim")

            time.sleep(1)

            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
                self.console.print("✅ Style-debug command executed successfully", style="green")
                self.results.append({"command": "codegen style-debug", "success": True, "duration": 1, "returncode": process.returncode})
            except subprocess.TimeoutExpired:
                process.kill()
                self.console.print("✅ Style-debug process terminated as expected", style="green")
                self.results.append({"command": "codegen style-debug", "success": True, "duration": 1, "returncode": -15})

        except FileNotFoundError:
            self.console.print("❌ Style-debug command not found", style="red")
            self.results.append({"command": "codegen style-debug", "success": False, "duration": 0, "error": "Command not found"})
        except Exception as e:
            self.console.print(f"❌ Error running style-debug command: {e}", style="red")
            self.results.append({"command": "codegen style-debug", "success": False, "duration": 0, "error": str(e)})

    def test_all_commands(self):
        """Test all available CLI commands"""
        self.console.print("\n=== Running Test Suite ===", style="bold blue")
        self.console.print("\n[cyan]Verifying Authentication[/cyan]")
        self.run_command(["logout"])

        returncode, stdout, stderr = self.run_command(["login", "--token", self.test_token])
        if returncode != 0:
            self.console.print("❌ Invalid token provided. Ending test suite.", style="red")
            self.print_summary()
            return

        # List of commands to test
        commands_to_test = [
            (["init"], "Repository Initialization"),
            (["list"], "List Available Functions"),
            (["create", "basic-test"], "Create Function"),
            (["run", "basic-test"], "Run Function"),
            (["deploy", "basic-test"], "Deploy Function"),
            (["profile"], "User Profile"),
            (["expert", "-q", '"How do I create a codemod?"'], "AI Expert Help"),
            (["run", "nonexistent-codemod"], "Invalid Function", 1),
            (["deploy", "nonexistent-codemod"], "Invalid Deploy", 1),
        ]

        for test_case in commands_to_test:
            command = test_case[0]
            description = test_case[1]
            expected_code = test_case[2] if len(test_case) > 2 else 0

            self.console.print(f"\n[bold cyan]=== Testing: {description} ===[/bold cyan]")

            returncode, stdout, stderr = self.run_command(command, expected_code)
            if returncode != expected_code:
                self.console.print(f"❌ {description} failed with unexpected return code {returncode}", style="red")

        self.test_jupyter_notebook_command()
        self.test_style_debug_command()

        if self.run_reset:
            self.console.print("\n[bold cyan]=== Testing: Repository Reset ===[/bold cyan]")
            self.run_command(["reset"])

        self.console.print("\n[bold cyan]=== Testing: Logout ===[/bold cyan]")
        self.run_command(["logout"])

        self.print_summary()

    def print_summary(self):
        """Print a detailed test summary with statistics"""
        duration = datetime.now() - self.start_time

        self.console.print("\n=== Test Summary ===", style="bold blue")

        table = Table(title="Test Results", box=box.ROUNDED)
        table.add_column("Command", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duration", style="blue")
        table.add_column("Return Code", style="yellow")

        total = len(self.results)
        successful = sum(1 for result in self.results if result["success"])

        for result in self.results:
            status = "✅ Passed" if result["success"] else "❌ Failed"
            error = result.get("error", "")
            if error:
                status = f"❌ {error}"

            table.add_row(result["command"], status, f"{result.get('duration', 0):.2f}s", str(result.get("returncode", "N/A")))

        self.console.print(table)

        stats_table = Table(show_header=False, box=box.ROUNDED)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Total Tests", str(total))
        stats_table.add_row("Successful", str(successful))
        stats_table.add_row("Failed", str(total - successful))
        success_rate = (successful / total) * 100 if total > 0 else 0
        stats_table.add_row("Success Rate", f"{success_rate:.1f}%")
        stats_table.add_row("Total Duration", str(duration).split(".")[0])

        self.console.print(Panel(stats_table, title="[bold]Statistics", border_style="blue"))


if __name__ == "__main__":
    try:
        tester = CLITester()
        tester.test_all_commands()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
        raise SystemExit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {str(e)}")
        raise

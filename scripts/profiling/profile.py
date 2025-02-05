import os
import subprocess
from subprocess import Popen

import typer


def profile(repo: str, memory: bool = False, extra_repos: bool = True):
    type = "mem" if memory else "cpu"
    base = f".profiles/{type}/{repo}"
    os.makedirs(base, exist_ok=True)
    output = f"{base}/raw.austin"
    compressed = f"{base}/compressed.austin"
    image = f"{base}/parse.svg"
    test = Popen(["pytest", "tests/integration/codemod/test_parse.py", "--durations=100", "-k", repo, "--extra-repos=True" if extra_repos else ""])
    try:
        command = ["sudo", "austin", "-p", str(test.pid), "-o", output]
        if memory:
            command.append("-m")
        subprocess.run(command)
        for_flamegraph = output
        # try:
        #     print("Compressing output")
        #     subprocess.run(["austin-compress", output, compressed], check=True)
        #     for_flamegraph = compressed
        # except subprocess.CalledProcessError as e:
        #     print("Error compressing:", e)
        if compressed == for_flamegraph:
            print("Opening image with speedscope")
            os.system(f"speedscope {compressed}")
        else:
            print("Converting to svg")
            os.system(f"flamegraph.pl {for_flamegraph} > {image}")
            print("Opening image")
            os.system(f"open {image}")
    finally:
        test.kill()


def main():
    typer.run(profile)


if __name__ == "__main__":
    main()

from collections.abc import Callable


class Codemod3:
    execute: Callable | None = None

    def __init__(self, name: str | None = None, execute: Callable | None = None, *args, **kwargs):
        self.name = name
        if execute:
            self.execute = execute

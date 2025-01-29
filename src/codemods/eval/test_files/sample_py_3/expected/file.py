from decorators import decorator_function


@decorator_function
def foo_bar() -> int:
    return 1


@decorator_function
def foo_char() -> int:
    return 2


def bar() -> int:
    return 3

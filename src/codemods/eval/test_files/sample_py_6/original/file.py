def foo_bar() -> int:
    return 1


def foo_char() -> int:
    return 2


def unused_func() -> int:
    return 3


def bar():
    return foo_bar() + foo_char()

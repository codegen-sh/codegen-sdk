def bar_bar() -> int:
    return 1


def bar_char() -> int:
    return 2


def bar():
    return bar_bar() + bar_char()

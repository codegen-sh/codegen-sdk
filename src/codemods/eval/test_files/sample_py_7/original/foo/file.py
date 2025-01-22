from enum import Enum


class Foo(Enum):
    BAR = 1
    CHAR = 2


def foo_bar():
    return 1


def foo_char():
    return 2


def bar():
    return foo_bar() + foo_char()


def foo_enum():
    return Foo.BAR

import pytest

from codegen_sdk.codebase.factory.get_session import get_codebase_session
from codegen_sdk.core.expressions.binary_expression import BinaryExpression
from codegen_sdk.python import PyFile


def test_all_binary_expression_types(tmpdir):
    # language=python
    content = """
a = 1 + 2
b = 3 - 4
c = 5 * 6
d = 7 / 8
e = 9 % 10
f = 11 ** 12
g = 13 // 14
h = 15 & 16
i = 17 | 18
j = 19 ^ 20
k = 21 << 22
l = 23 >> 24
m = 25 == 26
n = 27 != 28
o = 29 > 30
p = 31 < 32
q = 33 >= 34
r = 35 <= 36
s = 37 and 38
t = 39 or 40
u = 41 is 42
v = 43 is not 44
w = 45 in 46
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        assert all([isinstance(var.value, BinaryExpression) for var in file.global_vars])

        assert file.get_global_var("a").value.left.source == "1"
        assert file.get_global_var("a").value.right.source == "2"
        assert file.get_global_var("a").value.operator.source == "+"

        assert file.get_global_var("b").value.left.source == "3"
        assert file.get_global_var("b").value.right.source == "4"
        assert file.get_global_var("b").value.operator.source == "-"

        assert file.get_global_var("c").value.left.source == "5"
        assert file.get_global_var("c").value.right.source == "6"
        assert file.get_global_var("c").value.operator.source == "*"

        assert file.get_global_var("d").value.left.source == "7"
        assert file.get_global_var("d").value.right.source == "8"
        assert file.get_global_var("d").value.operator.source == "/"

        assert file.get_global_var("e").value.left.source == "9"
        assert file.get_global_var("e").value.right.source == "10"
        assert file.get_global_var("e").value.operator.source == "%"

        assert file.get_global_var("f").value.left.source == "11"
        assert file.get_global_var("f").value.right.source == "12"
        assert file.get_global_var("f").value.operator.source == "**"

        assert file.get_global_var("g").value.left.source == "13"
        assert file.get_global_var("g").value.right.source == "14"
        assert file.get_global_var("g").value.operator.source == "//"

        assert file.get_global_var("h").value.left.source == "15"
        assert file.get_global_var("h").value.right.source == "16"
        assert file.get_global_var("h").value.operator.source == "&"

        assert file.get_global_var("i").value.left.source == "17"
        assert file.get_global_var("i").value.right.source == "18"
        assert file.get_global_var("i").value.operator.source == "|"

        assert file.get_global_var("j").value.left.source == "19"
        assert file.get_global_var("j").value.right.source == "20"
        assert file.get_global_var("j").value.operator.source == "^"

        assert file.get_global_var("k").value.left.source == "21"
        assert file.get_global_var("k").value.right.source == "22"
        assert file.get_global_var("k").value.operator.source == "<<"

        assert file.get_global_var("l").value.left.source == "23"
        assert file.get_global_var("l").value.right.source == "24"
        assert file.get_global_var("l").value.operator.source == ">>"

        assert file.get_global_var("m").value.left.source == "25"
        assert file.get_global_var("m").value.right.source == "26"
        assert file.get_global_var("m").value.operator.source == "=="

        assert file.get_global_var("n").value.left.source == "27"
        assert file.get_global_var("n").value.right.source == "28"
        assert file.get_global_var("n").value.operator.source == "!="

        assert file.get_global_var("o").value.left.source == "29"
        assert file.get_global_var("o").value.right.source == "30"
        assert file.get_global_var("o").value.operator.source == ">"

        assert file.get_global_var("p").value.left.source == "31"
        assert file.get_global_var("p").value.right.source == "32"
        assert file.get_global_var("p").value.operator.source == "<"

        assert file.get_global_var("q").value.left.source == "33"
        assert file.get_global_var("q").value.right.source == "34"
        assert file.get_global_var("q").value.operator.source == ">="

        assert file.get_global_var("r").value.left.source == "35"
        assert file.get_global_var("r").value.right.source == "36"
        assert file.get_global_var("r").value.operator.source == "<="

        assert file.get_global_var("s").value.left.source == "37"
        assert file.get_global_var("s").value.right.source == "38"
        assert file.get_global_var("s").value.operator.source == "and"

        assert file.get_global_var("t").value.left.source == "39"
        assert file.get_global_var("t").value.right.source == "40"
        assert file.get_global_var("t").value.operator.source == "or"

        assert file.get_global_var("u").value.left.source == "41"
        assert file.get_global_var("u").value.right.source == "42"
        assert file.get_global_var("u").value.operator.source == "is"

        assert file.get_global_var("v").value.left.source == "43"
        assert file.get_global_var("v").value.right.source == "44"
        assert file.get_global_var("v").value.operator.source == "is not"

        assert file.get_global_var("w").value.left.source == "45"
        assert file.get_global_var("w").value.right.source == "46"
        assert file.get_global_var("w").value.operator.source == "in"


def test_chained_binary_expressions(tmpdir):
    # language=python
    content = """
a = 1 + 2 - 3 * 4 / 5 % 6 ** 7 // 8                                 # binary operators
b = 9 == 10 != 11 < 12 > 13 <= 14 >= 15 is 16 is not 17 in 18       # comparison operators
c = True and False or False and True or False                       # boolean operators
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")

        a = file.get_global_var("a").value
        assert [x.source for x in a.elements] == ["1", "2", "3", "4", "5", "6", "7", "8"]
        assert [x.source for x in a.operators] == ["+", "-", "*", "/", "%", "**", "//"]

        b = file.get_global_var("b").value
        assert [x.source for x in b.elements] == ["9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
        assert [x.source for x in b.operators] == ["==", "!=", "<", ">", "<=", ">=", "is", "is not", "in"]

        c = file.get_global_var("c").value
        assert [x.source for x in c.elements] == ["True", "False", "False", "True", "False"]
        assert [x.source for x in c.operators] == ["and", "or", "and", "or"]


@pytest.mark.skip(reason="CG-8883: Parenthesized expressions not implemented yet")
def test_chained_multiline_binary_expressions_using_parenthesis(tmpdir):
    # language=python
    content = """
a = (1 + 2 - 3 * 4
    / 5 % 6 ** 7 // 8)
b = (9 == 10 != 11 < 12 > 13 <= 14
     >= 15 is 16 is not
     17 in [18])
c = (True and False
    or False
    and True or False)
     """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")

        a = file.get_global_var("a").value
        assert [x.source for x in a.elements] == ["1", "2", "3", "4", "5", "6", "7", "8"]
        assert [x.source for x in a.operators] == ["+", "-", "*", "/", "%", "**", "//"]

        b = file.get_global_var("b").value
        assert [x.source for x in b.elements] == ["9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
        assert [x.source for x in b.operators] == ["==", "!=", "<", ">", "<=", ">=", "is", "is not", "in"]

        c = file.get_global_var("c").value
        assert [x.source for x in c.elements] == ["True", "False", "False", "True", "False"]
        assert [x.source for x in c.operators] == ["and", "or", "and", "or"]


def test_chained_multiline_binary_expressions_using_backslash(tmpdir):
    # language=python
    content = """
a = 1 + 2 - 3 * 4 \
    / 5 % 6 ** 7 // 8
b = 9 == 10 != 11 < 12 > 13 <= 14 \
    >= 15 is 16 is not \
    17 in [18]
c = True and False \
    or False \
    and True or False
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")

        a = file.get_global_var("a").value
        assert [x.source for x in a.elements] == ["1", "2", "3", "4", "5", "6", "7", "8"]
        assert [x.source for x in a.operators] == ["+", "-", "*", "/", "%", "**", "//"]

        b = file.get_global_var("b").value
        assert [x.source for x in b.elements] == ["9", "10", "11", "12", "13", "14", "15", "16", "17", "[18]"]
        assert [x.source for x in b.operators] == ["==", "!=", "<", ">", "<=", ">=", "is", "is not", "in"]

        c = file.get_global_var("c").value
        assert [x.source for x in c.elements] == ["True", "False", "False", "True", "False"]
        assert [x.source for x in c.operators] == ["and", "or", "and", "or"]


@pytest.mark.skip(reason="CG-8886: Mixed expression groups not implemented yet")
def test_chained_mixed_binary_expressions(tmpdir):
    # language=python
    content = """
a = 1 + 2 == True != False or True and False * 12
b = 3 == (4 + 5 or False and True + (6 + 7))
c = 45 < 12 + foo
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")

        a = file.get_global_var("a").value
        assert [x.source for x in a.elements] == ["1", "2", "True", "False", "True", "False", "12"]
        assert [x.source for x in a.operators] == ["+", "==", "!=", "or", "and", "*"]

        b = file.get_global_var("b").value
        assert [x.source for x in b.elements] == ["3", "4", "5", "False", "True", "6", "7"]
        assert [x.source for x in b.operators] == ["==", "+", "or", "and", "+"]

        c = file.get_global_var("c").value
        assert [x.source for x in c.elements] == ["45", "12", "foo"]
        assert [x.source for x in c.operators] == ["<", "+"]


@pytest.mark.skip(reason="CG-8883: Parenthesized expressions not implemented yet")
def test_chained_mixed_multiline_binary_expressions_with_parenthesis(tmpdir):
    # language=python
    content = """
a = (1 + 2 == True
    != False or True
    and False * 12)
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        a = file.get_global_var("a").value
        assert [x.source for x in a.elements] == ["1", "2", "True", "False", "True", "False", "12"]
        assert [x.source for x in a.operators] == ["+", "==", "!=", "or", "and", "*"]


@pytest.mark.skip(reason="CG-8886: Mixed expression groups not implemented yet")
def test_chained_mixed_multiline_binary_expressions_with_backslash(tmpdir):
    # language=python
    content = """
a = 1 + 2 == True \
    != False or True \
    and False * 12
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        a = file.get_global_var("a").value
        assert [x.source for x in a.elements] == ["1", "2", "True", "False", "True", "False", "12"]
        assert [x.source for x in a.operators] == ["+", "==", "!=", "or", "and", "*"]

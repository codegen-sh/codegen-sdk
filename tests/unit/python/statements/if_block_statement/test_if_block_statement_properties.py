from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.core.statements.statement import StatementType
from graph_sitter.python import PyFile
from graph_sitter.python.statements.if_block_statement import PyIfBlockStatement


def test_parse_conditional_statement_from_codeblock(tmpdir) -> None:
    # language=python
    content = """
def foo():
    if a + b:
        print(a)
    elif b and c:
        print(b)
    elif (c := a + b) and True:
        print(c)
        return
    else:
        return
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        if_blocks = function.code_block.get_statements(StatementType.IF_BLOCK_STATEMENT)
        assert len(if_blocks) == 1
        statement = if_blocks[0]
        assert statement.is_if_statement and not statement.is_elif_statement and not statement.is_else_statement
        assert statement.condition.source == "a + b"
        assert len(statement.consequence_block.statements) == 1
        assert statement.consequence_block.statements[0].source == "print(a)"

        else_ifs = statement.elif_statements
        assert len(else_ifs) == 2
        assert all([x.is_elif_statement and not x.is_else_statement and not x.is_if_statement for x in else_ifs])
        assert else_ifs[0].condition.source == "b and c"
        assert else_ifs[1].condition.source == "(c := a + b) and True"
        assert len(else_ifs[0].consequence_block.statements) == 1
        assert len(else_ifs[1].consequence_block.statements) == 2
        assert else_ifs[0].consequence_block.statements[0].source == "print(b)"
        assert else_ifs[1].consequence_block.statements[0].source == "print(c)"
        assert else_ifs[1].consequence_block.statements[1].source == "return"

        else_block = statement.else_statement
        assert else_block.condition is None
        assert len(else_block.consequence_block.statements) == 1
        assert else_block.consequence_block.statements[0].source == "return"
        assert else_block.is_else_statement and not else_block.is_elif_statement and not else_block.is_if_statement


def test_parse_nested_if_statements_from_codeblock(tmpdir) -> None:
    # language=python
    content = """
def foo():
    if a:
        if b:
            print(b)
        if c:
            print(c)
        elif d:
            return
    else:
        return
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        assert len(function.code_block.get_statements(StatementType.IF_BLOCK_STATEMENT)) == 3
        assert len(function.code_block.get_statements(StatementType.IF_BLOCK_STATEMENT, function.code_block.level)) == 1
        assert len(function.code_block.get_statements(StatementType.IF_BLOCK_STATEMENT, function.code_block.level + 1)) == 3

        top_if_block = function.code_block.get_statements(StatementType.IF_BLOCK_STATEMENT, function.code_block.level)[0]
        assert len(top_if_block.elif_statements) == 0
        assert top_if_block.else_statement is not None
        assert top_if_block.is_if_statement and not top_if_block.is_elif_statement and not top_if_block.is_else_statement

        nested_if_blocks: list[PyIfBlockStatement] = top_if_block.consequence_block.get_statements(StatementType.IF_BLOCK_STATEMENT)
        assert len(nested_if_blocks) == 2
        assert all(x.is_if_statement and not x.is_elif_statement and not x.is_else_statement for x in nested_if_blocks)
        assert nested_if_blocks[0].condition.source == "b"
        assert len(nested_if_blocks[0].elif_statements) == 0
        assert nested_if_blocks[0].else_statement is None

        assert nested_if_blocks[1].condition.source == "c"
        assert len(nested_if_blocks[1].elif_statements) == 1
        assert nested_if_blocks[1].else_statement is None


def test_get_alternative_if_blocks_from_codeblock(tmpdir) -> None:
    # language=python
    content = """
def foo():
    if a:
        print(a)
    elif b:
        print(b)
    elif c:
        print(c)
    else:
        return
    """
    with get_codebase_session(tmpdir=tmpdir, files={"dir/file1.py": content}) as codebase:
        file: PyFile = codebase.get_file("dir/file1.py")
        function = file.get_function("foo")
        if_blocks = function.code_block.get_statements(StatementType.IF_BLOCK_STATEMENT)
        assert len(if_blocks) == 1
        alt_blocks = if_blocks[0].alternative_blocks
        assert len(alt_blocks) == 3
        assert len(if_blocks[0].alternative_blocks) == 3
        assert len(if_blocks[0].elif_statements) == 2
        assert all(x.is_elif_statement and not x.is_else_statement and not x.is_if_statement for x in if_blocks[0].elif_statements)
        assert if_blocks[0].else_statement is not None
        assert if_blocks[0].else_statement.is_else_statement

        assert len(alt_blocks[0].alternative_blocks) == 2
        assert len(alt_blocks[0].elif_statements) == 1
        assert alt_blocks[0].else_statement is not None

        assert len(alt_blocks[1].alternative_blocks) == 1
        assert len(alt_blocks[1].elif_statements) == 0
        assert alt_blocks[1].else_statement is not None

        assert len(alt_blocks[2].alternative_blocks) == 0
        assert len(alt_blocks[2].elif_statements) == 0
        assert alt_blocks[2].else_statement is None

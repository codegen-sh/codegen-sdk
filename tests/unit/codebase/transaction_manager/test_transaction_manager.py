from os import PathLike
from pathlib import Path

from graph_sitter.codebase.factory.get_session import get_codebase_session
from graph_sitter.codebase.transaction_manager import (
    TransactionError,
    TransactionManager,
)
from graph_sitter.codebase.transactions import EditTransaction, InsertTransaction, RemoveTransaction


class MockFile:
    def __init__(self, path: PathLike) -> None:
        self.content = "x" * 100
        self.content_bytes = bytes(self.content, "utf-8")
        self.path = Path(path)


def test_edit_base_case(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create simple transaction
    t1 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")
    transaction_manager.add_transaction(t1)

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_remove_base_case(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create simple transaction
    t1 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))
    transaction_manager.add_transaction(t1)

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_insert_base_case(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create simple transaction
    t1 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="")
    transaction_manager.add_transaction(t1)

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_edit_ordering(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")
    t2 = EditTransaction(start_byte=5, end_byte=10, file=MockFile(FILENAME), new_content="")
    t3 = EditTransaction(start_byte=10, end_byte=15, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)
    transaction_manager.add_transaction(t2)
    transaction_manager.add_transaction(t3)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 3
    assert transaction_manager.queued_transactions[FILENAME][0] is t3
    assert transaction_manager.queued_transactions[FILENAME][1] is t2
    assert transaction_manager.queued_transactions[FILENAME][2] is t1

    # Create more transactions
    t4 = EditTransaction(start_byte=20, end_byte=25, file=MockFile(FILENAME), new_content="")
    t5 = EditTransaction(start_byte=15, end_byte=20, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t4)
    transaction_manager.add_transaction(t5)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 5
    assert transaction_manager.queued_transactions[FILENAME][0] is t4
    assert transaction_manager.queued_transactions[FILENAME][1] is t5
    assert transaction_manager.queued_transactions[FILENAME][2] is t3
    assert transaction_manager.queued_transactions[FILENAME][3] is t2
    assert transaction_manager.queued_transactions[FILENAME][4] is t1


def test_remove_ordering(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))
    t2 = RemoveTransaction(start_byte=5, end_byte=10, file=MockFile(FILENAME))
    t3 = RemoveTransaction(start_byte=10, end_byte=15, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)
    transaction_manager.add_transaction(t2)
    transaction_manager.add_transaction(t3)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 3
    assert transaction_manager.queued_transactions[FILENAME][0] is t3
    assert transaction_manager.queued_transactions[FILENAME][1] is t2
    assert transaction_manager.queued_transactions[FILENAME][2] is t1

    # Create more transactions
    t4 = RemoveTransaction(start_byte=20, end_byte=25, file=MockFile(FILENAME))
    t5 = RemoveTransaction(start_byte=15, end_byte=20, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t4)
    transaction_manager.add_transaction(t5)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 5
    assert transaction_manager.queued_transactions[FILENAME][0] is t4
    assert transaction_manager.queued_transactions[FILENAME][1] is t5
    assert transaction_manager.queued_transactions[FILENAME][2] is t3
    assert transaction_manager.queued_transactions[FILENAME][3] is t2
    assert transaction_manager.queued_transactions[FILENAME][4] is t1


def test_insert_ordering(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="a")
    t2 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="b")
    t3 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="c")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)
    transaction_manager.add_transaction(t2)
    transaction_manager.add_transaction(t3)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 3
    assert transaction_manager.queued_transactions[FILENAME][0] is t3
    assert transaction_manager.queued_transactions[FILENAME][1] is t2
    assert transaction_manager.queued_transactions[FILENAME][2] is t1

    # Create more transactions
    t4 = InsertTransaction(insert_byte=5, file=MockFile(FILENAME), new_content="d")
    t5 = InsertTransaction(insert_byte=5, file=MockFile(FILENAME), new_content="e")
    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t4)
    transaction_manager.add_transaction(t5)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 5
    assert transaction_manager.queued_transactions[FILENAME][0] is t5
    assert transaction_manager.queued_transactions[FILENAME][1] is t4
    assert transaction_manager.queued_transactions[FILENAME][2] is t3
    assert transaction_manager.queued_transactions[FILENAME][3] is t2
    assert transaction_manager.queued_transactions[FILENAME][4] is t1


def test_dedupe(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()
    # Create transactions
    t1 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="arg")
    t2 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="arg")
    t3 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="arg")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1, dedupe=True)
    transaction_manager.add_transaction(t2, dedupe=True)
    transaction_manager.add_transaction(t3, dedupe=True)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_edit_conflict(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="a")
    t2 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="b")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
        assert False, "Expected TransactionError"
    except TransactionError:
        pass


def test_remove_conflict(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))
    t2 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
    except TransactionError:
        assert False, "Should not raise TransactionError"

    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_edit_conflict_subset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = EditTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME), new_content="")
    t2 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
        assert False, "Expected TransactionError"
    except TransactionError:
        pass


def test_remove_conflict_subset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME))
    t2 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
    except TransactionError:
        assert False, "Should not raise TransactionError"

    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t2


def test_edit_remove_conflict_subset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = EditTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME), new_content="")
    t2 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
    except TransactionError:
        assert False, "Should not raise TransactionError"

    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t2


def test_remove_edit_conflict_subset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME))
    t2 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
        assert False, "Expected TransactionError"
    except TransactionError:
        pass


def test_insert_remove_conflict_subset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = InsertTransaction(insert_byte=1, file=MockFile(FILENAME), new_content="")
    t2 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
    except TransactionError:
        assert False, "Should not raise TransactionError"

    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t2


def test_insert_edit_conflict_subset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = InsertTransaction(insert_byte=1, file=MockFile(FILENAME), new_content="")
    t2 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
        assert False, "Expected TransactionError"
    except TransactionError:
        pass


def test_edit_conflict_superset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")
    t2 = EditTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
        assert False, "Expected TransactionError"
    except TransactionError:
        pass


def test_remove_conflict_superset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))
    t2 = RemoveTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
    except TransactionError:
        assert False, "Should not raise TransactionError"

    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_edit_remove_conflict_superset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")
    t2 = RemoveTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
        assert False, "Expected TransactionError"
    except TransactionError:
        pass


def test_remove_edit_conflict_superset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))
    t2 = EditTransaction(start_byte=1, end_byte=4, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
    except TransactionError:
        assert False, "Should not raise TransactionError"

    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_edit_insert_conflict_superset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = EditTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME), new_content="")
    t2 = InsertTransaction(insert_byte=1, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
        assert False, "Expected TransactionError"
    except TransactionError:
        pass


def test_remove_insert_conflict_superset(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=0, end_byte=5, file=MockFile(FILENAME))
    t2 = InsertTransaction(insert_byte=1, file=MockFile(FILENAME), new_content="")

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)

    try:
        transaction_manager.add_transaction(t2)
    except TransactionError:
        assert False, "Should not raise TransactionError"

    assert len(transaction_manager.queued_transactions[FILENAME]) == 1
    assert transaction_manager.queued_transactions[FILENAME][0] is t1


def test_remove_multi_conflict(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = RemoveTransaction(start_byte=0, end_byte=4, file=MockFile(FILENAME))
    t2 = InsertTransaction(insert_byte=4, file=MockFile(FILENAME), new_content="")
    t3 = EditTransaction(start_byte=4, end_byte=8, file=MockFile(FILENAME), new_content="")
    t4 = InsertTransaction(insert_byte=8, file=MockFile(FILENAME), new_content="")
    t5 = RemoveTransaction(start_byte=8, end_byte=12, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)
    transaction_manager.add_transaction(t2)
    transaction_manager.add_transaction(t3)
    transaction_manager.add_transaction(t4)
    transaction_manager.add_transaction(t5)
    transaction_manager.sort_transactions()

    # Create conflicting remove
    t6 = RemoveTransaction(start_byte=2, end_byte=10, file=MockFile(FILENAME))

    # Create non-conflicting remove
    t7 = RemoveTransaction(start_byte=12, end_byte=16, file=MockFile(FILENAME))

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t6)
    transaction_manager.add_transaction(t7)
    transaction_manager.sort_transactions()

    # Check if conflicting remove is added
    assert len(transaction_manager.queued_transactions[FILENAME]) == 2
    assert transaction_manager.queued_transactions[FILENAME][0] is t7
    assert transaction_manager.queued_transactions[FILENAME][1] is t6


def test_priority(tmpdir) -> None:
    FILENAME = Path("filename")

    # Create TransactionManager
    transaction_manager = TransactionManager()

    # Create transactions
    t1 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="a", priority=3)
    t2 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="b", priority=2)
    t3 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="c", priority=1)

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t1)
    transaction_manager.add_transaction(t2)
    transaction_manager.add_transaction(t3)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 3
    assert transaction_manager.queued_transactions[FILENAME][0] is t3
    assert transaction_manager.queued_transactions[FILENAME][1] is t2
    assert transaction_manager.queued_transactions[FILENAME][2] is t1

    # Create more transactions
    t4 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="d", priority=4)
    t5 = InsertTransaction(insert_byte=0, file=MockFile(FILENAME), new_content="e", priority=5)

    # Add transactions to TransactionManager
    transaction_manager.add_transaction(t4)
    transaction_manager.add_transaction(t5)
    transaction_manager.sort_transactions()

    # Verify
    assert len(transaction_manager.queued_transactions[FILENAME]) == 5
    assert transaction_manager.queued_transactions[FILENAME][0] is t3
    assert transaction_manager.queued_transactions[FILENAME][1] is t2
    assert transaction_manager.queued_transactions[FILENAME][2] is t1
    assert transaction_manager.queued_transactions[FILENAME][3] is t4
    assert transaction_manager.queued_transactions[FILENAME][4] is t5


def test_edit_suffix(tmpdir) -> None:
    FILENAME = "test.py"
    # language=python
    CONTENT = """
def content():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: CONTENT}) as codebase:
        file = codebase.get_file("test.py")
        file.edit(file.content + "Something")
        file.get_function("content").remove()
        assert len(file.transaction_manager.queued_transactions[tmpdir / FILENAME]) == 2
    # language=python
    assert file.content == """\n\nSomething"""


def test_edit_prefix(tmpdir) -> None:
    FILENAME = "test.py"
    # language=python
    CONTENT = """
def content():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: CONTENT}) as codebase:
        file = codebase.get_file("test.py")
        file.edit(file.content + "Something")
        file.get_function("content").remove()
        assert len(file.transaction_manager.queued_transactions[tmpdir / FILENAME]) == 2
    # language=python
    assert file.content == """\n\nSomething"""


def test_edit_prefix_suffix(tmpdir) -> None:
    FILENAME = "test.py"
    # language=python
    CONTENT = """
def content():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: CONTENT}) as codebase:
        for file in codebase.files:
            print(file.file_path)
        file = codebase.get_file("test.py")
        file.edit(file.content + "Something")
        file.get_function("content").remove()
        file.edit("Something" + file.content)
        assert len(file.transaction_manager.queued_transactions[tmpdir / FILENAME]) == 3
    # language=python
    assert file.content == """Something\n\nSomething"""


def test_edit_prefix_suffix_single(tmpdir) -> None:
    FILENAME = "test.py"
    # language=python
    CONTENT = """
def content():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: CONTENT}) as codebase:
        file = codebase.get_file("test.py")
        file.get_function("content").remove()
        file.edit("Something" + file.content + "Something")
        assert len(file.transaction_manager.queued_transactions[tmpdir / FILENAME]) == 3
    # language=python
    assert file.content == """Something\n\nSomething"""


def test_edit_prefix_ordering(tmpdir) -> None:
    FILENAME = "test.py"
    # language=python
    CONTENT = """
def content():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, files={FILENAME: CONTENT}) as codebase:
        file = codebase.get_file("test.py")
        file.edit("Something" + file.content + "SomethignElse")
        file.insert_before("Ok", newline=False)
        file.get_function("content").remove()
        file.edit(file.content + "Something")
        queue = file.transaction_manager.queued_transactions[tmpdir / FILENAME]
        assert len(queue) == 5
        assert isinstance(queue[0], InsertTransaction)
        assert isinstance(queue[1], InsertTransaction)
        assert isinstance(queue[2], InsertTransaction)
        assert queue[2].new_content == "Ok"
        assert isinstance(queue[3], RemoveTransaction)
        assert isinstance(queue[4], InsertTransaction)

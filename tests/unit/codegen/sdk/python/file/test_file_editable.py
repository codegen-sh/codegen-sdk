from codegen.sdk.codebase.factory.get_session import get_codebase_session


def test_file_find_string_literals_fuzzy_match(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        matches = file.find_string_literals(["b", "3"], fuzzy_match=True)
        assert len(matches) == 4
        assert set([m.source for m in matches]) == {'"abc"', '"123"', '"cba"', '"321"'}

        my_class = codebase.get_symbol("MyClass1")
        matches = my_class.find_string_literals(["b", "3"], fuzzy_match=True)
        assert len(matches) == 4
        assert set([m.source for m in matches]) == {'"abc"', '"123"', '"cba"', '"321"'}

        foo = my_class.get_method("foo")
        matches = foo.find_string_literals(["b", "3"], fuzzy_match=True)
        assert len(matches) == 2
        assert set([m.source for m in matches]) == {'"abc"', '"123"'}


def test_file_find_string_literals_exact_match_no_match(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        matches = file.find_string_literals(["b", "3"])
        assert len(matches) == 0


def test_file_find_string_literals_exact_match_has_match(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        matches = file.find_string_literals(["abc", "123"])
        assert len(matches) == 2
        assert set([m.source for m in matches]) == {'"abc"', '"123"'}

        my_class = codebase.get_symbol("MyClass1")
        matches = my_class.find_string_literals(["abc", "123"])
        assert len(matches) == 2
        assert set([m.source for m in matches]) == {'"abc"', '"123"'}

        foo = my_class.get_method("foo")
        matches = foo.find_string_literals(["abc", "123"])
        assert len(matches) == 2
        assert set([m.source for m in matches]) == {'"abc"', '"123"'}


def test_file_find(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        matches = file.find(["b"])
        assert len(matches) == 6
        assert set([m.source for m in matches]) == {"abc", "b", "bar", "cba"}


def test_file_search(tmpdir) -> None:
    # language=python
    content = """
class MyClass1:
    def foo(self):
        abc = "abc"
        b = "123"

    def bar(self):
        cba = "cba"
        d = "321"

    def hello(self):
        print("hellooo!")

    def world(self):
        print("world!")
    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        five_char_pattern = r"\b\w{5}\b"

        matches = file.search(five_char_pattern)
        assert len(matches) == 6
        assert set([m.source for m in matches]) == {"class", "hello", "print", "world", "world!"}


def test_file_search_exclude_comments(tmpdir) -> None:
    """Make sure that we can exclude comments from the search results."""
    # language=python
    content = """
def test():
    '''CAPS_INSIDE_MULTILINE_COMMENT'''
    SHOULD_MATCH_LITERAL = 123
    shouldnt_match_comment = 123 # CAPS_INSIDE_COMMENT
    shouldnt_match_string = "CAPS_INSIDE_STRING"

    """
    with get_codebase_session(tmpdir=tmpdir, files={"file.py": content}) as codebase:
        file = codebase.get_file("file.py")
        regex_pattern = r"\b[A-Z_]+\b"

        # =====[ Test with neither ]=====
        matches = file.search(regex_pattern, include_strings=False, include_comments=False)
        assert len(matches) == 1

        # =====[ Test with include_comments=True ]=====
        matches = file.search(regex_pattern, include_strings=False, include_comments=True)
        assert len(matches) == 2

        # =====[ Test with include_strings=True ]=====
        matches = file.search(regex_pattern, include_strings=True, include_comments=False)
        assert len(matches) == 3

        # =====[ Test with both include_strings=True and include_comments=True ]=====
        matches = file.search(regex_pattern, include_strings=True, include_comments=True)
        assert len(matches) == 4

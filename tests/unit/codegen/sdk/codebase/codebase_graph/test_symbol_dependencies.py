from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ProgrammingLanguage


def test_get_symbol_dependencies_python_basic(tmpdir):
    """Test basic Python symbol dependencies with default depth."""
    py_code = """
class BaseClass:
    def base_method(self):
        pass

class ChildClass(BaseClass):
    def child_method(self):
        self.base_method()

def helper_function():
    return ChildClass()

def main_function():
    obj = helper_function()
    obj.child_method()
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={"test.py": py_code}) as G:
        # Get the main function and check its dependencies
        main_func = G.get_function("main_function")
        deps = G.get_symbol_dependencies(main_func)

        # main_function should depend on helper_function
        assert main_func in deps
        assert len(deps[main_func]) == 1
        assert deps[main_func][0].name == "helper_function"

        # helper_function should depend on ChildClass
        helper_func = deps[main_func][0]
        assert helper_func in deps
        assert len(deps[helper_func]) == 1
        assert deps[helper_func][0].name == "ChildClass"


def test_get_symbol_dependencies_python_max_depth(tmpdir):
    """Test Python symbol dependencies with different max_depth values."""
    py_code = """
class A:
    def method_a(self):
        pass

class B(A):
    def method_b(self):
        self.method_a()

class C(B):
    def method_c(self):
        self.method_b()

def use_c():
    return C()
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={"test.py": py_code}) as G:
        use_c_func = G.get_function("use_c")

        # With depth 1, should only see direct dependency on C
        deps_depth1 = G.get_symbol_dependencies(use_c_func, max_depth=1)
        assert len(deps_depth1) == 2  # use_c and C
        assert len(deps_depth1[use_c_func]) == 1
        assert deps_depth1[use_c_func][0].name == "C"

        # With depth 2, should see C and its dependency on B
        deps_depth2 = G.get_symbol_dependencies(use_c_func, max_depth=2)
        c_class = deps_depth1[use_c_func][0]
        assert c_class in deps_depth2
        assert len(deps_depth2[c_class]) == 1
        assert deps_depth2[c_class][0].name == "B"

        # With depth 3, should see the full chain use_c -> C -> B -> A
        deps_depth3 = G.get_symbol_dependencies(use_c_func, max_depth=3)
        b_class = deps_depth2[c_class][0]
        assert b_class in deps_depth3
        assert len(deps_depth3[b_class]) == 1
        assert deps_depth3[b_class][0].name == "A"


def test_get_symbol_dependencies_typescript_basic(tmpdir):
    """Test basic TypeScript symbol dependencies."""
    ts_code = """
interface ILogger {
    log(message: string): void;
}

class ConsoleLogger implements ILogger {
    log(message: string) {
        console.log(message);
    }
}

class LoggerFactory {
    static createLogger(): ILogger {
        return new ConsoleLogger();
    }
}

function logMessage(message: string) {
    const logger = LoggerFactory.createLogger();
    logger.log(message);
}
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.TYPESCRIPT, files={"test.ts": ts_code}) as G:
        log_msg_func = G.get_function("logMessage")
        deps = G.get_symbol_dependencies(log_msg_func)

        # logMessage should depend on LoggerFactory
        assert log_msg_func in deps
        assert len(deps[log_msg_func]) == 1
        assert deps[log_msg_func][0].name == "LoggerFactory"

        # LoggerFactory should depend on ILogger and ConsoleLogger
        factory_class = deps[log_msg_func][0]
        assert factory_class in deps
        factory_deps = deps[factory_class]
        assert len(factory_deps) == 2
        assert {d.name for d in factory_deps} == {"ILogger", "ConsoleLogger"}


def test_get_symbol_dependencies_cyclic(tmpdir):
    """Test handling of cyclic dependencies."""
    py_code = """
class A:
    def method_a(self):
        return B()

class B:
    def method_b(self):
        return A()

def use_both():
    a = A()
    b = B()
    return a.method_a(), b.method_b()
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={"test.py": py_code}) as G:
        use_both_func = G.get_function("use_both")
        deps = G.get_symbol_dependencies(use_both_func)

        # use_both should depend on both A and B
        assert use_both_func in deps
        assert len(deps[use_both_func]) == 2
        assert {d.name for d in deps[use_both_func]} == {"A", "B"}

        # A should depend on B
        a_class = next(d for d in deps[use_both_func] if d.name == "A")
        assert a_class in deps
        assert len(deps[a_class]) == 1
        assert deps[a_class][0].name == "B"

        # B should depend on A
        b_class = next(d for d in deps[use_both_func] if d.name == "B")
        assert b_class in deps
        assert len(deps[b_class]) == 1
        assert deps[b_class][0].name == "A"


def test_get_symbol_dependencies_empty(tmpdir):
    """Test handling of symbols with no dependencies."""
    py_code = """
class EmptyClass:
    pass

def empty_function():
    pass
"""
    with get_codebase_session(tmpdir=tmpdir, programming_language=ProgrammingLanguage.PYTHON, files={"test.py": py_code}) as G:
        empty_class = G.get_class("EmptyClass")
        empty_func = G.get_function("empty_function")

        # Both symbols should have no dependencies
        class_deps = G.get_symbol_dependencies(empty_class)
        assert len(class_deps) == 1
        assert empty_class in class_deps
        assert len(class_deps[empty_class]) == 0

        func_deps = G.get_symbol_dependencies(empty_func)
        assert len(func_deps) == 1
        assert empty_func in func_deps
        assert len(func_deps[empty_func]) == 0

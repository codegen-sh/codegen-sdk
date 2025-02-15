from __future__ import annotations

from typing import TYPE_CHECKING

from codegen.sdk.core.autocommit import reader, writer
from codegen.sdk.core.expressions import Name
from codegen.sdk.core.statements.statement import StatementType

if TYPE_CHECKING:
    from codegen.sdk.core.detached_symbols.function_call import FunctionCall
    from codegen.sdk.core.statements.statement import Statement


class TSPromiseChain:
    """A class representing a TypeScript Promise chain.

    This class parses and handles Promise chains in TypeScript code, including .then(), .catch(), and .finally() chains.
    It provides functionality to convert Promise chains to async/await syntax.

    Attributes:
        base_chain (List[FunctionCall]): The initial function calls before any .then() calls
        then_chain (List[FunctionCall]): The sequence of .then() calls in the Promise chain
        catch_call (Optional[FunctionCall]): The .catch() call if present
        finally_call (Optional[FunctionCall]): The .finally() call if present
        after_promise_chain (List[FunctionCall]): Any function calls after the Promise chain
        base_attribute (Name): The base attribute that starts the Promise chain
        parent_statement (Statement): The parent statement containing this Promise chain
        declared_vars (Set[str]): Set of variables declared in the Promise chain
        base_indent (str): The base indentation level for code formatting
    """

    def __init__(self, attribute_chain: list[FunctionCall] | Name, inplace_edit: bool = True) -> None:
        """Initialize a TSPromiseChain instance.

        Args:
            attribute_chain: A list of function calls or a Name object representing the Promise chain
        """
        self.base_chain: list[FunctionCall]
        self.then_chain: list[FunctionCall]
        self.catch_call: FunctionCall | None
        self.finally_call: FunctionCall | None
        self.after_promise_chain: list[FunctionCall]
        self.inplace_edit: bool = inplace_edit

        (self.base_chain, self.then_chain, self.catch_call, self.finally_call, self.after_promise_chain) = self._parse_chain(attribute_chain)

        self.base_attribute: Name = self.base_chain[-1].parent.object
        self.parent_statement: Statement = self.base_chain[0].parent_statement
        self.declared_vars: set[str] = set()
        self.base_indent: str = " " * self.parent_statement._get_indent() if hasattr(self, "_get_indent") else "    "

    @reader
    def _parse_chain(self, attribute_chain: list[FunctionCall] | Name) -> tuple[list[FunctionCall], list[FunctionCall], FunctionCall | None, FunctionCall | None, list[FunctionCall]]:
        """Parse the Promise chain into its component parts.

        Args:
            attribute_chain: The chain of function calls to parse

        Returns:
            A tuple containing:
                - base_chain: Initial function calls
                - then_chain: .then() calls
                - catch_call: .catch() call if present
                - finally_call: .finally() call if present
                - after_promise_chain: Calls after the Promise chain
        """
        base_chain: list[FunctionCall] = []
        then_chain: list[FunctionCall] = []
        catch_call: FunctionCall | None = None
        finally_call: FunctionCall | None = None
        after_promise_chain: list[FunctionCall] = []

        in_then_chain: bool = False
        promise_chain_ended: bool = False

        for attribute in attribute_chain:
            if not isinstance(attribute, Name):
                if attribute.name == "then":
                    in_then_chain = True
                    then_chain.append(attribute)
                elif attribute.name == "catch":
                    catch_call = attribute
                    in_then_chain = False
                elif attribute.name == "finally":
                    finally_call = attribute
                    in_then_chain = False
                    promise_chain_ended = True
                else:
                    if promise_chain_ended:
                        after_promise_chain.append(attribute)
                    elif in_then_chain:
                        then_chain.append(attribute)
                    else:
                        base_chain.append(attribute)
            else:
                if promise_chain_ended:
                    after_promise_chain.append(attribute)
                elif in_then_chain:
                    then_chain.append(attribute)
                else:
                    base_chain.append(attribute)

        return base_chain, then_chain, catch_call, finally_call, after_promise_chain

    @property
    @reader
    def is_return_statement(self) -> bool:
        """Check if the parent statement is a return statement.

        Returns:
            bool: True if the parent statement is a return statement
        """
        return hasattr(self.parent_statement, "statement_type") and self.parent_statement.statement_type == StatementType.RETURN_STATEMENT

    @property
    @reader
    def is_assignment(self) -> bool:
        """Check if the parent statement is an assignment.

        Returns:
            bool: True if the parent statement is an assignment
        """
        return hasattr(self.parent_statement, "statement_type") and self.parent_statement.statement_type == StatementType.ASSIGNMENT

    @property
    @reader
    def assigned_var(self) -> str | None:
        """Get the variable being assigned to in an assignment statement.

        Returns:
            Optional[str]: The name of the variable being assigned to, or None if not an assignment
        """
        return self.parent_statement.left if self.is_assignment else None

    @reader
    def get_next_call_params(self, call: FunctionCall | None) -> list[str]:
        """Get parameters from the next then/catch/finally call.

        Args:
            call: The function call to extract parameters from

        Returns:
            List[str]: List of parameter names from the call
        """
        if not (call and hasattr(call.args[0].value, "parameters")):
            return []
        return [p.source for p in call.args[0].value.parameters]

    @reader
    def _needs_anonymous_function(self, arrow_fn: FunctionCall) -> bool:
        """Determine if we need to use an anonymous function wrapper.

        Returns True if:
        1. There are multiple return statements
        2. The code block has complex control flow (if/else, loops, etc)

        Args:
            arrow_fn: The arrow function to analyze

        Returns:
            bool: True if an anonymous function wrapper is needed
        """
        statements = arrow_fn.code_block.get_statements()
        return_count = sum(1 for stmt in statements if stmt.statement_type == StatementType.RETURN_STATEMENT)
        return return_count > 1

    @reader
    def format_param_assignment(self, params: list[str], base_expr: str, declare: bool = True) -> str:
        """Format parameter assignment with proper let declaration if needed.

        Args:
            params: List of parameter names to assign
            base_expr: The base expression to assign from
            declare: Whether to declare new variables with 'let'

        Returns:
            str: Formatted parameter assignment string
        """
        if not params:
            return base_expr

        if len(params) > 1:
            param_str = ", ".join(params)
            if declare and not any(p in self.declared_vars for p in params):
                self.declared_vars.update(params)
                return f"let [{param_str}] = {base_expr}"
            return f"[{param_str}] = {base_expr}"
        else:
            param = params[0]
            if declare and param not in self.declared_vars:
                self.declared_vars.add(param)
                return f"let {param} = {base_expr}"
            return f"{param} = {base_expr}"

    @reader
    def format_base_call(self, removed_middle: bool = False) -> str:
        """Format the base promise call.

        Args:
            removed_middle: Whether middle parts of the chain were removed

        Returns:
            str: Formatted base call string
        """
        new_handle = f"await {self.base_attribute.extended_source};" if "await" not in self.base_attribute.extended_source else f"{self.base_attribute.extended_source};"
        next_params = self.get_next_call_params(self.then_chain[0])
        if next_params:
            new_handle = self.format_param_assignment(next_params, new_handle)
        return new_handle

    @reader
    def format_arrow_function(self, call: FunctionCall, next_call: FunctionCall | None = None) -> str:
        """Format a then/catch/finally arrow function.

        Args:
            call: The function call to format
            next_call: The next function call in the chain, if any

        Returns:
            str: Formatted arrow function code
        """
        arrow_fn = call.args[0].value
        formatted_statements = []

        if call.name == "catch":
            error_param = arrow_fn.parameters[0].source if hasattr(arrow_fn, "parameters") and arrow_fn.parameters else ""
            formatted_statements.append(f"{self.base_indent}}} catch({error_param}) {{")
        elif call.name == "finally":
            formatted_statements.append(f"{self.base_indent}}} finally {{")

        statements = arrow_fn.code_block.statements
        for stmt in statements:
            formatted_stmt = self.format_statement(stmt, next_call)
            formatted_statements.append(f"{self.base_indent}{formatted_stmt}")

        return "\n".join(formatted_statements) + "\n"

    @reader
    def format_statement(self, stmt: Statement, next_call: FunctionCall | None = None, is_last_block: bool = False) -> str:
        """Format a single statement within an arrow function.

        Args:
            stmt: The statement to format
            next_call: The next function call in the chain, if any
            is_last_block: Whether this is the last block in the chain

        Returns:
            str: Formatted statement code
        """
        if hasattr(stmt, "value") and hasattr(stmt.value, "code_block"):
            if self._needs_anonymous_function(stmt.value):
                return self._format_anonymous_function(stmt.value, next_call)

        if is_last_block and stmt.statement_type == StatementType.RETURN_STATEMENT:
            return self.format_last_return(stmt, is_last_block=True)
        if stmt.statement_type == StatementType.RETURN_STATEMENT:
            return_value = stmt.source[7:].strip()
            next_params = self.get_next_call_params(next_call)
            if next_params:
                return self.format_param_assignment(next_params, f"await {return_value}")
            return f"await {return_value}"

        stmt_source = stmt.source.strip()
        return stmt_source.rstrip(";") + ";"

    @reader
    def parse_last_then_block(self, call: FunctionCall, custom_var_name: str | None = None) -> str:
        """Parse the last .then() block in the chain.

        Args:
            call: The last .then() call to parse
            custom_var_name: Optional custom variable name for assignment

        Returns:
            str: Formatted code for the last .then() block
        """
        arrow_fn = call.args[0].value
        statements = arrow_fn.code_block.statements

        return_stmt = None
        for stmt in reversed(statements):
            if stmt.statement_type == StatementType.RETURN_STATEMENT:
                return_stmt = stmt
                break

        if self._needs_anonymous_function(arrow_fn):
            return self._format_anonymous_function(arrow_fn, custom_var_name=custom_var_name)

        if self._is_implicit_return(arrow_fn):
            return self._handle_last_block_implicit_return(statements, custom_var_name=custom_var_name)
        else:
            formatted_statements = []
            for stmt in statements:
                if stmt == return_stmt:
                    return_value = self._handle_last_block_normal_return(stmt, custom_var_name=custom_var_name)
                    formatted_statements.append(return_value)
                else:
                    formatted_statements.append(stmt.source.strip())
            return "\n".join(formatted_statements)

    @reader
    def _handle_last_block_normal_return(self, stmt: Statement, is_catch: bool = False, custom_var_name: str | None = None) -> str:
        """Handle a normal return statement in the last block of a Promise chain.

        Args:
            stmt: The return statement to handle
            is_catch: Whether this is in a catch block
            custom_var_name: Optional custom variable name for assignment

        Returns:
            str: Formatted return statement code
        """
        return_value = stmt.source[7:].strip()  # Remove 'return ' prefix

        var_name = custom_var_name if custom_var_name else self.assigned_var
        if var_name:
            return self.format_param_assignment([var_name], return_value)
        elif self.is_return_statement:
            if is_catch:
                return f"throw {return_value}"
            else:
                return f"return {return_value}"
        else:
            if is_catch:
                return f"throw {return_value}"
            else:
                return f"await {return_value}"

    @reader
    def _handle_last_block_implicit_return(self, statements: list[Statement], is_catch: bool = False, custom_var_name: str | None = None) -> str:
        """Handle an implicit return in the last block of a Promise chain.

        Args:
            statements: The statements in the block
            is_catch: Whether this is in a catch block
            custom_var_name: Optional custom variable name for assignment

        Returns:
            str: Formatted implicit return code
        """
        stmt_source = statements[0].source.strip()
        var_name = custom_var_name if custom_var_name else self.assigned_var

        if var_name:
            return self.format_param_assignment([var_name], stmt_source)
        if self.is_return_statement:
            if is_catch:
                return f"throw {stmt_source}"
            else:
                return f"return {stmt_source}"
        if is_catch:
            return "throw " + stmt_source
        else:
            return "await " + stmt_source

    @reader
    def handle_catch_chain(self, call: FunctionCall, custom_var_name: str | None = None) -> str:
        """Handle catch block in the promise chain.

        Args:
            call: The catch function call to handle
            custom_var_name: Optional custom variable name for assignment

        Returns:
            str: Formatted catch block code
        """
        if not call or call.name != "catch":
            msg = "Invalid catch call provided"
            raise Exception(msg)

        arrow_fn = call.args[0].value
        statements = arrow_fn.code_block.statements
        error_param = arrow_fn.parameters[0].source if hasattr(arrow_fn, "parameters") and arrow_fn.parameters else ""

        formatted_statements = [f"{self.base_indent}}} catch({error_param}: any) {{"]

        return_stmt = None
        for stmt in reversed(statements):
            if stmt.statement_type == StatementType.RETURN_STATEMENT:
                return_stmt = stmt
                break

        if self._needs_anonymous_function(arrow_fn):
            anon_block = self._format_anonymous_function(arrow_fn, custom_var_name=custom_var_name)
            formatted_statements.append(f"{self.base_indent}    {anon_block}")
        elif self._is_implicit_return(arrow_fn):
            implicit_block = self._handle_last_block_implicit_return(statements, is_catch=True, custom_var_name=custom_var_name)
            formatted_statements.append(f"{self.base_indent}    {implicit_block}")
        else:
            for stmt in statements:
                if stmt == return_stmt:
                    return_block = self._handle_last_block_normal_return(stmt, is_catch=True, custom_var_name=custom_var_name)
                    formatted_statements.append(f"{self.base_indent}    {return_block}")
                else:
                    formatted_statements.append(f"{self.base_indent}    {stmt.source.strip()}")

        return "\n".join(formatted_statements)

    @reader
    def handle_finally_chain(self, call: FunctionCall, custom_var_name: str | None = None) -> str:
        """Handle finally block in the promise chain.

        Args:
            call: The finally function call to handle
            custom_var_name: Optional custom variable name for assignment

        Returns:
            str: Formatted finally block code
        """
        if not call or call.name != "finally":
            msg = "Invalid finally call provided"
            raise Exception(msg)

        arrow_fn = call.args[0].value
        statements = arrow_fn.code_block.statements

        formatted_statements = [f"{self.base_indent}}} finally {{"]

        for stmt in statements:
            formatted_statements.append(f"{self.base_indent}    {stmt.source.strip()}")

        return "\n".join(formatted_statements)

    @writer
    def convert_to_async_await(self, custom_var_name: str | None = None) -> str | None:
        """Convert the promise chain to async/await syntax.

        Args:
            custom_var_name: Optional custom variable name for assignment

        Returns:
            str: The converted async/await code
        """
        needs_wrapping = self.has_catch_call or self.has_finally_call
        formatted_blocks = []
        indent = self.base_indent

        if needs_wrapping:
            formatted_blocks.append(f"\n{self.base_indent}try {{")

        formatted_blocks.append(f"{indent}{self.format_base_call()}")

        for idx, then_call in enumerate(self.then_chain):
            is_last_then = idx == len(self.then_chain) - 1
            if is_last_then:
                formatted_block = self.parse_last_then_block(then_call, custom_var_name=custom_var_name)
            else:
                next_call = self.then_chain[idx + 1] if idx + 1 < len(self.then_chain) else None
                formatted_block = self.format_arrow_function(then_call, next_call)
            formatted_blocks.append(f"{indent}{formatted_block}")

        if self.catch_call:
            catch_block = self.handle_catch_chain(self.catch_call, custom_var_name=custom_var_name)
            formatted_blocks.append(catch_block)

        if self.finally_call:
            finally_block = self.handle_finally_chain(self.finally_call, custom_var_name=custom_var_name)
            formatted_blocks.append(finally_block)

        if needs_wrapping:
            formatted_blocks.append(f"{self.base_indent}}}")

        self.parent_statement.parent_function.asyncify()

        diff_changes = "\n".join(formatted_blocks)
        if self.inplace_edit:
            self.parent_statement.edit(diff_changes)
        else:
            return diff_changes

    @reader
    def _is_implicit_return(self, arrow_fn: FunctionCall) -> bool:
        """Check if an arrow function has an implicit return.

        An implicit return occurs when:
        1. The function has exactly one statement
        2. The statement is not a comment
        3. The function body is not wrapped in curly braces

        Args:
            arrow_fn: The arrow function to check

        Returns:
            bool: True if the function has an implicit return
        """
        statements = arrow_fn.code_block.statements
        if len(statements) != 1:
            return False

        stmt = statements[0]
        return not stmt.statement_type == StatementType.COMMENT and not arrow_fn.code_block.source.strip().startswith("{")

    @reader
    def _format_anonymous_function(self, arrow_fn: FunctionCall, next_call: FunctionCall | None = None, custom_var_name: str | None = None) -> str:
        """Format an arrow function as an anonymous async function.

        Args:
            arrow_fn: The arrow function to format
            next_call: The next function call in the chain, if any
            custom_var_name: Optional custom variable name for assignment

        Returns:
            str: Formatted anonymous function code
        """
        params = arrow_fn.parameters if hasattr(arrow_fn, "parameters") else []
        params_str = ", ".join(p.source for p in params) if params else ""
        lines = []

        var_name = custom_var_name if custom_var_name else self.assigned_var

        if next_call and next_call.name == "then":
            next_params = self.get_next_call_params(next_call)
            if next_params:
                lines.append(f"{self.base_indent}{self.format_param_assignment(next_params, f'await (async ({params_str}) => {{', declare=True)}")
        else:
            prefix = ""
            if self.is_return_statement:
                prefix = "return "
            elif var_name:
                prefix = f"{var_name} = "
            lines.append(f"{self.base_indent}{prefix}await (async ({params_str}) => {{")

        code_block = arrow_fn.code_block
        block_content = code_block.source.strip()
        if block_content.startswith("{"):
            block_content = block_content[1:]
        if block_content.endswith("}"):
            block_content = block_content[:-1]

        block_lines = block_content.split("\n")
        for line in block_lines:
            if line.strip():
                lines.append(f"{self.base_indent}    {line.strip()}")

        if params_str:
            lines.append(f"{self.base_indent}}})({params_str});")
        else:
            lines.append(f"{self.base_indent}}})();")

        return "\n".join(lines)

    @property
    @reader
    def has_catch_call(self) -> bool:
        """Check if the Promise chain has a catch call.

        Returns:
            bool: True if there is a catch call
        """
        return self.catch_call is not None

    @property
    @reader
    def has_finally_call(self) -> bool:
        """Check if the Promise chain has a finally call.

        Returns:
            bool: True if there is a finally call
        """
        return self.finally_call is not None

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Literal, Self, TypeVar, overload

from codegen.sdk.core.autocommit import reader
from codegen.sdk.core.detached_symbols.function_call import FunctionCall
from codegen.sdk.core.detached_symbols.parameter import Parameter
from codegen.sdk.core.interfaces.usable import Usable
from codegen.sdk.core.placeholder.placeholder import Placeholder
from codegen.sdk.core.symbol_group import SymbolGroup
from codegen.sdk.writer_decorators import apidoc

if TYPE_CHECKING:
    from codegen.sdk.core.class_definition import Class
    from codegen.sdk.core.expressions.type import Type
    from codegen.sdk.core.external_module import ExternalModule
    from codegen.sdk.core.function import Function
    from codegen.sdk.core.symbol import Symbol


@dataclass
class FunctionCallDefinition:
    """Represents a function call and its definitions.

    This class encapsulates information about a function call and the possible
    callable entities that define it.

    Attributes:
        call (FunctionCall): The function call object representing the invocation.
        callables (List[Union[Function, Class, ExternalModule]]): A list of callable
            entities that define the function being called.
    """

    call: FunctionCall
    callables: list["Function | Class | ExternalModule"]


TParameter = TypeVar("TParameter", bound="Parameter")
TType = TypeVar("TType", bound="Type")


@apidoc
class Callable(Usable, Generic[TParameter, TType]):
    """Any symbol that can be invoked with arguments eg.

    Function, Class, Decorator, ExternalModule
    """

    _parameters: SymbolGroup[TParameter, Self] | list[TParameter]

    return_type: TType | Placeholder[Self]

    @property
    @reader(cache=False)
    def call_sites(self) -> list[FunctionCall]:
        """Returns all call sites (invocations) of this callable in the codebase.

        Finds all locations in the codebase where this callable is invoked/called. Call sites exclude imports, certain exports, and external references.

        Returns:
            list[FunctionCall]: A list of FunctionCall objects representing each invocation of this callable.
            Returns empty list if the callable has no name.
        """
        # TODO - rename this and `function_calls` to be more clear
        call_sites: list[FunctionCall] = []

        for usage in self.usages:
            if isinstance(usage.match, FunctionCall):
                call_sites.append(usage.match)

        return list(dict.fromkeys(call_sites))

    @property
    @reader
    def parameters(self) -> SymbolGroup[TParameter, Self] | list[TParameter]:
        """Retrieves all parameters of a callable symbol.

        This property provides access to all parameters of a callable symbol (function, class, decorator, or external module).
        Parameters are stored as a SymbolGroup containing Parameter objects.

        Returns:
            SymbolGroup[TParameter, Self] | list[TParameter]: A group of Parameter objects representing the callable's parameters,
            or an empty list if the callable has no parameters.
        """
        return self._parameters

    @reader
    def get_parameter(self, name: str) -> TParameter | None:
        """Gets a specific parameter from the callable's parameters list by name.

        Args:
            name (str): The name of the parameter to retrieve.

        Returns:
            TParameter | None: The parameter with the specified name, or None if no parameter with that name exists or if there are no parameters.
        """
        return next((x for x in self._parameters if x.name == name), None)

    @reader
    def get_parameter_by_index(self, index: int) -> TParameter | None:
        """Returns the parameter at the given index.

        Retrieves a parameter from the callable's parameter list based on its positional index.

        Args:
            index (int): The index of the parameter to retrieve.

        Returns:
            TParameter | None: The parameter at the specified index, or None if the parameter list
                is empty or the index does not exist.
        """
        return next((x for x in self._parameters if x.index == index), None)

    @reader
    def get_parameter_by_type(self, type: "Symbol") -> TParameter | None:
        """Retrieves a parameter from the callable by its type.

        Searches through the callable's parameters to find a parameter with the specified type.

        Args:
            type (Symbol): The type to search for.

        Returns:
            TParameter | None: The parameter with the specified type, or None if no parameter is found or if the callable has no parameters.
        """
        if self._parameters is None:
            return None
        return next((x for x in self._parameters if x.type == type), None)

    @overload
    def call_graph_successors(
        self,
        *,
        include_classes: Literal[False],
        include_external: Literal[False],
    ) -> list["Function"]: ...

    @overload
    def call_graph_successors(
        self,
        *,
        include_classes: Literal[False],
        include_external: Literal[True] = ...,
    ) -> list["Function | ExternalModule"]: ...

    @overload
    def call_graph_successors(
        self,
        *,
        include_classes: Literal[True] = ...,
        include_external: Literal[False],
    ) -> list["Function | Class"]: ...

    @overload
    def call_graph_successors(
        self,
        *,
        include_classes: Literal[True] = ...,
        include_external: Literal[True] = ...,
    ) -> list["Function | Class | ExternalModule"]: ...

    @reader
    def call_graph_successors(
        self,
        *,
        include_classes: bool = True,
        include_external: bool = True,
    ) -> list[FunctionCallDefinition]:
        """Returns all function call definitions that are reachable from this callable.

        Analyzes the callable's implementation to find all function calls and their corresponding definitions. For classes, if a constructor exists,
        returns the call graph successors of the constructor; otherwise returns an empty list.

        Args:
            include_classes (bool): If True, includes class definitions in the results. Defaults to True.
            include_external (bool): If True, includes external module definitions in the results. Defaults to True.

        Returns:
            list[FunctionCallDefinition]: A list of FunctionCallDefinition objects, each containing a function call and its
                possible callable definitions (Functions, Classes, or ExternalModules based on include flags). Returns empty list
                for non-block symbols or classes without constructors.
        """
        from codegen.sdk.core.class_definition import Class
        from codegen.sdk.core.external_module import ExternalModule
        from codegen.sdk.core.function import Function
        from codegen.sdk.core.interfaces.has_block import HasBlock

        call_graph_successors: list[FunctionCallDefinition] = []

        # Check if Callable has function_calls:
        if isinstance(self, HasBlock):
            # Special handling for classes.
            # Classes with no constructors are not included in the code paths. Else, the code path of the constructor is included.
            if isinstance(self, Class):
                if self.constructor:
                    return self.constructor.call_graph_successors(include_classes=include_classes, include_external=include_external)
                else:
                    return []

            for call in self.function_calls:
                call_graph_successor = FunctionCallDefinition(call, [])
                # Extract function definition
                for call_func in call.function_definitions:
                    # Case - Function with definition
                    if isinstance(call_func, Function):
                        call_graph_successor.callables.append(call_func)

                    # =====[ Extract `__init__` from classes ]=====
                    elif isinstance(call_func, Class):
                        if include_classes:
                            call_graph_successor.callables.append(call_func)
                    # Case - external module (leaf node)
                    elif isinstance(call_func, ExternalModule) and include_external:
                        call_graph_successor.callables.append(call_func)

                if len(call_graph_successor.callables) > 0:
                    call_graph_successors.append(call_graph_successor)
        else:
            # Non-block symbols will not have any function calls
            return []

        return call_graph_successors

"""Tool for getting PR data including modified symbols and their dependencies."""

from typing import Any, Dict, Set, Tuple

from codegen import Codebase
from codegen.shared.enums.programming_language import ProgrammingLanguage
from codegen.sdk.codebase.config import CodebaseConfig, GSFeatureFlags, Secrets
from codegen.sdk.core.symbol import Symbol


class GetPRDataTool:
    """Tool for retrieving and analyzing PR data including modified symbols and their dependencies."""

    def __init__(self, codebase: Codebase):
        """Initialize the tool with a codebase instance.
        
        Args:
            codebase: The codebase to analyze
        """
        self.codebase = codebase

    def get_pr_data(self, pr_number_str: str) -> Tuple[list[Symbol], str, Set[Symbol]]:
        """Get modified symbols and their dependencies from a PR.
        
        Args:
            pr_number_str: String representation of the PR number to analyze
            
        Returns:
            Tuple containing:
            - List of modified symbols
            - PR patch/diff
            - Set of context symbols (dependencies)
        """
        pr_number = int(pr_number_str)
        context_symbols = set()
        
        # Get modified symbols and patch from PR
        modified_symbols, patch = self.codebase.get_modified_symbols_in_pr(pr_number)
        
        # Collect dependencies for each modified symbol
        for symbol in modified_symbols:
            # Get direct dependencies up to depth 2
            deps = symbol.dependencies(max_depth=2)
            context_symbols.update(deps)
            
        return modified_symbols, patch, context_symbols

    def format_symbol_data(self, symbol: Symbol) -> Dict[str, Any]:
        """Format symbol data into a dictionary.
        
        Args:
            symbol: Symbol to format
            
        Returns:
            Dictionary containing formatted symbol data
        """
        return {
            "name": symbol.name,
            "type": symbol.symbol_type.value,
            "filepath": symbol.filepath,
            "content": symbol.content,
        }

    def get_formatted_pr_data(self, pr_number_str: str) -> Dict[str, Any]:
        """Get formatted PR data including modified symbols and their dependencies.
        
        Args:
            pr_number_str: String representation of the PR number to analyze
            
        Returns:
            Dictionary containing formatted PR data including modified symbols and context
        """
        modified_symbols, patch, context_symbols = self.get_pr_data(pr_number_str)
        
        return {
            "modified_symbols": [
                self.format_symbol_data(symbol) for symbol in modified_symbols
            ],
            "context_symbols": [
                self.format_symbol_data(symbol) for symbol in context_symbols
            ],
            "patch": patch
        } 
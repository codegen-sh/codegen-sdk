from logging import getLogger
from typing import TYPE_CHECKING

from graph_sitter.core.detached_symbols.argument import Argument
from graph_sitter.core.detached_symbols.function_call import FunctionCall
from graph_sitter.core.expressions import String
from graph_sitter.core.interfaces.editable import Editable
from graph_sitter.core.plugins.plugin import Plugin
from graph_sitter.core.symbol_groups.dict import Dict
from graph_sitter.enums import ProgrammingLanguage

if TYPE_CHECKING:
    from graph_sitter.core.codebase import TSCodebaseType


logger = getLogger(__name__)


class AxiosApiFinder(Plugin):
    language: ProgrammingLanguage = ProgrammingLanguage.TYPESCRIPT

    def execute(self, codebase: "TSCodebaseType"):
        logger.info("Scanning for Axios API calls")
        api_calls = 0

        def resolve_http(val) -> Editable:
            if isinstance(val, Argument):
                val = val.value
            if isinstance(val, Dict):
                return resolve_http(val.get("baseURL"))
            return val.resolved_value

        for imp in codebase.imports:
            if "axios" in imp.module.source:
                for usage in imp.usages:
                    call = usage.match.parent.parent
                    if not isinstance(call, FunctionCall):
                        continue
                    if call.name in ("isAxiosError",):
                        continue
                    val = resolve_http(call.args[0])
                    if isinstance(val, String):
                        url = val.content.rsplit("--")[-1]
                        for split in url.rsplit("/"):
                            if split:
                                url = split
                                break
                        url = url.removesuffix(".modal.run")
                        call.register_api_call(url)
                        api_calls += 1
        if api_calls > 0:
            logger.info(f"Found {api_calls} Axios API calls")

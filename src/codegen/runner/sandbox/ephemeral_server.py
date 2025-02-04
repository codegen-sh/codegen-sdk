import logging
import tempfile

from fastapi import FastAPI

from codegen.runner.models.apis import (
    RUN_ON_STRING_ENDPOINT,
    GetRunOnStringRequest,
    GetRunOnStringResult,
)
from codegen.runner.sandbox.executor import SandboxExecutor
from codegen.sdk.codebase.factory.get_session import get_codebase_session
from codegen.sdk.enums import ProgrammingLanguage
from codegen.shared.compilation.string_to_code import create_execute_function_from_codeblock

logger = logging.getLogger(__name__)
app = FastAPI()


@app.post(RUN_ON_STRING_ENDPOINT)
async def run_on_string(request: GetRunOnStringRequest) -> GetRunOnStringResult:
    logger.info(f"====[ run_on_string ]====\n> Codemod source: {request.codemod_source}\n> Input: {request.files}\n> Language: {request.language}\n")
    language = ProgrammingLanguage(request.language.upper())
    with get_codebase_session(tmpdir=tempfile.mkdtemp(), files=request.files, programming_language=language) as codebase:
        executor = SandboxExecutor(codebase)
        code_to_exec = create_execute_function_from_codeblock(codeblock=request.codemod_source)
        result = await executor.execute(code_to_exec)
        logger.info(f"Result: {result}")
        return GetRunOnStringResult(result=result)

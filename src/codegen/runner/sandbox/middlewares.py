import logging
import traceback
from collections.abc import Callable
from functools import cached_property
from http import HTTPStatus  # Add this import
from typing import TypeVar

from starlette.background import BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from codegen.runner.models.apis import ServerInfo
from codegen.runner.sandbox.runner import SandboxRunner
from codegen.shared.exceptions.compilation import UserCodeException

logger = logging.getLogger(__name__)

TRequest = TypeVar("TRequest", bound=Request)
TResponse = TypeVar("TResponse", bound=Response)


class CodemodRunMiddleware[TRequest, TResponse](BaseHTTPMiddleware):
    def __init__(self, app, path: str, server_info_fn: Callable[[], ServerInfo], runner_fn: Callable[[], SandboxRunner]) -> None:
        super().__init__(app)
        self.path = path
        self.server_info_fn = server_info_fn
        self.runner_fn = runner_fn

    async def dispatch(self, request: TRequest, call_next: RequestResponseEndpoint) -> TResponse:
        if request.url.path == self.path:
            return await self.process_request(request, call_next)
        return await call_next(request)

    @cached_property
    def server_info(self) -> ServerInfo:
        return self.server_info_fn()

    @cached_property
    def runner(self) -> SandboxRunner:
        return self.runner_fn()

    async def process_request(self, request: TRequest, call_next: RequestResponseEndpoint) -> TResponse:
        self.server_info.is_running_codemod = True
        background_tasks = BackgroundTasks()
        try:
            logger.info(f"> (CodemodRunMiddleware) Request: {request.url.path}")
            self.runner.codebase.viz.clear_graphviz_data()
            response = await call_next(request)
            background_tasks.add_task(self.cleanup_after_codemod, is_exception=False)
            response.background = background_tasks
            return response

        except UserCodeException as e:
            message = f"Invalid user code for {request.url.path}"
            logger.info(message)
            self.server_info.is_running_codemod = False
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"detail": message, "error": str(e), "traceback": traceback.format_exc()})

        except Exception as e:
            message = f"Unexpected error for {request.url.path}"
            logger.exception(message)
            res = JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content={"detail": message, "error": str(e), "traceback": traceback.format_exc()})
            background_tasks.add_task(self.cleanup_after_codemod, is_exception=True)
            res.background = background_tasks
            return res

    async def cleanup_after_codemod(self, is_exception: bool = False):
        if is_exception:
            # TODO: instead of committing transactions, we should just rollback
            logger.info("Committing pending transactions due to exception")
            self.runner.codebase.G.commit_transactions(sync_graph=False)
        self.runner.reset_runner()
        self.server_info.is_running_codemod = False

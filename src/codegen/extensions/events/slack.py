import functools
import logging
import os
from typing import Callable

import modal  # deptry: ignore
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from codegen.extensions.events.interface import EventHandlerManagerProtocol

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RegisteredEventHandler(BaseModel):
    handler_func: Callable


# Global FastAPI app for handling Slack events
slack_web_app = FastAPI()


@slack_web_app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"[MIDDLEWARE] Received request: {request.method} {request.url}")
    try:
        body = await request.body()
        logger.info(f"[MIDDLEWARE] Request body: {body.decode()}")
    except Exception as e:
        logger.exception(f"[MIDDLEWARE] Error reading body: {e}")
    response = await call_next(request)
    logger.info(f"[MIDDLEWARE] Response status: {response.status_code}")
    return response


@slack_web_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"[ERROR] Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


@slack_web_app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"[ERROR] Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


class Slack(EventHandlerManagerProtocol):
    def __init__(self, app: modal.App):
        logger.info("[INIT] Initializing Slack handler")
        self.app = app
        self.bot_token = os.environ["SLACK_BOT_TOKEN"]
        self.signing_secret = os.environ["SLACK_SIGNING_SECRET"]
        self.registered_handlers = {}
        self.slack_app = App(token=self.bot_token, signing_secret=self.signing_secret)
        self.handler = SlackRequestHandler(self.slack_app)
        logger.info("[INIT] Slack handler initialized")

        # Add handlers for both root and /slack/events paths
        @slack_web_app.post("/")
        @slack_web_app.post("/slack/events")
        async def handle_slack_events(request: Request):
            """Handle all Slack events including verification."""
            logger.info("[ENDPOINT] Received request")
            try:
                # Log raw request details
                logger.info(f"[ENDPOINT] Headers: {dict(request.headers)}")
                body = await request.body()
                logger.info(f"[ENDPOINT] Raw body: {body.decode()}")

                # Parse JSON
                body_json = await request.json()
                logger.info(f"[ENDPOINT] Parsed JSON body: {body_json}")

                # Handle URL verification
                if body_json.get("type") == "url_verification":
                    logger.info("[ENDPOINT] Handling URL verification")
                    challenge = body_json.get("challenge")
                    logger.info(f"[ENDPOINT] Challenge value: {challenge}")
                    return {"challenge": challenge}

                # Handle all other events
                logger.info("[ENDPOINT] Passing to Slack handler")
                return await self.handler.handle(request)
            except Exception as e:
                logger.exception(f"[ENDPOINT] Error handling request: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def subscribe_handler_to_webhook(self, web_url: str, event_name: str):
        logger.info(f"[WEBHOOK] Subscribing to {event_name} at {web_url}")
        # Slack doesn't require explicit webhook registration like Linear
        # The events are handled through the Events API
        pass

    def unsubscribe_handler_to_webhook(self, registered_handler: RegisteredEventHandler):
        # Slack doesn't require explicit webhook unregistration
        pass

    def unsubscribe_all_handlers(self):
        logger.info("[HANDLERS] Clearing all handlers")
        self.registered_handlers.clear()

    def event(self, event_name: str):
        """Decorator for registering a Slack event handler."""
        logger.info(f"[EVENT] Registering handler for {event_name}")

        def decorator(func):
            # Register the handler with the app's registry
            modal_ready_func = func
            func_name = func.__qualname__
            logger.info(f"[EVENT] Registering function {func_name} for {event_name}")

            self.registered_handlers[func_name] = RegisteredEventHandler(handler_func=modal_ready_func)

            # Register the handler with Slack's event system
            @self.slack_app.event(event_name)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"[HANDLER] Executing handler {func_name}")
                logger.info(f"[HANDLER] Args: {args}")
                logger.info(f"[HANDLER] Kwargs: {kwargs}")
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_asgi_app(self) -> FastAPI:
        """Get the FastAPI app for handling Slack events."""
        logger.info("[APP] Getting ASGI app")
        return slack_web_app

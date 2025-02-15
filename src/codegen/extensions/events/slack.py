import functools
import logging
import os
from typing import Any, Callable

import modal  # deptry: ignore
from fastapi import FastAPI, Request
from pydantic import BaseModel
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from codegen.extensions.events.interface import EventHandlerManagerProtocol

logger = logging.getLogger(__name__)


class RegisteredEventHandler(BaseModel):
    handler_func: Callable


# Global FastAPI app for handling Slack events
slack_web_app = FastAPI()


class Slack(EventHandlerManagerProtocol):
    def __init__(self, app: modal.App):
        self.app = app
        self.bot_token = os.environ["SLACK_BOT_TOKEN"]
        self.signing_secret = os.environ["SLACK_SIGNING_SECRET"]
        self.registered_handlers = {}
        self.slack_app = App(token=self.bot_token, signing_secret=self.signing_secret)
        self.handler = SlackRequestHandler(self.slack_app)

        # Add URL verification endpoint
        @slack_web_app.post("/")
        async def handle_verification(request: Request):
            """Handle Slack URL verification challenge."""
            body = await request.json()
            if body.get("type") == "url_verification":
                return {"challenge": body["challenge"]}
            return await self.handler.handle(request)

    def subscribe_handler_to_webhook(self, web_url: str, event_name: str):
        # Slack doesn't require explicit webhook registration like Linear
        # The events are handled through the Events API
        pass

    def unsubscribe_handler_to_webhook(self, registered_handler: RegisteredEventHandler):
        # Slack doesn't require explicit webhook unregistration
        pass

    def unsubscribe_all_handlers(self):
        self.registered_handlers.clear()

    def event(self, event_name: str):
        """Decorator for registering a Slack event handler.

        :param event_name: The name of the Slack event to handle (e.g., 'app_mention', 'message', etc.)
        """

        def decorator(func):
            # Register the handler with the app's registry
            modal_ready_func = func
            func_name = func.__qualname__

            self.registered_handlers[func_name] = RegisteredEventHandler(handler_func=modal_ready_func)

            # Register the handler with Slack's event system
            @self.slack_app.event(event_name)
            @functools.wraps(func)
            def wrapper(event: dict[str, Any], say: Any):
                return func(event, say)

            return wrapper

        return decorator

    def get_asgi_app(self) -> FastAPI:
        """Get the FastAPI app for handling Slack events."""
        return slack_web_app

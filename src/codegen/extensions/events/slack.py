import logging
from typing import Callable

import modal  # deptry: ignore
from pydantic import BaseModel, Field

from codegen.extensions.events.interface import EventHandlerManagerProtocol

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SlackWebhookPayload(BaseModel):
    token: str | None = Field(None)
    team_id: str | None = Field(None)
    api_app_id: str | None = Field(None)
    event: dict | None = Field(None)
    type: str | None = Field(None)
    event_id: str | None = Field(None)
    event_time: int | None = Field(None)
    challenge: str | None = Field(None)
    subtype: str | None = Field(None)


class RegisteredEventHandler(BaseModel):
    handler_func: Callable


class Slack(EventHandlerManagerProtocol):
    def __init__(self, app: modal.App):
        logger.info("[INIT] Initializing Slack handler")
        self.app = app
        self.registered_handlers = {}
        logger.info("[INIT] Slack handler initialized")

    def subscribe_handler_to_webhook(self, web_url: str, event_name: str):
        logger.info(f"[WEBHOOK] Subscribing to {event_name} at {web_url}")
        # Slack doesn't require explicit webhook registration
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

            # Create the web endpoint for this handler
            @self.app.function(secrets=[modal.Secret.from_dotenv()])
            @modal.web_endpoint(method="POST")
            def handle_webhook(event: SlackWebhookPayload):
                logger.info(f"[HANDLER] Received Slack event type: {event.type}")

                # Handle URL verification
                if event.type == "url_verification":
                    logger.info("[HANDLER] Handling URL verification")
                    return {"challenge": event.challenge}

                # Handle actual events
                elif event.type == "event_callback":
                    if event.event and event.event.get("type") == event_name:
                        logger.info(f"[HANDLER] Handling {event_name} event")
                        return func(event.event)

                return {"message": "Event received but not handled"}

            return handle_webhook

        return decorator

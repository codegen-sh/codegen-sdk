import functools
import os
from typing import Callable, Optional
import modal
import modal.runner

from codegen.extensions.clients.linear import LinearClient

class CodegenApp:
    def __init__(self, name, modal_api_key, image: modal.Image):
        self._modal_api_key = modal_api_key
        self._image = image
        self._name = name

        self.modal_app = modal.App(name=name, image=image, )
        # Internal registry for event handlers, keyed by event name.
        self._registry = {}
        # Expose a linear attribute that provides the event decorator.
        self.linear = Linear(self)

    def _register_event_handler(self, event_name, handler):
        """Registers a handler for a given event."""
        self._registry.setdefault(event_name, []).append(handler)
        print(f"Registered handler '{handler}' for event '{event_name}'.")

    def dispatch_event(self, event_name, request):
        """
        Dispatches an event to all registered handlers for the event.
        """
        handlers = self._registry.get(event_name, [])
        if not handlers:
            print(f"No handlers registered for event '{event_name}'.")
            return
        for handler in handlers:
            print(f"Dispatching event '{event_name}' to {handler.__name__}.")
            handler(request)



class Linear:
    def __init__(self, app: CodegenApp):
        self.app = app
        self.access_token= os.environ["LINEAR_ACCESS_TOKEN"] # move to extensions config.
        self.signing_secret = os.environ["LINEAR_SIGNING_SECRET"]
        self.linear_team_id = os.environ["LINEAR_TEAM_ID"]


    def register_handler_to_webhook(self, func_name: str, modal_app: modal.App, event_name):
        app_name = modal_app.name
        web_url = modal.Function.from_name(app_name=app_name,name=func_name)
        client = LinearClient(access_token=self.access_token)
        client.register_webhook(
            team_id=self.linear_team_id, 
            webhook_url=web_url, 
            enabled=True, 
            resource_types=[event_name], 
            secret=self.signing_secret)
        
    # def unregister_handler(self):
        # TODO
        # pass


    def event(self, event_name, register_hook: Optional[Callable]=None):
        """
        Decorator for registering an event handler.

        :param event_name: The name of the event to handle.
        :param register_hook: An optional function to call during registration,
                              e.g., to make an API call to register the webhook.
        """
        def decorator(func):
            # Register the handler with the app's registry.

            modal_ready_func = apply_decorators(func=func, decorators=[modal.web_endpoint(method="POST"), self.app.modal_app.function()])
            self.app._register_event_handler(event_name, modal_ready_func)

            # If a custom registration hook is provided, execute it.
            if callable(register_hook):
                register_hook(event_name, func, self.app)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            result = modal.runner.deploy_app(self.app.modal_app)
            print(result)
            return wrapper
            
        
        return decorator
    
        
    

def apply_decorators(func, decorators):
    for decorator in decorators:
        func = decorator(func)
    return func
import logging

import modal  # deptry: ignore

from codegen.extensions.events.linear import Linear
from codegen.extensions.events.slack import Slack

logger = logging.getLogger(__name__)


# Create base image that installs from specific git commit
def create_base_image(repo_url: str, commit_id: str) -> modal.Image:
    """Create a base image with dependencies installed from a specific git commit."""
    return modal.Image.debian_slim().pip_install(
        "slack-bolt>=1.18.0",
        f"git+{repo_url}@{commit_id}",
    )


class CodegenApp(modal.App):
    linear: Linear
    slack: Slack

    def __init__(self, name: str, modal_api_key: str, image: modal.Image):
        self._modal_api_key = modal_api_key
        self._image = image
        self._name = name

        super().__init__(name=name, image=image)

        # Expose attributes that provide event decorators for different providers.
        self.linear = Linear(self)
        self.slack = Slack()

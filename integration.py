"""Slack chatbot for answering questions about FastAPI using Codegen's VectorIndex."""

import logging
from logging import getLogger
from typing import Any

import modal  # deptry: ignore

from codegen.extensions.events.app import CodegenApp

# set logging to info level
logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

########################################
# MODAL
########################################

# Create image with dependencies

image = (
    modal.Image.debian_slim(python_version="3.13")
    .apt_install("git")
    .pip_install(
        "fastapi[standard]",
    )
)

app = CodegenApp(name="slack", modal_api_key="", image=image)


@app.function()
@modal.web_endpoint(method="POST")
@app.slack.event("app_mention")
def handle_mention(event: dict[str, Any], say: Any):
    # Your event handling code here
    print("=====[ EVENT ]=====")
    print(event)

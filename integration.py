"""Slack chatbot for answering questions about FastAPI using Codegen's VectorIndex."""

import logging
from logging import getLogger

import modal

from codegen.extensions.events.app import CodegenApp

# set logging to info level
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)

########################################
# IMAGE
########################################

REPO_URL = "https://github.com/codegen-sh/codegen-sdk.git"
COMMIT_ID = "abc123"  # Replace with actual commit ID

# Create the base image with dependencies
base_image = (
    modal.Image.debian_slim(python_version="3.13")
    .apt_install("git")
    .pip_install(
        "openai>=1.1.0",
        "fastapi[standard]",
        f"git+{REPO_URL}@{COMMIT_ID}",
    )
)

########################################
# MODAL
########################################

logger.info("[INIT] Creating CodegenApp")
app = CodegenApp(name="slack", modal_api_key="", image=base_image)
logger.info("[INIT] CodegenApp created")


@app.slack.event("app_mention")
def handle_mention(event: dict):
    logger.info("[HANDLER] Received app_mention event")
    logger.info(f"[HANDLER] Event data: {event}")
    return {"message": "Event handled successfully"}

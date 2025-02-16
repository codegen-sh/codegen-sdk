"""Slack chatbot for answering questions about FastAPI using Codegen's VectorIndex."""

import os
from typing import Any

import modal
from codegen import Codebase
from codegen.extensions.events.app import CodegenApp
from codegen.shared.enums.programming_language import ProgrammingLanguage
from fastapi import FastAPI, Request
import requests
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from logging import getLogger
from codegen.shared.performance.stopwatch_utils import stopwatch

# ruff: noqa
import logging

# set logging to info level
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)

########################################
# MODAL
########################################

logger.info("[INIT] Creating CodegenApp")
app = CodegenApp(name="slack", modal_api_key="")
logger.info("[INIT] CodegenApp created")


@app.slack.event("app_mention")
def handle_mention(event: dict[str, Any], say: Any):
    logger.info("[HANDLER] Received app_mention event")
    logger.info(f"[HANDLER] Event data: {event}")
    # Your event handling code here
    print("=====[ EVENT ]=====")
    print(event)

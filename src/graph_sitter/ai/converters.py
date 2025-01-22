# TODO: these should move to claude
import json
import logging

import anthropic
import openai.types.chat as openai_types

logger = logging.getLogger(__name__)

"""
Utilities for converting messages between OpenAI and Claude formats.
"""


def convert_openai_messages_to_claude(messages: list) -> tuple[str | anthropic.NotGiven, list]:
    """Converts OpenAI chat messages to Claude chat messages."""
    messages, system_prompt = extract_system_prompt_from_openai_message(messages)
    converted_messages = convert_messages(messages)
    combined_messages = combine_consecutive_user_messages(converted_messages)
    return system_prompt, combined_messages


def extract_system_prompt_from_openai_message(messages: list) -> tuple[list, str | anthropic.NotGiven]:
    """Extracts the system prompt from the first message if it exists."""
    if len(messages) >= 1 and isinstance(messages[0], dict) and messages[0].get("role", None) == "system":
        system_prompt = messages[0]["content"]
        messages = messages[1:]
    else:
        system_prompt = anthropic.NotGiven()
    return messages, system_prompt


def convert_messages(messages: list) -> list:
    """Helper function to convert messages to Claude format."""
    new_messages = []
    for message in messages:
        if isinstance(message, openai_types.chat_completion_message.ChatCompletionMessage):
            new_message = convert_openai_message(message)
        elif isinstance(message, dict):
            new_message = convert_dict_message(message)
        else:
            logger.warn(f"Message type not supported: {type(message)}")
            continue
        new_messages.append(new_message)
    return new_messages


def combine_consecutive_user_messages(messages: list) -> list:
    """Combines consecutive user messages into a single message."""
    combined_messages = []
    for message in messages:
        if combined_messages and combined_messages[-1]["role"] == "user" and message["role"] == "user":
            merge_user_messages(combined_messages[-1], message)
        else:
            combined_messages.append(message)
    return combined_messages


def convert_openai_message(message):
    """Converts an OpenAI message to an Anthropic message."""
    if message.tool_calls is not None:
        return create_anthropic_message_with_tool_calls(message.role, message.content, message.tool_calls)
    return {"role": message.role, "content": message.content}


def convert_dict_message(message):
    """Converts a dictionary message to an Anthropic message."""
    role = message.get("role")
    if role == "user" or role == "assistant":
        if "tool_calls" in message:
            return create_anthropic_message_with_tool_calls(role, message["content"], message["tool_calls"])
        return {"role": role, "content": message["content"]}
    elif role == "tool":
        return {"role": "user", "content": [{"type": "tool_result", "tool_use_id": message["tool_call_id"], "content": message["content"]}]}
    else:
        logger.warn(f"Unsupported role: {role}")
        return None


def create_anthropic_message_with_tool_calls(role, content, tool_calls):
    """Converts a OpenAI message with tool calls to an Anthropic message."""
    message_content = []
    if content:
        message_content.append({"type": "text", "text": content})
    for tool_call in tool_calls:
        message_content.append(
            {
                "type": "tool_use",
                "id": tool_call.id if hasattr(tool_call, "id") else tool_call["id"],
                "name": tool_call.function.name if hasattr(tool_call, "function") else tool_call["function"]["name"],
                "input": json.loads(tool_call.function.arguments if hasattr(tool_call, "function") else tool_call["function"]["arguments"]),
            }
        )
    return {"role": role, "content": message_content}


def merge_user_messages(existing_message, new_message):
    """Merges two user messages into a single message."""
    if isinstance(existing_message["content"], list):
        existing_message["content"].extend(new_message["content"] if isinstance(new_message["content"], list) else [{"type": "text", "text": new_message["content"]}])
    else:
        existing_message["content"] = [
            {"type": "text", "text": existing_message["content"]},
            {"type": "text", "text": new_message["content"]} if isinstance(new_message["content"], str) else new_message["content"],
        ]

import json
import logging
from abc import ABC, abstractmethod

import anthropic
import anthropic.types as anthropic_types
import anthropic.types.beta.tools as anthropic_tool_types
import backoff
import openai
import openai.types.chat as openai_types
import tiktoken
from anthropic import Anthropic
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from codegen.sdk.ai.converters import convert_openai_messages_to_claude
from codegen.sdk.utils import XMLUtils

CLAUDE_OPENAI_MODEL_MAP = {
    "gpt-4o": "claude-3-5-sonnet-20240620",
    "gpt-4o-mini": "claude-3-haiku-20240307",
    "gpt-4-turbo": "claude-3-5-sonnet-20240620",
    "gpt-4-32k": "claude-3-opus-20240229",
    "gpt-4-1106-preview": "claude-3-opus-20240229",
    "gpt-4": "claude-3-opus-20240229",
    "gpt-3.5-turbo": "claude-3-sonnet-20240229",
}

ENCODERS = {
    "gpt-4-1106-preview": tiktoken.encoding_for_model("gpt-4-32k"),
    "gpt-4-32k": tiktoken.encoding_for_model("gpt-4-32k"),
}


def count_tokens(s: str, model_name: str = "gpt-4-32k") -> int:
    """Uses tiktoken"""
    if s is None:
        return 0
    enc = ENCODERS.get(model_name, None)
    if not enc:
        ENCODERS[model_name] = tiktoken.encoding_for_model(model_name)
        enc = ENCODERS[model_name]
    tokens = enc.encode(s)
    return len(tokens)


def get_headers(headers, cache_enabled: bool | None = True):
    tmp_headers = headers if headers else {"Helicone-Auth": "Bearer sk-pucao3a-blpeocy-qcdpbzi-i5n4pja"}

    if cache_enabled:
        tmp_headers["Helicone-Cache-Enabled"] = "true"
        tmp_headers["Cache-Control"] = "max-age=2592000"  # 30 days

    return tmp_headers


class AbstractAIHelper(ABC):
    api_base: str
    headers: dict[str, str]

    @abstractmethod
    def __init__(self) -> None:
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def embeddings_with_backoff(self, **kwargs):
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def get_embeddings(self, content_strs: list[str]) -> list[list[float]]:
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def get_embedding(self, content_str: str) -> list[float]:
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def llm_query_with_retry(self, **kwargs):
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def llm_query_no_retry(self, messages: list = [], model: str = "gpt-4-32k", max_tokens: int | None = None):
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def llm_query_functions_with_retry(self, model: str, messages: list, functions: list[dict], max_tokens: int | None = None):
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def llm_query_functions(self, model: str, messages: list, functions: list[dict], max_tokens: int | None = None):
        msg = "This is an abstract class"
        raise NotImplementedError(msg)

    @abstractmethod
    def llm_response_to_json(response) -> str:
        msg = "This is an abstract class"
        raise NotImplementedError(msg)


# TODO: move into utils/ai folder
class OpenAIHelper(AbstractAIHelper):
    client: OpenAI = None

    def __init__(
        self,
        openai_key: str,
        api_base: str = "https://oai.hconeai.com/v1",
        headers=None,
        cache: bool | None = True,
    ) -> None:
        if openai_key is None:
            msg = "The openai_key must be provided"
            raise ValueError(msg)

        self.openai_key = openai_key
        self.api_base = api_base
        self.headers = get_headers(headers, cache_enabled=cache)
        self.logger = logging.getLogger(__name__)
        self.embedding_model_name = "text-embedding-ada-002"
        self.completions_model_name = "text-embedding-ada-002"

        self.set_up_open_ai_key()

    def set_up_open_ai_key(self) -> None:
        self.client = OpenAI(api_key=self.openai_key, base_url=self.api_base, default_headers=self.headers)

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def embeddings_with_backoff(self, **kwargs):
        return self.client.embeddings.create(**kwargs)

    def get_embeddings(self, content_strs: list[str]) -> list[list[float]]:
        content_strs = [c[:1000] if type(c) in (str, bytes) else " " for c in content_strs]
        response = self.embeddings_with_backoff(input=content_strs, model=self.embedding_model_name)
        return [x.embedding for x in response.data]

    def get_embedding(self, content_str: str) -> list[float]:
        return self.get_embeddings([content_str])[0]

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def completions_with_backoff(self, **kwargs):
        return self.client.completions.create(**kwargs)

    @retry(wait=wait_random_exponential(min=70, max=600), stop=stop_after_attempt(10))
    def llm_query_with_retry(self, **kwargs):
        return self.llm_query_no_retry(**kwargs)

    def llm_query_no_retry(self, messages: list = [], model: str = "gpt-4-32k", max_tokens: int | None = None, **kwargs):
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=max_tokens or openai.NOT_GIVEN,
            **kwargs,
        )

    @retry(wait=wait_random_exponential(min=70, max=600), stop=stop_after_attempt(10))
    def llm_query_functions_with_retry(self, model: str, messages: list, functions: list[dict], max_tokens: int | None = None, **kwargs):
        return self.llm_query_functions(model, messages, functions, max_tokens, **kwargs)

    def llm_query_functions(self, model: str, messages: list, functions: list[dict], max_tokens: int | None = None, **kwargs):
        if functions is not None:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=functions,  # type: ignore
                max_tokens=max_tokens or openai.NOT_GIVEN,
                **kwargs,
                # tool_choice="auto", # has it do multiple
            )
        else:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens or openai.NOT_GIVEN,
                **kwargs,
            )

        return response

    @staticmethod
    def llm_response_to_json(response: openai_types.chat_completion.ChatCompletion) -> str:
        # the response needs an object of type ChatCompletionMessage
        js = json.loads(response.model_dump_json())
        if len(js["choices"]) == 0:
            return ""
        return js["choices"][0]["message"]["content"]


class AnthropicHelper(AbstractAIHelper):
    def __init__(
        self,
        anthropic_key: str,
        # Dont add /v1 to the path. Anthropic already adds it, so it will be a double /v1/v1
        api_base: str = "https://anthropic.hconeai.com/",
        headers=None,
        openai_anthropic_translation: bool = True,
        cache: bool | None = True,
    ) -> None:
        if anthropic_key is None:
            msg = "The anthropic_key must be provided"
            raise ValueError(msg)

        self.anthropic_key = anthropic_key
        self.api_base = api_base
        self.headers = get_headers(headers, cache_enabled=cache)
        self.logger = logging.getLogger(__name__)
        self.openai_anthropic_translation = openai_anthropic_translation
        self.set_up_claude_key()

    def set_up_claude_key(self) -> None:
        self.client = Anthropic(api_key=self.anthropic_key, base_url=self.api_base, default_headers=self.headers)

    def _convert_openai_functions_to_claude(self, functions: list[dict]) -> list[anthropic_tool_types.ToolParam]:
        new_functions = []
        for function in functions:
            if function["type"] == "function":
                new_function = {"name": function["function"]["name"], "description": function["function"]["description"], "input_schema": {"type": "object", "properties": {}}}
                if "parameters" in function["function"]:
                    new_function["input_schema"] = function["function"]["parameters"]
                new_functions.append(new_function)
        return new_functions

    def _convert_claude_response_to_openai(
        self, response: anthropic_types.Message | anthropic_tool_types.ToolsBetaMessage, parse_function_calls: bool = False, parse_result_block: bool = False
    ) -> openai_types.chat_completion.ChatCompletion:
        choices = []
        if len(response.content) != 0:
            for resp in response.content:
                if isinstance(resp, anthropic_types.ContentBlock):
                    if "result" in resp.text and parse_result_block:
                        xml_result = XMLUtils.extract_elements(resp.text, "result", keep_tag=False)
                        resp.text = resp.text if len(xml_result) <= 1 else xml_result[0]
                    elif isinstance(resp, anthropic_tool_types.ToolUseBlock) and parse_result_block:
                        xml_answer = XMLUtils.extract_elements(resp.text, "answer", keep_tag=False)[0]
                        resp.text = resp.text if len(xml_answer) <= 1 else xml_answer[0]
                    choices.append(
                        openai_types.chat_completion.Choice(
                            index=0,
                            finish_reason="stop" if response.stop_reason in ("end_turn", "stop_sequence") else "length",
                            message=openai_types.chat_completion_message.ChatCompletionMessage(content=resp.text, role="assistant"),
                        )
                    )
                elif isinstance(resp, anthropic_tool_types.ToolUseBlock):
                    # If the previous choice is a chat message, then we can add the tool call to it
                    if len(choices) > 0 and isinstance(choices[-1].message, openai_types.chat_completion_message.ChatCompletionMessage) and choices[-1].message.tool_calls is None:
                        text_response = choices[-1].message.content
                        choices = choices[:-1]
                    else:
                        text_response = None
                    choices.append(
                        openai_types.chat_completion.Choice(
                            index=0,
                            finish_reason="tool_calls",
                            message=openai_types.chat_completion_message.ChatCompletionMessage(
                                content=text_response,
                                role="assistant",
                                function_call=None,  # Function calls are deprecated
                                tool_calls=[
                                    openai_types.chat_completion_message_tool_call.ChatCompletionMessageToolCall(
                                        id=resp.id,
                                        function=openai_types.chat_completion_message_tool_call.Function(
                                            name=resp.name,
                                            arguments=json.dumps(resp.input),
                                        ),
                                        type="function",
                                    )
                                ],
                            ),
                        )
                    )
        return openai_types.chat_completion.ChatCompletion(
            id=response.id,
            choices=choices,
            created=0,  # TODO: Use current time
            model=response.model,
            object="chat.completion",
            system_fingerprint=None,  # TODO: What is this?
        )

    @backoff.on_exception(backoff.expo, anthropic.RateLimitError)
    def embeddings_with_backoff(self, **kwargs):
        msg = "Embeddings are not supported for AnthropicHelper"
        raise NotImplementedError(msg)
        # response = self.client.embeddings.create(**kwargs)
        # return response

    def get_embeddings(self, content_strs: list[str]) -> list[list[float]]:
        msg = "Embeddings are not supported for AnthropicHelper"
        raise NotImplementedError(msg)
        # content_strs = [c[:1000] if type(c) in (str, bytes) else " " for c in content_strs]
        # response = self.embeddings_with_backoff(input=content_strs, model=self.embedding_model_name)
        # return [x.embedding for x in response.data]

    def get_embedding(self, content_str: str) -> list[float]:
        msg = "Embeddings are not supported for AnthropicHelper"
        raise NotImplementedError(msg)
        # embeddings = self.get_embeddings([content_str])
        # return embeddings[0]

    @backoff.on_exception(backoff.expo, anthropic.RateLimitError)
    def completions_with_backoff(self, **kwargs):
        msg = "Claude's completion api is deprecated. Please use messages_with_backoff instead."
        raise Exception(msg)

    @backoff.on_exception(backoff.expo, anthropic.RateLimitError)
    def messages_with_backoff(self, **kwargs):
        return self.client.messages.create(**kwargs)

    @retry(wait=wait_random_exponential(min=70, max=600), stop=stop_after_attempt(10))
    def llm_query_with_retry(self, **kwargs):
        return self.llm_query_no_retry(**kwargs)

    def llm_query_no_retry(self, messages: list = [], model: str = "claude-2.0", max_tokens: int | None = None, system_prompt: str | anthropic.NotGiven | None = None, **kwargs):
        system_prompt = anthropic.NotGiven() if not system_prompt else system_prompt
        if self.openai_anthropic_translation and model in CLAUDE_OPENAI_MODEL_MAP:
            model = CLAUDE_OPENAI_MODEL_MAP[model]
        if self.openai_anthropic_translation:
            claude_system_prompt, messages = convert_openai_messages_to_claude(messages)
            if isinstance(system_prompt, str) and isinstance(claude_system_prompt, str):
                claude_system_prompt = system_prompt + claude_system_prompt
        else:
            claude_system_prompt = system_prompt
        response = self.client.beta.tools.messages.create(max_tokens=max_tokens, system=claude_system_prompt, messages=messages, model=model, **kwargs)
        if self.openai_anthropic_translation:
            return self._convert_claude_response_to_openai(response)
        else:
            return response

    @retry(wait=wait_random_exponential(min=70, max=600), stop=stop_after_attempt(10))
    def llm_query_functions_with_retry(self, **kwargs):
        return self.llm_query_functions(**kwargs)

    def llm_query_functions(self, model: str, messages: list, functions: list, max_tokens: int | None = None, system_prompt: str | anthropic.NotGiven | None = None, **kwargs):
        system_prompt = anthropic.NotGiven() if not system_prompt else system_prompt
        if self.openai_anthropic_translation and model in CLAUDE_OPENAI_MODEL_MAP:
            model = CLAUDE_OPENAI_MODEL_MAP[model]
        if functions is not None:
            if self.openai_anthropic_translation:
                claude_system_prompt, messages = convert_openai_messages_to_claude(messages)
                if isinstance(system_prompt, str) and isinstance(claude_system_prompt, str):
                    claude_system_prompt = system_prompt + claude_system_prompt
                claude_functions = self._convert_openai_functions_to_claude(functions)
            else:
                claude_functions = functions
                claude_system_prompt = system_prompt
            response = self.client.beta.tools.messages.create(
                max_tokens=max_tokens or anthropic.NotGiven(),
                system=claude_system_prompt,
                messages=messages,
                model=model,
                tools=claude_functions,
                **kwargs,
            )
            if self.openai_anthropic_translation:
                return self._convert_claude_response_to_openai(response, parse_function_calls=True, parse_result_block=True)
            else:
                return response
        else:
            response = self.llm_query_no_retry(
                model=model,
                messages=messages,
                max_tokens=max_tokens or anthropic.NotGiven(),
                system_prompt=system_prompt,
                **kwargs,
            )
        return response

    @staticmethod
    def llm_response_to_json(response: openai_types.chat_completion.ChatCompletion | anthropic_types.Message) -> str:
        if isinstance(response, openai_types.chat_completion.ChatCompletion):
            return OpenAIHelper.llm_response_to_json(response)
        else:
            js = json.loads(response.model_dump_json())
            if len(js["content"]) == 0:
                return ""
            return js["content"][0]["text"]


class MultiProviderAIHelper(AbstractAIHelper):
    def __init__(
        self,
        openai_key: str,
        anthropic_key: str | None = None,
        openai_base: str = "https://oai.hconeai.com/v1",
        anthropic_base: str = "https://anthropic.hconeai.com/",
        headers=None,
        use_openai: bool = True,
        use_claude: bool = True,
        cache: bool | None = True,
    ) -> None:
        self.use_openai = use_openai
        self.use_claude = use_claude
        self.cache = cache

        self.openai_helper = OpenAIHelper(openai_key, api_base=openai_base, headers=headers, cache=self.cache)
        if self.use_claude:
            if anthropic_key is None:
                msg = "Anthropic Key must be provided if use_claude is True"
                raise ValueError(msg)

            self.anthropic_helper = AnthropicHelper(anthropic_key, api_base=anthropic_base, headers=headers, openai_anthropic_translation=True, cache=self.cache)

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def embeddings_with_backoff(self, **kwargs):
        # Prioritize OpenAI First
        if self.use_openai:
            return self.openai_helper.embeddings_with_backoff(**kwargs)
        elif self.use_claude:
            return self.anthropic_helper.embeddings_with_backoff(**kwargs)
        else:
            msg = "MultiProviderAIHelper: No AI helper is enabled"
            raise Exception(msg)

    def get_embeddings(self, content_strs: list[str]) -> list[list[float]]:
        # Prioritize OpenAI First
        if self.use_openai:
            return self.openai_helper.get_embeddings(content_strs)
        elif self.use_claude:
            return self.anthropic_helper.get_embeddings(content_strs)
        else:
            msg = "MultiProviderAIHelper: No AI helper is enabled"
            raise Exception(msg)

    def get_embedding(self, content_str: str) -> list[float]:
        # Prioritize OpenAI First
        if self.use_openai:
            return self.openai_helper.get_embedding(content_str)
        elif self.use_claude:
            return self.anthropic_helper.get_embedding(content_str)
        else:
            msg = "MultiProviderAIHelper: No AI helper is enabled"
            raise Exception(msg)

    @backoff.on_exception(backoff.expo, anthropic.RateLimitError)
    def completions_with_backoff(self, **kwargs):
        # This is OpenAI specific
        if self.use_openai:
            return self.openai_helper.completions_with_backoff(**kwargs)
        else:
            msg = "MultiProviderAIHelper: OpenAI Helper is not enabled"
            raise Exception(msg)

    @backoff.on_exception(backoff.expo, anthropic.RateLimitError)
    def messages_with_backoff(self, **kwargs):
        # This is Anthropic specific
        if self.use_claude:
            return self.anthropic_helper.messages_with_backoff(**kwargs)
        else:
            msg = "MultiProviderAIHelper: Anthropic Helper is not enabled"
            raise Exception(msg)

    @retry(wait=wait_random_exponential(min=70, max=600), stop=stop_after_attempt(10))
    def llm_query_with_retry(self, **kwargs):
        return self.llm_query_no_retry(**kwargs)

    def llm_query_no_retry(self, messages: list = [], model: str = "gpt-4-32k", max_tokens: int | None = None, **kwargs):
        if self.use_openai and model.startswith("gpt"):
            return self.openai_helper.llm_query_no_retry(messages=messages, model=model, max_tokens=max_tokens, **kwargs)
        elif self.use_claude and model.startswith("claude"):
            return self.anthropic_helper.llm_query_no_retry(messages=messages, model=model, max_tokens=max_tokens, **kwargs)
        else:
            msg = f"MultiProviderAIHelper: Unknown Model {model}"
            raise Exception(msg)

    @retry(wait=wait_random_exponential(min=70, max=600), stop=stop_after_attempt(10))
    def llm_query_functions_with_retry(self, **kwargs):
        return self.llm_query_functions(**kwargs)

    def llm_query_functions(self, model: str, messages: list, functions: list[dict], max_tokens: int | None = None, **kwargs):
        if self.use_openai and model.startswith("gpt"):
            return self.openai_helper.llm_query_functions(model, messages, functions, max_tokens, **kwargs)
        elif self.use_claude and model.startswith("claude"):
            return self.anthropic_helper.llm_query_functions(model, messages, functions, max_tokens, **kwargs)
        else:
            msg = f"MultiProviderAIHelper: Unknown Model {model}"
            raise Exception(msg)

    @staticmethod
    def llm_response_to_json(response) -> str:
        # Prioritize Anthropic First (Has support for both, while OpenAI only supports OpenAI)
        return AnthropicHelper.llm_response_to_json(response)

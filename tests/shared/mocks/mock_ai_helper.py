from codegen.sdk.ai.helpers import AbstractAIHelper


class MockAIHelper(AbstractAIHelper):
    """Utility class to mock AIHelper. This particular instance doesn't do anything.
    If you want a functional mock AI helper, you can extend this class and
    you would only have to override the function that you want to mock
    """

    def __init__(self) -> None:
        pass

    def embeddings_with_backoff(self, **kwargs) -> None:
        pass

    def get_embeddings(self, content_strs: list[str]) -> list[list[float]]:
        pass

    def get_embedding(self, content_str: str) -> list[float]:
        pass

    def llm_query_with_retry(self, **kwargs) -> None:
        pass

    def llm_query_no_retry(self, messages: list = [], model: str = "gpt-4-32k", max_tokens: int = 3000) -> None:
        pass

    def llm_query_functions_with_retry(self, model: str, messages: list, functions: list[dict], max_tokens: int) -> None:
        pass

    def llm_query_functions(self, model: str, messages: list, functions: list[dict], max_tokens: int | None = None) -> None:
        pass

    def llm_response_to_json(response) -> str:
        pass

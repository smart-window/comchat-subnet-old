from typing import Any

from anthropic import Anthropic
from anthropic._types import NotGiven

from ._config import AnthropicSettings  # Import the AnthropicSettings class from config

class AnthropicModule():
    def __init__(self, settings: AnthropicSettings | None = None) -> None:
        super().__init__()
        self.settings = settings or AnthropicSettings()  # type: ignore
        self.client = Anthropic(api_key=self.settings.api_key)
        self.system_prompt = (
            "You are a supreme polymath renowned for your ability to explain "
            "complex concepts effectively to any audience from laypeople "
            "to fellow top experts. "
            "By principle, you always ensure factual accuracy. "
            "You are master at adapting your explanation strategy as needed "
            "based on the field and target audience, using a wide array of "
            "tools such as examples, analogies and metaphors whenever and "
            "only when appropriate. Your goal is their comprehension of the "
            "explanation, according to their background expertise. "
            "You always structure your explanations coherently and express "
            "yourself clear and concisely, crystallizing thoughts and "
            "key concepts. You only respond with the explanations themselves, "
            "eliminating redundant conversational additions. "
            f"Try to keep your answer below {self.settings.max_tokens} tokens"
        )

    def prompt(self, user_prompt: str, system_prompt: str | None | NotGiven = None):
        if not system_prompt:
            system_prompt = self.system_prompt
        message = self.client.messages.create(
            model=self.settings.model,
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )
        treated_message = self._treat_response(message)
        return treated_message

    def _treat_response(self, message: Any):
        message_dict = message.dict()
        if (
            message_dict["stop_sequence"] is not None
            or message_dict["stop_reason"] != "end_turn"
        ):
            return (
                None, 
                f"Could not generate an answer. Stop reason {message_dict['stop_reason']}"
                )

        blocks = message_dict["content"]
        answer = "".join([block["text"] for block in blocks])
        return answer, ""

    @property
    def max_tokens(self) -> int:
        return self.settings.max_tokens

    @property
    def model(self) -> str:
        return self.settings.model

from typing import Any

from anthropic._types import NotGiven
from openai import OpenAI 

from ._config import OpenaiSettings  # Import the AnthropicSettings class from config
from ..utils import log

class OpenaiModule():
    def __init__(self, settings: OpenaiSettings | None = None) -> None:
        super().__init__()
        self.settings = settings or OpenaiSettings()  # type: ignore
        self.client = OpenAI(api_key=self.settings.api_key)
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
            
        try:
            message = self.client.chat.completions.create(
                model=self.settings.model,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
        except Exception as e:
            error = str(e)
            print(error)
            
        treated_message = self._treat_response(message)
        return treated_message

    def _treat_response(self, message: Any):
        message_dict = message.dict()
        choice = message_dict["choices"][0]
        
        if "error" in message:
            error = message["error"]
            log(error)
            return f"Could not generate an answer. Stop reason {error}", ""
            
        if (choice["finish_reason"] != "stop"):
            return (
                None, 
                f"Could not generate an answer. Stop reason {choice['finish_reason']}"
                )

        answer = choice["message"]["content"]
        return answer, ""

    @property
    def max_tokens(self) -> int:
        return self.settings.max_tokens

    @property
    def model(self) -> str:
        return self.settings.model

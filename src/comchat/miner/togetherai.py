from typing import Any
import requests

from ..utils import log
from ._config import TogetherAISettings  # Import the TogetherAISettings class from config

class TogetherAIModule():
    
    def __init__(self, settings: TogetherAISettings | None = None) -> None:
        super().__init__()
        self.settings = settings or TogetherAISettings() # type: ignore

    def prompt(self, user_prompt: str, system_prompt: str | None = None):
        url = "https://api.together.xyz/v1/chat/completions"

        payload = {
            "model": self.settings.model,
            "messages": [
                {
                    "content": system_prompt,
                    "role": "system"
                },
                {
                    "content": user_prompt,
                    "role": "user"
                },
            ],
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
        }
 
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.settings.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)
        json_response: dict[Any, Any] = response.json()

        if "error" in json_response:
            message = json_response["error"]["message"]
            log(message)
            return None, message
        
        answer = json_response["choices"][0]
        return answer["message"]["content"], ""
        
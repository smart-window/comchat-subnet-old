from typing import Any
import requests

from ._config import MistralSettings  # Import the MistralSettings class from config

class MistralModule():
    
    def __init__(self, settings: MistralSettings | None = None) -> None:
        super().__init__()
        self.settings = settings or MistralSettings() # type: ignore

    def prompt(self, user_prompt: str, system_prompt: str | None = None):
        url = "https://api.mistral.ai/v1/chat/completions"

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
            "temperature": self.settings.temperature,
            "top_p": self.settings.top_p,
            "max_tokens": self.settings.max_tokens,
            "stream": False,
            "safe_prompt": False,
            "random_seed": self.settings.random_seed
        }
 
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.settings.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)
        json_response: dict[Any, Any] = response.json()

        if "message" in json_response:
            message = json_response["message"]
            return None, message
        
        answer = json_response["choices"][0]
        finish_reason = answer['finish_reason']
        if finish_reason != "stop":
            return None, f"Could not get a complete answer: {finish_reason}"
        
        return answer["message"]["content"], ""
        
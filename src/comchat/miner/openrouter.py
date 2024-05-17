from typing import Any

import requests
import json

from ._config import OpenrouterSettings  # Import the OpenrouterSettings class from config

class OpenrouterModule():
    
    def __init__(self, settings: OpenrouterSettings | None = None) -> None:
        super().__init__()
        self.settings = settings or OpenrouterSettings() # type: ignore
        self._max_tokens = self.settings.max_tokens

    @property
    def max_tokens(self) -> int:
        return self._max_tokens
    
    def prompt(self, user_prompt: str, system_prompt: str | None = None):
        context_prompt = system_prompt or self.get_context_prompt(self.max_tokens)
        prompt = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": context_prompt},
                {"role": "user", "content": user_prompt},
            ]
        }
        key = self.settings.api_key
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
            "Authorization": f"Bearer {key}",
            },
            data=json.dumps(prompt)
        )

        json_response: dict[Any, Any] = response.json()
        
        if "error" in json_response:
            raise Exception(json_response["error"])
            
        answer = json_response["choices"][0]

        return answer["message"]["content"], ""
    
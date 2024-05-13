from typing import Any
import requests

from ._config import PerplexitySettings  # Import the PerplexitySettings class from config

class PerplexityModule():
    
    def __init__(self, settings: PerplexitySettings | None = None) -> None:
        super().__init__()
        self.settings = settings or PerplexitySettings() # type: ignore

    def prompt(self, user_prompt: str, system_prompt: str | None = None):
        url = "https://api.perplexity.ai/chat/completions"

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
            "top_p": self.settings.top_p,
            "top_k": self.settings.top_k,
            "stream": False,
            "presence_penalty": self.settings.presence_penalty,
            "frequency_penalty": self.settings.frequency_penalty
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
            return None, message
            
        answer = json_response["choices"][0]
        finish_reason = answer['finish_reason']
        if finish_reason != "stop":
            return None, f"Could not get a complete answer: {finish_reason}"
        
        return answer["message"]["content"], ""
        
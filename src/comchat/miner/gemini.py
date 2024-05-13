import google.generativeai as genai

from ._config import GeminiSettings  # Import the GeminiSettings class from config

class GeminiModule():
    def __init__(self, settings: GeminiSettings | None = None) -> None:
        super().__init__()
        self.settings = settings or GeminiSettings()  # type: ignore
        genai.configure(api_key=self.settings.api_key)
        self.client = genai

    def prompt(self, user_prompt: str, system_prompt: str | None):
        model = self.client.GenerativeModel(self.settings.model)
        response = model.generate_content(user_prompt)
        
        return response.text, ""

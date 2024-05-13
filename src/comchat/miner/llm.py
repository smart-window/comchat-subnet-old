from communex.module.module import Module, endpoint  # type: ignore
from abc import ABC
from fastapi import HTTPException
from .anthropic import AnthropicModule
from .openrouter import OpenrouterModule
from .openai import OpenaiModule
from .perplexity import PerplexityModule
from .mistral import MistralModule
from .togetherai import TogetherAIModule
from .groq import GroqModule
from .gemini import GeminiModule
from ._config import AnthropicSettings, OpenrouterSettings, OpenaiSettings, PerplexitySettings, MistralSettings, TogetherAISettings, GroqSettings, GeminiSettings
from ..utils import log

class LLM(ABC, Module):
    @property
    def max_tokens(self) -> int:
        ...

    @property
    def model(self) -> str:
        ...

    def get_context_prompt(self, max_tokens: int) -> str:
        prompt = (
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
            f"Try to keep your answer below {max_tokens} tokens"
        )
        return prompt
    
    @endpoint
    def generate(self, service: str, model: str, prompt: str) -> dict[str, str]:
        log(f"Service: {service}, Model: {model}, Prompt: {prompt[:100]}...")
        # Select the module based on the service parameter
        if service == "anthropic":
            module = AnthropicModule(settings=AnthropicSettings(model=model))
        elif service == "openrouter":
            module = OpenrouterModule(settings=OpenrouterSettings(model=model))
        elif service == "openai":
            module = OpenaiModule(settings=OpenaiSettings(model=model))
        elif service == "perplexity":
            module = PerplexityModule(settings=PerplexitySettings(model=model))
        elif service == "mistral":
            module = MistralModule(settings=MistralSettings(model=model))
        elif service == "togetherai":
            module = TogetherAIModule(settings=TogetherAISettings(model=model))
        elif service == "groq":
            module = GroqModule(settings=GroqSettings(model=model))
        elif service == "gemini":
            module = GeminiModule(settings=GeminiSettings(model=model))
        else:
            raise HTTPException(status_code=400, detail="Unsupported service")

        try:
            message = module.prompt(prompt, self.get_context_prompt(self.max_tokens))
            log(f"Answer: {message[:100]}...")
        except Exception as e:
            raise HTTPException(status_code=e.status_code, detail=str(e)) from e  # type: ignore

        match message:
            case None, explanation:
                raise HTTPException(status_code=500, detail=explanation)
            case answer, _:
                return {"answer": answer}
            
    @endpoint
    def get_model(self):
        return {"model": self.model}
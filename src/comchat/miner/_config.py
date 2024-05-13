from pydantic_settings import BaseSettings

class OpenaiSettings(BaseSettings):
    api_key: str
    model: str = "gpt-4-turbo"
    max_tokens: int = 4096
    temperature: float = 1

    class Config:
        env_prefix = "OPENAI_"
        env_file = "env/config.env"
        extra = "ignore"
        
class AnthropicSettings(BaseSettings):
    api_key: str
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 3000
    temperature: float = 0.5

    class Config:
        env_prefix = "ANTHROPIC_"
        env_file = "env/config.env"
        extra = "ignore"

class OpenrouterSettings(BaseSettings):
    api_key: str
    model: str = "anthropic/claude-3-opus"
    max_tokens: int = 3000
    temperature: float = 0.5

    class Config:
        env_prefix = "OPENROUTER_"
        env_file = "env/config.env"
        extra = "ignore"
        
class PerplexitySettings(BaseSettings):
    api_key: str
    model: str = "mistral-7b-instruct"
    max_tokens: int = 0
    temperature: float = 0.5
    top_p: float = 0.9
    top_k: float = 0
    presence_penalty: float = 0
    frequency_penalty: float = 1

    class Config:
        env_prefix = "PERPLEXITY_"
        env_file = "env/config.env"
        extra = "ignore"
        
class TogetherAISettings(BaseSettings):
    api_key: str
    model: str
    max_tokens: int = 3000
    temperature: float = 0.8

    class Config:
        env_prefix = "TOGETHERAI_"
        env_file = "env/config.env"
        extra = "ignore"
        
class MistralSettings(BaseSettings):
    api_key: str
    model: str = "mistral-small-latest"
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 1
    random_seed: float = 1337

    class Config:
        env_prefix = "MISTRAL_"
        env_file = "env/config.env"
        extra = "ignore"
        
class GroqSettings(BaseSettings):
    api_key: str
    model: str
    max_tokens: int = 1024

    class Config:
        env_prefix = "GROQ_"
        env_file = "env/config.env"
        extra = "ignore"
        
class GeminiSettings(BaseSettings):
    api_key: str
    model: str

    class Config:
        env_prefix = "GEMINI_"
        env_file = "env/config.env"
        extra = "ignore"

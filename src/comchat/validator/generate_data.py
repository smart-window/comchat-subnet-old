import json
from typing import cast, Any

from .meta_prompt import explanation_prompt
from ..miner.llm import LLM


class InputGenerator:
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def gen_explanation(
        self,
    ):
        system_prompt = (
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
            f"Try to keep your answer below {self.llm.max_tokens} tokens"
        )

        user_prompt, criteria = explanation_prompt()
        val_answer = self.llm.prompt(
            user_prompt=user_prompt, system_prompt=system_prompt
        )
        match val_answer:
            case None, explanation:
                raise RuntimeError(f"Failed to generate explanation: {explanation}")
            case answer, _:
                return answer, user_prompt, criteria


if __name__ == "__main__":
    ig = InputGenerator()
    p = 5
    prompt, _ = explanation_prompt(p)
    response = ig.prompt_explanation_claude(ig.client, prompt, p)
    breakpoint()
    exit()
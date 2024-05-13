import asyncio
import concurrent.futures
import re
import time
import random
from functools import partial
from enum import Enum

import numpy as np
from communex.client import CommuneClient  # type: ignore
from communex.module.client import ModuleClient  # type: ignore
from communex.module.module import Module  # type: ignore
from communex.types import Ss58Address  # type: ignore
from fuzzywuzzy import fuzz  # type: ignore
from substrateinterface import Keypair  # type: ignore

from ..miner._config import AnthropicSettings, OpenrouterSettings
from ..miner.anthropic import AnthropicModule
from ..miner.openrouter import OpenrouterModule
from ..utils import retry, log
from ._config import ValidatorSettings
from .generate_data import InputGenerator
from .meta_prompt import get_miner_prompt
from .similarity import Embedder, OpenAIEmbedder, OpenAISettings, euclidean_distance
from .sigmoid import threshold_sigmoid_reward_distribution
from .models import models

# TODO: make it match ipv6
IP_REGEX = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")


def set_weights(
    score_dict: dict[int, float], netuid: int, client: CommuneClient, key: Keypair
) -> None:
    """
    Set weights for miners based on their scores.

    Args:
        score_dict (dict[int, float]): A dictionary mapping miner UIDs to their scores.
        netuid (int): The network UID.
        client (CommuneClient): The CommuneX client.
        key (Keypair): The keypair for signing transactions.
    """

    cut_weights = cut_to_max_allowed_weights(score_dict)
    adjsuted_to_sigmoid = threshold_sigmoid_reward_distribution(cut_weights)

    # Create a new dictionary to store the weighted scores
    weighted_scores: dict[int, int] = {}

    # Calculate the sum of all inverted scores
    scores = sum(adjsuted_to_sigmoid.values())

    # Iterate over the items in the score_dict
    for uid, score in adjsuted_to_sigmoid.items():
        # Calculate the normalized weight as an integer
        weight = int(score * 1000 / scores)

        # Add the weighted score to the new dictionary
        weighted_scores[uid] = weight

    # filter out 0 weights
    weighted_scores = {k: v for k, v in weighted_scores.items() if v != 0}

    uids = list(weighted_scores.keys())
    weights = list(weighted_scores.values())
    log(f"Settings weights for the following uids: {uids}")
    client.vote(key=key, uids=uids, weights=weights, netuid=netuid)


def cut_to_max_allowed_weights(
    score_dict: dict[int, float], settings: ValidatorSettings | None = None
) -> dict[int, float]:
    """
    Cuts the scores to the maximum allowed weights.

    Args:
        score_dict (dict[int, float]): A dictionary mapping miner UIDs to their scores.

    Returns:
            dict[int, float]: A dictionary mapping miner UIDs to their scores,
            where the scores have been cut to the maximum allowed weights.
    """

    if not settings:
        settings = ValidatorSettings()  # type: ignore

    max_allowed_weights = settings.max_allowed_weights
    
    # sort the score by highest to lowest
    sorted_scores = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

    # cut to max_allowed_weights
    cut_scores = sorted_scores[:max_allowed_weights]

    return dict(cut_scores)

def extract_address(string: str):
    """
    Extracts an address from a string.
    """
    return re.search(IP_REGEX, string)


def get_comchat_netuid(clinet: CommuneClient, subnet_name: str = "comchat"):
    """
    Retrieves the network UID of the ComChat subnet.

    Args:
        client (CommuneClient): The CommuneX client.
        subnet_name (str, optional): The name of the ComChat subnet. Defaults to "comchat".

    Returns:
        int: The network UID of the ComChat subnet.
    """

    subnets = clinet.query_map_subnet_names()
    for netuid, name in subnets.items():
        if name == subnet_name:
            return netuid
    raise ValueError(f"Subnet {subnet_name} not found")


def get_ip_port(modules_adresses: dict[int, str]):
    filtered_addr = {id: extract_address(addr) for id, addr in modules_adresses.items()}
    ip_port = {
        id: x.group(0).split(":") for id, x in filtered_addr.items() if x is not None
    }
    return ip_port

class ClaudeProviders(Enum):
    ANTHROPIC  = "anthropic"
    OPENROUTER = "openrouter"


class TextValidator(Module):
    """A class for validating text data using a ComChat network.

    This class provides methods for generating questions and answers, scoring miner
    answers, and validating text data using a ComChat network. It interacts with a
    Communex module client to communicate with the ComChat network.

    Attributes:
        client: A Communex module client instance for communicating with the ComChat
            network.
        settings: A ValidatorSettings instance containing configuration settings for
            the validator.
        input_generator: An InputGenerator instance for generating input data.
        question_prompt: A string containing the prompt for generating questions.
        answer_prompt: A string containing the prompt for generating answers.
        COMCHAT_NETUID: An integer representing the unique identifier of the ComChat
            network.

    Methods:
        __init__(self, settings: ValidatorSettings): Initializes a new instance of
            the TextValidator class with the specified settings.
        run(self): Runs the text validation process.
        score(self, val_answer: str, miner_answer: str) -> int: Scores a miner's
            answer against the validator's answer.
        extract_address(self, string: str) -> re.Match: Extracts an IP address and
            port from a string.
        get_ip_port(self, addresses: List[str]) -> List[Tuple[str, str]]: Extracts
            IP addresses and ports from a list of strings.
    """

    def __init__(
        self,
        key: Keypair,
        netuid: int,
        client: CommuneClient,
        provider: ClaudeProviders = ClaudeProviders.OPENROUTER,
        embedder: Embedder | None = None,
        call_timeout: int = 60,
    ) -> None:
        super().__init__()
        self.client = client
        self.key = key
        self.netuid = netuid
        if not embedder:
            embedder = OpenAIEmbedder(OpenAISettings())  # type: ignore
        self.embedder = embedder
        self.val_model = "openai/gpt-4-32k"
        self.call_timeout = call_timeout
        self.provider = provider

    def get_modules(self, client: CommuneClient, netuid: int) -> dict[int, str]:
        """Retrieves all module addresses from the subnet.

        Args:
            client: The CommuneClient instance used to query the subnet.
            netuid: The unique identifier of the subnet.

        Returns:
            A list of module addresses as strings.
        """
        module_addreses = client.query_map_address(netuid)
        return module_addreses

    def _get_validation_dataset(self, settings: ValidatorSettings):
        
        # TODO: make ValidatorSettings and the miners settings inherit from a
        # common protocol
        match self.provider:
            case ClaudeProviders.ANTHROPIC:
                claude_settings = AnthropicSettings()  # type: ignore
                claude_settings.temperature = settings.temperature
                claude_settings.max_tokens = settings.max_tokens
                claude_settings.model = self.val_model
                claude = AnthropicModule(claude_settings)
            case ClaudeProviders.OPENROUTER:
                claude_settings = OpenrouterSettings()  # type: ignore
                claude_settings.temperature = settings.temperature
                claude_settings.max_tokens = settings.max_tokens
                claude_settings.model = self.val_model
                claude = OpenrouterModule(claude_settings)
        
        ig = InputGenerator(claude)

        retrier = retry(4, [Exception])
        generate_explanations = retrier(ig.gen_explanation)

        explanations, prompt, criteria = generate_explanations()

        dataset: tuple[str, str] = (prompt, explanations)
        questions_age = time.time()
        return dataset, criteria, questions_age

    def _get_miner_prediction(
        self,
        question: str,
        service: str,
        model: str,
        miner_info: tuple[list[str], Ss58Address],
    ) -> str | str | str | None:
        connection, miner_key = miner_info
        module_ip, module_port = connection

        client = ModuleClient(module_ip, int(module_port), self.key)
        try:
            miner_answer = asyncio.run(
                client.call(
                    "generate", miner_key, 
                    {
                        "service": service,
                        "model": model,
                        "prompt": question,
                    }, 
                    timeout=self.call_timeout
                    )
            )
            miner_answer = miner_answer["answer"]

        except Exception as e:
            log(f"Miner {module_ip}:{module_port} failed to generate an answer")
            print(e)
            miner_answer = None

        return miner_answer

    def _get_unit_euclid_distance(
        self, embedded_miner_answer: list[float], embbeded_val_answer: list[float]
    ):
        distance = euclidean_distance(embedded_miner_answer, embbeded_val_answer)
        miner_norm = np.linalg.norm(embedded_miner_answer)
        val_norm = np.linalg.norm(embbeded_val_answer)
        normalized_distance = distance / (miner_norm + val_norm)
        return float(normalized_distance)  # i hate python's type system

    def _score_miner(
        self, miner_answer: str | None, embbeded_val_answer: list[float]
    ) -> float:
        if not miner_answer:
            return 0
        embedded_miner_answer = self.embedder.get_embedding(miner_answer)
        normalized_distance = self._get_unit_euclid_distance(
            embedded_miner_answer, embbeded_val_answer
        )
        return 1 - normalized_distance

    def _split_val_subject(self, val_answer: str):
        end_of_subject = val_answer.find("\n")
        subject = val_answer[:end_of_subject]
        val_answer = val_answer[end_of_subject + 1 :]
        return subject, val_answer

    def _test_score(self, text_a: str, text_b: str):
        embbeded_a = self.embedder.get_embedding(text_a)
        score = self._score_miner(text_b, embbeded_a)
        sim = fuzz.ratio(text_a, text_b)  # type: ignore
        log(f"Score: {score}, similarity: {sim}")

    async def validate_step(
        self, settings: ValidatorSettings, comchat_netuid: int
    ) -> list[dict[str, str]]:
        """Performs a validation step.

        Generates questions based on the provided settings, prompts modules to
        generate answers, and scores the generated answers against the validator's
        own answers.

        Args:
            settings: The validator settings to use for this validation step.
            comchat_netuid: The netuid of the ComChat subnet.
        """

        modules_adresses = self.get_modules(self.client, comchat_netuid)
        modules_keys = self.client.query_map_key(comchat_netuid)
        val_ss58 = self.key.ss58_address
        if val_ss58 not in modules_keys.values():
            raise RuntimeError(
                f"validator key {val_ss58} is not registered in subnet"
                )
        modules_info: dict[int, tuple[list[str], Ss58Address]] = {}

        modules_filtered_address = get_ip_port(modules_adresses)
        for module_id in modules_keys.keys():
            module_addr = modules_filtered_address.get(module_id, None)
            if not module_addr:
                continue
            modules_info[module_id] = (module_addr, modules_keys[module_id])

        response_cache: list[str] = []
        score_dict: dict[int, float] = {}
        # == Validation loop / Scoring ==

        dataset, criteria, _ = self._get_validation_dataset(settings)
        _, val_answer = dataset
        subject, val_answer = self._split_val_subject(val_answer)
        miner_prompt = get_miner_prompt(criteria, subject, len(val_answer))
        embedded_val_answer = self.embedder.get_embedding(val_answer)

        model = random.choice(models)
        get_miner_prediction = partial(self._get_miner_prediction, miner_prompt, model["service"], model["model"])
        log(f"Selected the following miners: {modules_info.keys()}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            it = executor.map(get_miner_prediction, modules_info.values())
            miner_answers = [*it]
        for uid, miner_response in zip(modules_info.keys(), miner_answers):
            miner_answer = miner_response
            if not miner_answer:
                log(f"Skipping miner {uid} that didn't answer")
                continue
            score = self._score_miner(miner_answer, embedded_val_answer)
            for answer in response_cache:
                similarity = fuzz.ratio(answer, miner_answer)  # type: ignore
                log(f"similarity: {similarity}")
            response_cache.append(miner_answer)

            # score has to be lower or eq to 1, as one is the best score
            assert score <= 1
            score_dict[uid] = score
        if not score_dict:
            log("No miner managed to give a valid answer")
            return []
        _ = set_weights(score_dict, self.netuid, self.client, self.key)

    def validation_loop(self, settings: ValidatorSettings | None = None) -> None:
        if not settings:
            settings = ValidatorSettings()  # type: ignore

        # Run validation
        while True:
            start_time = time.time()
            asyncio.run(self.validate_step(settings, self.netuid))

            elapsed = time.time() - start_time
            if elapsed < settings.iteration_interval:
                sleep_time = settings.iteration_interval - elapsed
                log(f"Sleeping for {sleep_time}")
                time.sleep(sleep_time)


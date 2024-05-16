# ComChat

Welcome to the ComChat Subnet, where together we'll shape the future of AI services on the Commune Blockchain Network!

## Overview

We are thrilled to embark on this exciting journey with you as we launch the ComChat Subnet on the Commune Blockchain Network. This venture represents a significant step forward in the fusion of blockchain and AI technologies, providing a platform for eight diverse AI services including OpenAI, OpenRouter, Anthropic, Groq, Gemini, Mistral, TogetherAI, and Perplexity.

As miners, you will be running these AI modules, contributing to the stability and functionality of the ComChat product, and laying the groundwork for a public ComChat API that will benefit all Commune users. Validators, your role is indispensable in continuously prompting AI services and models and scoring miners based on their responses, ensuring the integrity and quality of our network.

This initiative is not just about the technology; it's about the potential it holds. It's about creating a more robust, innovative, and inclusive digital landscape where AI services are accessible and reliable. It's about building a community where everyone can reap the benefits of advanced AI technologies.

We're looking forward to seeing what we can achieve together. Let's make the ComChat Subnet a beacon of innovation and collaboration in the world of AI and blockchain.

## Motivation

We stand at the precipice of a new era. An era where AI services are not just a tool, but a fundamental pillar of our digital society. Together, we have the ability to shape this future and make a significant impact on the Commune Blockchain Network and beyond.

As miners, you are the backbone of our ComChat Subnet. The AI services you run will not only fuel our product but also lay the foundation for a public ComChat API, opening a world of possibilities for Commune users. Your work will help democratize access to high-quality AI services, fostering innovation and creativity within our community.

Validators, your role is equally crucial. Your constant vigilance ensures the quality and efficiency of our ComChat product. The scoring you provide determines the weight of each miner, ensuring a fair and balanced network. Your work upholds the integrity of our system and guarantees that our users receive the best service possible.

The journey ahead will not be without challenges. But remember, every response you provide, every validation you make, brings us one step closer to our vision. A vision where AI services are accessible, reliable, and efficient. A vision where our ComChat product can serve the needs of every Commune user.

So, let's embrace this opportunity. Let's shape the future of AI services together. Let's create a world where technology serves not just the few, but the many.

Thank you for your dedication and commitment. Together, we will make the ComChat Subnet a success.

## Resources

- You can check the comchat platform [here](https://comchat.io)!

## Installation

Make sure you are on the latest CommuneX version.

```sh
pip install communex --upgrade
```

### Setup your environment
- Clone the repo
  - `git clone https://github.com/smart-window/comchat-subnet.git && cd comchat-subnet`
- Install Python 3 and pip
  - `sudo apt update`
  - `sudo apt install python3`
  - `sudo apt install python3-pip`
- Install the Python dependencies with `pip install -e .`

## Running A Miner

1. Create a file named `config.env` in the `env/` folder with the following
   contents (you can also see the `env/config.env.sample` as an example):

   ```sh
    ANTHROPIC_API_KEY="<your-anthropic-api-key>"
    OPENROUTER_API_KEY="<your-openrouter-api-key>"
    OPENAI_API_KEY="<your-openai-api-key>"
    PERPLEXITY_API_KEY="<your-perplexity-api-key>"
    GROQ_API_KEY="<your-groq-api-key>"
    MISTRAL_API_KEY="<your-mistral-api-key>"
    TOGETHERAI_API_KEY="<your-togetherai-api-key>"
    GEMINI_API_KEY="<your-gemini-api-key>"
   ```

   Validators will randomly pick the service to ping the miners.
2. Serve the miner:

   Make sure to be located in the root of comchat repository

   ```sh  
   cd comchat
   ```

   Proceed with running the miner:

   ```sh
    comx module serve comchat.miner.llm.LLM <your_commune_key> --subnets-whitelist 6 --ip 0.0.0.0
   ```

   The **ip** is passed as **0.0.0.0** to accept **outside connections**, since the default,
   **127.0.0.1** accepts **only local** connections. ComChat has the **netuid 6**. Key is a name of your commune wallet/key.
   If you don't have a wallet, generate one by running

   ```sh
   comx key create <name>
   ```

   **Note**: you need to keep this process alive, running in the background. Some
   options are [tmux](https://www.tmux.org/](https://ioflood.com/blog/install-tmux-command-linux/)), [pm2](https://pm2.io/docs/plus/quick-start/) or [nohup](https://en.wikipedia.org/wiki/Nohup).

   Example using pm2

   ```sh
   pm2 start "comx module serve comchat.miner.llm.LLM <your_commune_key> --subnets-whitelist 6 --ip 0.0.0.0" --name <name>
   ```

3. Finally register the module on the ComChat subnet:

    ```sh
    comx module register <name> <your_commune_key> --ip <your-ip-address> --port <port> --netuid 6  
    ```

### Note

- Make sure to **serve and register** the module using the **same key**.
- If you are not sure about your `public ip` address:

   ```sh
   curl -4 https://ipinfo.io/ip
   ```

- If you want to check for yourself, you can run:

   ```sh
   comx subnet list
   ```

   And look for the name `comchat`

## Running A Validator

1. Get an API key from [Anthropic](https://console.anthropic.com/).

2. Gen an API key for embeddings from [OpenAi](https://openai.com/product)

3. Create a file named `config.env` in the `env/` folder with the following contents (you can also see the `env/config.env.sample` as an example):

   ```sh
   ANTHROPIC_API_KEY="<your-anthropic-claude-api-key>"
   OPENROUTER_API_KEY="<your-openrouter-api-key>"
   OPENAI_API_KEY="<your-openai-api-key>"
   ```
  
    Alternatively, you can set up those values as enviroment variables.

4. Register the validator

   Note that you are required to register the validator first, this is because the validator has to be on the network in order to set weights. You can do this by running the following command:

   ```sh
   comx module register <name> <your_commune_key> --netuid 6
   ```

5. Serve the validator

   ```sh
   python3 -m comchat.cli <your_commune_key> [--call-timeout <seconds>] [--provider <provider_name>]
   ```

   The default value of the `--call-timeout` parameter is 65 seconds.
   You can pass --provider openrouter to run using openrouter provider

   Note: you need to keep this process alive, running in the background. Some options are [tmux](https://www.tmux.org/](https://ioflood.com/blog/install-tmux-command-linux/)), [pm2](https://pm2.io/docs/plus/quick-start/) or [nohup](https://en.wikipedia.org/wiki/Nohup).

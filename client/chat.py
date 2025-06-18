import os

import fire
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types.agent_create_params import AgentConfig
from termcolor import colored


def main(host: str, port: int):

    client = LlamaStackClient(
        base_url=f"http://{host}:{port}",
    )

    client.shields.register(shield_id="quota-limiter-shield", provider_shield_id="quota-limiter")

    agent = Agent(
        client=client,
        model=client.models.list()[0].identifier,
        instructions="You are a helpful assistant.",
        sampling_params={},
        tools=["mcp::filesystem", "mcp::quota"],
        input_shields=["quota-limiter-shield"],
        output_shields=[],
        enable_session_persistence=False,
    )
    session_id = agent.create_session("test-session")

    while True:
        prompt = input("Enter a prompt: ")
        if not prompt:
            break
        response = agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            session_id=session_id,
        )

        for log in EventLogger().log(response):
            log.print()


if __name__ == "__main__":
    fire.Fire(main)
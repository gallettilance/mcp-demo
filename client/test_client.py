import fire
from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger
from termcolor import colored


def main():
    host = 'localhost'
    port = 8321

    client = LlamaStackClient(
        base_url=f"http://{host}:{port}",
    )

    available_shields = [shield.identifier for shield in client.shields.list()]
    if not available_shields:
        print(colored("No available shields. Disabling safety.", "yellow"))
    else:
        print(f"Available shields found: {available_shields}")

    available_models = [
        model.identifier for model in client.models.list() if model.model_type == "llm"
    ]

    # the model decision logic is basic
    if not available_models:
        print(colored("No available models. Exiting.", "red"))
        return
    else:
        selected_model = available_models[0]
        print(f"Using model: {selected_model}")

    tools = client.tools.list(toolgroup_id="mcp::filesystem")
    print(f'Available tools: {tools}')

    agent = Agent(
        client=client,
        model=selected_model,
        instructions="You are a helpful assistant.",
        sampling_params={},
        tools=["mcp::filesystem"],
        input_shields=[],
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
        
        # acc = ""
        for log in EventLogger().log(response):
            log.print()
            # if log.role != 'tool_execution':
            #     acc += log.content

        # print(acc)

if __name__ == "__main__":
    fire.Fire(main)
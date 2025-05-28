from llama_stack_client import LlamaStackClient

PROMPT = "Say Hello"

client = LlamaStackClient(base_url="http://localhost:8321")

print(client.agents)

session = client.agents.session.create(
    agent_id="meta-reference",
    session_name="test-session"
)

response = client.agents.session.chat(
    session_id=session.session_id,
    messages=[{"role": "user", "content": PROMPT}],
)

print(response.completion_message.content)
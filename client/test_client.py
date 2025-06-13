from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.lib.agents.event_logger import EventLogger

import streamlit as st
import requests
import re

def pretty_response(response):
    prev_role, ok = None, False
    for log in EventLogger().log(response):
        if ok:
            yield log.content
        elif prev_role is None and log.role == "tool_execution":
            yield "🛠 Used Tool: "
            match = re.search(r"Tool:(\w+)", log.content)
            if match:
                tool_name = match.group(1)
                yield f":orange[`{tool_name}`]"
            yield '  \n'
            prev_role = log.role
        elif prev_role == 'tool_execution' and log.role == "inference":
            ok = True
            prev_role = log.role
            yield log.content

host = 'localhost'
port = 8321

client = LlamaStackClient(
    base_url=f"http://{host}:{port}",
)

agent = Agent(
    client=client,
    model=client.models.list()[0].identifier,
    instructions="You are a helpful assistant.",
    sampling_params={},
    tools=["mcp::filesystem"],
    input_shields=[],
    output_shields=[],
    enable_session_persistence=False,
)

session_id = agent.create_session("test-session")

st.set_page_config(page_title="Router Agent UI", layout="centered")
st.title("🔀 Multi-Agent Router Interface")
user_input = st.text_area("🗣️ Enter your prompt", height=150)

if st.button("Run Agent") and user_input.strip():
    try:
        response = agent.create_turn(
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            session_id=session_id,
        )
        
        st.subheader("🤖 Agent Response")
        with st.spinner("Thinking..."):
            st.write_stream(pretty_response(response))

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to reach router agent: {e}")
else:
    st.info("Enter a prompt and press 'Run Agent' to begin.")

import threading
import streamlit as st

from response_lock import reset, append_response, set_done, set_error, get_response
from utils import prettyPrint
from hil_service.hil import approval_store, approve_tool, ApprovalRequest, Decision

from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent

from streamlit_autorefresh import st_autorefresh

host = 'localhost'
port = 8321

client = LlamaStackClient(base_url=f"http://{host}:{port}")

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

def run_agent_async(user_input, session_id):
    try:
        reset()
        for event in agent.create_turn(
            messages=[{"role": "user", "content": user_input}],
            session_id=session_id
        ):
            append_response(event)
        set_done()
    except Exception as e:
        set_error(e)

# === Streamlit UI ===
st.set_page_config(page_title="Router Agent UI", layout="wide")
st.title("🔀 Multi-Agent Router")

approval_text = "🧍 Human Approvals" if len(approval_store.items()) == 0 else f'({len(approval_store.items())}) 🧍 Human Approvals'
tab1, tab2 = st.tabs(["🧠 Agent Chat", approval_text])

with tab1:
    if "agent_running" not in st.session_state:
        st.session_state["agent_running"] = False
    
    with st.form(key="agent-form"):
        user_input = st.text_area("🗣️ Enter your prompt", height=100, placeholder="Tell me a fun physics fact")
        submitted = st.form_submit_button("Run Agent")

    if submitted:
        st.session_state["agent_running"] = True
        threading.Thread(target=run_agent_async, args=(user_input, session_id)).start()

    state = get_response()

    if state["status"] == "idle":
        st.info("Enter a prompt and press 'Run Agent' to begin.")
    elif state["status"] == "running":
        st.subheader("🤖 Agent Response")
        for line in state["display_log"]:
            st.info(line)
        st_autorefresh(interval=1000, key="agent-refresh")
    elif state["status"] == "done":
        st.subheader("🤖 Agent Response")
        st.write_stream(prettyPrint(state["agent_response"]))
        st.session_state["agent_running"] = False
    elif state["status"] == "error":
        st.error(f"❌ Agent Error: {state['error']}")
        st.session_state["agent_running"] = False
    
    if st.session_state["agent_running"] == True:
        print("hello")
        print(approval_store)
        st_autorefresh(interval=1000, limit=1000, key="refresh")

with tab2:
    st.subheader("⏳ Pending Tool Approvals")
    if not approval_store:
        st.info("No pending approvals.")
    else:
        for key, decision in list(approval_store.items()):
            with st.expander(f"Tool: {key.tool_name} (ID: {key.id})", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Approve {key.tool_name}", key=f"approve-{key.id}"):
                        req = ApprovalRequest(
                            id = key.id,
                            tool_name=key.tool_name,
                            decision=Decision.approved
                        )
                        resp = approve_tool(req)
                        st.success("Approved")
                with col2:
                    if st.button(f"❌ Reject {key.tool_name}", key=f"reject-{key.id}"):
                        req = ApprovalRequest(
                            id = key.id,
                            tool_name=key.tool_name,
                            decision=Decision.rejected
                        )
                        resp = approve_tool(req)
                        st.error("Rejected")

import threading
import streamlit as st

from response_lock import reset, append_response, set_done, set_error, get_response
from approval import ApprovalGate, pending_approvals
from agent import HumanApprovalAgent
from utils import prettyPrint

from llama_stack_client import LlamaStackClient

from streamlit_autorefresh import st_autorefresh

def approval_callback(tool):
    gate = ApprovalGate(tool.identifier)
    pending_approvals[gate.key] = gate
    gate.wait(timeout=120)
    del pending_approvals[gate.key]
    if gate.result is None:
        raise RuntimeError(f"Tool {tool.identifier} was rejected.")
    return gate.result or "Approved"


host = 'localhost'
port = 8321

client = LlamaStackClient(base_url=f"http://{host}:{port}")

agent = HumanApprovalAgent(
    client=client,
    model=client.models.list()[0].identifier,
    instructions="You are a helpful assistant.",
    sampling_params={},
    tools=["mcp::filesystem"],
    input_shields=[],
    output_shields=[],
    enable_session_persistence=False,
    approval_callback=approval_callback,
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

approval_text = "🧍 Human Approvals" if len(pending_approvals.items()) == 0 else f'({len(pending_approvals.items())}) 🧍 Human Approvals'
tab1, tab2 = st.tabs(["🧠 Agent Chat", approval_text])

with tab1:
    with st.form(key="agent-form"):
        user_input = st.text_area("🗣️ Enter your prompt", height=100, placeholder="Tell me a fun physics fact")
        submitted = st.form_submit_button("Run Agent")

    if submitted:
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
    elif state["status"] == "error":
        st.error(f"❌ Agent Error: {state['error']}")

with tab2:
    st.subheader("⏳ Pending Tool Approvals")
    if not pending_approvals:
        st.info("No pending approvals.")
    else:
        for key, gate in list(pending_approvals.items()):
            with st.expander(f"Tool: {gate.tool_name} (Request ID: {key})", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Approve {gate.tool_name}", key=f"approve-{key}"):
                        gate.approve("Approved")
                        st.success("Approved")
                with col2:
                    if st.button(f"❌ Reject {gate.tool_name}", key=f"reject-{key}"):
                        gate.reject()
                        st.error("Rejected")

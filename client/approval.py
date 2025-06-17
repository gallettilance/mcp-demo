# approval_store.py
import threading

class ApprovalGate:
    def __init__(self, tool_name):
        self.tool_name = tool_name
        self.result = None
        self._event = threading.Event()
        self.key = f"{tool_name}-{id(self)}"

    def approve(self, result):
        self.result = result
        self._event.set()

    def reject(self):
        self.result = None
        self._event.set()

    def wait(self, timeout=None):
        self._event.wait(timeout=timeout)
        return self.result

# 💡 This dictionary is now shared across threads and persists across Streamlit reruns
pending_approvals = {}

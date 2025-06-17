import time
from llama_stack_client.lib.agents.agent import Agent
from response_lock import log_display

class HumanApprovalAgent(Agent):
    def __init__(self, *args, approval_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.approval_callback = approval_callback
        self._tools_by_id = {}

    def _load_tool_lookup(self):
        self.tools = self.client.tool_runtime.list_tools()
        self._tools_by_id = {tool.identifier: tool for tool in self.tools}

    def create_turn(self, messages, session_id, **kwargs):
        if not self._tools_by_id:
            self._load_tool_lookup()

        stream = super().create_turn(messages=messages, session_id=session_id)
        for event in stream:
            # Intercept tool execution events
            if hasattr(event.event, "payload") and hasattr(event.event.payload, "step_details"):
                step = event.event.payload.step_details
                if step.step_type == "tool_execution":
                    for call in step.tool_calls:
                        tool_def = self._tools_by_id.get(call.tool_name)
                        if not tool_def:
                            continue

                        log_display(f"🛠 Calling tool: `{call.tool_name}`")

                        is_destructive = (
                            tool_def.annotations.get("destructiveHint", False)
                            if tool_def.annotations else False
                        )

                        if is_destructive and self.approval_callback:
                            log_display("🟡 Waiting for human approval...")
                            tool_result = None
                            while tool_result is None:
                                tool_result = self.approval_callback(tool_def)
                                if tool_result is None:
                                    time.sleep(0.1)
                            log_display("✅ Tool approved!")

            yield event
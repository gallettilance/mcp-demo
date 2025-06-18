import time
import asyncio
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.types.agents import AgentTurnResponseStreamChunk
from response_lock import log_display
from hil_service import approval_store

def extract_tool_calls_from_turn_complete(chunk: AgentTurnResponseStreamChunk):
    calls = []
    if getattr(chunk, "event", None) and getattr(chunk.event.payload, "turn", None):
        for step in chunk.event.payload.turn.steps:
            if step.step_type == "inference":
                response = getattr(step, "api_model_response", None)
                if response and getattr(response, "tool_calls", None):
                    calls.extend(response.tool_calls)
    return calls

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
        for tool in self.client.tool_runtime.list_tools():
            key = (session_id, tool.identifier)
            is_destructive = (
                tool_def.annotations.get("destructiveHint", False)
                if tool_def.annotations else False
            )

            if not is_destructive:
                approval_store[key] = "approved"
            else:
                approval_store[key] = None

        # 1. create an agent turn
        turn_response = self.client.agents.turn.create(
            agent_id=self.agent_id,
            session_id=session_id,
            messages=messages,
            stream=True,
        )
        
        # 2. process turn and resume if there's a tool call
        for chunk in turn_response:
            print(chunk.event)
            if hasattr(chunk.event.payload, "event_type"):
                if chunk.event.payload.event_type == 'turn_awaiting_input':
                    # print(chunk)
                    if chunk.event.payload.turn.output_message.tool_calls:
                        for tool in chunk.event.payload.turn.output_message.tool_calls:
                            tool_def = self._tools_by_id.get(tool.tool_name)
                            
                            
                                log_display(f"🛠 Calling tool: `{tool.tool_name}`")

                            if is_destructive and self.approval_callback:
                                log_display(f"🟡 Waiting for human approval to use tool `{tool.tool_name}`...")
                                tool_result = None
                                while tool_result is None:
                                    tool_result = self.approval_callback(tool_def)
                                    if tool_result is None:
                                        print("hello")
                                        time.sleep(0.1)

                        tool_responses = self._run_tool_calls(chunk.event.payload.turn.output_message.tool_calls)

                        turn_response = self.client.agents.turn.resume(
                            turn_id=chunk.event.payload.turn.turn_id,
                            agent_id=self.agent_id,
                            session_id=session_id,
                            tool_responses=tool_responses,
                            stream=True,
                        )
                        
            yield chunk

# # my_custom_agent.py

# from llama_stack.agent import BaseAgent
# from llama_stack.types import AgentMessage, AgentResponse, ToolCall
# from llama_stack.client import LlamaStackClient

# class MyCustomAgent(BaseAgent):
#     def __init__(self, config):
#         super().__init__(config)
#         self.client = LlamaStackClient(base_url="http://localhost:8321")
#         self.model = config.get("model_id", "meta-llama/Llama-3.2-3B-Instruct")
#         toolgroups = self.client.toolgroups.list()
#         self.mcp_toolgroup_ids = [
#             tg.toolgroup_id for tg in toolgroups if tg.provider_id == "model-context-protocol"
#         ]

#         # Retrieve available tools from the MCP tool groups
#         self.available_tools = []
#         for tg_id in self.mcp_toolgroup_ids:
#             tools = self.client.tools.list_tools(toolgroup_id=tg_id)
#             self.available_tools.extend(tools)
#         self.available_tools = self.client.tools.list_tools(toolgroup_id=self.mcp_toolgroup_id)


#     def handle(self, input_data):
#         # Prepare the user message
#         messages = {"role": "user", "content": input_data}

#         # Call the inference API with tool support
#         response = self.client.chat.completions.create(
#                         model=self.model,
#                         messages=messages,
#                         tools=self.available_tools,
#                         tool_choice="auto"
#                     )
#         call_number += 1

#         assistant_msg = response.choices[0].message
#         messages.append(assistant_msg)

#         tool_calls = assistant_msg.tool_calls
#         if tool_calls is None:
#             print('No tool calls')
#             return {
#                 "response": messages
#             }
        
#         print(f'This call requires {len(tool_calls)} number of tool calls')
#         for tool_call in assistant_msg.tool_calls:
#             args = json.loads(tool_call.function.arguments)
#             tool_name = tool_call.function.name

#             if tool_name == "evaluate":
#                 print('Calling Evaluate')
#                 result = call_mcp(args["expression"], method="evaluate")
#             elif tool_name == "reverse":
#                 print('Calling Reverse')
#                 result = call_mcp(args["number"], method="reverse")
#             else:
#                 result = "Unsupported tool"

#             messages.append({
#                 "role": "tool",
#                 "tool_call_id": tool_call.id,
#                 "name": tool_name,
#                 "content": str(result)
#             })

#             # Return the assistant's response
#             return {
#                 "response": response.completion_message.content
#             }

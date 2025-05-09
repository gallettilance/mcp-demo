from openai import OpenAI
import requests
import json

PROMPT = "Evaluate 20 + 20. Then reverse the result."

try:
    with open("apikey.txt", "r") as file:
        APIKEY = file.readline().strip()
except FileNotFoundError:
    raise FileNotFoundError("The file 'apikey.txt' was not found. Please make sure it exists.")

client = OpenAI(api_key=APIKEY)


def call_mcp(value, method="evaluate"):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "expression" if method == "evaluate" else "number": value
        }
    }
    response = requests.post("http://localhost:8000/mcp", json=payload)
    return response.json()

# Define the tool (function)
tools = [
    {
        "type": "function",
        "function": {
            "name": "evaluate",
            "description": "Evaluate a math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, like '2 + 2 * 5'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reverse",
            "description": "Reverse the string form of a number",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": "The number as a string (e.g., '1234')"
                    }
                },
                "required": ["number"]
            }
        }
    }
]

messages = [{"role": "user", "content": PROMPT}]

call_number = 0
while True:
    print(f'This is call number {call_number} to the LLM')
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    call_number += 1

    assistant_msg = response.choices[0].message
    messages.append(assistant_msg)

    tool_calls = assistant_msg.tool_calls
    if tool_calls is None:
        print('No tool calls')
    else:
        print(f'This call requires {len(tool_calls)} number of tool calls')

    if not tool_calls:
        print("Final answer:", assistant_msg.content)
        break

    for tool_call in assistant_msg.tool_calls:
        args = json.loads(tool_call.function.arguments)
        tool_name = tool_call.function.name

        if tool_name == "evaluate":
            print('Calling Evaluate')
            result = call_mcp(args["expression"], method="evaluate")
        elif tool_name == "reverse":
            print('Calling Reverse')
            result = call_mcp(args["number"], method="reverse")
        else:
            result = "Unsupported tool"

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_name,
            "content": str(result)
        })


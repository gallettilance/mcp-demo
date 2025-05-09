from openai import OpenAI
import requests
import json

PROMPT = "Reverse 1234. Then compute 7 * (3 + 2)."

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

# Step 3: Call GPT with tool usage
response = client.chat.completions.create(model="gpt-4",
messages=messages,
tools=tools,
tool_choice="auto")

tool_calls = response.choices[0].message.tool_calls
print(f'Number of tool calls = {len(tool_calls)}')
messages.append(response.choices[0].message)

if tool_calls:
    for tool_call in tool_calls:
        if tool_call.function.name == "evaluate":
            print("CALLING EVALUATE")
            args = json.loads(tool_call.function.arguments)
            expr = args["expression"]
            result = call_mcp(expr, method='evaluate')
        if tool_call.function.name == "reverse":
            print("CALLING REVERSE")
            args = json.loads(tool_call.function.arguments)
            expr = args["number"]
            result = call_mcp(expr, method='reverse')

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": str(result)
        })
    followup = client.chat.completions.create(model="gpt-4", messages=messages)
    
    print("TOOL WAS CALLED")
    print("Final Answer:", followup.choices[0].message.content)
else:
    print("No tool was called.")

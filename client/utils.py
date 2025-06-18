import re
from llama_stack_client.lib.agents.event_logger import EventLogger

def prettyPrint(stream):
    tool_name = None
    tool_already_printed = {
        "biology" : False,
        "physics" : False,
        "read_quota" : False,
        "set_quota" : False,
    }
    inference = ""
    show_shield = False
    shield_buffer = ""

    # first pass to remember all tool names
    for log in EventLogger().log(stream):
        print(log)
        if log.role == "shield_call":
            show_shield = True
            shield_buffer = log.content

        # Buffer the lines following input_shield
        elif show_shield and log.role is None:
            shield_buffer += log.content

            if "Exceeded quota" in shield_buffer:
                yield "🚫 **Safety Violation:**  "
                yield '  \n'
                yield shield_buffer
            else:
                yield "🛡️ **Shield Info:**  "
                yield '  \n'
                yield shield_buffer
            yield '  \n'
            show_shield = False
            shield_buffer = ""

        elif log.role == "tool_execution":
            match = re.search(r"Tool:(\w+)", log.content)
            if match:
                tool_name = match.group(1)
                if not tool_already_printed[tool_name]:
                    yield "🛠 Used Tool: "
                    yield f":orange[`{tool_name}`]"
                    yield '  \n'
                    tool_already_printed[tool_name] = True

                inference = ""

        elif log.role == "inference":
            show_shield = False
            inference += log.content

        elif log.role is None:
            inference += log.content
    
    yield inference

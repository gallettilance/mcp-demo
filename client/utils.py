import re
from llama_stack_client.lib.agents.event_logger import EventLogger

def prettyPrint(response):
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
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Union, Callable
import traceback
import inspect
import json

app = FastAPI()


class JSONRPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: dict[str, Any]
    id: Union[int, str, None]


class EvalInput(BaseModel):
    expression: str

class ReverseInput(BaseModel):
    number: str


ToolFunc = Callable[[dict[str, Any]], Any]
ToolEntry = dict[str, Union[str, Callable, BaseModel]]

tool_registry: dict[str, dict] = {}

def register_tool(name: str, func: ToolFunc, schema: dict[str, Any]):
    tool_registry[name] = {
        "func": func,
        "schema": schema,
        "description": inspect.getdoc(func) or "No description provided"
    }

def evaluate_tool(params: dict[str, Any]) -> Any:
    """Evaluate a math expression."""
    validated = EvalInput(**params)
    return eval(validated.expression, {"__builtins__": {}}, {})

def reverse_tool(params: dict[str, Any]) -> str:
    """Reverse a number string."""
    validated = ReverseInput(**params)
    return validated.number[::-1]


register_tool("evaluate", evaluate_tool, EvalInput.model_json_schema())
register_tool("reverse", reverse_tool, ReverseInput.model_json_schema())


def list_tools() -> Any:
    return json.loads(json.dumps([
        {
            "name": name,
            "description": meta["description"],
            "parameters": meta["schema"]
        }
        for name, meta in tool_registry.items()
    ]))


def make_response(result: Any = None, error: dict = None, id: Any = None) -> dict:
    if error:
        return {"jsonrpc": "2.0", "id": id, "error": error}
    return {"jsonrpc": "2.0", "id": id, "result": result}


@app.post("/mcp")
async def handle_mcp(request: Request) -> JSONResponse:
    try:
        payload = await request.json()
        req = JSONRPCRequest(**payload)

        if req.method == "list_tools":
            return JSONResponse(content=make_response(result=list_tools(), id=req.id))

        tool = tool_registry.get(req.method)
        if tool is not None:
            try:
                result = tool["func"](req.params)
                return JSONResponse(content=make_response(result=result, id=req.id))
            except Exception as e:
                return JSONResponse(content=make_response(
                    error={"code": -32000, "message": str(e)}, id=req.id
                ))

        return JSONResponse(content=make_response(
            error={"code": -32601, "message": "Method not found"}, id=req.id
        ))

    except Exception:
        return JSONResponse(content=make_response(
            error={"code": -32700, "message": "Parse error", "data": traceback.format_exc()},
            id=None
        ))


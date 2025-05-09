from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import traceback

app = FastAPI()


class JSONRPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: dict
    id: int | str | None


@app.post("/mcp")
async def handle_mcp(request: Request):
    try:
        payload = await request.json()
        req = JSONRPCRequest(**payload)

        if req.method == "evaluate":
            expr = req.params.get("expression", "")
            try:
                result = eval(expr, {"__builtins__": {}}, {})
                return {
                    "jsonrpc": "2.0",
                    "id": req.id,
                    "result": result
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req.id,
                    "error": {"code": -32000, "message": f"Eval error: {str(e)}"}
                }
        elif req.method == "reverse":
            num_str = str(req.params.get("number", ""))
            result = num_str[::-1]
            return {"jsonrpc": "2.0", "id": req.id, "result": result}
        
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "error": {"code": -32601, "message": "Method not found"}
        }

    except Exception:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error",
                "data": traceback.format_exc()
            }
        }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

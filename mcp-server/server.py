from mcp.server.fastmcp import FastMCP
from llama_stack_client import LlamaStackClient

mcp = FastMCP(name="mcp-lance")

BIOLOGY_URL = 'http://localhost:8002'
PHYSICS_URL = 'http://localhost:8003'
PHYSICS_CONTENT = "You are a physics expert assistant. You answer university-level physics questions clearly, using equations and theory where appropriate. You refuse to answer non-physics questions."
BIOLOGY_CONTENT = "You are a biology expert assistant. You answer university-level biology questions clearly, using equations and theory where appropriate. You refuse to answer non-biology questions."

physics_client = LlamaStackClient(base_url=PHYSICS_URL)
biology_client = LlamaStackClient(base_url=BIOLOGY_URL)

@mcp.tool()
def biology(text: str) -> str:
    """Answer Biology questions."""
    response = biology_client.inference.chat_completion(
        messages = [
            {"role": 'system', "content": BIOLOGY_CONTENT},
            {"role": "user", "content": text}],
        model_id=biology_client.models.list()[0].identifier,
    )
    
    return response.completion_message.content

@mcp.tool()
def physics(text: str) -> str:
    """Answer Physics questions."""
    response = physics_client.inference.chat_completion(
        messages = [
            {"role": 'system', "content": PHYSICS_CONTENT},
            {"role": "user", "content": text}],
        model_id=physics_client.models.list()[0].identifier,
    )
    
    return response.completion_message.content

if __name__ == "__main__":
    mcp.run(transport="sse")

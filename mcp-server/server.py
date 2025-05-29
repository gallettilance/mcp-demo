from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="mcp-lance")

@mcp.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b."""
    return str(a / b)

@mcp.tool()
def reverse(text: str) -> str:
    """Reverse the text"""
    return text[::-1]

if __name__ == "__main__":
    mcp.run(transport="sse")

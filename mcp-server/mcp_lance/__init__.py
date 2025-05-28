import click
import logging
import sys
import uvicorn

@click.command()
@click.option("-v", "--verbose", count=True)
def main(verbose: int):
    """Start the FastAPI MCP server over HTTP"""
    logging_level = logging.WARNING
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    uvicorn.run("mcp_lance.server:app", host="0.0.0.0", port=8001, reload=False)
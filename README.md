# Instructions

## Get modified llama stack v0.2.8

- clone https://github.com/gallettilance/llama-stack/tree/safe-tool-calls in parent directory
- clone https://github.com/gallettilance/llama-stack-client-python/tree/safe-tool-calls in parent

Parent should look like:

```
    parent/
    ├── llama-stack-client-python/
    ├── llama-stack/
    └── mcp-demo/
```

## Install and run

```bash
    make install
    cd tool-stack
    make run
    cd ../mcp-server
    make run
    cd ../stack
    make run
    cd ../client
    make run
```

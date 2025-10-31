# Examples

This folder contains example scripts demonstrating how to use the pardusagnet library.

## test_agent.py

A simple example that demonstrates using the Agent with `add` and `minus` tools.

### Usage

1. Install the package in editable mode (for local development):
```bash
pip install -e .
```

Or using uv:
```bash
uv pip install -e .
```

2. Make sure the server is running at `http://localhost:8080`

3. Run the example:
```bash
python examples/test_agent.py
```

Or using uv:
```bash
uv run examples/test_agent.py
```

### What it does

- Creates two simple tools: `add` (adds two integers) and `minus` (subtracts two integers)
- Creates an Agent instance with these tools
- Sends a request to the server to test tool execution
- Prints the results from the server and tool execution


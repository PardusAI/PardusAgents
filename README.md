# PardusAgent

A Python client library for building AI agents with tool-calling capabilities powered by Pardus AI.

## Quick Start

To get API key visit http://pardusai.org/ ! 

### Installation

```bash
pip install pardusagnet
```

### Basic Usage

```python
import asyncio
from pardusagnet import Tool, Agent


def add(a: int, b: int) -> int:
    """Add two integers together"""
    return a + b


def minus(a: int, b: int) -> int:
    """Subtract b from a"""
    return a - b


async def main():
    agent = Agent(
        tools=[Tool(add), Tool(minus)],
        models="minimax/minimax-m2:free",
        PardusAPI="pk_your_api_key_here" # better export PARDUS_API_KEY="YOUR API KEY HERE"
    )
    
    result = await agent.run("Calculate 100 minus 42")
    
    print(result['text'])
    for tool_result in result['tool_results']:
        print(f"{tool_result['name']}: {tool_result['result']}")


asyncio.run(main())
```

### Configuration

- **API Key**: Set via `PardusAPI` parameter or `PARDUS_API_KEY` environment variable
- **Server URL**: Default is `pardusai.org`, customize with `base_url` parameter
- **Model**: Any model supported by Pardus AI (e.g., `minimax/minimax-m2:free`)

### Example

See the complete example in `examples/simple_agent.py`

```bash
python examples/simple_agent.py
```
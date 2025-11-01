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
        models="z-ai/glm-4.5-air:free",
        PardusAPI="" #sugegst using export PARDUS_API_KEY="YOUR API KEY"
    )
    
    result = await agent.run("Calculate 100 minus 42")
    
    print(result['text'])
    for tool_result in result['tool_results']:
        print(f"{tool_result['name']}: {tool_result['result']}")


if __name__ == "__main__":
    asyncio.run(main())


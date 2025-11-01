"""Example script to test the Agent with add and minus tools"""
import asyncio
import traceback

from pardusagnet import Tool, Agent


def add(a: int, b: int) -> int:
    """Add two integers together"""
    return a + b


def minus(a: int, b: int) -> int:
    """Subtract b from a"""
    return a - b


async def main():
    # Create tool objects
    add_tool = Tool(add, {"a":"first parameter" , "b":"second parameters"})
    minus_tool = Tool(minus)
    
    # Create agent with tools
    agent = Agent(
        tools=[add_tool, minus_tool],
        models="minimax/minimax-m2:free"
    )
    
    # Test the agent
    print("Testing Agent with add and minus tools...")
    print(f"Server URL: {agent.server_url}")
    print("\nSending request to server...")
    
    try:
        result = await agent.run("Add 5 and 3 You must use the add_tool")
        print("\nResult:")
        print(f"Text: {result.get('text', 'No text response')}")
        
        if result.get('tool_results'):
            print("\nTool Execution Results:")
            for tool_result in result['tool_results']:
                print(f"  - {tool_result['name']}: {tool_result['result']}")
        else:
            print("No tool results returned")
            
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
        print("\nMake sure the server is running at http://localhost:8080")


if __name__ == "__main__":
    asyncio.run(main())


import json
import httpx
from ..tools import Tool
SERVER_URL = "http://localhost:8080"

class Agent:
    def __init__(
        self,
        tools: list[Tool],
        models: str,
    ):
        self.tools = tools 
        self.models = models
        self.server_url = SERVER_URL
        
        # Create a mapping of tool names to Tool objects for easy lookup
        self.tool_map = {tool.func.__name__: tool for tool in tools}

    async def run(self, input: str):
        """send all tools and input to the server side and return the text and call the tool"""
        # Convert tools to schema format
        tools_schema = []
        for tool in self.tools:
            schema = tool._get_schema()
            tools_schema.append(schema)
        
        # Prepare request payload
        payload = {
            "input": input,
            "tools": tools_schema,
            "model": self.models
        }
        
        # Send POST request to server
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.server_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
        
        # Parse OpenAI-style response format
        tool_results = []
        text_content = ""
        
        # Extract content and tool_calls from choices[0].message
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            text_content = message.get("content", "")
            
            # Check for tool_calls in OpenAI format
            if "tool_calls" in message:
                for tool_call in message["tool_calls"]:
                    # OpenAI format: tool_call.function.name and tool_call.function.arguments (as JSON string)
                    function_info = tool_call.get("function", {})
                    tool_name = function_info.get("name")
                    arguments_str = function_info.get("arguments", "{}")
                    
                    # Parse arguments if it's a string
                    try:
                        if isinstance(arguments_str, str):
                            arguments = json.loads(arguments_str)
                        else:
                            arguments = arguments_str
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # Find the tool and execute it
                    if tool_name and tool_name in self.tool_map:
                        tool = self.tool_map[tool_name]
                        tool_result = tool.func(**arguments)
                        tool_results.append({
                            "name": tool_name,
                            "result": tool_result
                        })
        
        return {
            "text": text_content,
            "tool_results": tool_results
        }

    def stream_run(self, input:str):
        pass

# please note that this file will not be maintained. Strongly suggest using pardus agent services. 
import os
import httpx
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pardus Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default model
DEFAULT_MODEL = "llama3.2"

# Ollama API endpoint
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/v1/chat/completions")


class Tool(BaseModel):
    type: str
    name: str
    description: str
    parameters: Dict[str, Any]
    required: Optional[List[str]] = []
    additionalProperties: Optional[bool] = False


class RequestPayload(BaseModel):
    input: str
    tools: List[Tool] = []
    model: Optional[str] = DEFAULT_MODEL


class Message(BaseModel):
    role: str
    content: str


class ToolCall(BaseModel):
    id: str
    type: str
    function: Dict[str, Any]


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat")
async def handle_chat_request(payload: RequestPayload):
    logger.info("=== INCOMING REQUEST ===")
    logger.info(f"Input: {payload.input}")
    logger.info(f"Model: {payload.model}")
    logger.info(f"Tools count: {len(payload.tools)}")
    
    if len(payload.tools) > 0:
        import json
        logger.info(f"Tools: {json.dumps([tool.dict() for tool in payload.tools], indent=2)}")
    
    # Validate input
    if not payload.input:
        logger.error("ERROR: input field is empty")
        raise HTTPException(status_code=400, detail="input field is required")
    
    # Convert tools to Ollama format
    ollama_tools = []
    for tool in payload.tools:
        ollama_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        })
    
    # Build Ollama request
    ollama_payload = {
        "model": payload.model,
        "messages": [
            {
                "role": "user",
                "content": payload.input
            }
        ]
    }
    
    # Add tools if provided
    if len(ollama_tools) > 0:
        ollama_payload["tools"] = ollama_tools
    
    # Log Ollama request
    logger.info("=== OLLAMA REQUEST ===")
    import json
    logger.info(f"Request to Ollama: {json.dumps(ollama_payload, indent=2)}")
    
    # Send request to Ollama
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OLLAMA_API_URL,
                json=ollama_payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
    except httpx.RequestError as e:
        logger.error(f"ERROR: Failed to send to Ollama: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with Ollama: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"ERROR: Ollama returned error: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Ollama API error: {str(e)}"
        )
    
    # Log Ollama response
    logger.info("=== OLLAMA RESPONSE ===")
    logger.info(f"Response from Ollama: {json.dumps(result, indent=2)}")
    
    # Check for tool calls
    if "choices" in result and len(result["choices"]) > 0:
        message = result["choices"][0].get("message", {})
        if "tool_calls" in message and len(message["tool_calls"]) > 0:
            logger.info("=== TOOL CALLS DETECTED ===")
            logger.info(f"Tool Calls: {json.dumps(message['tool_calls'], indent=2)}")
            logger.info(f"Finish Reason: {result['choices'][0].get('finish_reason', 'unknown')}")
        else:
            logger.info("No tool calls in response")
            logger.info(f"Finish Reason: {result['choices'][0].get('finish_reason', 'unknown')}")
    
    # Log what we're sending back
    logger.info("=== SENDING TO CLIENT ===")
    logger.info(f"Response: {json.dumps(result, indent=2)}")
    
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Server starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

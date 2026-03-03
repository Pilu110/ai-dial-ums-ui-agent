import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from agent.clients.dial_client import DialClient
from agent.clients.http_mcp_client import HttpMCPClient
from agent.clients.stdio_mcp_client import StdioMCPClient
from agent.conversation_manager import ConversationManager
from agent.models.message import Message

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

conversation_manager: Optional[ConversationManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MCP clients, Redis, and ConversationManager on startup"""
    global conversation_manager

    logger.info("Application startup initiated")

    tools = []
    tool_name_client_map: dict[str, HttpMCPClient | StdioMCPClient] = {}

    try:
        # Initialize UMS MCP Client
        logger.info("Connecting to UMS MCP Server...")
        ums_client = await HttpMCPClient.create("http://localhost:8005/mcp")
        ums_tools = await ums_client.get_tools()
        tools.extend(ums_tools)
        for tool in ums_tools:
            tool_name_client_map[tool["function"]["name"]] = ums_client
        logger.info(f"Connected to UMS MCP, loaded {len(ums_tools)} tools")

        # Initialize Fetch MCP Client
        logger.info("Connecting to Fetch MCP Server...")
        fetch_client = await HttpMCPClient.create("https://remote.mcpservers.org/fetch/mcp")
        fetch_tools = await fetch_client.get_tools()
        tools.extend(fetch_tools)
        for tool in fetch_tools:
            tool_name_client_map[tool["function"]["name"]] = fetch_client
        logger.info(f"Connected to Fetch MCP, loaded {len(fetch_tools)} tools")

        # Initialize DuckDuckGo MCP Client (Optional - requires Docker)
        # Set ENABLE_DUCKDUCKGO=false to skip this client
        enable_duckduckgo = os.getenv("ENABLE_DUCKDUCKGO", "true").lower() == "true"

        if enable_duckduckgo:
            logger.info("Connecting to DuckDuckGo MCP Server...")
            try:
                duckduckgo_client = await StdioMCPClient.create("mcp/duckduckgo:latest")
                duckduckgo_tools = await duckduckgo_client.get_tools()
                tools.extend(duckduckgo_tools)
                for tool in duckduckgo_tools:
                    tool_name_client_map[tool["function"]["name"]] = duckduckgo_client
                logger.info(f"Connected to DuckDuckGo MCP, loaded {len(duckduckgo_tools)} tools")
            except FileNotFoundError as e:
                logger.warning("DuckDuckGo MCP Server not available (Docker not found). Continuing without it.")
            except Exception as e:
                logger.warning(f"Failed to connect to DuckDuckGo MCP Server: {e}. Continuing without it.")
        else:
            logger.info("DuckDuckGo MCP Client disabled (ENABLE_DUCKDUCKGO=false)")

        logger.info(f"Total tools loaded: {len(tools)}")

        # Initialize DIAL Client
        api_key = os.getenv("DIAL_API_KEY", "")
        endpoint = os.getenv("DIAL_ENDPOINT", "https://ai-proxy.lab.epam.com")
        model = os.getenv("DIAL_MODEL", "gpt-4o")

        logger.info(f"Initializing DIAL Client with model: {model}")
        dial_client = DialClient(
            api_key=api_key,
            endpoint=endpoint,
            model=model,
            tools=tools,
            tool_name_client_map=tool_name_client_map
        )
        logger.info("DIAL Client initialized")

        # Initialize Redis Client
        logger.info("Connecting to Redis...")
        redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        await redis_client.ping()
        logger.info("Connected to Redis")

        # Create ConversationManager
        conversation_manager = ConversationManager(dial_client, redis_client)
        logger.info("ConversationManager initialized")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise

    yield

    logger.info("Application shutdown initiated")
    if conversation_manager:
        try:
            await redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")


app = FastAPI(
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request/Response Models
class ChatRequest(BaseModel):
    message: Message
    stream: bool = True


class ChatResponse(BaseModel):
    content: str
    conversation_id: str


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class CreateConversationRequest(BaseModel):
    title: str = None


# Endpoints
@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "conversation_manager_initialized": conversation_manager is not None
    }


#TODO:
# Create such endpoints:
# 1. POST: "/conversations". Applies CreateConversationRequest and creates new conversation.
# 2. GET: "/conversations" Extracts all conversation from storage. Returns list of ConversationSummary objects
# 3. GET: "/conversations/{conversation_id}". Applies conversation_id string and extracts from storage full conversation
# 4. DELETE: "/conversations/{conversation_id}". Applies conversation_id string and deletes conversation. Returns dict
#    with message with info if conversation has been deleted
# 5. POST: "/conversations/{conversation_id}/chat". Chat endpoint that processes messages and returns assistant response.
#    Supports both streaming and non-streaming modes.
#    Applies conversation_id and ChatRequest.
#    If `request.stream` then return `StreamingResponse(result, media_type="text/event-stream")`, otherwise return `ChatResponse(**result)`


@app.post("/conversations")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation"""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    conversation = await conversation_manager.create_conversation(
        title=request.title or "New Conversation"
    )
    return conversation


@app.get("/conversations")
async def list_conversations():
    """Get all conversations"""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    conversations = await conversation_manager.list_conversations()
    return conversations


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    conversation = await conversation_manager.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    deleted = await conversation_manager.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted successfully"}


@app.post("/conversations/{conversation_id}/chat")
async def chat(conversation_id: str, request: ChatRequest):
    """Chat endpoint with streaming support"""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        result = await conversation_manager.chat(
            user_message=request.message,
            conversation_id=conversation_id,
            stream=request.stream
        )

        if request.stream:
            return StreamingResponse(result, media_type="text/event-stream")
        else:
            return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting UMS Agent server")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8011,
        log_level="debug"
    )
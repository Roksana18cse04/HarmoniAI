# app/api/routes/mcp_routes.py
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional
import logging

# Import schemas
from app.schemas.TextToImage import TextToImageRequest
from app.schemas.enhance_prompt import EnhanceRequest

# Import MCP server
from app.mcp_server import mcp_server

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mcp", tags=["MCP Tools"])

# Generic request models for MCP tool calls
class MCPToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None
    domain: Optional[str] = "general"

class ContentRequest(BaseModel):
    content_type: str
    topic: str
    length: Optional[str] = "medium"
    tone: Optional[str] = "professional"
    target_audience: Optional[str] = "general"

@router.post("/enhance-prompt")
async def enhance_prompt_endpoint(request: EnhanceRequest):
    """
    Enhance a prompt using the MCP enhance-prompt tool
    """
    try:
        logger.info(f"Enhancing prompt for platform: {request.platform}")
        
        # Call MCP tool directly
        response = await mcp_server.call_tool_direct(
            tool_name="enhance-prompt",
            arguments=request.dict()
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response
        )
        
    except ValidationError as ve:
        logger.error(f"Validation error in enhance-prompt: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ve.errors()
        )
    except Exception as e:
        logger.error(f"Error in enhance-prompt endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance prompt: {str(e)}"
        )

@router.post("/text-to-image")
async def text_to_image_endpoint(request: TextToImageRequest):
    """
    Generate image from text using the MCP text-to-image tool
    """
    try:
        logger.info(f"Generating image with model: {request.model_name}")
        
        # Call MCP tool directly
        response = await mcp_server.call_tool_direct(
            tool_name="text-to-image",
            arguments=request.dict()
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response
        )
        
    except ValidationError as ve:
        logger.error(f"Validation error in text-to-image: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ve.errors()
        )
    except Exception as e:
        logger.error(f"Error in text-to-image endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}"
        )

@router.post("/answer-question")
async def answer_question_endpoint(request: QuestionRequest):
    """
    Answer a question using the MCP answer-question tool
    """
    try:
        logger.info(f"Answering question in domain: {request.domain}")
        
        # Call MCP tool directly
        response = await mcp_server.call_tool_direct(
            tool_name="answer-question",
            arguments=request.dict()
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response
        )
        
    except ValidationError as ve:
        logger.error(f"Validation error in answer-question: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ve.errors()
        )
    except Exception as e:
        logger.error(f"Error in answer-question endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )

@router.post("/create-content")
async def create_content_endpoint(request: ContentRequest):
    """
    Create content using the MCP create-content tool
    """
    try:
        logger.info(f"Creating {request.content_type} content about: {request.topic}")
        
        # Call MCP tool directly
        response = await mcp_server.call_tool_direct(
            tool_name="create-content",
            arguments=request.dict()
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response
        )
        
    except ValidationError as ve:
        logger.error(f"Validation error in create-content: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ve.errors()
        )
    except Exception as e:
        logger.error(f"Error in create-content endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create content: {str(e)}"
        )

@router.post("/call-tool")
async def generic_tool_call_endpoint(request: MCPToolRequest):
    """
    Generic endpoint to call any MCP tool
    """
    try:
        logger.info(f"Calling MCP tool: {request.tool_name}")
        
        # Call MCP tool directly
        response = await mcp_server.call_tool_direct(
            tool_name=request.tool_name,
            arguments=request.arguments
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response
        )
        
    except ValidationError as ve:
        logger.error(f"Validation error in generic tool call: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ve.errors()
        )
    except Exception as e:
        logger.error(f"Error in generic tool call endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to call tool '{request.tool_name}': {str(e)}"
        )

@router.get("/tools")
async def list_available_tools():
    """
    List all available MCP tools
    """
    try:
        # Get tool list from MCP server
        tools = []
        for handler in mcp_server.server._list_tools_handlers:
            tools_list = await handler()
            tools.extend([{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in tools_list])
            break
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "available_tools": tools,
                "total_count": len(tools)
            }
        )
        
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for MCP integration
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": "harmoni-mcp-server",
            "tools_available": True
        }
    )
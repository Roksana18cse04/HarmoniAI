"""
MCP Routes for FastAPI Integration

This module provides FastAPI routes to integrate MCP server functionality
with the main HarmoniAI application.
"""

import time
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.mcp.server import HarmoniMCPServer
from app.mcp.schemas.mcp_models import MCPToolRequest, MCPToolResponse, MCPHealthCheck
from app.mcp.utils.mcp_utils import format_tool_response, get_tool_categories

logger = logging.getLogger(__name__)

# Create router
mcp_router = APIRouter(prefix="/mcp", tags=["MCP Server"])

# Initialize MCP server instance
mcp_server = HarmoniMCPServer()


@mcp_router.get("/health", response_model=MCPHealthCheck)
async def health_check():
    """Health check endpoint for MCP server"""
    try:
        tools = mcp_server.server.list_tools()
        return MCPHealthCheck(
            status="healthy",
            version="1.0.0",
            available_tools=len(tools),
            uptime=time.time()  # This should be actual uptime tracking
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )


@mcp_router.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    try:
        tools = mcp_server.server.list_tools()
        return {
            "success": True,
            "tools": tools,
            "categories": get_tool_categories()
        }
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tools: {str(e)}"
        )


@mcp_router.post("/execute", response_model=MCPToolResponse)
async def execute_tool(request: MCPToolRequest):
    """Execute an MCP tool"""
    start_time = time.time()
    
    try:
        # Execute the tool
        result = await mcp_server.tool_handler.execute_tool(
            request.tool_name, 
            request.arguments
        )
        
        execution_time = time.time() - start_time
        
        return MCPToolResponse(
            success=True,
            result=result,
            request_id=request.request_id,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error executing tool {request.tool_name}: {str(e)}")
        
        return MCPToolResponse(
            success=False,
            result="",
            error=str(e),
            request_id=request.request_id,
            execution_time=execution_time
        )


@mcp_router.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    try:
        tools = mcp_server.server.list_tools()
        
        for tool in tools:
            if tool.name == tool_name:
                return {
                    "success": True,
                    "tool": {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_name}' not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting tool info: {str(e)}"
        )


@mcp_router.get("/categories")
async def get_categories():
    """Get tool categories"""
    try:
        return {
            "success": True,
            "categories": get_tool_categories()
        }
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting categories: {str(e)}"
        )


@mcp_router.get("/tools/category/{category}")
async def get_tools_by_category(category: str):
    """Get tools by category"""
    try:
        categories = get_tool_categories()
        
        if category not in categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found"
            )
        
        tools = mcp_server.server.list_tools()
        category_tools = [tool for tool in tools if tool.name in categories[category]]
        
        return {
            "success": True,
            "category": category,
            "tools": category_tools
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tools by category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting tools by category: {str(e)}"
        ) 
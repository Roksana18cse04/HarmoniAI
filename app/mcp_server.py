# #!/usr/bin/env python3
# """
# MCP Server for HARMONI-AI
# Exposes your AI agents as MCP tools for seamless integration
# """

# import asyncio
# import sys
# from typing import Any, Sequence
# from mcp.server import Server
# from mcp.server.stdio import stdio_server
# from mcp.types import (
#     Tool,
#     TextContent,
#     CallToolRequest,
#     CallToolResult,
#     CallToolTextToImageRequest
# )

# # Import your existing agents
# from app.services.enhance_prompt_generate import enhance_prompt
# from app.agents.image_generator_agent import text_to_generate_image
# from app.schemas.TextToImage import TextToImageRequest
# # from app.agents.image_generator_agent import ImageGeneratorAgent
# # from app.agents.qa_agent import QAAgent
# # from app.agents.content_creator_agent import ContentCreatorAgent
# # Add more imports as needed

# class HarmoniMCPServer:
#     def __init__(self):
#         self.server = Server("harmoni-ai")
#         self.setup_tools()
    
#     def setup_tools(self):
#         """Register all your AI agents as MCP tools"""
        
#         @self.server.list_tools()
#         async def list_tools() -> list[Tool]:
#             return [
#                 Tool(
#                     name="text-to-imge",
#                     description="Generate images using AI based on text prompts",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "prompt": {"type": "string", "description": "Text prompt for image generation"},
#                             "model_name":{"type":"string","description":"Image Generation eachlabs model name"},
#                             "intend":{"type":"string","description":"image generationintend"},
#                             "style": {"type": "string", "description": "Image style (optional)"},
#                             "size": {"type": "string", "description": "Image size (optional)"}
#                         },
#                         "required": ["prompt","model_name","intend"]
#                     }
#                 ),
#                 Tool(
#                     name="answer_question",
#                     description="Answer questions using AI knowledge base",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "question": {"type": "string", "description": "Question to answer"},
#                             "context": {"type": "string", "description": "Additional context (optional)"}
#                         },
#                         "required": ["question"]
#                     }
#                 ),
#                 Tool(
#                     name="create_content",
#                     description="Create various types of content (articles, summaries, etc.)",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "content_type": {"type": "string", "description": "Type of content to create"},
#                             "topic": {"type": "string", "description": "Topic or subject"},
#                             "length": {"type": "string", "description": "Desired length (optional)"}
#                         },
#                         "required": ["content_type", "topic"]
#                     }
#                 ),
#                 Tool(
#                     name="process_media",
#                     description="Process audio, video, or image files",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "media_type": {"type": "string", "description": "Type of media (audio/video/image)"},
#                             "operation": {"type": "string", "description": "Operation to perform"},
#                             "file_path": {"type": "string", "description": "Path to media file"}
#                         },
#                         "required": ["media_type", "operation", "file_path"]
#                     }
#                 ),
#                 Tool(
#                     name="enhance_prompt",
#                     description="Enhance and optimize prompts for better AI responses",
#                     inputSchema={
#                         "type": "object",
#                         "properties": {
#                             "prompt": {"type": "string", "description": "Original prompt to enhance"},
#                             "purpose": {"type": "string", "description": "Purpose of the prompt (optional)"}
#                         },
#                         "required": ["prompt"]
#                     }
#                 )
#             ]
        
#         @self.server.call_tool()
#         async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
#             try:
#                 if name == "text-to-image":
#                     prompt = arguments["prompt"]
#                     model_name = arguments["model_name"]
#                     intend = arguments["intend"]

#                     request_obj = TextToImageRequest(prompt=prompt, model_name=model_name, intend=intend)
#                     image_response = text_to_generate_image(request_obj)
                    
#                     if image_response["image_url"]:
#                         result = f"✅ Image generated!\nPrompt: {prompt}\nURL: {image_response['image_url']}"
#                     else:
#                         result = f"⚠️ Failed to generate image for prompt: {prompt}"
                    
#                     return [TextContent(type="text", text=result)]

#                 elif name == "answer_question":
#                     question = arguments["question"]
#                     context = arguments.get("context", "")
                    
#                     # Replace with actual QA agent call
#                     # result = await your_qa_agent.answer(question, context)
#                     result = f"Answer to '{question}': This would be the AI-generated answer."
                    
#                     return [TextContent(type="text", text=result)]
                
#                 elif name == "create_content":
#                     content_type = arguments["content_type"]
#                     topic = arguments["topic"]
#                     length = arguments.get("length", "medium")
                    
#                     # Replace with actual content creation agent call
#                     # result = await your_content_agent.create(content_type, topic, length)
#                     result = f"Created {content_type} about '{topic}' with {length} length."
                    
#                     return [TextContent(type="text", text=result)]
                
#                 elif name == "process_media":
#                     media_type = arguments["media_type"]
#                     operation = arguments["operation"]
#                     file_path = arguments["file_path"]
                    
#                     # Replace with actual media processing agent call
#                     # result = await your_media_agent.process(media_type, operation, file_path)
#                     result = f"Processed {media_type} file at {file_path} with operation: {operation}"
                    
#                     return [TextContent(type="text", text=result)]
                
#                 elif name == "enhance_prompt":
#                     prompt = arguments["prompt"]
#                     purpose = arguments.get("purpose", "")
                    
#                     # Call your actual prompt enhancement service
#                     try:
#                         enhanced_prompt = enhance_prompt(prompt, purpose)
#                         result = f"Enhanced prompt: {enhanced_prompt}"
#                     except Exception as e:
#                         result = f"Error enhancing prompt: {str(e)}"
                    
#                     return [TextContent(type="text", text=result)]
                
#                 else:
#                     return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
#             except Exception as e:
#                 return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

# async def main():
#     """Run the MCP server"""
#     harmoni_server = HarmoniMCPServer()
    
#     async with stdio_server() as (read_stream, write_stream):
#         await harmoni_server.server.run(
#             read_stream,
#             write_stream,
#             harmoni_server.server.create_initialization_options()
#         )

# if __name__ == "__main__":
#     asyncio.run(main())
# app/mcp_server.py
import asyncio
from mcp.server import Server
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from app.services.enhance_prompt_generate import enhance_prompt
from app.schemas.enhance_prompt import EnhanceRequest
from pydantic import BaseModel, ValidationError
import json

print("[BOOT] Starting MCP server...")

# Request model for the /call-tool route
class ToolCallParams(BaseModel):
    name: str
    arguments: dict

class ToolCallRequest(BaseModel):
    params: ToolCallParams

class HarmoniMCP:
    def __init__(self):
        self.server = Server("harmoni-ai")
        self.router = APIRouter()
        print("[INFO] Harmoni MCP server instance created on port 50051")
        self.setup_tools()
        self.setup_routes()

    def setup_tools(self):
        print("[INFO] Registering tools...")

        @self.server.list_tools()
        async def list_tools():
            print("[DEBUG] list_tools called")
            return [
                Tool(
                    name="enhancedprompt",
                    description="Enhance generation prompt",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "platform": {"type": "string"},
                            "base_prompt": {"type": "string"},
                            "target_model": {"type": "string"},
                            "intend": {"type": "string"},
                        },
                        "required": ["platform", "base_prompt", "target_model", "intend"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, args: dict):
            print(f"[DEBUG] call_tool called with name={name} args={args}")
            if name == "enhancedprompt":
                try:
                    args_obj = EnhanceRequest(**args)
                    response = await enhance_prompt(
                        base_prompt=args_obj.base_prompt,
                        target_model=args_obj.target_model,
                        platform=args_obj.platform,
                        intend=args_obj.intend,
                    )
                    return [TextContent(type="text", text=json.dumps(response))]
                except Exception as e:
                    print(f"[ERROR] call_tool error: {e}")
                    return [TextContent(type="text", text="Failed to generate enhanced prompt.")]
            print("[WARN] Unknown tool requested")
            return [TextContent(type="text", text="Unknown tool requested")]

    def setup_routes(self):
        @self.router.post("/call-tool")
        async def call_tool_route(request: ToolCallRequest):
            try:
                if request.params.name == "enhancedprompt":
                    # Convert dict to Pydantic model
                    args_obj = EnhanceRequest(**request.params.arguments)
                    
                    # Call the enhance_prompt function (now async)
                    response = await enhance_prompt(
                        base_prompt=args_obj.base_prompt,
                        target_model=args_obj.target_model,
                        platform=args_obj.platform,
                        intend=args_obj.intend,
                    )
                    
                    print(f"Response: {response}")
                    
                    # Return the response as JSON
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content=response
                    )
                    
                else:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": "Unknown tool"}
                    )
                    
            except ValidationError as ve:
                print(f"[ERROR] Validation error: {ve}")
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={"detail": ve.errors()}
                )
            except Exception as e:
                print(f"[ERROR] Unexpected error: {e}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"error": str(e)}
                )

    def get_router(self):
        """Return the router to be included in FastAPI app"""
        return self.router

async def main():
    server = HarmoniMCP()
    async with stdio_server() as (r, w):
        print("[INFO] MCP server running (stdio mode)")
        await server.server.run(r, w, server.server.create_initialization_options())
        print("[INFO] MCP server stopped")

mcp_server = HarmoniMCP()

if __name__ == "__main__":
    asyncio.run(main())
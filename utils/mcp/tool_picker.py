import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from utils.mcp.server import read_project_file
from mcp.types import TextContent

# Set this to False to use the Direct Local Call
# Set this to True to use the Formal Local Stdio Server
USE_MCP_SERVER = False 

async def execute_read_file(relative_path: str):
    """Switcher that chooses between local execution and formal MCP server."""
    
    if not USE_MCP_SERVER:
        # CASE 1: Direct Local Call (Fast, no process overhead)
        return read_project_file(relative_path)
    
    else:
        # CASE 2: Formal Local MCP Server (Decoupled, Standardized)
        server_params = StdioServerParameters(
            command="python",
            args=["utils/mcp/fs_server.py"],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "read_project_file", 
                    arguments={"relative_path": relative_path}
                )
               # 1. Ensure we have content
            if not result.content:
                return "File is empty."
            
            # 2. Extract only the text blocks
            # This satisfies Pylance and handles multi-part responses
            text_parts = [
                block.text for block in result.content 
                if isinstance(block, TextContent)
            ]
            
            return "\n".join(text_parts) if text_parts else "No text content found."
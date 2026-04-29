from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP - it handles the protocol boilerplate for you
mcp = FastMCP("FlutterProjectExplorer")

@mcp.tool()
def read_project_file(relative_path: str) -> str:
    """Reads a file from the Flutter project to provide extra context."""
    # Safety: Ensure we stay within the project root
    base_path = os.getcwd() 
    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    
    if not full_path.startswith(base_path):
        return "Error: Access denied. Path outside project root."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    mcp.run()
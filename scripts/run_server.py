import asyncio
import sys
import logging
import os
from pathlib import Path
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp import stdio_server
from config.settings import settings

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the server app
from src.server import app

logger = logging.getLogger(__name__)

async def main():
    """Run the MCP server."""
    logger.info(f"Starting {settings.SERVER_NAME} v{settings.SERVER_VERSION}")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=settings.SERVER_NAME,
                    server_version=settings.SERVER_VERSION,
                    capabilities=app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

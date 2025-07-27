#!/usr/bin/env python3
"""
TCP wrapper for the arXiv Research MCP Server
This allows the server to run on a specific port instead of stdin/stdout
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import stdio_server
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
from config.settings import settings

# Import the server app
from src.server import app

logger = logging.getLogger(__name__)

async def handle_client(reader, writer):
    """Handle a single client connection."""
    client_addr = writer.get_extra_info('peername')
    logger.info(f"New client connected: {client_addr}")
    
    try:
        # Create a mock stdio interface using the socket
        async def read_stream():
            while True:
                try:
                    data = await reader.readline()
                    if not data:
                        break
                    yield data.decode('utf-8').strip()
                except Exception as e:
                    logger.error(f"Error reading from client: {e}")
                    break
        
        async def write_stream(data):
            try:
                writer.write(data.encode('utf-8'))
                await writer.drain()
            except Exception as e:
                logger.error(f"Error writing to client: {e}")
        
        # Run the MCP server with the socket streams
        try:
            await app.run(
                read_stream(),
                write_stream(),
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
            logger.error(f"Error running MCP server: {e}")
        
    except Exception as e:
        logger.error(f"Error handling client {client_addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        logger.info(f"Client disconnected: {client_addr}")

async def main():
    """Run the MCP server on a TCP port."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run arXiv Research MCP Server on TCP port')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8090, help='Port to bind to (default: 8080)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else getattr(logging, settings.LOG_LEVEL)
    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT
    )
    
    logger.info(f"Starting {settings.SERVER_NAME} v{settings.SERVER_VERSION} on {args.host}:{args.port}")
    
    try:
        server = await asyncio.start_server(
            handle_client,
            args.host,
            args.port,
            reuse_address=True
        )
        
        logger.info(f"Server listening on {args.host}:{args.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        async with server:
            await server.serve_forever()
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
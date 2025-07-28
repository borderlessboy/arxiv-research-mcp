# arXiv Research MCP Server - MCPO Integration Guide

## Overview

This guide shows how to use the arXiv Research MCP server with MCPO (Model Context Protocol Orchestrator) to enable AI assistants to search and analyze academic papers from arXiv.

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ and the virtual environment activated
2. **Dependencies**: All required packages are installed via `requirements.txt`
3. **MCPO**: You'll need MCPO installed and configured

## Quick Start

### 1. Start the MCP Server

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start the server
python scripts/run_server.py
```

The server will start and listen for MCP protocol messages via stdin/stdout.

### 2. Configure MCPO

Create an MCPO configuration file (e.g., `mcpo_config.json`):

```json
{
  "servers": {
    "arxiv-research": {
      "command": "python",
      "args": ["scripts/run_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

### 3. Available Tools

The server provides three main tools:

#### `search_arxiv_papers`
Search for academic papers with relevance ranking and full text extraction.

**Parameters:**
- `query` (required): Search query (e.g., "transformer models", "quantum computing")
- `max_results` (optional): Maximum number of papers to return (default: 10)
- `years_back` (optional): Number of years back to search (default: 2)
- `include_full_text` (optional): Whether to include full paper text (default: true)

**Example:**
```json
{
  "name": "search_arxiv_papers",
  "arguments": {
    "query": "transformer models",
    "max_results": 5,
    "years_back": 1,
    "include_full_text": false
  }
}
```

#### `clear_cache`
Clear all cached search results.

**Parameters:** None

#### `get_cache_stats`
Get cache statistics and information.

**Parameters:** None

## Integration Examples

### Example 1: Basic Paper Search

```python
# Using MCPO with Python
import asyncio
from mcpo import MCPOClient

async def search_papers():
    async with MCPOClient() as client:
        result = await client.call_tool("arxiv-research", "search_arxiv_papers", {
            "query": "machine learning",
            "max_results": 3
        })
        print(result)

asyncio.run(search_papers())
```

### Example 2: Research Analysis Workflow

```python
# Multi-step research analysis
async def research_workflow():
    async with MCPOClient() as client:
        # Step 1: Search for papers
        papers = await client.call_tool("arxiv-research", "search_arxiv_papers", {
            "query": "transformer architecture",
            "max_results": 5,
            "include_full_text": True
        })
        
        # Step 2: Get cache stats
        stats = await client.call_tool("arxiv-research", "get_cache_stats", {})
        
        # Step 3: Clear cache if needed
        # await client.call_tool("arxiv-research", "clear_cache", {})
        
        return papers, stats
```

### Example 3: CLI Usage

```bash
# Start MCPO with the arXiv server
mcpo --config mcpo_config.json

# In another terminal, use MCPO CLI
mcpo call arxiv-research search_arxiv_papers '{"query": "deep learning", "max_results": 3}'
```

## Advanced Usage

### Custom Search Queries

The server supports various search patterns:

```json
{
  "query": "transformer models",
  "max_results": 10,
  "years_back": 2,
  "include_full_text": true
}
```

### Cache Management

```python
# Check cache status
stats = await client.call_tool("arxiv-research", "get_cache_stats", {})

# Clear cache when needed
await client.call_tool("arxiv-research", "clear_cache", {})
```

### Error Handling

```python
try:
    result = await client.call_tool("arxiv-research", "search_arxiv_papers", {
        "query": "quantum computing"
    })
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

## Server Configuration

### Environment Variables

You can configure the server behavior:

```bash
export ARXIV_API_BASE_URL="https://export.arxiv.org/api/query"
export DEFAULT_MAX_RESULTS=10
export DEFAULT_YEARS_BACK=2
export MIN_RELEVANCE_SCORE=0.001
export CACHE_ENABLED=true
export CACHE_TTL_HOURS=24
```

### Settings File

Modify `config/settings.py` for custom configurations:

```python
# Example custom settings
DEFAULT_MAX_RESULTS = 15
DEFAULT_YEARS_BACK = 3
MIN_RELEVANCE_SCORE = 0.001
CACHE_TTL_HOURS = 48
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure virtual environment is activated
2. **Connection Issues**: Check if server is running and accessible
3. **Timeout Errors**: Increase timeout settings for large searches
4. **Cache Issues**: Clear cache if corrupted

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing

Run the test suite to verify functionality:

```bash
python tests/test_direct_mcp.py
```

## Performance Tips

1. **Use Caching**: The server caches results to improve performance
2. **Limit Results**: Use `max_results` to control response size
3. **Disable Full Text**: Set `include_full_text: false` for faster searches
4. **Batch Requests**: Group related searches together

## Security Considerations

1. **Input Validation**: All inputs are validated using Pydantic models
2. **Rate Limiting**: Consider implementing rate limiting for production use
3. **Error Handling**: Sensitive information is not exposed in error messages
4. **Cache Security**: Cache files are stored locally with appropriate permissions

## Production Deployment

### Docker Support

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "scripts/run_server.py"]
```

### Systemd Service

```ini
[Unit]
Description=arXiv Research MCP Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/arxiv-research-mcp
ExecStart=/opt/arxiv-research-mcp/.venv/bin/python scripts/run_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Support

For issues and questions:
1. Check the logs for error messages
2. Run the test suite to verify functionality
3. Review the configuration settings
4. Check network connectivity for arXiv API access

The server is designed to be robust and handle various edge cases gracefully. 
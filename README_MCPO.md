# arXiv Research MCP Server - MCPO Integration

## 🚀 Quick Start with MCPO

### 1. Start the Server

```powershell
# Windows PowerShell
.\start_mcpo_server.ps1

# Or manually:
.venv\Scripts\activate
python scripts/run_server.py
```

### 2. Configure MCPO

The server is configured in `mcpo_config.json`:

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

### 3. Use with MCPO

```bash
# Start MCPO with the arXiv server
mcpo --config mcpo_config.json

# In another terminal, use MCPO CLI
mcpo call arxiv-research search_arxiv_papers '{"query": "deep learning", "max_results": 3}'
```

## 📋 Available Tools

### `search_arxiv_papers`
Search arXiv for academic papers with relevance ranking.

**Parameters:**
- `query` (required): Search query
- `max_results` (optional): Number of papers (default: 10)
- `years_back` (optional): Years to search back (default: 2)
- `include_full_text` (optional): Include full text (default: true)

### `clear_cache`
Clear all cached search results.

### `get_cache_stats`
Get cache statistics and information.

## 🔧 Examples

### Python Example

```python
import asyncio
from src.server import call_tool

async def search_papers():
    result = await call_tool("search_arxiv_papers", {
        "query": "transformer models",
        "max_results": 5
    })
    print(result[0].text)

asyncio.run(search_papers())
```

### MCPO CLI Example

```bash
# Search for papers
mcpo call arxiv-research search_arxiv_papers '{"query": "quantum computing", "max_results": 3}'

# Get cache stats
mcpo call arxiv-research get_cache_stats '{}'

# Clear cache
mcpo call arxiv-research clear_cache '{}'
```

## 🧪 Testing

```bash
# Test server functions directly
python tests/test_direct_mcp.py

# Run usage examples
python examples/mcpo_usage.py
```

## 📖 Documentation

- **Full Guide**: `MCPO_INTEGRATION_GUIDE.md`
- **Configuration**: `mcpo_config.json`
- **Examples**: `examples/mcpo_usage.py`

## ⚡ Performance Tips

1. **Use caching**: Results are cached for 24 hours
2. **Limit results**: Use `max_results` to control response size
3. **Disable full text**: Set `include_full_text: false` for faster searches
4. **Batch requests**: Group related searches together

## 🔍 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Activate virtual environment
2. **Connection Issues**: Check if server is running
3. **Timeout Errors**: Increase timeout for large searches
4. **Cache Issues**: Clear cache if corrupted

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Use Cases

- **Research Analysis**: Search and analyze academic papers
- **Literature Review**: Find relevant papers for topics
- **Trend Analysis**: Track research trends over time
- **Paper Discovery**: Discover new papers in your field

## 📊 Features

- ✅ **arXiv Integration**: Search arXiv API
- ✅ **Relevance Ranking**: TF-IDF based ranking
- ✅ **Caching**: Intelligent caching system
- ✅ **Full Text Extraction**: PDF text extraction
- ✅ **MCP Protocol**: Standard MCP implementation
- ✅ **Error Handling**: Robust error handling
- ✅ **Logging**: Comprehensive logging

The server is ready for production use with MCPO! 🚀 
# arXiv Research MCP Server

A comprehensive Model Context Protocol (MCP) server for searching and analyzing academic papers from arXiv with AI-powered relevance ranking and full-text extraction.

## Features

- **Smart Search**: Search arXiv with date filtering and relevance ranking
- **Full Text Extraction**: Download and extract complete paper content
- **Caching**: Intelligent caching to reduce API calls
- **Multiple Integrations**: Works with Claude, LangChain, Streamlit, and more
- **Batch Processing**: Process multiple research topics efficiently
- **API Wrapper**: REST API for easy integration
- **Jupyter Integration**: Interactive analysis and visualization tools
- **Relevance Ranking**: TF-IDF based ranking for better results
- **PDF Processing**: Multi-method text extraction from PDFs

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/borderlessboy/arxiv-research-mcp
cd arxiv-research-mcp

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
# cp .env.example .env  # Create .env file with your configuration
```

### Basic Usage

```python
# Run the MCP server
python scripts/run_server.py

# Or use the Streamlit dashboard
streamlit run integrations/streamlit_app.py
```

## Installation Options

### Full Installation
```bash
pip install "arxiv-research-mcp[all]"
```

### Specific Components
```bash
# API server only
pip install "arxiv-research-mcp[api]"

# Jupyter integration
pip install "arxiv-research-mcp[jupyter]"

# Dashboard
pip install "arxiv-research-mcp[dashboard]"

# LangChain integration
pip install "arxiv-research-mcp[langchain]"
```

## Usage Examples

### 1. Basic MCP Server Usage

```python
from src.server import search_arxiv_papers_tool

# Search for papers
result = await search_arxiv_papers_tool({
    "query": "transformer models",
    "max_results": 10,
    "years_back": 4,
    "include_full_text": True
})
```

### 2. LangChain Integration

```python
from integrations.langchain_tool import ResearchAgent

agent = ResearchAgent()
result = agent.research_topic("quantum machine learning")
```

### 3. Jupyter Analysis

```python
from integrations.jupyter_helper import search_papers

# Search and analyze
helper = await search_papers("machine learning", max_results=20)

# Create visualizations
fig = helper.create_publication_timeline()
plt.show()
```

### 4. Streamlit Dashboard

```bash
streamlit run integrations/streamlit_app.py
```

## Configuration

Create a `.env` file with your settings:

```env
# Server Configuration
SERVER_NAME=arxiv-research-server
LOG_LEVEL=INFO

# arXiv API Configuration
ARXIV_REQUEST_TIMEOUT=30
ARXIV_MAX_RETRIES=3

# Caching
CACHE_ENABLED=true
CACHE_TTL_HOURS=24

# Content Processing
MAX_FULL_TEXT_LENGTH=50000
DEFAULT_MAX_RESULTS=10
DEFAULT_YEARS_BACK=4
```

## API Reference

### MCP Tools

#### `search_arxiv_papers`
Search for academic papers with relevance ranking.

**Parameters:**
- `query` (string): Search query
- `max_results` (integer, default: 10): Maximum papers to return
- `years_back` (integer, default: 4): Years to search back
- `include_full_text` (boolean, default: true): Include full paper text

#### `clear_cache`
Clear all cached search results.

#### `get_cache_stats`
Get cache statistics and information.

### LangChain Tools

#### `ArxivResearchTool`
Search arXiv papers with LangChain integration.

#### `ArxivCacheManagementTool`
Manage cache with LangChain integration.

## Advanced Features

### Relevance Ranking
The server uses TF-IDF vectorization and cosine similarity to rank papers by relevance to your query.

### PDF Processing
Multiple extraction methods (PyPDF2, pdfplumber) ensure robust text extraction from PDFs.

### Caching System
Intelligent caching reduces API calls and improves response times.

### Batch Processing
Process multiple research topics efficiently with the batch processor.

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Building
```bash
python setup.py build
```

## Architecture

```
arxiv-research-mcp/
├── src/
│   ├── server.py              # Main MCP server
│   ├── models/                # Data models
│   ├── services/              # Core services
│   └── utils/                 # Utility functions
├── integrations/              # External integrations
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
└── examples/                  # Usage examples
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/borderlessboy/arxiv-research-mcp/issues)
- **Documentation**: [GitHub Wiki](https://github.com/borderlessboy/arxiv-research-mcp/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/borderlessboy/arxiv-research-mcp/discussions)

## Acknowledgments

- arXiv for providing the academic paper database
- MCP (Model Context Protocol) for the server framework
- The open-source community for the various libraries used
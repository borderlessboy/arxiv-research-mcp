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

### Docker Usage

The project includes a Dockerfile for easy containerized deployment.

#### Quick Start with Docker

```bash
# Build the Docker image
docker build -t arxiv-research-mcp .

# Run the container
docker run -p 8090:8090 arxiv-research-mcp
```

#### Docker with Custom Configuration

```bash
# Build with custom tag
docker build -t arxiv-research-mcp:latest .

# Run with custom port mapping
docker run -p 8080:8090 arxiv-research-mcp

# Run with volume for persistent cache
docker run -p 8090:8090 -v $(pwd)/cache:/app/cache arxiv-research-mcp

# Run with environment variables
docker run -p 8090:8090 \
  -e CACHE_ENABLED=true \
  -e CACHE_TTL_HOURS=24 \
  -e LOG_LEVEL=INFO \
  arxiv-research-mcp
```

#### Docker Compose (Recommended)

The project includes a `docker-compose.yml` file for easy deployment:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

Or create a custom `docker-compose.yml`:

```yaml
version: '3.8'
services:
  arxiv-research-mcp:
    build: .
    ports:
      - "8090:8090"
    volumes:
      - ./cache:/app/cache
    environment:
      - CACHE_ENABLED=true
      - CACHE_TTL_HOURS=24
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Docker Development

```bash
# Build for development with all dependencies
docker build -t arxiv-research-mcp:dev .

# Run with mounted source code for development
docker run -p 8090:8090 \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/cache:/app/cache \
  arxiv-research-mcp:dev
```

## Installation Options

### Docker Installation (Recommended)
```bash
# Quick start with Docker
docker build -t arxiv-research-mcp .
docker run -p 8090:8090 arxiv-research-mcp
```

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

### Docker Deployment
The project includes a production-ready Dockerfile with:
- Lightweight Python 3.11-slim base image
- Optimized layer caching for faster builds
- Pre-configured HTTP server on port 8090
- Volume support for persistent caching
- Environment variable configuration

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

### Docker Development
```bash
# Build development image
docker build -t arxiv-research-mcp:dev .

# Run with source code mounted for development
docker run -p 8090:8090 \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/cache:/app/cache \
  arxiv-research-mcp:dev

# Run tests in Docker
docker run arxiv-research-mcp:dev pytest tests/
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

## Documentation

For detailed documentation and guides, see the [Docs/](Docs/) directory:

- **[MCPO Integration Guide](Docs/MCPO_INTEGRATION_GUIDE.md)** - Complete guide for MCPO integration
- **[Port Running Guide](Docs/PORT_RUNNING_GUIDE.md)** - How to run the server on different ports
- **[README for MCPO](Docs/README_MCPO.md)** - MCPO-specific documentation
- **[Bug Fixes Summary](Docs/BUG_FIXES_SUMMARY.md)** - Summary of bug fixes and improvements
- **[Code Cleanup Summary](Docs/CLEANUP_SUMMARY.md)** - Documentation of code cleanup and optimization
- **[Docker Setup Guide](Docs/DOCKER_SETUP.md)** - Comprehensive Docker deployment guide
- **[License Information](Docs/LICENSE_INFORMATION.md)** - License details and compliance guide

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Use a different port
docker run -p 8080:8090 arxiv-research-mcp
```

**Permission denied:**
```bash
# Run with proper permissions
sudo docker run -p 8090:8090 arxiv-research-mcp
```

**Build fails:**
```bash
# Clean build
docker system prune -a
docker build --no-cache -t arxiv-research-mcp .
```

**Container exits immediately:**
```bash
# Check logs
docker logs <container_id>
# Run interactively
docker run -it arxiv-research-mcp /bin/bash
```

## Support

- **Issues**: [GitHub Issues](https://github.com/borderlessboy/arxiv-research-mcp/issues)
- **Documentation**: [GitHub Wiki](https://github.com/borderlessboy/arxiv-research-mcp/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/borderlessboy/arxiv-research-mcp/discussions)

## Acknowledgments

- arXiv for providing the academic paper database
- MCP (Model Context Protocol) for the server framework
- The open-source community for the various libraries used
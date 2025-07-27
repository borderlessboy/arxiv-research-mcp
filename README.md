# arXiv Research MCP Server

A comprehensive Model Context Protocol (MCP) server for searching and analyzing academic papers from arXiv with AI-powered relevance ranking and full-text extraction.

## Features

- **Smart Search**: Search arXiv with date filtering and relevance ranking
- **Full Text Extraction**: Download and extract complete paper content
- **Caching**: Intelligent caching to reduce API calls
- **Multiple Integrations**: Works with Claude, LangChain, Streamlit, and more
- **Batch Processing**: Process multiple research topics efficiently
- **API Wrapper**: REST API for easy integration

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/arxiv-research-mcp
cd arxiv-research-mcp

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
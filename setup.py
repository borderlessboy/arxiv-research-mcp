"""Setup script for the arXiv Research MCP Server."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements_path = this_directory / "requirements.txt"
with open(requirements_path, 'r', encoding='utf-8') as f:
    requirements = [
        line.strip() for line in f 
        if line.strip() and not line.startswith('#') and not line.startswith('-')
    ]

# Development requirements
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "isort>=5.12.0",
    "pre-commit>=3.0.0",
]

# Optional dependencies for different use cases
extras_require = {
    "dev": dev_requirements,
    
    "api": [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
        "python-multipart>=0.0.6",
    ],
    
    "dashboard": [
        "streamlit>=1.28.0",
        "plotly>=5.15.0",
        "altair>=5.0.0",
    ],
    
    "jupyter": [
        "jupyter>=1.0.0",
        "ipython>=8.0.0",
        "ipywidgets>=8.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "wordcloud>=1.9.0",
        "networkx>=3.0.0",
    ],
    
    "bots": [
        "slack-bolt>=1.18.0",
        "discord.py>=2.3.0",
        "python-telegram-bot>=20.0.0",
    ],
    
    "langchain": [
        "langchain>=0.1.0",
        "langchain-openai>=0.1.0",
        "langchain-anthropic>=0.1.0",
        "langchain-community>=0.0.20",
    ],
    
    "redis": [
        "redis>=4.5.0",
        "aioredis>=2.0.0",
    ],
    
    "advanced": [
        "spacy>=3.6.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "sentence-transformers>=2.2.0",
    ],
}

# All optional dependencies
extras_require["all"] = list(set(sum(extras_require.values(), [])))

setup(
    name="arxiv-research-mcp",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive MCP server for searching and analyzing academic papers from arXiv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/arxiv-research-mcp",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/arxiv-research-mcp/issues",
        "Source": "https://github.com/yourusername/arxiv-research-mcp",
        "Documentation": "https://github.com/yourusername/arxiv-research-mcp/wiki",
    },
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Text Processing :: Linguistic",
        "Framework :: AsyncIO",
        "Framework :: FastAPI",
        "Framework :: Jupyter",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "arxiv-research-server=scripts.run_server:main",
            "arxiv-batch-processor=scripts.batch_processor:main",
            "arxiv-api-server=integrations.api_wrapper:main",
            "arxiv-streamlit=integrations.streamlit_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.json", "*.yaml", "*.yml"],
        "config": ["*.py"],
        "examples": ["*.json", "*.py"],
    },
    zip_safe=False,
    keywords=[
        "arxiv", "research", "papers", "academic", "search", "mcp", "server",
        "machine-learning", "nlp", "pdf", "text-processing", "relevance-ranking",
        "langchain", "streamlit", "jupyter", "api", "claude", "ai", "assistant"
    ],
    
    # Additional metadata
    license="MIT",
    platforms=["any"],
    
    # Testing configuration
    test_suite="tests",
    tests_require=dev_requirements,
    
    # Options for different environments
    options={
        "bdist_wheel": {
            "universal": False,
        },
    },
    
    # Minimum versions for critical dependencies
    python_requires=">=3.8",
    
    # Additional configuration for development
    cmdclass={},
    
    # Data files (if any)
    data_files=[
        ("examples", ["examples/claude_config.json", "examples/example_usage.py"]),
    ],
)

# Post-install message
def post_install_message():
    """Display post-installation message."""
    print("""
🎉 arXiv Research MCP Server installed successfully!

🚀 Quick Start:
1. Set up your environment:
   cp .env.example .env
   
2. Run the MCP server:
   python scripts/run_server.py
   
3. Or try the Streamlit dashboard:
   streamlit run integrations/streamlit_app.py

📚 Documentation:
- GitHub: https://github.com/yourusername/arxiv-research-mcp
- Examples: See the 'examples/' directory

🔧 Optional Dependencies:
- For API server: pip install "arxiv-research-mcp[api]"
- For Jupyter: pip install "arxiv-research-mcp[jupyter]"
- For dashboard: pip install "arxiv-research-mcp[dashboard]"
- For everything: pip install "arxiv-research-mcp[all]"

❓ Need help? Check the README.md or open an issue on GitHub.
""")

if __name__ == "__main__":
    import sys
    if "install" in sys.argv:
        # Run setup
        setup()
        # Show post-install message
        post_install_message()
    else:
        setup()

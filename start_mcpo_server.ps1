# PowerShell script to start the arXiv Research MCP Server for MCPO
# Usage: .\start_mcpo_server.ps1

Write-Host "Starting arXiv Research MCP Server for MCPO..." -ForegroundColor Green

# Activate virtual environment
if (Test-Path ".venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\activate.ps1
} else {
    Write-Host "Virtual environment not found. Please run: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import feedparser, httpx, pydantic" 2>$null
    Write-Host "Dependencies OK" -ForegroundColor Green
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Start the MCP server
Write-Host "Starting MCP server..." -ForegroundColor Green
Write-Host "The server will listen for MCP protocol messages via stdin/stdout" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python scripts/run_server.py 
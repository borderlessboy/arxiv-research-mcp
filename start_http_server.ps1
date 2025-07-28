# PowerShell script to start the arXiv Research MCP Server on HTTP port
# Usage: .\start_http_server.ps1 [--port 8080] [--host localhost]

param(
    [int]$Port = 8090,
    [string]$HostName = "localhost",
    [switch]$Debug
)

Write-Host "Starting arXiv Research MCP Server on HTTP port..." -ForegroundColor Green
Write-Host "Host: $HostName" -ForegroundColor Cyan
Write-Host "Port: $Port" -ForegroundColor Cyan

# Activate virtual environment
if (Test-Path ".venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\activate.ps1
} elseif (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\activate.ps1
} else {
    Write-Host "Virtual environment not found. Please run: python -m venv .venv" -ForegroundColor Red
    Write-Host "Or create a virtual environment named 'venv'" -ForegroundColor Red
    exit 1
}

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    $null = python -c "import mcp, feedparser, httpx, pydantic" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies OK" -ForegroundColor Green
    } else {
        throw "Dependencies missing"
    }
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies. Please check requirements.txt" -ForegroundColor Red
        exit 1
    }
}

# Build command arguments
$scriptArgs = @("scripts/run_server_http.py", "--host", $HostName, "--port", $Port)
if ($Debug) {
    $scriptArgs += "--debug"
}

# Start the MCP server on TCP port
Write-Host "Starting MCP server on $HostName`:$Port..." -ForegroundColor Green
Write-Host "The server will listen for MCP protocol messages via HTTP" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python @scriptArgs 
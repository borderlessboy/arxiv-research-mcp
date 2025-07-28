# Running arXiv Research MCP Server on Specific Ports

This guide shows how to run the arXiv Research MCP server on different ports and protocols.

## 🚀 Quick Start Options

### 1. Standard MCP (stdin/stdout)
```powershell
# Standard MCP protocol (for MCPO integration)
.\start_mcpo_server.ps1
```

### 2. TCP Server (Port 8080)
```powershell
# TCP server on localhost:8080
.\start_tcp_server.ps1

# Custom port
.\start_tcp_server.ps1 -Port 9000

# Custom host and port
.\start_tcp_server.ps1 -Host 0.0.0.0 -Port 8080
```

### 3. HTTP API Server (Port 8000)
```powershell
# HTTP API on localhost:8000
python scripts/run_server_http.py

# Custom port
python scripts/run_server_http.py --port 3000

# Debug mode
python scripts/run_server_http.py --debug
```

## 📋 Port Options

### Standard MCP (stdin/stdout)
- **Use Case**: MCPO integration, subprocess communication
- **Command**: `python scripts/run_server.py`
- **Protocol**: MCP over stdin/stdout
- **Best for**: MCPO clients, direct integration

### TCP Server (Port 8080)
- **Use Case**: Direct TCP connections, custom clients
- **Command**: `python scripts/run_server_tcp.py --port 8080`
- **Protocol**: MCP over TCP
- **Best for**: Network clients, custom MCP implementations

### HTTP API Server (Port 8000)
- **Use Case**: REST API, web applications, easy testing
- **Command**: `python scripts/run_server_http.py --port 8000`
- **Protocol**: HTTP REST API
- **Best for**: Web apps, curl testing, browser access

## 🔧 Configuration Examples

### TCP Server Configuration

**Default (localhost:8080):**
```powershell
.\start_tcp_server.ps1
```

**Custom port:**
```powershell
.\start_tcp_server.ps1 -Port 9000
```

**Network accessible:**
```powershell
.\start_tcp_server.ps1 -Host 0.0.0.0 -Port 8080
```

**Debug mode:**
```powershell
.\start_tcp_server.ps1 -Debug
```

### HTTP API Configuration

**Default (localhost:8000):**
```bash
python scripts/run_server_http.py
```

**Custom port:**
```bash
python scripts/run_server_http.py --port 3000
```

**Network accessible:**
```bash
python scripts/run_server_http.py --host 0.0.0.0 --port 8000
```

**Debug mode:**
```bash
python scripts/run_server_http.py --debug
```

## 🧪 Testing Different Ports

### Test TCP Server
```bash
# Start TCP server
python scripts/run_server_tcp.py --port 8080

# Test with TCP client
python tests/test_tcp_client.py
```

### Test HTTP API
```bash
# Start HTTP server
python scripts/run_server_http.py --port 8000

# Test with curl
curl http://localhost:8000/
curl http://localhost:8000/tools
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer models", "max_results": 2}'
```

### Test Standard MCP
```bash
# Start standard server
python scripts/run_server.py

# Test with direct functions
python tests/test_direct_mcp.py
```

## 📊 Port Comparison

| Protocol | Port | Use Case | Pros | Cons |
|----------|------|----------|------|------|
| MCP stdio | - | MCPO integration | Standard MCP | Requires subprocess |
| TCP | 8080 | Network clients | Direct TCP | Custom client needed |
| HTTP | 8000 | Web/REST | Easy testing | Not native MCP |

## 🔍 Available Endpoints (HTTP API)

### GET Endpoints
- `GET /` - Server info and available endpoints
- `GET /tools` - List available tools
- `GET /cache/stats` - Get cache statistics
- `GET /health` - Health check

### POST Endpoints
- `POST /search` - Search for papers
- `POST /tools/call` - Call any tool
- `POST /cache/clear` - Clear cache

### Example HTTP Requests

**Search for papers:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing",
    "max_results": 3,
    "years_back": 1,
    "include_full_text": false
  }'
```

**Get cache stats:**
```bash
curl http://localhost:8000/cache/stats
```

**Call specific tool:**
```bash
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_cache_stats",
    "arguments": {}
  }'
```

## 🛠️ MCPO Integration with TCP

Update your MCPO configuration for TCP:

```json
{
  "servers": {
    "arxiv-research-tcp": {
      "command": "python",
      "args": ["scripts/run_server_tcp.py", "--host", "localhost", "--port", "8080"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 🔒 Security Considerations

### Local Development
- Use `localhost` for local development
- Default ports are fine for local use

### Production Deployment
- Use `0.0.0.0` to bind to all interfaces
- Consider using non-standard ports
- Implement proper authentication
- Use HTTPS in production

### Network Security
```bash
# Bind to specific interface only
python scripts/run_server_tcp.py --host 192.168.1.100 --port 8080

# Use firewall rules
# Windows: netsh advfirewall firewall add rule
# Linux: iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

## 🚀 Production Deployment

### Docker with Custom Port
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "scripts/run_server_tcp.py", "--host", "0.0.0.0", "--port", "8080"]
```

### Systemd Service
```ini
[Unit]
Description=arXiv Research MCP Server (TCP)
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/arxiv-research-mcp
ExecStart=/opt/arxiv-research-mcp/.venv/bin/python scripts/run_server_tcp.py --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8080

# Kill the process
taskkill /PID <PID> /F
```

### Permission Denied
```bash
# Run as administrator (Windows)
# Use sudo (Linux)
sudo python scripts/run_server_tcp.py --host 0.0.0.0 --port 80
```

### Firewall Issues
```bash
# Windows: Allow through firewall
netsh advfirewall firewall add rule name="MCP Server" dir=in action=allow protocol=TCP localport=8080

# Linux: Open port
sudo ufw allow 8080
```

## 📈 Performance Tips

1. **Use appropriate protocol**:
   - MCP stdio for MCPO integration
   - TCP for network clients
   - HTTP for web applications

2. **Port selection**:
   - Use standard ports (8000, 8080) for development
   - Use custom ports for production
   - Avoid privileged ports (< 1024)

3. **Network configuration**:
   - Use `localhost` for local development
   - Use `0.0.0.0` for network access
   - Configure firewall appropriately

The server is now ready to run on any port you choose! 🎉 
# Docker Setup Guide

This guide covers Docker deployment for the arXiv Research MCP Server.

## 🐳 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier deployment)

### Basic Docker Usage

```bash
# Build the image
docker build -t arxiv-research-mcp .

# Run the container
docker run -p 8090:8090 arxiv-research-mcp
```

The server will be available at `http://localhost:8090`

## 📦 Docker Compose (Recommended)

The project includes a pre-configured `docker-compose.yml` file:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## ⚙️ Configuration Options

### Environment Variables

You can customize the server behavior using environment variables:

```bash
docker run -p 8090:8090 \
  -e CACHE_ENABLED=true \
  -e CACHE_TTL_HOURS=24 \
  -e LOG_LEVEL=INFO \
  -e ARXIV_REQUEST_TIMEOUT=30 \
  -e MAX_FULL_TEXT_LENGTH=50000 \
  arxiv-research-mcp
```

### Volume Mounts

For persistent caching:

```bash
docker run -p 8090:8090 \
  -v $(pwd)/cache:/app/cache \
  arxiv-research-mcp
```

### Custom Port Mapping

```bash
# Map to different host port
docker run -p 8080:8090 arxiv-research-mcp
```

## 🔧 Development with Docker

### Development Mode

```bash
# Build development image
docker build -t arxiv-research-mcp:dev .

# Run with source code mounted
docker run -p 8090:8090 \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/cache:/app/cache \
  arxiv-research-mcp:dev
```

### Running Tests

```bash
# Run tests in Docker
docker run arxiv-research-mcp:dev pytest tests/
```

## 🏗️ Dockerfile Details

The Dockerfile is optimized for production:

- **Base Image**: `python:3.11-slim` (lightweight)
- **System Dependencies**: Installed for PDF processing
- **Layer Caching**: Optimized for faster rebuilds
- **Security**: Minimal attack surface
- **Size**: Optimized for smaller image size

### Build Context

The `.dockerignore` file excludes unnecessary files:
- Documentation files
- Test files
- Cache directories
- IDE files
- Git files

## 🚀 Production Deployment

### Docker Compose for Production

```yaml
services:
  arxiv-research-mcp:
    build: .
    container_name: arxiv-research-mcp
    ports:
      - "8090:8090"
    volumes:
      - ./cache:/app/cache
    environment:
      - CACHE_ENABLED=true
      - CACHE_TTL_HOURS=24
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: arxiv-research-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: arxiv-research-mcp
  template:
    metadata:
      labels:
        app: arxiv-research-mcp
    spec:
      containers:
      - name: arxiv-research-mcp
        image: arxiv-research-mcp:latest
        ports:
        - containerPort: 8090
        env:
        - name: CACHE_ENABLED
          value: "true"
        - name: LOG_LEVEL
          value: "INFO"
```

## 🔍 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8090
# Use different port
docker run -p 8080:8090 arxiv-research-mcp
```

**Permission denied:**
```bash
# Run with sudo
sudo docker run -p 8090:8090 arxiv-research-mcp
# Or add user to docker group
sudo usermod -aG docker $USER
```

**Build fails:**
```bash
# Clean Docker cache
docker system prune -a
# Rebuild without cache
docker build --no-cache -t arxiv-research-mcp .
```

**Container exits immediately:**
```bash
# Check logs
docker logs <container_id>
# Run interactively
docker run -it arxiv-research-mcp /bin/bash
```

### Debugging

```bash
# Check container status
docker ps -a

# View container logs
docker logs <container_id>

# Execute commands in running container
docker exec -it <container_id> /bin/bash

# Inspect container
docker inspect <container_id>
```

## 📊 Performance Tips

1. **Use Volume Mounts**: Mount cache directory for persistence
2. **Optimize Build**: Use `.dockerignore` to reduce build context
3. **Resource Limits**: Set memory and CPU limits for production
4. **Health Checks**: Monitor container health
5. **Logging**: Configure proper log levels

## 🔐 Security Considerations

- Base image is updated regularly
- Minimal attack surface with slim image
- No root user in container
- Proper file permissions
- Environment variable configuration

## 📈 Monitoring

### Health Check

The container includes a health check endpoint:

```bash
# Test health endpoint
curl http://localhost:8090/health
```

### Logs

```bash
# View real-time logs
docker logs -f <container_id>

# View last 100 lines
docker logs --tail 100 <container_id>
```

## 🎯 Best Practices

1. **Use Docker Compose** for easier management
2. **Mount volumes** for persistent data
3. **Set resource limits** in production
4. **Use health checks** for monitoring
5. **Configure proper logging** levels
6. **Regular image updates** for security
7. **Backup cache data** regularly
8. **Monitor resource usage**

The Docker setup provides a production-ready deployment option with easy scaling and management capabilities. 
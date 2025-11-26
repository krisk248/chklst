# Docker Deployment Guide for chklst

This guide provides comprehensive instructions for deploying the chklst application using Docker for both local development and production environments.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Local Development](#local-development)
4. [Production Deployment](#production-deployment)
5. [VPS Deployment](#vps-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Architecture Overview](#architecture-overview)

---

## Quick Start

### Single Command Deployment (Production)

```bash
# Build and start the application
./scripts/deploy.sh start

# Application will be available at http://localhost:8000
```

### Single Command Development

```bash
# Start development environment with hot-reload
./scripts/dev.sh

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

---

## Prerequisites

### Required Software

- **Docker** (version 20.10 or later)
  - [Install Docker](https://docs.docker.com/engine/install/)

- **Docker Compose** (version 1.29 or later)
  - Included with Docker Desktop for Mac/Windows
  - [Install Docker Compose for Linux](https://docs.docker.com/compose/install/)

### Optional Tools

- **curl** (for health checks)
- **git** (for cloning the repository)

### System Requirements

- **RAM**: Minimum 2GB (recommended 4GB)
- **Disk Space**: Minimum 5GB available
- **Ports**: Ensure ports 8000 and 80 are available (5173 for development)

---

## Local Development

### Setup Development Environment

```bash
# 1. Clone the repository
git clone <repository-url>
cd chklst

# 2. Start development environment
./scripts/dev.sh
```

This will:
- Start the Python backend with auto-reload on code changes
- Start the Vue.js frontend with hot-reload on file changes
- Initialize the database
- Set up WebSocket connections

### Access Points

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs

### Development Commands

```bash
# View live logs
./scripts/dev.sh logs

# Stop development environment
./scripts/dev.sh stop

# Access backend shell
docker-compose -f docker-compose.dev.yml exec backend bash

# Access frontend shell
docker-compose -f docker-compose.dev.yml exec frontend sh

# Install additional frontend packages
docker-compose -f docker-compose.dev.yml exec frontend npm install package-name
```

### Database Management

```bash
# Reset database
docker-compose -f docker-compose.dev.yml exec backend rm -f /app/data/chklst.db

# View database
docker-compose -f docker-compose.dev.yml exec backend sqlite3 /app/data/chklst.db
```

---

## Production Deployment

### Local Production Testing

```bash
# 1. Build and start production containers
./scripts/deploy.sh build
./scripts/deploy.sh start

# 2. Access application
# http://localhost:8000

# 3. View logs
./scripts/deploy.sh logs

# 4. Stop services
./scripts/deploy.sh stop
```

### Production with Nginx Reverse Proxy

```bash
# Start with Nginx profile (SSL-ready)
docker-compose --profile production up -d

# Configure SSL certificates:
# 1. Place cert.pem and key.pem in docker/ssl/
# 2. Update server_name in docker/nginx.conf
# 3. Uncomment HTTPS section in docker/nginx.conf
# 4. Restart: docker-compose --profile production restart nginx
```

### Deploy Commands

```bash
# Build images
./scripts/deploy.sh build

# Start services
./scripts/deploy.sh start

# Restart services
./scripts/deploy.sh restart

# Stop services
./scripts/deploy.sh stop

# View logs
./scripts/deploy.sh logs

# Check status
./scripts/deploy.sh status
```

---

## VPS Deployment

### Deployment to DigitalOcean, Linode, AWS, etc.

#### Step 1: Prepare VPS

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add current user to docker group (optional, for non-root access)
usermod -aG docker $USER
newgrp docker

# Install Docker Compose (if not included)
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Clone Repository

```bash
# Create app directory
mkdir -p /opt/chklst
cd /opt/chklst

# Clone repository
git clone <repository-url> .

# Or copy files directly
# scp -r chklst/ root@your-vps-ip:/opt/chklst/
```

#### Step 3: Configure for Production

```bash
# Create environment file (optional)
cat > .env << EOF
PYTHONUNBUFFERED=1
DEBUG=false
EOF

# Create data persistence directories
mkdir -p data/
mkdir -p reports/pdfs/
mkdir -p projects/

# Copy your existing data (if any)
# scp -r your-data/ root@your-vps-ip:/opt/chklst/projects/
```

#### Step 4: Deploy Application

```bash
# Build and start
./scripts/deploy.sh start

# Verify services are running
docker-compose ps

# Check health
curl http://localhost:8000/health
```

#### Step 5: Configure Domain and SSL

```bash
# If using a domain, update nginx config
# Edit docker/nginx.conf and update server_name

# For HTTPS with Let's Encrypt:
# 1. Install certbot on VPS
apt-get install certbot python3-certbot-nginx

# 2. Generate certificate
certbot certonly --standalone -d your-domain.com

# 3. Copy certificates to docker/ssl/
mkdir -p docker/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/key.pem

# 4. Update docker/nginx.conf with domain
# 5. Start with production profile
docker-compose --profile production up -d
```

#### Step 6: Setup Auto-Restart and Monitoring

```bash
# Enable auto-restart on system reboot
cd /opt/chklst

# Create systemd service (optional)
sudo tee /etc/systemd/system/chklst.service > /dev/null << 'EOF'
[Unit]
Description=chklst Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/chklst
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.yml down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable chklst
sudo systemctl start chklst
```

#### Step 7: Backup and Maintenance

```bash
# Backup data
tar -czf chklst-backup-$(date +%Y%m%d).tar.gz \
  data/ \
  projects/ \
  library.json \
  settings.json

# Upload to backup storage
scp chklst-backup-*.tar.gz backup-server:/backups/

# Update application
cd /opt/chklst
git pull
./scripts/deploy.sh restart

# View logs
./scripts/deploy.sh logs
```

---

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000
# or
netstat -tlnp | grep 8000

# Kill the process
kill -9 <PID>

# Or use different port in docker-compose.yml
# Change: "8000:8000" to "8001:8000"
```

#### Docker Build Fails

```bash
# Clear build cache and rebuild
docker-compose build --no-cache

# Check Docker disk space
docker system df

# Clean up unused images and volumes
docker system prune -a --volumes
```

#### Application Not Starting

```bash
# Check logs
./scripts/deploy.sh logs

# Check container status
docker-compose ps

# Inspect specific container
docker-compose logs chklst

# Access container shell for debugging
docker-compose exec chklst /bin/bash
```

#### Database Issues

```bash
# Verify database file exists
ls -la data/

# Check database integrity
sqlite3 data/chklst.db "SELECT COUNT(*) FROM projects;"

# Reset database (warning: deletes all data)
docker-compose exec chklst rm -f /app/data/chklst.db
docker-compose restart chklst
```

#### Frontend/Backend Connection Issues

```bash
# Check if backend is responding
curl http://localhost:8000/health

# Check frontend environment variables
docker-compose -f docker-compose.dev.yml exec frontend env | grep VITE

# Check network connectivity between containers
docker-compose exec frontend ping backend
docker-compose exec backend ping frontend
```

### Get Help

```bash
# View help
./scripts/deploy.sh help
./scripts/dev.sh help

# Check system requirements
docker --version
docker-compose --version
docker info

# Enable debug logging
export DEBUG=true
./scripts/deploy.sh start
```

---

## Architecture Overview

### Multi-Stage Build (Production)

```
Stage 1: Frontend Builder
├── Build Node.js environment
├── Install frontend dependencies
├── Build Vue.js application
└── Output: /frontend/dist

Stage 2: Python Backend
├── Python 3.12 slim base
├── Install system dependencies
├── Install Python packages (Pipenv)
├── Copy built frontend from Stage 1
├── Mount data volumes
└── Run FastAPI + Uvicorn
```

### Service Architecture

#### Development (docker-compose.dev.yml)

```
┌─────────────────────────────────────────┐
│         Development Environment         │
├─────────────────────────────────────────┤
│                                         │
│  Backend Container          Frontend    │
│  ┌────────────────────────┐  Container │
│  │ Python 3.12          │  ┌────────┐ │
│  │ FastAPI + Uvicorn    │  │ Node   │ │
│  │ Port: 8000           │  │ Port:  │ │
│  │ Auto-reload: On      │  │ 5173   │ │
│  │ Debug: true          │  │ Hot:   │ │
│  │ DB: SQLite           │  │ reload │ │
│  └────────────────────────┘  └────────┘ │
│         (localhost)      (localhost)    │
└─────────────────────────────────────────┘
```

#### Production (docker-compose.yml)

```
┌──────────────────────────────────────────┐
│       Production Environment             │
├──────────────────────────────────────────┤
│                                          │
│  ┌──────────────────────────────────┐   │
│  │    Nginx (Reverse Proxy)         │   │
│  │    Port: 80, 443 (HTTPS)        │   │
│  │    Compression: gzip             │   │
│  │    Load balancing                │   │
│  └──────────────────────────────────┘   │
│              |                            │
│              v                            │
│  ┌──────────────────────────────────┐   │
│  │    chklst Backend                │   │
│  │    Python 3.12 (slim)           │   │
│  │    FastAPI + Uvicorn            │   │
│  │    Port: 8000 (internal)        │   │
│  │    Health checks: Enabled       │   │
│  │    Restart: unless-stopped      │   │
│  │    Volumes: data, reports, etc  │   │
│  └──────────────────────────────────┘   │
│                                          │
└──────────────────────────────────────────┘
```

### Data Persistence

```
Host System                  Docker Container
├── ./data              <--> /app/data
├── ./reports           <--> /app/reports
├── ./projects          <--> /app/projects
├── ./library.json      <--> /app/library.json
└── ./settings.json     <--> /app/settings.json
```

---

## Advanced Configuration

### Environment Variables

```bash
# Create .env file for customization
cat > .env << EOF
# Python settings
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
DEBUG=false

# Application settings
APP_NAME=chklst
LOG_LEVEL=INFO

# Frontend settings
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=production
EOF
```

### Custom Nginx Configuration

Edit `docker/nginx.conf` for:
- Custom domain configuration
- SSL/TLS setup
- Request headers
- Rate limiting
- Caching policies

### Resource Limits

Edit `docker-compose.yml` to limit resources:

```yaml
services:
  chklst:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Scaling

For multiple instances with load balancing:

```yaml
services:
  chklst-1:
    build: .
    ports:
      - "8001:8000"
  chklst-2:
    build: .
    ports:
      - "8002:8000"
```

---

## Performance Tips

1. **Frontend Optimization**
   - Vite builds optimized assets in production
   - Gzip compression enabled in Nginx
   - Image optimization with Vue.js

2. **Backend Optimization**
   - Database indexing on frequently queried columns
   - Connection pooling in SQLAlchemy
   - Async/await for non-blocking I/O

3. **Infrastructure**
   - Use managed database for production
   - Enable CDN for static assets
   - Monitor resource usage with docker stats

```bash
# Monitor Docker resources
docker stats

# Check container performance
docker-compose exec chklst ps aux
docker-compose exec chklst top
```

---

## Security Considerations

### Production Checklist

- [ ] Enable HTTPS with SSL certificates
- [ ] Update `docker/nginx.conf` with domain
- [ ] Set secure random secrets for JWT
- [ ] Enable authentication middleware
- [ ] Implement rate limiting
- [ ] Regular backups of data volume
- [ ] Monitor logs for suspicious activity
- [ ] Keep Docker images updated
- [ ] Use private container registry
- [ ] Network segmentation with firewall rules

### Secret Management

```bash
# Store secrets in .env (add to .gitignore)
cat >> .gitignore << EOF
.env
.env.local
.env.*.local
EOF

# Load environment variables
set -a
source .env
set +a
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review logs: `./scripts/deploy.sh logs`
3. Open GitHub issue with:
   - Error message
   - Docker version
   - System information
   - Steps to reproduce

---

**Last Updated**: 2025-11-26
**Version**: 1.0
**Compatible with**: Docker 20.10+, Docker Compose 1.29+

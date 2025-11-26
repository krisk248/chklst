# Docker Quick Start Guide for chklst

A fast 5-minute guide to get chklst running with Docker.

## 5-Minute Setup

### Option 1: Production (Single Command)

```bash
./scripts/deploy.sh start
```

**That's it!** Your application will be:
- Built with optimized multi-stage Docker build
- Available at http://localhost:8000
- Automatically restarted if it crashes
- Persisting data in local volumes

### Option 2: Development (Single Command)

```bash
./scripts/dev.sh
```

Your application will be:
- Running with hot-reload (changes instant)
- Backend at http://localhost:8000
- Frontend at http://localhost:5173
- Database auto-initialized
- Perfect for coding!

---

## What's Happening Behind the Scenes?

### Production Build (docker-compose.yml)

```dockerfile
Stage 1: Build Frontend Assets
├─ Node 20 Alpine
├─ npm install frontend dependencies
├─ npm run build
└─ Output: dist/

Stage 2: Run Backend with Frontend
├─ Python 3.12 Slim
├─ Install Python dependencies
├─ Copy built frontend assets
├─ Run FastAPI on 0.0.0.0:8000
└─ Health checks enabled
```

### Development Setup (docker-compose.dev.yml)

```
Container 1: Backend
├─ Python 3.12
├─ Uvicorn with --reload
├─ Port 8000
└─ Auto-restarts on code change

Container 2: Frontend
├─ Node 20 Alpine
├─ Vite dev server
├─ Port 5173 (or 3000)
└─ Hot module reload
```

---

## Common Commands

```bash
# Production
./scripts/deploy.sh start    # Start application
./scripts/deploy.sh stop     # Stop application
./scripts/deploy.sh logs     # View live logs
./scripts/deploy.sh status   # Check service status

# Development
./scripts/dev.sh             # Start dev environment
./scripts/dev.sh stop        # Stop dev environment
./scripts/dev.sh logs        # View dev logs

# Raw Docker
docker-compose ps            # List running containers
docker-compose logs -f       # View logs
docker-compose exec chklst bash  # Access backend shell
```

---

## Accessing Your Application

### Local Access

- **Application**: http://localhost:8000
- **Frontend (dev only)**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs (when running)
- **ReDoc**: http://localhost:8000/redoc

### Data Files

- Projects: `./projects/` (mounted as volume)
- Reports: `./reports/` (mounted as volume)
- Database: `./data/chklst.db`
- Settings: `./settings.json`
- Library: `./library.json`

---

## Troubleshooting

### "Port 8000 is already in use"

```bash
# Kill the process using port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or change port in docker-compose.yml
# "8000:8000" → "8001:8000"
```

### "Docker not found"

Install Docker: https://docs.docker.com/engine/install/

### Application doesn't respond

```bash
# Check logs
./scripts/deploy.sh logs

# Verify services are running
docker-compose ps

# Restart
./scripts/deploy.sh restart
```

### Database issues

```bash
# Reset database
docker-compose exec chklst rm -f /app/data/chklst.db
docker-compose restart
```

---

## Deployment to VPS

### Step 1: SSH into VPS

```bash
ssh root@your-vps-ip
```

### Step 2: Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Step 3: Clone and Deploy

```bash
mkdir -p /opt/chklst
cd /opt/chklst
git clone <your-repo-url> .

./scripts/deploy.sh start
```

### Step 4: Access

```
http://your-vps-ip:8000
```

---

## File Structure

```
chklst/
├── Dockerfile              # Production image (multi-stage)
├── Dockerfile.dev          # Development image
├── docker-compose.yml      # Production services
├── docker-compose.dev.yml  # Development services
├── .dockerignore          # Files to exclude from Docker image
├── docker/
│   ├── nginx.conf         # Reverse proxy (optional)
│   └── ssl/               # SSL certificates (optional)
├── scripts/
│   ├── deploy.sh          # Production deployment
│   └── dev.sh             # Development startup
├── frontend/              # Vue.js application
├── backend/               # FastAPI application
└── data/                  # Persistent data volumes
```

---

## Next Steps

1. **Customize Configuration**
   - Edit `docker-compose.yml` for production settings
   - Update `docker/nginx.conf` for domain configuration

2. **Add SSL (HTTPS)**
   - Place certificates in `docker/ssl/`
   - Start with: `docker-compose --profile production up`

3. **Scale Application**
   - Add multiple service instances
   - Use Nginx load balancing

4. **Setup Backups**
   - Use `docker cp` or volume mounts
   - Schedule automated backups

5. **Monitor Performance**
   - Use `docker stats` for resource monitoring
   - Check `docker-compose logs` for errors

---

## Environment Variables

### Available Options

```bash
# Create .env file for customization
cat > .env << EOF
# Python
DEBUG=false
PYTHONUNBUFFERED=1

# Application
APP_NAME=chklst
LOG_LEVEL=INFO

# Frontend (development)
VITE_API_URL=http://localhost:8000
EOF

# Load with: set -a && source .env && set +a
```

---

## Performance Tips

- **Frontend**: Built with Vite (optimized bundles)
- **Backend**: Async/await with FastAPI
- **Database**: SQLite with proper indexing
- **Nginx**: Gzip compression enabled
- **Resources**: Light on memory (< 1GB)

---

## Getting Help

```bash
# View help for deployment
./scripts/deploy.sh help

# View help for development
./scripts/dev.sh help

# Check Docker is working
docker --version
docker ps

# Check logs for errors
docker-compose logs
```

---

## Architecture Summary

| Component | Technology | Port | Auto-Reload |
|-----------|-----------|------|-------------|
| Backend | FastAPI + Uvicorn | 8000 | Dev: Yes |
| Frontend | Vue 3 + Vite | 5173 | Dev: Yes |
| Database | SQLite | N/A | N/A |
| Reverse Proxy | Nginx | 80/443 | Opt. |

---

**All set!** Your chklst application is now fully containerized and ready to deploy anywhere.

For advanced configuration, see: [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

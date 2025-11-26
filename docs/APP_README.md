# chklst Application Entry Point

This document explains how to run the chklst web application using the `app.py` entry point.

## Quick Start

### Production Mode (Default)

Run the application in production mode with a single command:

```bash
pipenv run python app.py
```

This will:
1. Start the FastAPI backend on port 8000
2. Serve the pre-built Vue frontend from `frontend/dist/`
3. Automatically open your browser to `http://localhost:8000`
4. Display API documentation at `http://localhost:8000/docs`

### Development Mode

For development with hot reload on both frontend and backend:

```bash
pipenv run python app.py --dev
```

This will:
1. Start FastAPI backend on port 8000 with auto-reload
2. Start Vite dev server on port 3000
3. Allow frontend code changes to hot-reload instantly
4. Allow backend code changes to trigger server restart

## Command Line Options

### `--port PORT`

Specify a custom port for the server (production mode only):

```bash
pipenv run python app.py --port 9000
```

If the specified port is already in use, the application will automatically find an available port.

### `--no-browser`

Run the server without automatically opening a browser:

```bash
pipenv run python app.py --no-browser
```

### `--dev`

Run in development mode with hot reload:

```bash
pipenv run python app.py --dev
```

## Architecture

### Production Mode

**Directory Structure:**
```
chklst/
├── app.py                 # Main entry point (you are here)
├── backend/
│   ├── main.py           # FastAPI application
│   ├── api/              # API endpoints
│   ├── models/           # SQLAlchemy models
│   └── schemas/          # Pydantic schemas
├── frontend/
│   ├── src/              # Vue source code
│   ├── dist/             # Built frontend (served by backend)
│   │   ├── index.html
│   │   └── assets/
│   └── package.json
└── data/                 # SQLite database
```

**Flow:**
1. User makes request to `http://localhost:8000`
2. FastAPI receives request
3. If path is `/api/v1/*`, route to API endpoints
4. If path is `/assets/*`, serve static assets from `frontend/dist/assets/`
5. Otherwise, serve `frontend/dist/index.html` (SPA fallback for Vue Router)

### Development Mode

**Separate Processes:**
- **Backend:** FastAPI on port 8000 (auto-reload on changes)
- **Frontend:** Vite dev server on port 3000 (hot module replacement)

**Configuration:**
- Frontend dev server configured to proxy API calls to backend
- CORS enabled for localhost development
- Both processes show logs in terminal

## Building for Production

Before deploying to production, build the frontend:

```bash
./build.sh
```

Or manually:

```bash
cd frontend
npm run build
cd ..
```

This creates optimized bundles in `frontend/dist/` that are served by the backend.

## Environment Variables

Configuration is controlled by `.env` file or environment variables. Key settings:

- `DATABASE_URL`: SQLite database location (default: `./data/chklst.db`)
- `DEBUG`: Enable debug mode (default: `True`)
- `API_V1_PREFIX`: API endpoint prefix (default: `/api/v1`)

See `backend/config.py` for all available settings.

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Option 1: Use a different port
pipenv run python app.py --port 9000

# Option 2: Kill process on port 8000 (Linux/Mac)
lsof -ti:8000 | xargs kill -9
```

### Frontend Not Building

If you see "Frontend not built" error:

```bash
# Build the frontend
./build.sh

# Or manually
cd frontend
npm install
npm run build
```

### Hot Reload Not Working (Dev Mode)

Try using the absolute path to app.py:

```bash
pipenv run python /full/path/to/chklst/app.py --dev
```

### Can't Connect to Backend (Dev Mode)

Ensure backend is running:

```bash
# Check if port 8000 is open
curl http://localhost:8000/health

# If not responsive, kill and restart
pipenv run python app.py --dev
```

## Architecture Details

### Key Features

1. **Port Detection**
   - Automatically detects if port is in use
   - Finds alternative port if needed
   - Shows clear message about which port was chosen

2. **Browser Auto-Opening**
   - Opens browser with slight delay (1.5s) to allow server startup
   - Can be disabled with `--no-browser`
   - Cross-platform (Windows, Mac, Linux)

3. **Graceful Shutdown**
   - Handles Ctrl+C to cleanly stop servers
   - Properly terminates all child processes
   - No orphaned processes left behind

4. **Development Mode**
   - Runs both backend and frontend simultaneously
   - Proper signal handling for Ctrl+C
   - Shows logs from both servers
   - Auto-detects and reports crashed servers

### Static File Serving

The FastAPI backend is configured in `backend/main.py` to:

1. **Mount Assets** (`/assets/*`)
   - Serves optimized Vue assets (JavaScript, CSS, images)
   - Located in `frontend/dist/assets/`
   - Configured in `app.mount("/assets", StaticFiles(...))`

2. **SPA Fallback Route** (`/{full_path:path}`)
   - Serves `frontend/dist/index.html` for any non-API route
   - Allows Vue Router client-side routing to work
   - Catches 404s and returns the SPA shell

## API Documentation

Once running, access API documentation at:

```
http://localhost:8000/docs           # Swagger UI
http://localhost:8000/redoc          # ReDoc documentation
http://localhost:8000/openapi.json   # OpenAPI schema
```

## Database

SQLite database is stored in `data/chklst.db`. On first run:

1. Database is automatically initialized
2. Tables are created from SQLAlchemy models
3. Database persists across runs

To reset database:

```bash
rm -f data/chklst.db
```

## Code Structure

### app.py Functions

- `is_port_in_use(port)` - Check if port is already in use
- `find_available_port(start_port, max_attempts)` - Find available port
- `open_browser(url, delay)` - Open browser in a thread
- `run_production(port, open_browser_flag)` - Run production server
- `run_development(backend_port, frontend_port)` - Run dev mode with hot reload
- `main()` - Entry point with argument parsing

### backend/main.py Modifications

Added for production serving:

```python
# Mount static assets
app.mount("/assets", StaticFiles(directory=...), name="assets")

# SPA fallback route
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("frontend/dist/index.html")
```

## Testing

Run tests for app.py:

```bash
pipenv run pytest tests/test_app.py -v
pipenv run pytest tests/test_app_integration.py -v
```

Tests cover:
- Port detection and availability checking
- Browser opening functionality
- Production and development mode execution
- Command line argument parsing
- Static file serving configuration
- Build script verification

## Performance

### Production Mode
- Single process: Minimal resource usage
- Pre-built frontend: Fast asset delivery
- Uvicorn with default worker settings

### Development Mode
- Dual processes: Frontend and backend
- Hot reload: Fast iteration
- Source maps: Easy debugging

## Security

**CORS Configuration** (backend/config.py):
- Localhost only in development
- Can be configured via environment variables
- Restrict to specific domains in production

**Static Files**:
- Assets served from `frontend/dist/assets/` only
- No directory listing enabled
- Paths validated by FastAPI

## Next Steps

1. **Development**: Start with `pipenv run python app.py --dev`
2. **Build**: Run `./build.sh` before deployment
3. **Production**: Use `pipenv run python app.py`
4. **Monitor**: Check logs for errors and issues

---

For more information on the chklst project, see the main README.md.

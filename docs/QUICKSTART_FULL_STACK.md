# chklst Full Stack - Quick Start Guide

Complete guide to running the full stack (backend + frontend) for the chklst deployment tracker application.

## Prerequisites

- **Python**: 3.11+ (for backend)
- **Node.js**: 18+ (for frontend)
- **npm**: 9+ or yarn/pnpm
- **Git**: Version control

## Project Structure

```
chklst/
├── backend/              # FastAPI backend
│   ├── api/             # API routes
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── main.py          # FastAPI app
│   ├── config.py        # Configuration
│   └── database.py      # Database setup
│
├── frontend/            # Vue 3 frontend
│   ├── src/            # Vue components and logic
│   ├── dist/           # Production build output
│   ├── package.json    # Dependencies
│   └── vite.config.ts  # Vite configuration
│
├── tests/              # Backend tests
├── data/               # SQLite database location
└── README.md
```

## Step 1: Backend Setup & Run

### 1.1 Navigate to backend directory
```bash
cd chklst
# Backend code is in ./backend/ directory
```

### 1.2 Create Python environment (if not using pipenv)
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using pipenv (recommended)
pipenv shell
```

### 1.3 Install dependencies
```bash
# Using pipenv (recommended)
pipenv install

# Or using pip
pip install fastapi uvicorn sqlalchemy pydantic aiosqlite pytest pytest-asyncio httpx
```

### 1.4 Verify backend structure
```bash
# Check that backend files exist
ls -la backend/
ls -la backend/api/routes/
ls -la backend/models/
```

### 1.5 Run backend server
```bash
# Development with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or using pipenv
pipenv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 1.6 Verify backend is working
```bash
# In another terminal, test the health endpoint
curl http://localhost:8000/health

# Expected response
{"status":"ok","app":"chklst"}

# Check API docs
# Open browser: http://localhost:8000/docs
```

### Backend Commands Reference
```bash
# Run tests
pytest tests/ -v
pytest tests/ --cov=backend

# Check specific test
pytest tests/test_api/test_health.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

## Step 2: Frontend Setup & Run

### 2.1 Open new terminal window, navigate to frontend
```bash
cd chklst/frontend
```

### 2.2 Install dependencies
```bash
npm install
# or
npm ci  # For exact versions
```

### 2.3 Verify frontend structure
```bash
# Check that all files exist
ls -la src/
ls -la src/components/
ls -la src/views/
```

### 2.4 Run frontend dev server
```bash
npm run dev
```

**Expected Output**:
```
VITE v5.4.21  ready in 302 ms
➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### 2.5 Open in browser
```
http://localhost:3000
```

You should see:
- Dark theme sidebar with 7 menu items
- Deployment view with statistics cards
- All navigation working
- No API data yet (backend integration in Phase 2)

### Frontend Commands Reference
```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Watch mode for tests
npm test -- --watch

# Coverage report
npm run coverage

# Type checking
npm run type-check
```

## Step 3: Full Stack Verification

### 3.1 Check both servers are running
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
npm run dev

# Terminal 3: Verification
# Backend health check
curl http://localhost:8000/health

# Frontend is accessible
curl http://localhost:3000
```

### 3.2 Test API from Frontend
Open browser console (F12 → Console) and test:
```javascript
// Test API call
fetch('/api/v1/projects')
  .then(r => r.json())
  .then(d => console.log(d))

// Expected: Empty list initially
// {"status":"ok"} or project list
```

### 3.3 Check Network Tab
In browser DevTools → Network tab:
1. Navigate between pages
2. Verify requests go to `/api/v1/*`
3. All requests should show CORS headers
4. Status should be 200 (OK) or 404 for non-existent data

## Typical Development Workflow

### Terminal 1: Backend
```bash
cd chklst
pipenv shell
uvicorn backend.main:app --reload
```

### Terminal 2: Frontend
```bash
cd chklst/frontend
npm run dev
```

### Terminal 3: Testing/Additional Commands
```bash
# Run backend tests
cd chklst
pytest tests/ -v

# Or frontend tests
cd chklst/frontend
npm test

# Or build frontend for production
npm run build
```

## Environment Configuration

### Backend Configuration
Create `.env` file in project root:
```
APP_NAME=chklst
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./data/chklst.db
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
CORS_CREDENTIALS=True
CORS_METHODS=["GET","POST","PUT","DELETE","PATCH","OPTIONS"]
CORS_HEADERS=["*"]
```

### Frontend Configuration
Create `.env.local` in `frontend/` directory:
```
VITE_API_BASE_URL=/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

## Database Setup

### Initialize Database
The database is automatically created on first run. To reset:
```bash
# Remove existing database
rm -f data/chklst.db

# Restart backend - new DB will be created
uvicorn backend.main:app --reload
```

### Database Location
```
data/chklst.db  # SQLite database file
```

### Database Schema
Automatically created with these tables:
- `projects` - Deployment projects
- `components` - Project components
- `deployments` - Deployment records
- `library` - Reusable library items
- `appsettings` - Application settings

## Troubleshooting

### Issue: Port 8000 already in use
```bash
# Change backend port
uvicorn backend.main:app --reload --port 8001

# Update frontend proxy in vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8001',  # Updated port
  }
}
```

### Issue: Port 3000 already in use
```bash
# Change frontend port in vite.config.ts
server: {
  port: 3001,  // New port
}
```

### Issue: CORS errors
- Verify backend has CORS enabled
- Check `CORS_ORIGINS` in backend config includes `http://localhost:3000`
- Restart backend after config changes

### Issue: Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend proxy is configured
cat frontend/vite.config.ts | grep -A5 proxy

# Verify network in browser DevTools
# Check that /api requests go to http://localhost:8000
```

### Issue: Database errors
```bash
# Check database exists
ls -la data/chklst.db

# Delete and recreate
rm -f data/chklst.db
# Restart backend

# Check backend logs for initialization messages
# Should see: "Database initialized"
```

## Testing the Application

### Backend Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_api/test_health.py::test_health_check -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

### Frontend Tests
```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm run coverage

# UI mode
npm test:ui
```

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
# Output in dist/ directory
```

### Run Backend in Production
```bash
# Using gunicorn (install first: pip install gunicorn)
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Or uvicorn with multiple workers
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Serve Frontend
```bash
# Using any static file server
# Example with Python
python -m http.server 8080 --directory dist/

# Or nginx, Apache, etc.
```

## Development Tips

### Hot Module Replacement (HMR)
- Frontend: Changes auto-reload in browser
- Backend: Changes auto-reload with uvicorn --reload

### Vue DevTools
Install Vue DevTools browser extension for better debugging:
- Chrome: Vue DevTools in Chrome Web Store
- Firefox: Vue.js DevTools addon

### TypeScript IntelliSense
For better IDE support:
- Use VS Code recommended
- Install Vetur or Volar extension
- Enable TypeScript language server

### API Documentation
FastAPI provides automatic documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## Monitoring & Debugging

### Backend Logging
Check backend console for:
```
DEBUG logs for requests
Error logs for exceptions
SQL query logs
```

### Frontend Console Errors
Check browser console (F12) for:
```
Vue warnings
Axios errors
WebSocket connection issues
TypeScript errors
```

### Network Requests
Check DevTools → Network tab:
```
All /api/v1/* requests
Response status codes
Response headers (CORS)
Response body
```

## Common Development Commands

### Backend
```bash
# Start server
uvicorn backend.main:app --reload

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_api/test_health.py -v

# Check code style (if configured)
pylint backend/
```

### Frontend
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Type checking
npm run type-check

# Check code style (if configured)
npm run lint
```

## Next Steps

1. **Phase 2**: API Integration
   - Implement data fetching in views
   - Connect components to backend
   - Add loading and error states
   - Implement real-time updates

2. **Phase 3**: Authentication
   - User login/logout
   - JWT token management
   - Protected routes
   - User profile

3. **Phase 4**: Advanced Features
   - WebSocket real-time updates
   - Charts and visualizations
   - Advanced search and filtering
   - Export functionality (Excel, PDF)

## Support & Resources

- Vue 3 Docs: https://vuejs.org/
- FastAPI Docs: https://fastapi.tiangolo.com/
- Vite Docs: https://vitejs.dev/
- Tailwind CSS: https://tailwindcss.com/
- TypeScript: https://www.typescriptlang.org/

## Summary

You now have:
- ✓ Backend API running on port 8000
- ✓ Frontend development server running on port 3000
- ✓ Database initialized at `data/chklst.db`
- ✓ Dark theme UI with sidebar navigation
- ✓ 7 page views ready for data integration
- ✓ API client and WebSocket support
- ✓ Full TypeScript type safety

The full stack is operational and ready for Phase 2 development!

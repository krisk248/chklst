# Backend Quick Start Guide

## Installation

### Prerequisites
- Python 3.12+
- pipenv (installed via `pip install pipenv`)

### Setup Steps

```bash
# 1. Navigate to project directory
cd /home/kannan/Projects/Active/chklst

# 2. Install dependencies
pipenv install --dev

# 3. Activate virtual environment
pipenv shell

# 4. Create data directory
mkdir -p data

# 5. Verify installation
python -c "from backend.main import app; print('Backend ready!')"
```

## Running the Application

### Development Mode (with hot reload)
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then open: http://localhost:8000

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok", "app": "chklst"}
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_models.py -v
```

### Run with coverage
```bash
pytest --cov=backend --cov-report=html
```

Coverage report will be in `htmlcov/index.html`

### Run async tests only
```bash
pytest -m asyncio -v
```

## Project Structure

```
backend/
├── config.py           # Application settings
├── database.py         # SQLAlchemy async setup
├── main.py            # FastAPI app
├── api/
│   └── routes/        # API endpoints
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── services/          # Business logic (Phase 2)
└── websocket/         # WebSocket handlers (Phase 2)

tests/
├── conftest.py        # Pytest configuration
├── test_models.py     # Model tests
└── test_api/          # API endpoint tests
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```
APP_NAME=chklst
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./data/chklst.db
API_V1_PREFIX=/api/v1
```

See `.env.example` for all available options.

## API Endpoints

All endpoints are prefixed with `/api/v1`

### Projects
- `GET /projects` - List all projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get specific project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Deployments
- `GET /deployments` - List deployments
- `POST /deployments` - Create deployment
- `GET /deployments/{id}` - Get specific deployment
- `PUT /deployments/{id}` - Update deployment
- `DELETE /deployments/{id}` - Delete deployment

### Library
- `GET /library` - Get library data
- `POST /library/developers` - Add developer
- `POST /library/build-servers` - Add build server
- `POST /library/deploy-servers` - Add deploy server
- `POST /library/environments` - Add environment

### Reports
- `GET /reports/excel` - Export to Excel
- `GET /reports/pdf` - Export to PDF

## Development Workflow

### TDD Workflow for New Features

1. **Write Test (RED)**
   ```bash
   # Create test in tests/test_api/test_something.py
   pytest tests/test_api/test_something.py -v
   ```

2. **Implement Code (GREEN)**
   ```bash
   # Edit backend/api/routes/something.py
   # or backend/services/something_service.py
   pytest tests/test_api/test_something.py -v
   ```

3. **Refactor (REFACTOR)**
   ```bash
   # Clean up code while keeping tests passing
   pytest tests/test_api/test_something.py -v
   ```

## Database

### Database File Location
- Development: `./data/chklst.db` (SQLite)
- Testing: In-memory SQLite (automatically created)

### Database Initialization
The database is automatically initialized when the app starts through the lifespan context manager.

### Reset Database (Development)
```bash
# Delete the database file
rm data/chklst.db

# Restart the app - it will create a fresh database
uvicorn backend.main:app --reload
```

## Debugging

### Enable SQL Logging
In `backend/config.py`, set `DATABASE_ECHO = True` to see all SQL queries:

```python
DATABASE_ECHO = True
```

### Debug API Requests
Install httpie for easier API testing:

```bash
pip install httpie
```

Then use:
```bash
http GET http://localhost:8000/api/v1/projects
http POST http://localhost:8000/api/v1/projects name="New Project"
```

## Common Issues

### Port Already in Use
If port 8000 is already in use:
```bash
# Use a different port
uvicorn backend.main:app --reload --port 8001
```

### Database Locked Error
Delete the database and restart:
```bash
rm data/chklst.db
uvicorn backend.main:app --reload
```

### Import Errors
Make sure you're in the virtual environment:
```bash
pipenv shell
```

## Next Steps

1. **Phase 2 - Service Implementation**: Create service layer for business logic
2. **Phase 2 - API Implementation**: Implement endpoint handlers
3. **Phase 2 - Data Migration**: Import existing Excel and JSON data
4. **Phase 3 - Frontend Integration**: Connect Vue 3 frontend

## Useful Commands

```bash
# List all dependencies
pipenv graph

# Update specific dependency
pipenv update fastapi

# Install new dependency
pipenv install new-package

# Run specific test
pytest tests/test_models.py::test_project_creation -v

# Run tests matching pattern
pytest -k deployment -v

# Generate coverage report
pytest --cov=backend --cov-report=term-missing
```

## Documentation

- [PHASE1_IMPLEMENTATION_SUMMARY.md](./PHASE1_IMPLEMENTATION_SUMMARY.md) - Detailed Phase 1 summary
- [SPEC-WEB-MIGRATION-001](./moai/specs/SPEC-WEB-MIGRATION-001/) - Full specification
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)

## Support

For issues or questions, refer to:
1. SPEC document for requirements
2. PHASE1_IMPLEMENTATION_SUMMARY.md for architecture
3. Code comments and docstrings
4. Official documentation links above

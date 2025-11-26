# chklst - Deployment Tracking Web Application

A modern web application for tracking software deployments across multiple projects and environments. Originally developed as a PyQt5 desktop application, chklst has been transformed into a powerful and intuitive web interface built with Vue 3 and FastAPI.

**Developed by:** Kannan
**Organization:** TTS

---

## Overview

**chklst** is now a full-stack web application that helps development and DevOps teams:
- **Track deployments** across multiple projects and environments
- **Maintain deployment history** in organized databases
- **Generate deployment summaries** for JIRA tickets and team notifications
- **Monitor deployment statistics** with built-in reports and analytics
- **Prevent duplicate deployments** with intelligent duplicate detection
- **Access from anywhere** via web browser on any device
- **Real-time updates** via WebSocket support

---

## Key Features

### Deployment Tracking
- Record deployments with JIRA IDs, timestamps, and detailed status
- Track across multiple projects and environments
- Support for multi-component deployments
- Prevent duplicate deployments with intelligent detection

### Project & Component Management
- Organize deployments by projects
- Manage multiple components per project
- Maintain developer assignments and server configurations
- Component-specific build and deploy servers

### JIRA & Teams Integration
- Quick copy-to-clipboard functionality
- Format deployment summaries for JIRA tickets
- Direct integration with Microsoft Teams messaging
- Automatic notification support

### Reports & Analytics
- Monthly deployment statistics and trends
- Success/failure rate analysis by project and environment
- PDF report generation with charts
- Excel export with detailed deployment data
- Real-time statistics dashboard

### Library Management
- Reusable presets for developers, build servers, deploy servers
- Quick selection from saved libraries
- Easy customization and management

### Real-time Updates
- WebSocket support for live deployment notifications
- Real-time updates across multiple browser tabs
- Automatic refresh of dashboards and reports

---

## Technology Stack

### Frontend
- **Vue 3** - Progressive JavaScript framework with TypeScript
- **Tailwind CSS** - Utility-first CSS framework
- **Radix Vue** - Accessible component library
- **Pinia** - State management for Vue
- **Axios** - HTTP client for API calls
- **Vite** - Modern build tool

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.12** - Programming language
- **SQLAlchemy 2.0** - Object-relational mapper
- **PostgreSQL/SQLite** - Database
- **Pydantic** - Data validation
- **ReportLab** - PDF generation
- **Openpyxl** - Excel file handling

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Pipenv (for Python)
- npm or yarn (for Node)

### Installation & Running

1. **Install dependencies**
   ```bash
   pipenv install
   cd frontend && npm install && cd ..
   ```

2. **Run in Development Mode** (with hot reload)
   ```bash
   pipenv run python app.py --dev
   ```
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000 (opens automatically)

3. **Run in Production Mode**
   ```bash
   cd frontend && npm run build && cd ..
   pipenv run python app.py
   ```
   - Application: http://localhost:8000

### Command Options
```bash
pipenv run python app.py              # Production on port 8000
pipenv run python app.py --port 9000  # Custom port
pipenv run python app.py --dev        # Development mode with hot reload
pipenv run python app.py --no-browser # Don't auto-open browser
```

---

## Testing

```bash
# Run all tests with coverage
pipenv run python run_tests.py

# Run without coverage
pipenv run python run_tests.py --no-cov

# Run specific test
pipenv run python run_tests.py -k test_health

# Verbose output
pipenv run python run_tests.py -v
```

---

## Project Structure

```
chklst/
├── backend/                      # FastAPI application
│   ├── api/routes/              # API endpoints
│   ├── models/                  # Database models
│   ├── services/                # Business logic
│   ├── websocket/               # WebSocket handlers
│   ├── main.py                  # FastAPI app
│   ├── database.py              # Database config
│   └── config.py                # Settings
├── frontend/                    # Vue 3 application
│   ├── src/
│   │   ├── components/         # Vue components
│   │   ├── views/             # Page components
│   │   ├── stores/            # Pinia state management
│   │   ├── router/            # Vue Router config
│   │   └── App.vue            # Root component
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── tests/                       # Test suite
│   ├── test_api/               # API tests
│   ├── conftest.py             # Pytest fixtures
│   └── test_*.py
├── app.py                       # Entry point
├── run_tests.py                 # Test runner
├── Pipfile                      # Python dependencies
└── README.md                    # This file
```

---

## Database

### Development
SQLite is used by default (no setup required - auto-created)

### Production
Set environment variable for PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@localhost/chklst"
```

---

## API Documentation

When running locally, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Configuration

Create `.env` file in project root:
```env
DATABASE_URL=sqlite:///chklst.db
DEBUG=true
HOST=127.0.0.1
PORT=8000
```

---

## Troubleshooting

### Port Already in Use
```bash
pipenv run python app.py --port 9000
```

### Database Reset (Development)
```bash
rm chklst.db  # Remove SQLite database
# Database will be recreated on next run
```

### Frontend Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
cd ..
```

---

## Contributing

1. Create feature branch
2. Make changes
3. Run tests: `pipenv run python run_tests.py`
4. Submit pull request

---

## License & Attribution

© 2025 chklst. All Rights Reserved.

**Developed by:** Kannan
**Organization:** TTS

This application was built with a focus on user experience, performance, and maintainability. The transition from desktop to web ensures accessibility across all platforms while maintaining the powerful functionality that teams depend on for deployment tracking and management.

---

## Support

For issues, questions, or feature requests, please contact the development team.

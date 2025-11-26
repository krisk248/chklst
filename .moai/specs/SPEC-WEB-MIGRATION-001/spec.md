---
id: SPEC-WEB-MIGRATION-001
version: 1.0.0
status: draft
created: 2025-11-26
updated: 2025-11-26
author: Alfred
priority: high
tags: [migration, web-app, vue3, fastapi, sqlite]
---

# SPEC-WEB-MIGRATION-001: PyQt5 to Modern Web Application Migration

## 1. Executive Summary

This specification defines the complete migration of the **chklst** deployment tracking application from a PyQt5 desktop application to a modern web application using Vue 3 + FastAPI architecture.

### Current State
- **Technology**: PyQt5 desktop application (~5,500 lines Python)
- **Storage**: Excel files (monthly) + JSON project configs
- **Features**: 7 tabs (Deployment, Projects, Library, History, Reports, Settings, About)
- **Users**: Single user, local deployment tracking

### Target State
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS + shadcn-vue
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Database**: SQLite (primary) + Excel export (compatibility)
- **Real-time**: WebSocket for multi-tab synchronization
- **Deployment**: Local + VPS + Docker support

---

## 2. Environment

### 2.1 Development Environment

| Component | Specification |
|-----------|---------------|
| Python Version | 3.11+ |
| Node.js Version | 20 LTS+ |
| Package Manager (Python) | pipenv |
| Package Manager (Node) | npm/pnpm |
| IDE | VS Code recommended |
| OS Support | Linux, Windows, macOS |

### 2.2 Runtime Environment

| Component | Specification |
|-----------|---------------|
| Backend Server | Uvicorn (ASGI) |
| Frontend Build | Vite |
| Database | SQLite 3.x |
| Browser Support | Chrome, Firefox, Edge, Safari (latest 2 versions) |

### 2.3 Deployment Environment

| Scenario | Configuration |
|----------|---------------|
| Local Development | `pipenv run python app.py` starts both servers |
| Local Production | Single command startup with auto browser open |
| VPS Deployment | Docker container with nginx reverse proxy |
| Port Configuration | Backend: 8000, Frontend: 3000 (dev), 8000/app (prod) |

---

## 3. Assumptions

### 3.1 Technical Assumptions

- **A1**: Users have Python 3.11+ and Node.js 20+ installed
- **A2**: SQLite is sufficient for single-user workload (no concurrent writes)
- **A3**: Existing Excel files follow the documented format from ExcelManager
- **A4**: Project JSON files follow the documented ProjectJSONManager schema
- **A5**: WebSocket support is available in target browsers
- **A6**: File system access is available for Excel export/import

### 3.2 Business Assumptions

- **A7**: Single user operation (no authentication required)
- **A8**: Data migration from existing files is a one-time operation
- **A9**: Excel export format must remain compatible with existing files
- **A10**: Dark theme is required to match current application aesthetics
- **A11**: All existing functionality must be preserved (feature parity)

### 3.3 User Assumptions

- **A12**: Users are familiar with the current PyQt5 interface
- **A13**: Users expect similar workflow for deployment tracking
- **A14**: Users need JIRA and Teams copy functionality to continue working

---

## 4. Requirements

### 4.1 Functional Requirements

#### 4.1.1 Application Startup (FR-STARTUP)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-STARTUP-001 | **Ubiquitous**: The system SHALL start both backend and frontend servers with a single command `pipenv run python app.py` | Ubiquitous |
| FR-STARTUP-002 | **Event-Driven**: WHEN the application starts, THEN the system SHALL automatically open the default browser to the application URL | Event-Driven |
| FR-STARTUP-003 | **State-Driven**: WHILE the application is running, THEN the system SHALL keep both servers active until explicitly terminated | State-Driven |
| FR-STARTUP-004 | **Unwanted**: IF the configured port is already in use, THEN the system SHALL display an error message and suggest an alternative port | Unwanted |

#### 4.1.2 Deployment Form (FR-DEPLOY)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-DEPLOY-001 | **Ubiquitous**: The system SHALL display a deployment form with project selection, component selection, and deployment details fields | Ubiquitous |
| FR-DEPLOY-002 | **Event-Driven**: WHEN the user selects a project, THEN the system SHALL populate the component dropdown with enabled components for that project | Event-Driven |
| FR-DEPLOY-003 | **Event-Driven**: WHEN the user selects a component, THEN the system SHALL auto-fill component name, developer, VCS URL from project configuration | Event-Driven |
| FR-DEPLOY-004 | **Event-Driven**: WHEN the user clicks "Now" button, THEN the system SHALL set the timestamp to current date/time | Event-Driven |
| FR-DEPLOY-005 | **Event-Driven**: WHEN the user enables "DB Script", THEN the system SHALL enable the database script input field | Event-Driven |
| FR-DEPLOY-006 | **Event-Driven**: WHEN the user clicks "Save Deployment", THEN the system SHALL validate required fields and save to SQLite database | Event-Driven |
| FR-DEPLOY-007 | **Event-Driven**: WHEN a deployment is saved, THEN the system SHALL also export to Excel file in the existing format | Event-Driven |
| FR-DEPLOY-008 | **Unwanted**: IF a duplicate deployment is detected (same JIRA ID or within 5 minutes), THEN the system SHALL warn the user and request confirmation | Unwanted |
| FR-DEPLOY-009 | **Event-Driven**: WHEN a deployment is saved successfully, THEN the system SHALL enable Copy to JIRA, Copy to Teams, and Copy Both buttons | Event-Driven |
| FR-DEPLOY-010 | **Event-Driven**: WHEN the user clicks "Copy JIRA", THEN the system SHALL format deployment data as Markdown table and copy to clipboard | Event-Driven |
| FR-DEPLOY-011 | **Event-Driven**: WHEN the user clicks "Copy Teams", THEN the system SHALL format deployment data with bullets and emojis and copy to clipboard | Event-Driven |
| FR-DEPLOY-012 | **State-Driven**: WHILE project-level fields (environment, build server, deploy server, database) exist, THEN the system SHALL display them as read-only auto-filled fields | State-Driven |

#### 4.1.3 Projects Management (FR-PROJECTS)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-PROJECTS-001 | **Ubiquitous**: The system SHALL display a split view with project list on the left and project details form on the right | Ubiquitous |
| FR-PROJECTS-002 | **Event-Driven**: WHEN the user clicks "+ New Project", THEN the system SHALL create a new project with default structure | Event-Driven |
| FR-PROJECTS-003 | **Event-Driven**: WHEN the user selects a project from the list, THEN the system SHALL load and display project details in the form | Event-Driven |
| FR-PROJECTS-004 | **Event-Driven**: WHEN the user clicks "Save Project", THEN the system SHALL validate and save project data to SQLite | Event-Driven |
| FR-PROJECTS-005 | **Event-Driven**: WHEN the user clicks "Delete Project", THEN the system SHALL request confirmation and delete the project | Event-Driven |
| FR-PROJECTS-006 | **Ubiquitous**: The system SHALL support dynamic components list (not fixed Frontend/Backend/Backoffice) | Ubiquitous |
| FR-PROJECTS-007 | **Event-Driven**: WHEN the user clicks "+ Add Component", THEN the system SHALL display a modal dialog to add a new component | Event-Driven |
| FR-PROJECTS-008 | **Event-Driven**: WHEN the user toggles component ON/OFF, THEN the system SHALL update the component enabled status | Event-Driven |
| FR-PROJECTS-009 | **Event-Driven**: WHEN the user clicks "Edit" on a component, THEN the system SHALL display a modal with component details for editing | Event-Driven |
| FR-PROJECTS-010 | **Event-Driven**: WHEN the user clicks "Remove" on a component, THEN the system SHALL request confirmation and remove the component | Event-Driven |

#### 4.1.4 Library/Presets Management (FR-LIBRARY)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-LIBRARY-001 | **Ubiquitous**: The system SHALL display four sections: Developers, Build Servers, Deploy Servers, Environments | Ubiquitous |
| FR-LIBRARY-002 | **Event-Driven**: WHEN the user clicks "+ Add Developer", THEN the system SHALL prompt for name and add to developers list | Event-Driven |
| FR-LIBRARY-003 | **Event-Driven**: WHEN the user clicks "Remove Selected" on any list, THEN the system SHALL request confirmation and remove the item | Event-Driven |
| FR-LIBRARY-004 | **Unwanted**: IF the user tries to add a duplicate item, THEN the system SHALL display a warning and reject the addition | Unwanted |
| FR-LIBRARY-005 | **Event-Driven**: WHEN library data is updated, THEN the system SHALL broadcast changes via WebSocket to all open tabs | Event-Driven |

#### 4.1.5 Last Saved/History (FR-HISTORY)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-HISTORY-001 | **Ubiquitous**: The system SHALL display the last 50 deployments for the current month sorted by timestamp (newest first) | Ubiquitous |
| FR-HISTORY-002 | **Event-Driven**: WHEN the user selects a deployment from the table, THEN the system SHALL display full deployment details in the details panel | Event-Driven |
| FR-HISTORY-003 | **Event-Driven**: WHEN a deployment is selected, THEN the system SHALL enable Copy to JIRA, Copy to Teams, and Copy Both buttons | Event-Driven |
| FR-HISTORY-004 | **Event-Driven**: WHEN the user clicks "Refresh", THEN the system SHALL reload deployments from the database | Event-Driven |

#### 4.1.6 Reports (FR-REPORTS)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-REPORTS-001 | **Ubiquitous**: The system SHALL display month/year selection controls and three sub-tabs: Summary, Deployments, Statistics | Ubiquitous |
| FR-REPORTS-002 | **Event-Driven**: WHEN the user changes month or year, THEN the system SHALL reload all report data for the selected period | Event-Driven |
| FR-REPORTS-003 | **Ubiquitous**: The Summary tab SHALL display Total Deployments, Success Rate, and Active Projects as summary cards | Ubiquitous |
| FR-REPORTS-004 | **Ubiquitous**: The Deployments tab SHALL display a filterable table with all deployments for the selected period | Ubiquitous |
| FR-REPORTS-005 | **Ubiquitous**: The Statistics tab SHALL display Component Breakdown, Project Breakdown, and Success/Failure Analysis | Ubiquitous |
| FR-REPORTS-006 | **Event-Driven**: WHEN the user clicks "Export Excel", THEN the system SHALL generate a combined Excel file for all projects in the selected month | Event-Driven |
| FR-REPORTS-007 | **Event-Driven**: WHEN the user clicks "Generate PDF", THEN the system SHALL generate a comprehensive PDF report with charts and analytics | Event-Driven |
| FR-REPORTS-008 | **State-Driven**: WHILE PDF generation is in progress, THEN the system SHALL display a progress bar and disable the Generate PDF button | State-Driven |

#### 4.1.7 Settings (FR-SETTINGS)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-SETTINGS-001 | **Ubiquitous**: The system SHALL display User Defaults and Excel Export Settings sections | Ubiquitous |
| FR-SETTINGS-002 | **Event-Driven**: WHEN the user sets a default "Deployed By" name, THEN the system SHALL pre-fill this value in the Deployment form | Event-Driven |
| FR-SETTINGS-003 | **Event-Driven**: WHEN the user clicks "Browse" for export path, THEN the system SHALL open a directory picker dialog | Event-Driven |
| FR-SETTINGS-004 | **Event-Driven**: WHEN the user clicks "Save Settings", THEN the system SHALL persist settings to the database | Event-Driven |

#### 4.1.8 About Page (FR-ABOUT)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-ABOUT-001 | **Ubiquitous**: The system SHALL display application title, version, description, and feature list | Ubiquitous |
| FR-ABOUT-002 | **Ubiquitous**: The system SHALL display development information and technical details | Ubiquitous |

#### 4.1.9 Data Migration (FR-MIGRATION)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-MIGRATION-001 | **Event-Driven**: WHEN the application starts for the first time, THEN the system SHALL detect and import existing JSON project files | Event-Driven |
| FR-MIGRATION-002 | **Event-Driven**: WHEN the application starts for the first time, THEN the system SHALL detect and import existing library.json | Event-Driven |
| FR-MIGRATION-003 | **Event-Driven**: WHEN the application starts for the first time, THEN the system SHALL detect and import existing settings.json | Event-Driven |
| FR-MIGRATION-004 | **Event-Driven**: WHEN the application starts for the first time, THEN the system SHALL detect and import existing Excel deployment data | Event-Driven |
| FR-MIGRATION-005 | **Optional**: WHERE the user prefers, THEN the system SHALL allow manual import of Excel files through a UI option | Optional |

#### 4.1.10 Real-time Synchronization (FR-REALTIME)

| ID | Requirement | EARS Pattern |
|----|-------------|--------------|
| FR-REALTIME-001 | **Event-Driven**: WHEN any data changes (deployment saved, project updated, library changed), THEN the system SHALL broadcast the change via WebSocket | Event-Driven |
| FR-REALTIME-002 | **Event-Driven**: WHEN a WebSocket message is received, THEN all connected browser tabs SHALL refresh their relevant data | Event-Driven |
| FR-REALTIME-003 | **Unwanted**: IF WebSocket connection is lost, THEN the system SHALL attempt to reconnect automatically with exponential backoff | Unwanted |

### 4.2 Non-Functional Requirements

#### 4.2.1 Performance (NFR-PERF)

| ID | Requirement |
|----|-------------|
| NFR-PERF-001 | The application SHALL start and display UI within 3 seconds |
| NFR-PERF-002 | Page navigation SHALL complete within 200ms |
| NFR-PERF-003 | Form submission SHALL complete within 500ms |
| NFR-PERF-004 | Excel export SHALL complete within 5 seconds for up to 1000 records |
| NFR-PERF-005 | PDF generation SHALL complete within 30 seconds for monthly report |

#### 4.2.2 Usability (NFR-UX)

| ID | Requirement |
|----|-------------|
| NFR-UX-001 | The system SHALL use a dark theme consistent with the current PyQt5 application |
| NFR-UX-002 | The system SHALL use a sidebar navigation instead of tabs |
| NFR-UX-003 | The system SHALL provide keyboard shortcuts for common actions |
| NFR-UX-004 | The system SHALL display loading indicators during async operations |
| NFR-UX-005 | The system SHALL display toast notifications for success/error feedback |

#### 4.2.3 Compatibility (NFR-COMPAT)

| ID | Requirement |
|----|-------------|
| NFR-COMPAT-001 | Excel files generated SHALL be readable by the current PyQt5 application |
| NFR-COMPAT-002 | The system SHALL import existing Excel files without data loss |
| NFR-COMPAT-003 | The system SHALL support both old and new JSON project formats |

#### 4.2.4 Reliability (NFR-REL)

| ID | Requirement |
|----|-------------|
| NFR-REL-001 | The system SHALL auto-save form data to prevent loss on browser close |
| NFR-REL-002 | The system SHALL create database backups before migrations |
| NFR-REL-003 | The system SHALL recover gracefully from WebSocket disconnections |

#### 4.2.5 Portability (NFR-PORT)

| ID | Requirement |
|----|-------------|
| NFR-PORT-001 | The system SHALL run on Linux, Windows, and macOS |
| NFR-PORT-002 | The system SHALL support deployment via Docker |
| NFR-PORT-003 | The system SHALL work in both local and VPS environments |

---

## 5. Specifications

### 5.1 Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Frontend** | Vue 3 | 3.4+ |
| | TypeScript | 5.x |
| | Tailwind CSS | 3.4+ |
| | shadcn-vue | latest |
| | Pinia | 2.x |
| | Vue Router | 4.x |
| | Vite | 5.x |
| **Backend** | FastAPI | 0.110+ |
| | SQLAlchemy | 2.0+ |
| | Pydantic | 2.x |
| | Uvicorn | 0.27+ |
| | openpyxl | 3.1+ |
| | reportlab | 4.x |
| | matplotlib | 3.8+ |
| **Database** | SQLite | 3.x |
| **Testing** | pytest | 8.x |
| | Vitest | 1.x |
| | Playwright | 1.x (E2E) |

### 5.2 Directory Structure

```
chklst/
├── app.py                      # Single command entry point
├── Pipfile                     # Python dependencies
├── Pipfile.lock
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # SQLAlchemy setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── deployments.py  # Deployment CRUD
│   │   │   ├── projects.py     # Project CRUD
│   │   │   ├── library.py      # Library CRUD
│   │   │   ├── reports.py      # Reports generation
│   │   │   ├── settings.py     # Settings management
│   │   │   └── health.py       # Health check
│   │   └── deps.py             # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── deployment.py       # Deployment SQLAlchemy model
│   │   ├── project.py          # Project & Component models
│   │   ├── library.py          # Library model
│   │   └── settings.py         # Settings model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── deployment.py       # Pydantic schemas
│   │   ├── project.py
│   │   ├── library.py
│   │   ├── settings.py
│   │   └── reports.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── deployment_service.py
│   │   ├── project_service.py
│   │   ├── library_service.py
│   │   ├── excel_service.py    # Excel import/export
│   │   ├── pdf_service.py      # PDF generation
│   │   ├── formatter_service.py # JIRA/Teams formatting
│   │   └── migration_service.py # Data migration
│   ├── websocket/
│   │   ├── __init__.py
│   │   └── manager.py          # WebSocket connection manager
│   └── tests/
│       ├── __init__.py
│       ├── test_deployments.py
│       ├── test_projects.py
│       └── ...
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── stores/
│   │   │   ├── deployment.ts
│   │   │   ├── project.ts
│   │   │   ├── library.ts
│   │   │   ├── settings.ts
│   │   │   └── websocket.ts
│   │   ├── views/
│   │   │   ├── DeploymentView.vue
│   │   │   ├── ProjectsView.vue
│   │   │   ├── LibraryView.vue
│   │   │   ├── HistoryView.vue
│   │   │   ├── ReportsView.vue
│   │   │   ├── SettingsView.vue
│   │   │   └── AboutView.vue
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── Header.vue
│   │   │   ├── deployment/
│   │   │   │   ├── DeploymentForm.vue
│   │   │   │   ├── ProjectSelector.vue
│   │   │   │   └── CopyButtons.vue
│   │   │   ├── projects/
│   │   │   │   ├── ProjectList.vue
│   │   │   │   ├── ProjectForm.vue
│   │   │   │   └── ComponentDialog.vue
│   │   │   ├── library/
│   │   │   │   └── LibrarySection.vue
│   │   │   ├── history/
│   │   │   │   ├── DeploymentTable.vue
│   │   │   │   └── DeploymentDetails.vue
│   │   │   ├── reports/
│   │   │   │   ├── SummaryCards.vue
│   │   │   │   ├── DeploymentsTab.vue
│   │   │   │   └── StatisticsTab.vue
│   │   │   └── ui/
│   │   │       └── (shadcn-vue components)
│   │   ├── composables/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useClipboard.ts
│   │   │   └── useToast.ts
│   │   ├── lib/
│   │   │   ├── api.ts          # API client
│   │   │   └── utils.ts
│   │   └── assets/
│   │       └── styles/
│   │           └── main.css
│   └── tests/
│       └── ...
├── data/
│   ├── chklst.db               # SQLite database
│   └── exports/                # Excel exports
├── reports/                    # Legacy Excel files (for import)
│   └── {Mon_YYYY}/
│       └── {ProjectName}.xlsx
├── projects/                   # Legacy JSON configs (for import)
│   └── {ProjectName}.json
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── tests/
    └── e2e/
        └── ...
```

### 5.3 Database Schema

#### 5.3.1 Projects Table

```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    environment TEXT DEFAULT 'QA',
    build_server TEXT,
    deploy_server TEXT,
    db_name TEXT,
    db_backup_location TEXT,
    backup_location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.3.2 Components Table

```sql
CREATE TABLE components (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    developer_name TEXT,
    vcs_type TEXT DEFAULT 'Git',
    vcs_url TEXT,
    build_command TEXT,
    component_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.3.3 Deployments Table

```sql
CREATE TABLE deployments (
    id TEXT PRIMARY KEY,
    jira_patch_id TEXT DEFAULT 'N/A',
    timestamp TIMESTAMP NOT NULL,
    project_id TEXT NOT NULL REFERENCES projects(id),
    project_name TEXT NOT NULL,
    component_id TEXT REFERENCES components(id),
    component_name TEXT NOT NULL,
    component_url TEXT,
    environment TEXT,
    vcs_url TEXT,
    developer_name TEXT,
    build_server TEXT,
    deploy_server TEXT,
    database_name TEXT,
    db_backup_location TEXT,
    database_script TEXT DEFAULT 'N/A',
    backup_location TEXT,
    build_status BOOLEAN DEFAULT TRUE,
    deploy_status BOOLEAN DEFAULT TRUE,
    notes TEXT,
    deployed_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5.3.4 Library Table

```sql
CREATE TABLE library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('developer', 'build_server', 'deploy_server', 'environment')),
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(type, value)
);
```

#### 5.3.5 Settings Table

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.4 API Endpoints

#### 5.4.1 Deployments API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/deployments` | List deployments (with pagination, filtering) |
| GET | `/api/deployments/{id}` | Get deployment by ID |
| POST | `/api/deployments` | Create new deployment |
| GET | `/api/deployments/check-duplicate` | Check for duplicate deployment |
| GET | `/api/deployments/monthly/{month}/{year}` | Get deployments for month |
| GET | `/api/deployments/stats/{month}/{year}` | Get deployment statistics |
| POST | `/api/deployments/{id}/format/jira` | Format deployment for JIRA |
| POST | `/api/deployments/{id}/format/teams` | Format deployment for Teams |

#### 5.4.2 Projects API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all projects |
| GET | `/api/projects/{id}` | Get project by ID |
| POST | `/api/projects` | Create new project |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |
| GET | `/api/projects/{id}/components` | Get project components |
| POST | `/api/projects/{id}/components` | Add component |
| PUT | `/api/projects/{id}/components/{comp_id}` | Update component |
| DELETE | `/api/projects/{id}/components/{comp_id}` | Delete component |

#### 5.4.3 Library API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/library` | Get all library items |
| GET | `/api/library/{type}` | Get items by type |
| POST | `/api/library` | Add library item |
| DELETE | `/api/library/{id}` | Remove library item |

#### 5.4.4 Reports API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/summary/{month}/{year}` | Get monthly summary |
| GET | `/api/reports/export/excel/{month}/{year}` | Export Excel report |
| GET | `/api/reports/export/pdf/{month}/{year}` | Generate PDF report |

#### 5.4.5 Settings API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings` | Get all settings |
| GET | `/api/settings/{key}` | Get setting by key |
| PUT | `/api/settings/{key}` | Update setting |

#### 5.4.6 WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://host/ws` | WebSocket connection for real-time updates |

### 5.5 WebSocket Events

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `deployment:created` | Server -> Client | `{deployment}` | New deployment saved |
| `project:updated` | Server -> Client | `{project}` | Project was updated |
| `library:updated` | Server -> Client | `{type, items}` | Library data changed |
| `settings:updated` | Server -> Client | `{key, value}` | Setting was changed |

### 5.6 UI Component Specifications

#### 5.6.1 Sidebar Navigation

- Icon + text for each section
- Highlight active section
- Collapsible on mobile
- Dark theme background (#1e1e2e or similar)

#### 5.6.2 Dark Theme Colors

| Element | Color |
|---------|-------|
| Background (main) | #1e1e2e |
| Background (card) | #2b2b3d |
| Background (input) | #34495e |
| Text (primary) | #ecf0f1 |
| Text (secondary) | #7f8c8d |
| Accent (primary) | #4a9eff |
| Success | #27ae60 |
| Error | #e74c3c |
| Warning | #f39c12 |

---

## 6. Constraints

### 6.1 Technical Constraints

- **C1**: Must use SQLite for database (single-file, no server setup)
- **C2**: Must maintain Excel export compatibility with existing format
- **C3**: Single command startup requirement limits architecture choices
- **C4**: No external authentication services (single user)

### 6.2 Business Constraints

- **C5**: Zero downtime for existing users during migration
- **C6**: Existing Excel reports must remain accessible
- **C7**: No changes to JIRA/Teams copy format (users expect same output)

### 6.3 Resource Constraints

- **C8**: Single developer implementation
- **C9**: Target minimal dependencies for maintainability

---

## 7. Acceptance Criteria

### 7.1 Startup Criteria

- **AC-STARTUP-001**: Running `pipenv run python app.py` SHALL start the application and open browser
- **AC-STARTUP-002**: Application SHALL be usable within 3 seconds of startup

### 7.2 Deployment Form Criteria

- **AC-DEPLOY-001**: GIVEN a project with components, WHEN I select the project, THEN I see enabled components in dropdown
- **AC-DEPLOY-002**: GIVEN valid deployment data, WHEN I click Save, THEN deployment is saved to SQLite AND Excel
- **AC-DEPLOY-003**: GIVEN a saved deployment, WHEN I click Copy JIRA, THEN correctly formatted text is in clipboard

### 7.3 Data Migration Criteria

- **AC-MIGRATION-001**: GIVEN existing JSON project files, WHEN app starts first time, THEN all projects are imported
- **AC-MIGRATION-002**: GIVEN existing Excel files, WHEN app starts first time, THEN all deployments are imported
- **AC-MIGRATION-003**: Imported data SHALL match original data with 100% accuracy

### 7.4 Feature Parity Criteria

- **AC-PARITY-001**: All 7 tabs from PyQt5 app SHALL have equivalent functionality in web app
- **AC-PARITY-002**: JIRA copy output SHALL match existing PyQt5 output format exactly
- **AC-PARITY-003**: Teams copy output SHALL match existing PyQt5 output format exactly

---

## 8. Traceability

### 8.1 Requirement to Source Mapping

| Web App Feature | PyQt5 Source File | Lines |
|-----------------|-------------------|-------|
| Deployment Form | ui/simple_deployment_new.py | 1-567 |
| Projects Management | ui/simple_projects_form.py | 1-643 |
| Library/Presets | ui/simple_library.py | 1-357 |
| History/Last Saved | ui/simple_last_saved.py | 1-396 |
| Reports | ui/simple_reports.py | 1-678 |
| Settings | ui/simple_settings.py | 1-87 |
| About | ui/simple_about.py | 1-108 |
| Excel Manager | utils/excel_manager.py | 1-548 |
| JSON Manager | utils/json_manager.py | 1-278 |
| Library Manager | utils/library_manager.py | 1-152 |
| PDF Generator | utils/pdf_generator.py | 1-1197 |
| JIRA/Teams Format | utils/integration_formatter.py | 1-240 |

### 8.2 TAG Block

```
<!-- TAG:SPEC-WEB-MIGRATION-001:START -->
Specification ID: SPEC-WEB-MIGRATION-001
Version: 1.0.0
Status: draft
Created: 2025-11-26
Author: Alfred (spec-builder)
Domain: Migration, Web Application
Technology: Vue 3, FastAPI, SQLite, TypeScript
Priority: High
<!-- TAG:SPEC-WEB-MIGRATION-001:END -->
```

---

## 9. References

- Current PyQt5 Application Source: `/home/kannan/Projects/Active/chklst/`
- Vue 3 Documentation: https://vuejs.org/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- shadcn-vue: https://www.shadcn-vue.com/
- Tailwind CSS: https://tailwindcss.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/
- Pydantic v2: https://docs.pydantic.dev/

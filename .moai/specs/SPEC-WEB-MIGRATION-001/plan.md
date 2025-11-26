---
id: SPEC-WEB-MIGRATION-001-PLAN
version: 1.0.0
status: draft
created: 2025-11-26
updated: 2025-11-26
author: Alfred
parent_spec: SPEC-WEB-MIGRATION-001
---

# Implementation Plan: PyQt5 to Web Application Migration

## 1. Overview

This implementation plan outlines the phased approach to migrate the chklst PyQt5 desktop application to a modern Vue 3 + FastAPI web application.

### 1.1 Implementation Strategy

- **Approach**: Backend-first, then frontend
- **Testing**: TDD for backend, component testing for frontend
- **Integration**: Incremental feature migration with parallel operation support
- **Validation**: Each phase includes verification against original functionality

---

## 2. Implementation Phases

### Phase 1: Foundation Setup

**Priority**: Primary Goal (Must complete first)

#### 1.1 Backend Foundation

| Task | Description | Dependencies |
|------|-------------|--------------|
| 1.1.1 | Create project structure (backend directory layout) | None |
| 1.1.2 | Setup Pipfile with dependencies | 1.1.1 |
| 1.1.3 | Configure SQLAlchemy 2.0 with SQLite | 1.1.2 |
| 1.1.4 | Create database models (Projects, Components, Deployments, Library, Settings) | 1.1.3 |
| 1.1.5 | Implement Pydantic schemas | 1.1.4 |
| 1.1.6 | Create FastAPI app with CORS configuration | 1.1.2 |
| 1.1.7 | Implement database initialization and migration logic | 1.1.4 |

#### 1.2 Frontend Foundation

| Task | Description | Dependencies |
|------|-------------|--------------|
| 1.2.1 | Initialize Vue 3 + TypeScript project with Vite | None |
| 1.2.2 | Configure Tailwind CSS | 1.2.1 |
| 1.2.3 | Setup shadcn-vue components | 1.2.2 |
| 1.2.4 | Configure Vue Router with 7 routes | 1.2.1 |
| 1.2.5 | Setup Pinia stores structure | 1.2.1 |
| 1.2.6 | Create dark theme configuration | 1.2.2 |
| 1.2.7 | Implement Sidebar layout component | 1.2.3, 1.2.6 |

#### 1.3 Integration

| Task | Description | Dependencies |
|------|-------------|--------------|
| 1.3.1 | Create app.py entry point script | 1.1.6, 1.2.1 |
| 1.3.2 | Implement browser auto-open functionality | 1.3.1 |
| 1.3.3 | Configure static file serving for production | 1.3.1 |
| 1.3.4 | Verify single command startup works | 1.3.2, 1.3.3 |

**Deliverables**:
- Working project structure
- Empty application shell with sidebar navigation
- Single command startup functional
- Database schema created

---

### Phase 2: Core API Development

**Priority**: Primary Goal

#### 2.1 Library API & Service

| Task | Description | Dependencies |
|------|-------------|--------------|
| 2.1.1 | Implement LibraryService (CRUD operations) | Phase 1 |
| 2.1.2 | Create library API routes | 2.1.1 |
| 2.1.3 | Write unit tests for LibraryService | 2.1.1 |
| 2.1.4 | Test API endpoints with pytest | 2.1.2 |

#### 2.2 Projects API & Service

| Task | Description | Dependencies |
|------|-------------|--------------|
| 2.2.1 | Implement ProjectService (Project CRUD) | Phase 1 |
| 2.2.2 | Implement ComponentService (Component CRUD) | 2.2.1 |
| 2.2.3 | Create projects API routes | 2.2.1, 2.2.2 |
| 2.2.4 | Handle both old and new JSON format imports | 2.2.1 |
| 2.2.5 | Write unit tests for ProjectService | 2.2.1 |
| 2.2.6 | Write unit tests for ComponentService | 2.2.2 |

#### 2.3 Deployments API & Service

| Task | Description | Dependencies |
|------|-------------|--------------|
| 2.3.1 | Implement DeploymentService | Phase 1 |
| 2.3.2 | Implement duplicate detection logic | 2.3.1 |
| 2.3.3 | Create deployments API routes | 2.3.1 |
| 2.3.4 | Implement monthly deployment queries | 2.3.1 |
| 2.3.5 | Implement deployment statistics | 2.3.4 |
| 2.3.6 | Write unit tests | 2.3.1 |

#### 2.4 Formatter Service

| Task | Description | Dependencies |
|------|-------------|--------------|
| 2.4.1 | Port JiraFormatter to Python service | 2.3.1 |
| 2.4.2 | Port TeamsFormatter to Python service | 2.3.1 |
| 2.4.3 | Create format API endpoints | 2.4.1, 2.4.2 |
| 2.4.4 | Verify output matches original exactly | 2.4.3 |

#### 2.5 Settings API

| Task | Description | Dependencies |
|------|-------------|--------------|
| 2.5.1 | Implement SettingsService | Phase 1 |
| 2.5.2 | Create settings API routes | 2.5.1 |
| 2.5.3 | Write unit tests | 2.5.1 |

**Deliverables**:
- All CRUD APIs functional
- Unit test coverage > 85%
- API documentation (auto-generated via FastAPI)

---

### Phase 3: Excel Integration

**Priority**: Primary Goal

#### 3.1 Excel Service

| Task | Description | Dependencies |
|------|-------------|--------------|
| 3.1.1 | Port ExcelManager.add_deployment() | Phase 2 |
| 3.1.2 | Port ExcelManager.get_monthly_deployments() | 3.1.1 |
| 3.1.3 | Port ExcelManager.get_deployment_stats() | 3.1.2 |
| 3.1.4 | Port ExcelManager.check_duplicate_deployment() | 3.1.1 |
| 3.1.5 | Port ExcelManager.log_history() | 3.1.1 |
| 3.1.6 | Implement combined Excel export | 3.1.2 |

#### 3.2 Export Integration

| Task | Description | Dependencies |
|------|-------------|--------------|
| 3.2.1 | Create reports export API endpoint | 3.1.6 |
| 3.2.2 | Configure file download responses | 3.2.1 |
| 3.2.3 | Test Excel file compatibility | 3.2.1 |

**Deliverables**:
- Excel export functional
- Output compatible with original PyQt5 format
- Dual write (SQLite + Excel) operational

---

### Phase 4: Frontend Views Implementation

**Priority**: Primary Goal

#### 4.1 API Client & Stores

| Task | Description | Dependencies |
|------|-------------|--------------|
| 4.1.1 | Create TypeScript API client | Phase 3 |
| 4.1.2 | Implement deploymentStore | 4.1.1 |
| 4.1.3 | Implement projectStore | 4.1.1 |
| 4.1.4 | Implement libraryStore | 4.1.1 |
| 4.1.5 | Implement settingsStore | 4.1.1 |

#### 4.2 Deployment View

| Task | Description | Dependencies |
|------|-------------|--------------|
| 4.2.1 | Create ProjectSelector component | 4.1.2, 4.1.3 |
| 4.2.2 | Create DeploymentForm component | 4.2.1 |
| 4.2.3 | Implement auto-fill logic | 4.2.2 |
| 4.2.4 | Create CopyButtons component | 4.2.2 |
| 4.2.5 | Implement clipboard functionality | 4.2.4 |
| 4.2.6 | Integrate duplicate detection warning | 4.2.2 |
| 4.2.7 | Create DeploymentView page | 4.2.2, 4.2.4 |

#### 4.3 Projects View

| Task | Description | Dependencies |
|------|-------------|--------------|
| 4.3.1 | Create ProjectList component | 4.1.3 |
| 4.3.2 | Create ProjectForm component | 4.3.1 |
| 4.3.3 | Create ComponentDialog modal | 4.3.2 |
| 4.3.4 | Implement component table with actions | 4.3.3 |
| 4.3.5 | Create ProjectsView page | 4.3.2, 4.3.4 |

#### 4.4 Library View

| Task | Description | Dependencies |
|------|-------------|--------------|
| 4.4.1 | Create LibrarySection component | 4.1.4 |
| 4.4.2 | Implement add/remove dialogs | 4.4.1 |
| 4.4.3 | Create LibraryView page | 4.4.2 |

#### 4.5 History View

| Task | Description | Dependencies |
|------|-------------|--------------|
| 4.5.1 | Create DeploymentTable component | 4.1.2 |
| 4.5.2 | Create DeploymentDetails component | 4.5.1 |
| 4.5.3 | Implement row selection and copy | 4.5.2 |
| 4.5.4 | Create HistoryView page | 4.5.3 |

#### 4.6 Settings View

| Task | Description | Dependencies |
|------|-------------|--------------|
| 4.6.1 | Create SettingsForm component | 4.1.5 |
| 4.6.2 | Implement directory picker (file input) | 4.6.1 |
| 4.6.3 | Create SettingsView page | 4.6.2 |

#### 4.7 About View

| Task | Description | Dependencies |
|------|-------------|--------------|
| 4.7.1 | Create AboutView page | None |

**Deliverables**:
- All 7 views functional
- Feature parity with PyQt5 application
- Dark theme applied consistently

---

### Phase 5: Reports & PDF Generation

**Priority**: Secondary Goal

#### 5.1 Reports API

| Task | Description | Dependencies |
|------|-------------|--------------|
| 5.1.1 | Create reports summary endpoint | Phase 2 |
| 5.1.2 | Create reports statistics endpoint | 5.1.1 |

#### 5.2 PDF Service

| Task | Description | Dependencies |
|------|-------------|--------------|
| 5.2.1 | Port PDFGenerator to backend service | Phase 3 |
| 5.2.2 | Port chart generation (matplotlib) | 5.2.1 |
| 5.2.3 | Create PDF generation API endpoint | 5.2.2 |
| 5.2.4 | Implement async PDF generation with progress | 5.2.3 |

#### 5.3 Reports View

| Task | Description | Dependencies |
|------|-------------|--------------|
| 5.3.1 | Create SummaryCards component | 5.1.1 |
| 5.3.2 | Create DeploymentsTab component | 5.1.2 |
| 5.3.3 | Create StatisticsTab component | 5.1.2 |
| 5.3.4 | Implement month/year selector | 5.3.1 |
| 5.3.5 | Create export buttons (Excel/PDF) | 5.2.3 |
| 5.3.6 | Implement PDF progress indicator | 5.2.4 |
| 5.3.7 | Create ReportsView page | 5.3.1-5.3.6 |

**Deliverables**:
- Reports view fully functional
- PDF generation with all charts
- Export functionality working

---

### Phase 6: Real-time & WebSocket

**Priority**: Secondary Goal

#### 6.1 WebSocket Backend

| Task | Description | Dependencies |
|------|-------------|--------------|
| 6.1.1 | Create WebSocket connection manager | Phase 1 |
| 6.1.2 | Implement broadcast mechanism | 6.1.1 |
| 6.1.3 | Integrate WebSocket with API endpoints | 6.1.2 |
| 6.1.4 | Add event broadcasting on data changes | 6.1.3 |

#### 6.2 WebSocket Frontend

| Task | Description | Dependencies |
|------|-------------|--------------|
| 6.2.1 | Create useWebSocket composable | 6.1.1 |
| 6.2.2 | Implement auto-reconnect logic | 6.2.1 |
| 6.2.3 | Create websocketStore | 6.2.2 |
| 6.2.4 | Integrate with existing stores | 6.2.3 |

**Deliverables**:
- Real-time updates across browser tabs
- Automatic reconnection on disconnect

---

### Phase 7: Data Migration

**Priority**: Secondary Goal

#### 7.1 Migration Service

| Task | Description | Dependencies |
|------|-------------|--------------|
| 7.1.1 | Implement JSON project file importer | Phase 2 |
| 7.1.2 | Handle old vs new JSON format detection | 7.1.1 |
| 7.1.3 | Implement library.json importer | Phase 2 |
| 7.1.4 | Implement settings.json importer | Phase 2 |
| 7.1.5 | Implement Excel deployment importer | Phase 3 |
| 7.1.6 | Create first-run migration trigger | 7.1.1-7.1.5 |

#### 7.2 Migration UI

| Task | Description | Dependencies |
|------|-------------|--------------|
| 7.2.1 | Create migration progress component | 7.1.6 |
| 7.2.2 | Add manual import option in Settings | 7.1.5 |

**Deliverables**:
- Automatic data migration on first run
- Manual import option available
- 100% data fidelity verification

---

### Phase 8: Testing & Polish

**Priority**: Final Goal

#### 8.1 Testing

| Task | Description | Dependencies |
|------|-------------|--------------|
| 8.1.1 | Complete backend unit tests (>85% coverage) | All Phases |
| 8.1.2 | Write frontend component tests | Phase 4 |
| 8.1.3 | Create E2E tests with Playwright | All Phases |
| 8.1.4 | Test cross-browser compatibility | 8.1.3 |
| 8.1.5 | Performance testing | 8.1.3 |

#### 8.2 Polish

| Task | Description | Dependencies |
|------|-------------|--------------|
| 8.2.1 | Add keyboard shortcuts | Phase 4 |
| 8.2.2 | Implement toast notifications | Phase 4 |
| 8.2.3 | Add loading indicators | Phase 4 |
| 8.2.4 | Implement form auto-save | Phase 4 |
| 8.2.5 | Responsive design adjustments | Phase 4 |

#### 8.3 Documentation

| Task | Description | Dependencies |
|------|-------------|--------------|
| 8.3.1 | Update README with web app instructions | All Phases |
| 8.3.2 | Create deployment guide | Phase 9 |

**Deliverables**:
- Full test coverage
- Polished user experience
- Complete documentation

---

### Phase 9: Docker & Deployment

**Priority**: Final Goal

#### 9.1 Docker Setup

| Task | Description | Dependencies |
|------|-------------|--------------|
| 9.1.1 | Create Dockerfile (multi-stage build) | All Phases |
| 9.1.2 | Create docker-compose.yml | 9.1.1 |
| 9.1.3 | Configure volume mounts for data persistence | 9.1.2 |
| 9.1.4 | Test Docker build and run | 9.1.3 |

#### 9.2 VPS Deployment

| Task | Description | Dependencies |
|------|-------------|--------------|
| 9.2.1 | Configure nginx reverse proxy (optional) | 9.1.4 |
| 9.2.2 | Document VPS deployment steps | 9.2.1 |

**Deliverables**:
- Working Docker image
- Deployment documentation

---

## 3. Technical Approach

### 3.1 Backend Architecture

```
┌─────────────────────────────────────────────────┐
│                   FastAPI App                   │
├─────────────────────────────────────────────────┤
│  Routes (API Layer)                             │
│  ├── /api/deployments                           │
│  ├── /api/projects                              │
│  ├── /api/library                               │
│  ├── /api/reports                               │
│  └── /api/settings                              │
├─────────────────────────────────────────────────┤
│  Services (Business Logic)                      │
│  ├── DeploymentService                          │
│  ├── ProjectService                             │
│  ├── LibraryService                             │
│  ├── ExcelService                               │
│  ├── PDFService                                 │
│  └── FormatterService                           │
├─────────────────────────────────────────────────┤
│  Models (SQLAlchemy ORM)                        │
│  ├── Project                                    │
│  ├── Component                                  │
│  ├── Deployment                                 │
│  ├── Library                                    │
│  └── Settings                                   │
├─────────────────────────────────────────────────┤
│  Database (SQLite)                              │
└─────────────────────────────────────────────────┘
```

### 3.2 Frontend Architecture

```
┌─────────────────────────────────────────────────┐
│                    Vue 3 App                    │
├─────────────────────────────────────────────────┤
│  Views (Pages)                                  │
│  ├── DeploymentView                             │
│  ├── ProjectsView                               │
│  ├── LibraryView                                │
│  ├── HistoryView                                │
│  ├── ReportsView                                │
│  ├── SettingsView                               │
│  └── AboutView                                  │
├─────────────────────────────────────────────────┤
│  Components                                     │
│  ├── Layout (Sidebar, Header)                   │
│  ├── Deployment (Form, Selector, CopyButtons)   │
│  ├── Projects (List, Form, ComponentDialog)     │
│  ├── Library (LibrarySection)                   │
│  ├── History (Table, Details)                   │
│  ├── Reports (Cards, Tabs)                      │
│  └── UI (shadcn-vue)                            │
├─────────────────────────────────────────────────┤
│  Stores (Pinia)                                 │
│  ├── deploymentStore                            │
│  ├── projectStore                               │
│  ├── libraryStore                               │
│  ├── settingsStore                              │
│  └── websocketStore                             │
├─────────────────────────────────────────────────┤
│  Composables                                    │
│  ├── useWebSocket                               │
│  ├── useClipboard                               │
│  └── useToast                                   │
├─────────────────────────────────────────────────┤
│  API Client                                     │
└─────────────────────────────────────────────────┘
```

### 3.3 Data Flow

```
User Action
    │
    ▼
Vue Component ──▶ Pinia Store ──▶ API Client
                                      │
                                      ▼
                              FastAPI Route
                                      │
                                      ▼
                              Service Layer
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
              SQLAlchemy         ExcelService     WebSocket
              (SQLite)           (Excel file)     (Broadcast)
                                                      │
                                                      ▼
                                              Other Browser Tabs
```

---

## 4. Risk Mitigation

### 4.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Excel format incompatibility | Medium | High | Test with existing files early; maintain original ExcelManager logic |
| Data migration errors | Medium | High | Implement validation checks; create backup before migration |
| WebSocket reliability | Low | Medium | Implement reconnection logic; fallback to polling if needed |
| Performance issues with large data | Low | Medium | Implement pagination; optimize database queries |

### 4.2 Implementation Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | Medium | Medium | Strict adherence to feature parity; defer enhancements |
| Integration issues | Medium | Medium | Incremental integration; continuous testing |
| Browser compatibility | Low | Medium | Test on all target browsers early |

---

## 5. Dependencies

### 5.1 Python Dependencies

```toml
[packages]
fastapi = ">=0.110.0"
uvicorn = {extras = ["standard"], version = ">=0.27.0"}
sqlalchemy = ">=2.0.0"
pydantic = ">=2.0.0"
python-multipart = "*"
openpyxl = ">=3.1.0"
reportlab = ">=4.0.0"
matplotlib = ">=3.8.0"
numpy = "*"
websockets = "*"

[dev-packages]
pytest = ">=8.0.0"
pytest-asyncio = "*"
httpx = "*"
```

### 5.2 Node.js Dependencies

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.0.0",
    "pinia": "^2.0.0",
    "@vueuse/core": "^10.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

---

## 6. Milestone Summary

| Milestone | Phases | Key Deliverables |
|-----------|--------|------------------|
| **M1: Foundation** | 1 | Project structure, empty shell, single command startup |
| **M2: APIs Complete** | 2-3 | All backend APIs, Excel integration |
| **M3: UI Complete** | 4 | All 7 views functional |
| **M4: Reports & Real-time** | 5-6 | Reports with PDF, WebSocket sync |
| **M5: Migration Ready** | 7 | Automatic data migration |
| **M6: Production Ready** | 8-9 | Testing complete, Docker deployment |

---

## 7. TAG Block

```
<!-- TAG:SPEC-WEB-MIGRATION-001-PLAN:START -->
Plan ID: SPEC-WEB-MIGRATION-001-PLAN
Version: 1.0.0
Status: draft
Created: 2025-11-26
Author: Alfred (spec-builder)
Parent SPEC: SPEC-WEB-MIGRATION-001
Total Phases: 9
Total Tasks: ~90
<!-- TAG:SPEC-WEB-MIGRATION-001-PLAN:END -->
```

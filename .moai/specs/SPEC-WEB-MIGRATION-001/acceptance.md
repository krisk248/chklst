---
id: SPEC-WEB-MIGRATION-001-ACCEPTANCE
version: 1.0.0
status: draft
created: 2025-11-26
updated: 2025-11-26
author: Alfred
parent_spec: SPEC-WEB-MIGRATION-001
---

# Acceptance Criteria: PyQt5 to Web Application Migration

## 1. Overview

This document defines the acceptance criteria and test scenarios for validating the successful migration of the chklst application from PyQt5 to a modern web application.

---

## 2. Application Startup

### AC-STARTUP-001: Single Command Startup

**Given** the user has Python 3.11+ and Node.js 20+ installed
**And** the user has run `pipenv install`
**When** the user runs `pipenv run python app.py`
**Then** the application SHALL start both backend and frontend servers
**And** the default browser SHALL open to `http://localhost:8000`
**And** the UI SHALL be displayed within 3 seconds

**Verification**:
- [ ] Command executes without errors
- [ ] Backend server starts on port 8000
- [ ] Browser opens automatically
- [ ] UI loads within 3 seconds
- [ ] Dark theme is applied correctly

### AC-STARTUP-002: Port Conflict Handling

**Given** port 8000 is already in use by another application
**When** the user runs `pipenv run python app.py`
**Then** the application SHALL display an error message
**And** the error SHALL suggest an alternative port or instructions

**Verification**:
- [ ] Clear error message displayed
- [ ] Application does not crash
- [ ] Instructions provided for resolution

### AC-STARTUP-003: Graceful Shutdown

**Given** the application is running
**When** the user presses Ctrl+C in the terminal
**Then** both servers SHALL shutdown gracefully
**And** no orphan processes SHALL remain

**Verification**:
- [ ] No error messages on shutdown
- [ ] Port 8000 is freed
- [ ] No zombie processes

---

## 3. Deployment Form

### AC-DEPLOY-001: Project Selection Auto-fill

**Given** projects exist in the database
**When** the user navigates to the Deployment page
**Then** the project dropdown SHALL be populated with all projects
**And** the first item SHALL be "-- Select Project --"

**Verification**:
- [ ] All projects from database appear in dropdown
- [ ] Projects are sorted alphabetically
- [ ] Default selection is placeholder text

### AC-DEPLOY-002: Component Population

**Given** the user has selected a project with multiple components
**When** the project selection changes
**Then** the component dropdown SHALL show only enabled components
**And** the first item SHALL be "-- Select Component --"

**Verification**:
- [ ] Only enabled components appear
- [ ] Disabled components are excluded
- [ ] Component names match project configuration

### AC-DEPLOY-003: Auto-fill Project Fields

**Given** the user has selected a project
**When** the project selection completes
**Then** the following fields SHALL be auto-filled as read-only:
  - Environment (from project.environment)
  - Build Server (from project.build_server)
  - Deploy Server (from project.deploy_server)
  - Database Name (from project.db_name)

**Verification**:
- [ ] All fields populated correctly
- [ ] Fields are read-only (cannot be edited)
- [ ] Fields clear when project is deselected

### AC-DEPLOY-004: Auto-fill Component Fields

**Given** the user has selected a component
**When** the component selection completes
**Then** the following fields SHALL be auto-filled as read-only:
  - Component Name
  - Developer Name
  - VCS URL

**Verification**:
- [ ] All fields populated from component data
- [ ] Fields are read-only
- [ ] Fields update when component changes

### AC-DEPLOY-005: Timestamp Now Button

**Given** the deployment form is displayed
**When** the user clicks the "Now" button
**Then** the timestamp field SHALL be set to the current date and time
**And** the format SHALL be "dd-MMM-yyyy h:mmAP" (e.g., "26-Nov-2025 3:30PM")

**Verification**:
- [ ] Timestamp updates to current time
- [ ] Format matches expected pattern
- [ ] Timezone is local system time

### AC-DEPLOY-006: Database Script Toggle

**Given** the deployment form is displayed
**When** the user selects "Yes" for DB Script
**Then** the Database Script input field SHALL become enabled
**When** the user selects "No" for DB Script
**Then** the Database Script input field SHALL become disabled and cleared

**Verification**:
- [ ] Field enables/disables correctly
- [ ] Field clears when disabled
- [ ] Value is preserved when re-enabled

### AC-DEPLOY-007: Save Deployment - Success

**Given** the user has filled all required fields:
  - Project selected
  - Component selected
  - Deployed By entered
**When** the user clicks "Save Deployment"
**Then** the deployment SHALL be saved to SQLite database
**And** the deployment SHALL be exported to Excel file
**And** a success notification SHALL be displayed
**And** Copy JIRA, Copy Teams, and Copy Both buttons SHALL be enabled

**Verification**:
- [ ] Record exists in SQLite deployments table
- [ ] Excel file created/updated in reports/{Month_Year}/{Project}.xlsx
- [ ] Excel row contains all deployment data
- [ ] Copy buttons are now clickable
- [ ] Form fields are partially reset (keep project/component)

### AC-DEPLOY-008: Save Deployment - Validation

**Given** the user has NOT selected a project
**When** the user clicks "Save Deployment"
**Then** the system SHALL display a validation error
**And** the deployment SHALL NOT be saved

**Given** the user has NOT entered "Deployed By"
**When** the user clicks "Save Deployment"
**Then** the system SHALL display a validation error
**And** the deployment SHALL NOT be saved

**Verification**:
- [ ] Clear error message for missing project
- [ ] Clear error message for missing component
- [ ] Clear error message for missing deployed by
- [ ] No database record created on validation failure

### AC-DEPLOY-009: Duplicate Detection - Same JIRA ID

**Given** a deployment exists with JIRA ID "PROJ-123" for project "TestProject" and component "Frontend"
**When** the user tries to save another deployment with JIRA ID "PROJ-123" for the same project and component
**Then** the system SHALL display a duplicate warning dialog
**And** the dialog SHALL show the existing deployment details
**And** the user SHALL be able to choose "Save Anyway" or "Cancel"

**Verification**:
- [ ] Warning dialog appears
- [ ] Existing deployment details shown (timestamp, JIRA ID)
- [ ] "Save Anyway" saves the deployment
- [ ] "Cancel" returns to form without saving

### AC-DEPLOY-010: Duplicate Detection - Time Proximity

**Given** a deployment exists for project "TestProject" and component "Backend" with JIRA ID "N/A" saved 3 minutes ago
**When** the user tries to save another deployment for the same project/component with JIRA ID "N/A"
**Then** the system SHALL display a duplicate warning dialog
**And** the reason SHALL indicate "within 5 minutes"

**Verification**:
- [ ] Warning triggers for deployments within 5 minutes
- [ ] No warning for deployments older than 5 minutes
- [ ] Only applies when both JIRA IDs are "N/A"

### AC-DEPLOY-011: Copy to JIRA

**Given** a deployment has been saved successfully
**When** the user clicks "Copy JIRA"
**Then** the clipboard SHALL contain a Markdown table formatted for JIRA
**And** the format SHALL match the existing PyQt5 output exactly

**Expected JIRA Format**:
```markdown
| Field | Value |
|-------|-------|
| JIRA Ticket | PROJ-123 |
| Project | TestProject - Frontend |
| Environment | QA |
| Timestamp | 26-Nov-2025 3:30PM |
| Build Server | 192.168.1.149 |
| Build | PASS |
| VCS URL | https://github.com/... |
| Deploy Server | 192.168.1.142 |
| Build Backup | C:\Backup\20251126 PASS |
| Deployment | PASS |
| Health Check | PASS |
| Deployed By | Kannan |
```

**Verification**:
- [ ] Clipboard contains valid Markdown table
- [ ] All fields present and correct
- [ ] Format matches original PyQt5 output character-for-character

### AC-DEPLOY-012: Copy to Teams

**Given** a deployment has been saved successfully
**When** the user clicks "Copy Teams"
**Then** the clipboard SHALL contain a formatted message with bullets and emojis
**And** the format SHALL match the existing PyQt5 output exactly

**Expected Teams Format**:
```
PATCH: PROJ-123 | TestProject - Deployment Complete

- Project: TestProject - Frontend
- Environment: QA
- URL: http://app.example.com
- Build Server: 192.168.1.149
- Build: PASS
- Git URL: https://github.com/...
- Deploy Server: 192.168.1.142
- Build Backup: C:\Backup\20251126 PASS
- Deployment: PASS
- Health Check: PASS
- Developer: John Doe
- Deployed By: Kannan
- Timestamp: 26-Nov-2025 3:30PM
```

**Verification**:
- [ ] Clipboard contains bulleted list
- [ ] Emojis present in header
- [ ] Format matches original PyQt5 output

### AC-DEPLOY-013: Copy Both

**Given** a deployment has been saved successfully
**When** the user clicks "Copy Both"
**Then** the clipboard SHALL contain both JIRA and Teams formats
**And** they SHALL be separated by a clear delimiter

**Verification**:
- [ ] Both formats present
- [ ] Clear separation between formats
- [ ] Each format independently correct

---

## 4. Projects Management

### AC-PROJECTS-001: Project List Display

**Given** multiple projects exist in the database
**When** the user navigates to the Projects page
**Then** the left panel SHALL display all projects sorted alphabetically
**And** no project SHALL be selected initially

**Verification**:
- [ ] All projects listed
- [ ] Alphabetical sorting
- [ ] Form panel shows empty/disabled state

### AC-PROJECTS-002: Create New Project

**Given** the user is on the Projects page
**When** the user clicks "+ New Project"
**And** enters "NewProject" in the dialog
**And** clicks OK
**Then** a new project SHALL be created with default structure
**And** the project SHALL appear in the list
**And** the project SHALL be selected automatically

**Verification**:
- [ ] Project created in database
- [ ] Appears in project list immediately
- [ ] Form populated with default values
- [ ] Empty components list

### AC-PROJECTS-003: Duplicate Project Prevention

**Given** a project named "ExistingProject" exists
**When** the user tries to create a project with the same name
**Then** the system SHALL display a duplicate warning
**And** the project SHALL NOT be created

**Verification**:
- [ ] Clear error message
- [ ] No duplicate record created

### AC-PROJECTS-004: Edit Project Details

**Given** the user has selected a project
**And** modifies the build server to "192.168.1.200"
**When** the user clicks "Save Project"
**Then** the project SHALL be updated in the database
**And** a success notification SHALL be displayed

**Verification**:
- [ ] Database record updated
- [ ] Changes persist on page refresh
- [ ] Success notification shown

### AC-PROJECTS-005: Delete Project

**Given** the user has selected a project with components
**When** the user clicks "Delete Project"
**Then** a confirmation dialog SHALL appear
**And** if confirmed, the project and all components SHALL be deleted
**And** associated deployment records SHALL remain (historical data)

**Verification**:
- [ ] Confirmation required
- [ ] Project removed from list
- [ ] Components cascade deleted
- [ ] Deployment history preserved

### AC-PROJECTS-006: Add Component

**Given** the user has selected a project
**When** the user clicks "+ Add Component"
**And** fills in component details (Name: "API Service", Developer: "John")
**And** clicks Save
**Then** the component SHALL be added to the project
**And** appear in the components table with enabled status

**Verification**:
- [ ] Component appears in table
- [ ] All fields saved correctly
- [ ] Toggle shows "ON" status

### AC-PROJECTS-007: Toggle Component

**Given** a project has a component with enabled=true
**When** the user clicks the toggle button
**Then** the component enabled status SHALL change to false
**And** the toggle SHALL show "OFF"
**And** the change SHALL be persisted immediately

**Verification**:
- [ ] Visual toggle updates
- [ ] Database record updated
- [ ] Component excluded from deployment dropdown when OFF

### AC-PROJECTS-008: Edit Component

**Given** a project has components
**When** the user clicks "Edit" on a component
**Then** a dialog SHALL appear with current component data
**When** the user modifies and saves
**Then** the component SHALL be updated

**Verification**:
- [ ] Dialog pre-populated with existing data
- [ ] Changes saved to database
- [ ] Table updates to reflect changes

### AC-PROJECTS-009: Remove Component

**Given** a project has multiple components
**When** the user clicks "Remove" on a component
**Then** a confirmation dialog SHALL appear
**And** if confirmed, the component SHALL be removed from the project

**Verification**:
- [ ] Confirmation required
- [ ] Component removed from table
- [ ] Database record deleted

---

## 5. Library/Presets

### AC-LIBRARY-001: Display All Sections

**Given** the user navigates to the Library page
**Then** four sections SHALL be displayed:
  - Developers
  - Build Servers
  - Deploy Servers
  - Environments

**Verification**:
- [ ] All four sections visible
- [ ] Each section shows current items

### AC-LIBRARY-002: Add Developer

**Given** the user is viewing the Developers section
**When** the user clicks "+ Add Developer"
**And** enters "Jane Doe"
**Then** "Jane Doe" SHALL appear in the developers list
**And** SHALL be available in project component dropdowns

**Verification**:
- [ ] Item added to list
- [ ] Database updated
- [ ] Available in component developer dropdown

### AC-LIBRARY-003: Prevent Duplicate

**Given** "Kannan" exists in the developers list
**When** the user tries to add "Kannan" again
**Then** a duplicate warning SHALL be displayed
**And** the item SHALL NOT be added

**Verification**:
- [ ] Duplicate detected
- [ ] Warning message shown
- [ ] List unchanged

### AC-LIBRARY-004: Remove Item

**Given** multiple items exist in the Build Servers list
**When** the user selects "192.168.1.149"
**And** clicks "Remove Selected"
**Then** a confirmation dialog SHALL appear
**And** if confirmed, "192.168.1.149" SHALL be removed

**Verification**:
- [ ] Confirmation required
- [ ] Item removed from list
- [ ] Database updated

### AC-LIBRARY-005: Real-time Update

**Given** the Library page is open in two browser tabs
**When** the user adds a developer in Tab 1
**Then** the developers list in Tab 2 SHALL update automatically

**Verification**:
- [ ] WebSocket event triggered
- [ ] Other tabs receive update
- [ ] List refreshes without manual action

---

## 6. History/Last Saved

### AC-HISTORY-001: Display Recent Deployments

**Given** deployments exist for the current month
**When** the user navigates to the History page
**Then** up to 50 most recent deployments SHALL be displayed
**And** sorted by timestamp (newest first)

**Verification**:
- [ ] Deployments from current month shown
- [ ] Maximum 50 rows
- [ ] Newest at top

### AC-HISTORY-002: Select Deployment

**Given** the deployments table is displayed
**When** the user clicks on a deployment row
**Then** the row SHALL be highlighted
**And** the details panel SHALL show full deployment information
**And** Copy buttons SHALL be enabled

**Verification**:
- [ ] Row highlight on selection
- [ ] Details panel populated
- [ ] All deployment fields visible
- [ ] Copy buttons enabled

### AC-HISTORY-003: Copy from History

**Given** a deployment is selected in the history table
**When** the user clicks "Copy for JIRA"
**Then** the JIRA-formatted text SHALL be copied to clipboard

**Verification**:
- [ ] Clipboard contains correct format
- [ ] Success notification shown

### AC-HISTORY-004: Refresh Data

**Given** the History page is displayed
**When** the user clicks "Refresh"
**Then** the deployments list SHALL reload from database
**And** any new deployments SHALL appear

**Verification**:
- [ ] Data reloads
- [ ] New deployments visible
- [ ] No page flicker

---

## 7. Reports

### AC-REPORTS-001: Month/Year Selection

**Given** the user is on the Reports page
**When** the user changes the month to "October" and year to "2025"
**Then** all report data SHALL reload for October 2025

**Verification**:
- [ ] Summary cards update
- [ ] Deployments table updates
- [ ] Statistics update

### AC-REPORTS-002: Summary Cards

**Given** deployments exist for the selected month
**When** the Reports page loads
**Then** three summary cards SHALL display:
  - Total Deployments (count)
  - Success Rate (percentage)
  - Active Projects (count)

**Verification**:
- [ ] Correct total count
- [ ] Correct success rate calculation
- [ ] Correct project count

### AC-REPORTS-003: Deployments Tab Filter

**Given** the Deployments tab is active
**When** the user selects "TestProject" from the project filter
**Then** only deployments for "TestProject" SHALL be displayed

**Verification**:
- [ ] Filter works correctly
- [ ] "All Projects" shows all
- [ ] Table updates immediately

### AC-REPORTS-004: Export Excel

**Given** deployments exist for November 2025
**When** the user clicks "Export Excel"
**Then** a combined Excel file SHALL be downloaded
**And** the file SHALL contain all deployments for November 2025
**And** the format SHALL match the existing Excel format

**Verification**:
- [ ] File downloads
- [ ] Contains all projects' deployments
- [ ] Headers match existing format
- [ ] Data values correct

### AC-REPORTS-005: Generate PDF

**Given** deployments exist for November 2025
**When** the user clicks "Generate PDF"
**Then** a progress indicator SHALL appear
**And** a PDF report SHALL be generated
**And** the PDF SHALL contain charts and statistics

**Verification**:
- [ ] Progress bar shown during generation
- [ ] PDF downloads successfully
- [ ] Contains title page
- [ ] Contains executive summary
- [ ] Contains charts (timeline, day of week, etc.)
- [ ] Contains JIRA compliance section

---

## 8. Settings

### AC-SETTINGS-001: Default Deployed By

**Given** the user sets "John Doe" as the default Deployed By
**And** clicks "Save Settings"
**When** the user navigates to the Deployment page
**Then** the Deployed By dropdown SHALL have "John Doe" pre-selected

**Verification**:
- [ ] Setting saved to database
- [ ] Pre-fills deployment form
- [ ] Persists across sessions

### AC-SETTINGS-002: Export Path

**Given** the user sets export path to "/home/user/exports"
**And** clicks "Save Settings"
**When** a deployment is saved
**Then** the Excel file SHALL be created in "/home/user/exports"

**Verification**:
- [ ] Path saved correctly
- [ ] Directory created if not exists
- [ ] Excel files use the configured path

---

## 9. Data Migration

### AC-MIGRATION-001: First Run Detection

**Given** this is the first time running the web application
**And** no SQLite database exists
**When** the application starts
**Then** the system SHALL detect existing legacy files:
  - projects/*.json
  - library.json
  - settings.json
  - reports/{Month_Year}/*.xlsx

**Verification**:
- [ ] All legacy files detected
- [ ] Count reported to user

### AC-MIGRATION-002: Project JSON Import

**Given** legacy project files exist in projects/ directory
**When** migration runs
**Then** all projects SHALL be imported to SQLite
**And** both old format (dict components) and new format (list components) SHALL be handled
**And** all component data SHALL be preserved

**Verification**:
- [ ] All projects imported
- [ ] Component count matches
- [ ] All fields migrated correctly

### AC-MIGRATION-003: Excel Deployment Import

**Given** Excel files exist in reports/{Month_Year}/ directories
**When** migration runs
**Then** all deployments SHALL be imported to SQLite
**And** no duplicate records SHALL be created
**And** all fields SHALL be preserved

**Verification**:
- [ ] All deployments imported
- [ ] No duplicates
- [ ] Data matches source Excel

### AC-MIGRATION-004: Migration Verification

**Given** migration has completed
**When** the user views any page
**Then** all data SHALL match the original PyQt5 application

**Verification**:
- [ ] Project count matches
- [ ] Component count matches
- [ ] Deployment count matches
- [ ] Library items match
- [ ] Settings match

---

## 10. Real-time Synchronization

### AC-REALTIME-001: Deployment Broadcast

**Given** the application is open in two browser tabs
**When** a deployment is saved in Tab 1
**Then** the History page in Tab 2 SHALL update automatically (if viewing)
**And** the Reports page in Tab 2 SHALL reflect the new deployment

**Verification**:
- [ ] WebSocket event sent
- [ ] Other tabs receive event
- [ ] UI updates without refresh

### AC-REALTIME-002: Reconnection

**Given** the WebSocket connection is lost
**When** the server becomes available again
**Then** the client SHALL reconnect automatically
**And** no user action SHALL be required

**Verification**:
- [ ] Auto-reconnect attempts
- [ ] Exponential backoff implemented
- [ ] Connection restored successfully

---

## 11. Non-Functional Acceptance

### AC-NFR-001: Performance

| Metric | Acceptance Criteria | Verification |
|--------|---------------------|--------------|
| Startup time | < 3 seconds | [ ] Measured |
| Page navigation | < 200ms | [ ] Measured |
| Form submission | < 500ms | [ ] Measured |
| Excel export (1000 records) | < 5 seconds | [ ] Measured |
| PDF generation | < 30 seconds | [ ] Measured |

### AC-NFR-002: Browser Compatibility

| Browser | Version | Verification |
|---------|---------|--------------|
| Chrome | Latest 2 | [ ] Tested |
| Firefox | Latest 2 | [ ] Tested |
| Edge | Latest 2 | [ ] Tested |
| Safari | Latest 2 | [ ] Tested |

### AC-NFR-003: Dark Theme

**Given** the application loads
**Then** the UI SHALL use dark theme colors:
  - Background: #1e1e2e (or similar dark)
  - Text: #ecf0f1 (light)
  - Accent: #4a9eff (blue)

**Verification**:
- [ ] Consistent dark theme across all pages
- [ ] No bright/white elements
- [ ] Good contrast for readability

---

## 12. Definition of Done

A feature is considered DONE when:

1. [ ] All acceptance criteria for the feature pass
2. [ ] Unit tests written and passing (backend)
3. [ ] Component tests written and passing (frontend)
4. [ ] No regression in existing functionality
5. [ ] Code reviewed and merged
6. [ ] Dark theme applied correctly
7. [ ] Works in all target browsers
8. [ ] Performance requirements met
9. [ ] No console errors or warnings

---

## 13. Quality Gate Criteria

### Phase Completion Gates

| Phase | Gate Criteria |
|-------|---------------|
| Phase 1 | Application starts, displays empty UI, sidebar works |
| Phase 2 | All API endpoints respond correctly, 85% test coverage |
| Phase 3 | Excel export creates valid files, matches original format |
| Phase 4 | All 7 views functional, feature parity achieved |
| Phase 5 | Reports display correctly, PDF generates successfully |
| Phase 6 | Real-time updates work across tabs |
| Phase 7 | All legacy data migrated with 100% accuracy |
| Phase 8 | All tests pass, no critical bugs |
| Phase 9 | Docker image builds and runs successfully |

### Final Release Gate

- [ ] All phase gates passed
- [ ] Full E2E test suite passes
- [ ] Performance benchmarks met
- [ ] No P1 or P2 bugs outstanding
- [ ] Documentation complete
- [ ] Data migration verified with production data copy

---

## 14. TAG Block

```
<!-- TAG:SPEC-WEB-MIGRATION-001-ACCEPTANCE:START -->
Acceptance ID: SPEC-WEB-MIGRATION-001-ACCEPTANCE
Version: 1.0.0
Status: draft
Created: 2025-11-26
Author: Alfred (spec-builder)
Parent SPEC: SPEC-WEB-MIGRATION-001
Total Test Scenarios: 50+
Coverage Areas: Startup, Deployment, Projects, Library, History, Reports, Settings, Migration, Real-time
<!-- TAG:SPEC-WEB-MIGRATION-001-ACCEPTANCE:END -->
```

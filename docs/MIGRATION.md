# Data Migration - Phase 7

This document describes the data migration service for importing existing data from JSON and Excel files into the SQLite database.

## Overview

The migration service automatically imports data from:

1. **Projects** (`projects/*.json`) - Project definitions with components
2. **Components** (defined in project JSON files) - Component configurations
3. **Deployments** (`reports/**/*.xlsx`) - Deployment records from Excel files
4. **Library Presets** (`library.json`) - Dropdown options for developers, servers, environments
5. **Settings** (`settings.json`) - Application configuration

## Architecture

### Components

#### MigrationService (`backend/services/migration_service.py`)

Core service handling all data import operations:

```python
class MigrationService:
    def __init__(self)

    # Main entry point
    async def run_full_migration() -> Dict[str, Any]

    # Individual import methods
    async def _import_library(db: AsyncSession) -> None
    async def _import_settings(db: AsyncSession) -> None
    async def _import_projects(db: AsyncSession) -> Tuple[int, int]
    async def _import_deployments(db: AsyncSession) -> int

    # Utility methods
    async def _parse_timestamp(timestamp_value: Any) -> datetime
    def _parse_status(status_value: Any) -> bool
    def _parse_status_string(status_value: Any) -> str

    # Flag management
    def check_migration_needed() -> bool
    def mark_migration_complete() -> None
```

#### API Routes (`backend/api/routes/migration.py`)

REST endpoints for managing migration:

- `POST /api/v1/migration/run` - Execute migration
- `GET /api/v1/migration/status` - Check migration status
- `GET /api/v1/migration/preview` - Preview what will be migrated
- `POST /api/v1/migration/reset` - Reset migration flag (dev only)

#### Startup Integration (`backend/main.py`)

Migration automatically runs on application startup if needed.

## Data Flow

### 1. Project Import

**Input**: `projects/*.json`

**Process**:
- Read each JSON file
- Extract project metadata
- Import components (supports both dict and list formats)
- Create relationships between projects and components

**Example Project JSON** (dict-based components):
```json
{
  "project_name": "BRHUB",
  "build_server": "192.168.1.149",
  "deploy_server": "192.168.1.60->192.168.14.8",
  "db_name": "BR_HUB_QA",
  "environment": "QA",
  "components": {
    "frontend": {
      "enabled": true,
      "component_name": "BR-IWS",
      "developer_name": "Kaarthiga Ayyappan",
      "vcs_type": "Git",
      "vcs_url": "https://github.com/TTS-FZLLC/...",
      "build_command": "ng"
    },
    "backend": { ... }
  }
}
```

**Example Project JSON** (list-based components):
```json
{
  "project_name": "ADX-SIP",
  "components": [
    {
      "enabled": true,
      "component_name": "ADX-SIP",
      "developer_name": "Kaarthiga Ayyappan",
      "vcs_type": "SVN",
      "vcs_url": "https://dic.ttsme.net/SVN2/..."
    },
    { ... }
  ]
}
```

**Output**: Projects and Components in database

### 2. Library Import

**Input**: `library.json`

**Process**:
- Read JSON file
- Extract arrays for developers, build servers, deploy servers, environments
- Store as JSON in Library table for use in dropdowns

**Example**:
```json
{
  "developers": ["Kannan", "Irfan", "Syed", ...],
  "build_servers": ["192.168.1.149", "192.168.1.136"],
  "deploy_servers": ["192.168.1.142"],
  "environments": ["QA"]
}
```

**Output**: Library record in database

### 3. Settings Import

**Input**: `settings.json`

**Process**:
- Read JSON file
- Store each setting as individual AppSettings record
- Use for application configuration

**Example**:
```json
{
  "deployed_by_default": "Kannan",
  "excel_export_path": "/home/kannan/projects/active/chklst/reports"
}
```

**Output**: AppSettings records in database

### 4. Deployment Import

**Input**: `reports/{Month}_{Year}/*.xlsx`

**Process**:
1. Find all month folders (Nov_2025, Oct_2025, etc.)
2. Read each Excel file
3. Parse "Deployments" sheet
4. Extract headers from row 1
5. Process data rows 2+
6. Parse timestamps (supports multiple formats)
7. Parse status values (success/failed/pending)
8. Lookup project and component by name
9. Create Deployment records with proper relationships

**Excel Headers Expected**:
```
JIRA PATCH ID | Timestamp | Project Name | Component Name | Environment
SVN/GIT URL | Developer Name | Build Server | Deploy Server | Database Name
DB Backup Location | Database Script | Previous Build Backup | Build Status
Deploy Status | Notes | Deployed By
```

**Timestamp Formats Supported**:
- `%d-%b-%Y %I:%M%p` (15-Jan-2025 10:30AM)
- `%Y-%m-%d %H:%M:%S` (2025-01-15 10:30:00)
- `%d/%m/%Y %H:%M:%S` (15/01/2025 10:30:00)
- `%m/%d/%Y %H:%M:%S` (01/15/2025 10:30:00)

**Status Values Mapped**:
- Success: "success", "true", "1", "pass", "completed", "yes" → "success"
- Failed: "failed", "failure", "false", "0", "error" → "failed"
- Default: "pending"

**Output**: Deployment records in database

## Usage

### Automatic Migration (Startup)

Migration runs automatically when application starts:

```
Starting up...
Database initialized
Running data migration from existing files...
Migration completed successfully:
  - Projects: 13
  - Components: 47
  - Deployments: 286
  - Library: True
  - Settings: True
```

### Manual Migration via API

```bash
# Check status
curl http://localhost:8000/api/v1/migration/status

# Preview what will be imported
curl http://localhost:8000/api/v1/migration/preview

# Run migration
curl -X POST http://localhost:8000/api/v1/migration/run

# Reset migration flag (development only)
curl -X POST http://localhost:8000/api/v1/migration/reset
```

### REST API Details

#### 1. Check Migration Status

```bash
GET /api/v1/migration/status
```

**Response**:
```json
{
  "migration_needed": false,
  "migration_flag_exists": true,
  "data_sources": {
    "projects": {
      "exists": true,
      "file_count": 13,
      "files": ["BRHUB.json", "ADX-SIP.json", ...],
      "path": "/home/kannan/Projects/Active/chklst/projects"
    },
    "deployments": {
      "exists": true,
      "file_count": 142,
      "files": ["Nov_2025/BRHUB.xlsx", ...],
      "path": "/home/kannan/Projects/Active/chklst/reports"
    },
    "library": {
      "exists": true,
      "path": "/home/kannan/Projects/Active/chklst/library.json"
    },
    "settings": {
      "exists": true,
      "path": "/home/kannan/Projects/Active/chklst/settings.json"
    }
  }
}
```

#### 2. Preview Migration

```bash
GET /api/v1/migration/preview
```

**Response**:
```json
{
  "preview": {
    "projects": 13,
    "components": 47,
    "deployments": 286,
    "library": true,
    "settings": true
  },
  "sources": {
    "projects_directory": "/home/kannan/Projects/Active/chklst/projects",
    "reports_directory": "/home/kannan/Projects/Active/chklst/reports",
    "library_file": "/home/kannan/Projects/Active/chklst/library.json",
    "settings_file": "/home/kannan/Projects/Active/chklst/settings.json"
  }
}
```

#### 3. Run Migration

```bash
POST /api/v1/migration/run
```

**Response** (Success):
```json
{
  "status": "complete",
  "message": "Migration completed",
  "results": {
    "projects_imported": 13,
    "components_imported": 47,
    "deployments_imported": 286,
    "library_imported": true,
    "settings_imported": true
  },
  "errors": [],
  "flag_location": "/home/kannan/Projects/Active/chklst/data/.migration_complete"
}
```

**Response** (With Errors):
```json
{
  "status": "partial",
  "message": "Migration completed with errors",
  "results": {
    "projects_imported": 13,
    "components_imported": 45,
    "deployments_imported": 280,
    "library_imported": true,
    "settings_imported": false
  },
  "errors": [
    "Settings import failed: settings.json not found"
  ]
}
```

#### 4. Reset Migration Flag

```bash
POST /api/v1/migration/reset
```

**Response**:
```json
{
  "status": "success",
  "message": "Migration flag removed. Migration can be run again.",
  "warning": "This does not clear existing database records."
}
```

## Data Mapping

### Projects

| JSON Field | Database Column |
|-----------|-----------------|
| project_name | name |
| build_server | build_server |
| deploy_server | deploy_server |
| db_name | database_name |
| environment | environment |
| backup_location | backup_location |

### Components

| JSON Field | Database Column |
|-----------|-----------------|
| component_name | name |
| developer_name | developer |
| vcs_type | vcs_type |
| vcs_url | vcs_url |
| build_command | build_command |
| component_url | component_url |
| enabled | enabled |

### Deployments

| Excel Column | Database Column |
|-------------|-----------------|
| JIRA PATCH ID | jira_id |
| Timestamp | timestamp |
| Project Name | project_id (lookup) |
| Component Name | component_id (lookup) |
| Environment | environment |
| SVN/GIT URL | vcs_url |
| Developer Name | developer_name |
| Build Server | build_server |
| Deploy Server | deploy_server |
| Database Name | database_name |
| DB Backup Location | db_backup_location |
| Database Script | database_script |
| Previous Build Backup | previous_build_backup |
| Build Status | build_status (parsed) |
| Deploy Status | deploy_status (parsed) |
| Notes | notes |
| Deployed By | deployed_by |

## Error Handling

The migration service is resilient:

1. **Single file errors** - Skips that file and continues
2. **Missing files** - Logs warning and continues
3. **Invalid JSON/Excel** - Logs error and continues
4. **Missing relationships** - Uses NULL for missing foreign keys, logs warning
5. **Duplicate jira_id** - Handled by unique constraint

All errors are collected and returned in the response.

## Migration Flag

A flag file `/data/.migration_complete` indicates migration status:

- **Exists** - Migration already done, won't run again
- **Missing** - Migration needed, will run on startup

This prevents re-importing data on every restart.

## Testing

Run tests with:

```bash
pytest tests/test_migration_service.py -v
```

### Test Coverage

- Library import from JSON
- Settings import from JSON
- Projects import from JSON (dict and list formats)
- Components creation and linking
- Deployments import from Excel
- Status and timestamp parsing
- Full migration workflow
- Error handling
- Data preservation
- Migration flag management

## Performance

- **13 Projects**: ~200ms
- **47 Components**: ~300ms
- **286 Deployments**: ~2-3 seconds
- **Total Migration**: ~3-4 seconds on first startup

## Future Enhancements

1. **Batch Import Progress** - Show progress during large imports
2. **Selective Import** - Import only specific projects/months
3. **Incremental Updates** - Update existing records instead of skipping
4. **Export** - Create export functionality for backup
5. **Validation** - Enhanced validation before import
6. **Scheduling** - Periodic auto-import from source files
7. **Audit Trail** - Track what was imported and when

## Troubleshooting

### Migration Not Running

**Problem**: Flag file exists but migration needed

**Solution**: Delete flag file and restart:
```bash
rm data/.migration_complete
# Restart application
```

### Projects Not Imported

**Problem**: Projects JSON files not found

**Check**:
1. Ensure `projects/` directory exists
2. Verify JSON files are in correct format
3. Check file permissions
4. Review logs for errors

### Deployments Not Imported

**Problem**: Excel files not found or wrong sheet name

**Check**:
1. Ensure `reports/` directory exists with month folders
2. Verify sheet name is exactly "Deployments"
3. Check headers are on row 1
4. Review logs for parsing errors

## Files

- **Service**: `/backend/services/migration_service.py`
- **Routes**: `/backend/api/routes/migration.py`
- **Tests**: `/tests/test_migration_service.py`
- **Main**: `/backend/main.py` (startup integration)

## Dependencies

- `openpyxl` - Excel file reading
- `sqlalchemy` - ORM and async database
- `fastapi` - REST API framework
- `json` - JSON file handling

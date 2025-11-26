# Phase 2 API Usage Examples

## Overview
This document provides practical examples for using the Phase 2 API endpoints.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Not yet implemented (Phase 3+)

## Content-Type
All requests should use `application/json`

---

## Projects API

### Create a Project
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App",
    "build_server": "192.168.1.149",
    "deploy_server": "192.168.1.150",
    "database_name": "mobile_db",
    "environment": "QA",
    "backup_location": "/backups/mobile",
    "description": "Mobile application backend"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Mobile App",
  "build_server": "192.168.1.149",
  "deploy_server": "192.168.1.150",
  "database_name": "mobile_db",
  "environment": "QA",
  "backup_location": "/backups/mobile",
  "description": "Mobile application backend",
  "created_at": "2024-11-26T10:30:00",
  "updated_at": "2024-11-26T10:30:00",
  "components": []
}
```

### List All Projects
```bash
curl http://localhost:8000/api/v1/projects?skip=0&limit=10
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Mobile App",
    "environment": "QA",
    "created_at": "2024-11-26T10:30:00"
  },
  {
    "id": 2,
    "name": "Web App",
    "environment": "Production",
    "created_at": "2024-11-26T10:35:00"
  }
]
```

### Get Specific Project
```bash
curl http://localhost:8000/api/v1/projects/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Mobile App",
  "build_server": "192.168.1.149",
  "deploy_server": "192.168.1.150",
  "database_name": "mobile_db",
  "environment": "QA",
  "backup_location": "/backups/mobile",
  "description": "Mobile application backend",
  "created_at": "2024-11-26T10:30:00",
  "updated_at": "2024-11-26T10:30:00",
  "components": []
}
```

### Update Project
```bash
curl -X PUT http://localhost:8000/api/v1/projects/1 \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "UAT",
    "deploy_server": "192.168.1.151"
  }'
```

### Delete Project
```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1
```

**Response (204 No Content):** (empty body)

---

## Deployments API

### Create a Deployment
```bash
curl -X POST http://localhost:8000/api/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "jira_id": "PATCH-001",
    "project_id": 1,
    "component_id": 1,
    "environment": "QA",
    "vcs_url": "https://github.com/company/mobile-app.git",
    "developer_name": "John Doe",
    "build_server": "192.168.1.149",
    "deploy_server": "192.168.1.150",
    "database_name": "mobile_db",
    "db_backup_location": "/backups/mobile/2024-11-26.sql",
    "database_script": "UPDATE users SET status=1",
    "previous_build_backup": "/backups/builds/app-v1.2.3.war",
    "build_status": "success",
    "deploy_status": "pending",
    "notes": "Hotfix for login issue",
    "deployed_by": "Admin User"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "jira_id": "PATCH-001",
  "timestamp": "2024-11-26T10:45:00",
  "project_id": 1,
  "component_id": 1,
  "environment": "QA",
  "vcs_url": "https://github.com/company/mobile-app.git",
  "developer_name": "John Doe",
  "build_server": "192.168.1.149",
  "deploy_server": "192.168.1.150",
  "database_name": "mobile_db",
  "db_backup_location": "/backups/mobile/2024-11-26.sql",
  "database_script": "UPDATE users SET status=1",
  "previous_build_backup": "/backups/builds/app-v1.2.3.war",
  "build_status": "success",
  "deploy_status": "pending",
  "notes": "Hotfix for login issue",
  "deployed_by": "Admin User",
  "created_at": "2024-11-26T10:45:00",
  "updated_at": "2024-11-26T10:45:00"
}
```

### Duplicate Deployment Detection
```bash
# Trying to create same JIRA ID again
curl -X POST http://localhost:8000/api/v1/deployments \
  -H "Content-Type: application/json" \
  -d '{"jira_id": "PATCH-001", ...}'
```

**Response (409 Conflict):**
```json
{
  "detail": "Deployment with JIRA ID PATCH-001 already exists in recent records"
}
```

### List Deployments with Filters
```bash
# All deployments
curl http://localhost:8000/api/v1/deployments

# Filter by project
curl http://localhost:8000/api/v1/deployments?project_id=1

# Filter by month and year
curl http://localhost:8000/api/v1/deployments?month=11&year=2024

# Combine filters
curl http://localhost:8000/api/v1/deployments?project_id=1&month=11&year=2024

# Pagination
curl http://localhost:8000/api/v1/deployments?skip=0&limit=10
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "jira_id": "PATCH-001",
    "timestamp": "2024-11-26T10:45:00",
    "project_id": 1,
    "component_id": 1,
    "environment": "QA",
    "deploy_status": "pending"
  },
  {
    "id": 2,
    "jira_id": "PATCH-002",
    "timestamp": "2024-11-26T11:00:00",
    "project_id": 1,
    "component_id": 2,
    "environment": "UAT",
    "deploy_status": "success"
  }
]
```

### Get Deployment by Project
```bash
curl http://localhost:8000/api/v1/deployments/project/1
```

### Update Deployment
```bash
curl -X PUT http://localhost:8000/api/v1/deployments/1 \
  -H "Content-Type: application/json" \
  -d '{
    "deploy_status": "success",
    "notes": "Hotfix deployed successfully"
  }'
```

### Delete Deployment
```bash
curl -X DELETE http://localhost:8000/api/v1/deployments/1
```

---

## Library API

### Get All Library Presets
```bash
curl http://localhost:8000/api/v1/library
```

**Response (200 OK):**
```json
{
  "id": 1,
  "developers": ["John Doe", "Jane Smith", "Kannan"],
  "build_servers": ["192.168.1.149", "192.168.1.155"],
  "deploy_servers": ["192.168.1.150", "192.168.1.151"],
  "environments": ["QA", "UAT", "Production"],
  "created_at": "2024-11-26T10:00:00",
  "updated_at": "2024-11-26T10:00:00"
}
```

### Update All Presets
```bash
curl -X PUT http://localhost:8000/api/v1/library \
  -H "Content-Type: application/json" \
  -d '{
    "developers": ["John Doe", "Jane Smith", "Kannan", "New Dev"],
    "build_servers": ["192.168.1.149", "192.168.1.155"],
    "deploy_servers": ["192.168.1.150", "192.168.1.151"],
    "environments": ["QA", "UAT", "Staging", "Production"]
  }'
```

### Add Developer
```bash
curl -X POST http://localhost:8000/api/v1/library/developers \
  -H "Content-Type: application/json" \
  -d '{"name": "New Developer"}'
```

### Remove Developer
```bash
curl -X DELETE http://localhost:8000/api/v1/library/developers/New%20Developer
```

### Add Build Server
```bash
curl -X POST http://localhost:8000/api/v1/library/build-servers \
  -H "Content-Type: application/json" \
  -d '{"name": "192.168.1.160"}'
```

### Add Deploy Server
```bash
curl -X POST http://localhost:8000/api/v1/library/deploy-servers \
  -H "Content-Type: application/json" \
  -d '{"name": "192.168.1.160"}'
```

### Add Environment
```bash
curl -X POST http://localhost:8000/api/v1/library/environments \
  -H "Content-Type: application/json" \
  -d '{"name": "Staging"}'
```

---

## Settings API

### Get All Settings
```bash
curl http://localhost:8000/api/v1/settings
```

**Response (200 OK):**
```json
{
  "app_theme": "dark",
  "auto_save_interval": "30",
  "excel_export_path": "/exports",
  "pdf_page_size": "A4"
}
```

### Get Specific Setting
```bash
curl http://localhost:8000/api/v1/settings/app_theme
```

**Response (200 OK):**
```json
{
  "key": "app_theme",
  "value": "dark",
  "description": "Application theme (light or dark)"
}
```

### Create Setting
```bash
curl -X POST http://localhost:8000/api/v1/settings/new_setting \
  -H "Content-Type: application/json" \
  -d '{
    "value": "some_value",
    "description": "Description of the setting"
  }'
```

### Update Setting
```bash
curl -X PUT http://localhost:8000/api/v1/settings/app_theme \
  -H "Content-Type: application/json" \
  -d '{
    "value": "light",
    "description": "Updated application theme"
  }'
```

---

## Error Examples

### 404 Not Found
```bash
curl http://localhost:8000/api/v1/projects/999
```

**Response (404 Not Found):**
```json
{
  "detail": "Project with ID 999 not found"
}
```

### 500 Internal Server Error
```bash
# Database connection error or other server issue
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Failed to create deployment: database connection error"
}
```

---

## Testing with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create a project
project_data = {
    "name": "Test Project",
    "build_server": "192.168.1.149",
    "environment": "QA"
}
response = requests.post(f"{BASE_URL}/projects", json=project_data)
project = response.json()
print(f"Created project: {project['id']}")

# Create a deployment
deployment_data = {
    "jira_id": "PATCH-TEST-001",
    "project_id": project['id'],
    "component_id": 1,
    "environment": "QA",
    "build_status": "success",
    "deploy_status": "pending"
}
response = requests.post(f"{BASE_URL}/deployments", json=deployment_data)
deployment = response.json()
print(f"Created deployment: {deployment['id']}")

# List deployments for project
response = requests.get(f"{BASE_URL}/deployments/project/{project['id']}")
deployments = response.json()
print(f"Deployments for project: {len(deployments)}")

# Get library
response = requests.get(f"{BASE_URL}/library")
library = response.json()
print(f"Developers: {library['developers']}")
```

---

## Testing with Curl Scripts

### Create Full Workflow
```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1"

# Create project
PROJECT=$(curl -s -X POST $BASE_URL/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","environment":"QA"}')
PROJECT_ID=$(echo $PROJECT | jq '.id')
echo "Created project: $PROJECT_ID"

# Create deployment
DEPLOYMENT=$(curl -s -X POST $BASE_URL/deployments \
  -H "Content-Type: application/json" \
  -d "{\"jira_id\":\"TEST-001\",\"project_id\":$PROJECT_ID,\"component_id\":1,\"environment\":\"QA\"}")
DEPLOYMENT_ID=$(echo $DEPLOYMENT | jq '.id')
echo "Created deployment: $DEPLOYMENT_ID"

# List deployments
curl -s $BASE_URL/deployments | jq '.'
```

---

## Health Check

### Check API Status
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "app": "chklst"
}
```

---

## API Rate Limiting
Not yet implemented (Phase 4+)

## Pagination Guidelines
- Default limit: 100
- Max limit: 100
- Use `skip` and `limit` parameters
- Example: `?skip=0&limit=10` for first 10 records

## Date Filtering
- Format: ISO 8601 (YYYY-MM-DD)
- Supports month/year filtering with extraction
- Example: `?month=11&year=2024`

## Notes
- All timestamps are UTC
- All operations are case-sensitive
- Duplicate JIRA IDs detected in last 10 records
- Project deletion cascades to components and deployments

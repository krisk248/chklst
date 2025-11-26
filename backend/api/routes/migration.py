"""Migration API routes for managing data migration from existing files to SQLite"""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session
from backend.services.migration_service import MigrationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/migration",
    tags=["migration"]
)

migration_service = MigrationService()


@router.post("/run")
async def run_migration(db: AsyncSession = Depends(get_db_session)):
    """Run data migration from existing files to SQLite.

    This endpoint imports:
    - Projects from projects/*.json
    - Components from project JSON files
    - Library presets from library.json
    - Application settings from settings.json
    - Deployments from reports/**/*.xlsx

    Returns 200 if migration completes (may have partial errors)
    Returns 409 if migration already completed
    """
    # Check if migration already done
    if not migration_service.check_migration_needed():
        return {
            "status": "already_complete",
            "message": "Migration has already been completed",
            "flag_location": str(migration_service.migration_flag)
        }

    try:
        # Run full migration
        results = await migration_service.run_full_migration()

        # Mark as complete if no critical errors
        if not results["errors"] or len(results["errors"]) == 0:
            migration_service.mark_migration_complete()

        return {
            "status": "complete" if not results["errors"] else "partial",
            "message": "Migration completed" if not results["errors"]
                       else "Migration completed with errors",
            "results": {
                "projects_imported": results["projects"],
                "components_imported": results["components"],
                "deployments_imported": results["deployments"],
                "library_imported": results["library_imported"],
                "settings_imported": results["settings_imported"],
            },
            "errors": results["errors"],
            "flag_location": str(migration_service.migration_flag) if not results["errors"] else None
        }

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {str(e)}"
        )


@router.get("/status")
async def migration_status():
    """Check migration status and data availability.

    Returns information about:
    - Whether migration is needed
    - Available data sources (projects, reports, library, settings)
    - File counts in each source
    """
    projects_path = Path("projects")
    reports_path = Path("reports")

    # Count project files
    project_files = []
    if projects_path.exists():
        project_files = list(projects_path.glob("*.json"))

    # Count Excel files
    excel_files = []
    if reports_path.exists():
        excel_files = list(reports_path.glob("*/*.xlsx"))

    return {
        "migration_needed": migration_service.check_migration_needed(),
        "migration_flag_exists": migration_service.migration_flag.exists(),
        "data_sources": {
            "projects": {
                "exists": projects_path.exists(),
                "file_count": len(project_files),
                "files": [f.name for f in sorted(project_files)][:10],  # First 10
                "path": str(projects_path.resolve())
            },
            "deployments": {
                "exists": reports_path.exists(),
                "file_count": len(excel_files),
                "files": [f.relative_to(reports_path) for f in sorted(excel_files)][:10],
                "path": str(reports_path.resolve())
            },
            "library": {
                "exists": migration_service.library_path.exists(),
                "path": str(migration_service.library_path.resolve())
            },
            "settings": {
                "exists": migration_service.settings_path.exists(),
                "path": str(migration_service.settings_path.resolve())
            }
        }
    }


@router.post("/reset")
async def reset_migration_flag():
    """Reset migration flag to allow re-running migration.

    WARNING: This will allow the migration to run again.
    It does NOT delete existing database records.

    Use with caution in development only!
    """
    if migration_service.migration_flag.exists():
        try:
            migration_service.migration_flag.unlink()
            return {
                "status": "success",
                "message": "Migration flag removed. Migration can be run again.",
                "warning": "This does not clear existing database records."
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove migration flag: {str(e)}"
            )
    else:
        return {
            "status": "not_found",
            "message": "Migration flag does not exist"
        }


@router.get("/preview")
async def preview_migration():
    """Preview what data will be migrated without actually migrating.

    Returns counts of what would be imported from each source.
    This is useful for validation before running full migration.
    """
    projects_path = Path("projects")
    reports_path = Path("reports")

    # Count projects and components
    project_count = 0
    component_count = 0

    if projects_path.exists():
        import json
        for json_file in projects_path.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    project_count += 1
                    components = data.get("components", {})
                    if isinstance(components, dict):
                        component_count += sum(
                            1 for v in components.values()
                            if v and v.get("enabled", True)
                        )
                    elif isinstance(components, list):
                        component_count += sum(
                            1 for c in components
                            if c and c.get("enabled", True)
                        )
            except Exception:
                continue

    # Count deployments
    deployment_count = 0
    if reports_path.exists():
        from openpyxl import load_workbook
        for excel_file in reports_path.glob("*/*.xlsx"):
            try:
                wb = load_workbook(excel_file, read_only=True)
                if "Deployments" in wb.sheetnames:
                    ws = wb["Deployments"]
                    # Count non-empty rows (skip header)
                    deployment_count += sum(
                        1 for row in ws.iter_rows(min_row=2)
                        if row[0].value
                    )
            except Exception:
                continue

    return {
        "preview": {
            "projects": project_count,
            "components": component_count,
            "deployments": deployment_count,
            "library": migration_service.library_path.exists(),
            "settings": migration_service.settings_path.exists()
        },
        "sources": {
            "projects_directory": str(projects_path.resolve()),
            "reports_directory": str(reports_path.resolve()),
            "library_file": str(migration_service.library_path.resolve()),
            "settings_file": str(migration_service.settings_path.resolve())
        }
    }

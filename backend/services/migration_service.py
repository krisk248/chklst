"""Migration service for importing existing data to SQLite database"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from openpyxl import load_workbook

from backend.models import Project, Component, Deployment, Library, AppSettings
from backend.database import async_session_factory

logger = logging.getLogger(__name__)


class MigrationService:
    """Service for migrating existing data from JSON and Excel files to SQLite"""

    def __init__(self):
        """Initialize migration service with data paths"""
        self.projects_path = Path("projects")
        self.reports_path = Path("reports")
        self.library_path = Path("library.json")
        self.settings_path = Path("settings.json")
        self.migration_flag = Path("data/.migration_complete")
        # Track imported JIRA IDs to avoid duplicates across Excel files
        self._imported_jira_ids: set = set()

    async def run_full_migration(self) -> Dict[str, Any]:
        """Run complete data migration from existing files to SQLite.

        Returns:
            Dict with migration results including counts and any errors
        """
        results = {
            "projects": 0,
            "components": 0,
            "deployments": 0,
            "library_imported": False,
            "settings_imported": False,
            "errors": []
        }

        async with async_session_factory() as db:
            # 1. Import library presets first (needed for dropdowns)
            try:
                await self._import_library(db)
                results["library_imported"] = True
                logger.info("Library imported successfully")
            except Exception as e:
                error_msg = f"Library import failed: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

            # 2. Import settings
            try:
                await self._import_settings(db)
                results["settings_imported"] = True
                logger.info("Settings imported successfully")
            except Exception as e:
                error_msg = f"Settings import failed: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

            # 3. Import projects and components from JSON
            try:
                project_count, component_count = await self._import_projects(db)
                results["projects"] = project_count
                results["components"] = component_count
                logger.info(
                    f"Projects imported: {project_count}, "
                    f"Components imported: {component_count}"
                )
            except Exception as e:
                error_msg = f"Projects import failed: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

            # 4. Import deployments from Excel
            try:
                deployment_count = await self._import_deployments(db)
                results["deployments"] = deployment_count
                logger.info(f"Deployments imported: {deployment_count}")
            except Exception as e:
                error_msg = f"Deployments import failed: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

            await db.commit()

        return results

    async def _import_library(self, db: AsyncSession) -> None:
        """Import library.json into SQLite.

        The library contains presets for:
        - developers
        - build servers
        - deploy servers
        - environments
        """
        if not self.library_path.exists():
            logger.warning(f"Library file not found: {self.library_path}")
            return

        try:
            with open(self.library_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in library file: {e}")
            raise

        # Create or update library record
        library = Library(
            id=1,
            developers=data.get("developers", []),
            build_servers=data.get("build_servers", []),
            deploy_servers=data.get("deploy_servers", []),
            environments=data.get("environments", [])
        )

        await db.merge(library)
        logger.info(
            f"Library imported: {len(library.developers)} developers, "
            f"{len(library.build_servers)} build servers, "
            f"{len(library.deploy_servers)} deploy servers, "
            f"{len(library.environments)} environments"
        )

    async def _import_settings(self, db: AsyncSession) -> None:
        """Import settings.json into SQLite.

        Settings include:
        - deployed_by_default
        - excel_export_path
        """
        if not self.settings_path.exists():
            logger.warning(f"Settings file not found: {self.settings_path}")
            return

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in settings file: {e}")
            raise

        # Create or update settings record
        settings = AppSettings(
            id=1,
            key="deployed_by_default",
            value=data.get("deployed_by_default", ""),
            description="Default person to assign deployments to"
        )

        await db.merge(settings)

        # Add excel export path as separate setting
        export_setting = AppSettings(
            id=2,
            key="excel_export_path",
            value=data.get("excel_export_path", "reports"),
            description="Path where Excel reports are exported"
        )

        await db.merge(export_setting)
        logger.info("Settings imported successfully")

    async def _import_projects(self, db: AsyncSession) -> Tuple[int, int]:
        """Import all projects from JSON files.

        Projects can have components defined as either:
        1. Dictionary: {"frontend": {...}, "backend": {...}}
        2. List: [{...}, {...}]

        Returns:
            Tuple of (project_count, component_count)
        """
        project_count = 0
        component_count = 0

        if not self.projects_path.exists():
            logger.warning(f"Projects directory not found: {self.projects_path}")
            return 0, 0

        for json_file in sorted(self.projects_path.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading {json_file.name}: {e}")
                continue

            try:
                # Create project
                project = Project(
                    name=data.get("project_name", json_file.stem),
                    build_server=data.get("build_server", ""),
                    deploy_server=data.get("deploy_server", ""),
                    database_name=data.get("db_name", ""),
                    environment=data.get("environment", ""),
                    backup_location=data.get("backup_location", "")
                )

                db.add(project)
                await db.flush()  # Get project ID
                project_count += 1
                logger.info(f"Imported project: {project.name}")

                # Import components
                components_data = data.get("components", {})

                # Handle both dict and list formats
                if isinstance(components_data, dict):
                    # Dictionary format: {"frontend": {...}, "backend": {...}}
                    for comp_type, comp_data in components_data.items():
                        if comp_data and comp_data.get("enabled", True):
                            component_count += await self._create_component(
                                db, project.id, comp_type, comp_data
                            )
                elif isinstance(components_data, list):
                    # List format: [{...}, {...}]
                    for idx, comp_data in enumerate(components_data):
                        if comp_data and comp_data.get("enabled", True):
                            component_type = comp_data.get(
                                "id",
                                f"component_{idx}"
                            )
                            component_count += await self._create_component(
                                db, project.id, component_type, comp_data
                            )

            except Exception as e:
                logger.error(f"Error importing project from {json_file.name}: {e}")
                continue

        logger.info(
            f"Project import completed: "
            f"{project_count} projects, {component_count} components"
        )
        return project_count, component_count

    async def _create_component(
        self,
        db: AsyncSession,
        project_id: int,
        component_type: str,
        comp_data: Dict[str, Any]
    ) -> int:
        """Create a single component record.

        Returns:
            1 if component created, 0 otherwise
        """
        try:
            component = Component(
                project_id=project_id,
                name=comp_data.get("component_name", ""),
                developer=comp_data.get("developer_name", ""),
                vcs_type=comp_data.get("vcs_type", "git"),
                vcs_url=comp_data.get("vcs_url", ""),
                build_command=comp_data.get("build_command", ""),
                component_url=comp_data.get("component_url", ""),
                enabled=comp_data.get("enabled", True)
            )
            db.add(component)
            await db.flush()
            logger.debug(f"Created component: {component.name} in project {project_id}")
            return 1
        except Exception as e:
            logger.error(f"Error creating component: {e}")
            return 0

    async def _import_deployments(self, db: AsyncSession) -> int:
        """Import all deployments from Excel files.

        Looks for Excel files in subdirectories of reports/
        (e.g., reports/Nov_2025/*.xlsx, reports/Oct_2025/*.xlsx)

        Returns:
            Total number of deployments imported
        """
        deployment_count = 0

        if not self.reports_path.exists():
            logger.warning(f"Reports directory not found: {self.reports_path}")
            return 0

        # Find all month folders
        for month_folder in sorted(self.reports_path.iterdir()):
            if not month_folder.is_dir() or month_folder.name in ["pdfs", "pdfs"]:
                continue

            logger.info(f"Processing month folder: {month_folder.name}")

            # Process each Excel file in the month folder
            for excel_file in sorted(month_folder.glob("*.xlsx")):
                try:
                    count = await self._import_excel_file(db, excel_file)
                    deployment_count += count
                    logger.info(
                        f"Imported {count} deployments from {excel_file.name}"
                    )
                except Exception as e:
                    logger.error(f"Error importing {excel_file.name}: {e}")
                    continue

        logger.info(f"Deployment import completed: {deployment_count} total")
        return deployment_count

    async def _import_excel_file(self, db: AsyncSession, file_path: Path) -> int:
        """Import deployments from a single Excel file.

        Excel file should have a "Deployments" sheet with headers:
        - JIRA PATCH ID
        - Timestamp
        - Project Name
        - Component Name
        - Environment
        - SVN/GIT URL
        - Developer Name
        - Build Server
        - Deploy Server
        - Database Name
        - DB Backup Location
        - Database Script
        - Previous Build Backup
        - Build Status
        - Deploy Status
        - Notes
        - Deployed By

        Returns:
            Number of deployments imported from this file
        """
        count = 0

        try:
            wb = load_workbook(file_path, read_only=True)
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {e}")
            return 0

        if "Deployments" not in wb.sheetnames:
            logger.warning(
                f"No 'Deployments' sheet found in {file_path.name}. "
                f"Available sheets: {wb.sheetnames}"
            )
            return 0

        ws = wb["Deployments"]

        # Get headers from first row
        headers = []
        for cell in ws[1]:
            if cell.value:
                headers.append(cell.value)

        if not headers:
            logger.warning(f"No headers found in {file_path.name}")
            return 0

        # Process data rows
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                if not row[0]:  # Skip empty rows
                    continue

                row_dict = dict(zip(headers, row))

                # Parse timestamp
                timestamp = await self._parse_timestamp(row_dict.get("Timestamp"))

                # Get project and component IDs
                project_name = str(row_dict.get("Project Name", "") or "").strip()
                component_name = str(row_dict.get("Component Name", "") or "").strip()

                project = await self._get_project_by_name(db, project_name)
                component = await self._get_component_by_name(
                    db, component_name, project.id if project else None
                )

                if not project:
                    logger.warning(
                        f"Project '{project_name}' not found for "
                        f"deployment in row {row_idx}"
                    )
                    continue

                if not component:
                    logger.warning(
                        f"Component '{component_name}' not found in project "
                        f"'{project_name}' for deployment in row {row_idx}"
                    )
                    # Still create deployment with project_id but NULL component_id
                    # or create a temporary component

                # Create deployment record
                jira_id = str(row_dict.get("JIRA PATCH ID", "") or "").strip()
                if not jira_id:
                    # Generate unique ID if not provided
                    jira_id = f"MIGRATED_{file_path.stem}_{row_idx}"

                # Parse status and convert to string representation
                build_status_str = self._parse_status_string(
                    row_dict.get("Build Status", "")
                )
                deploy_status_str = self._parse_status_string(
                    row_dict.get("Deploy Status", "")
                )

                # Check if deployment with this JIRA ID already exists (in DB or current batch)
                if jira_id in self._imported_jira_ids:
                    logger.debug(f"Deployment with JIRA ID {jira_id} already imported, skipping")
                    continue

                stmt = select(Deployment).where(Deployment.jira_id == jira_id)
                existing = await db.execute(stmt)
                if existing.scalars().first():
                    logger.debug(f"Deployment with JIRA ID {jira_id} already exists in DB, skipping")
                    self._imported_jira_ids.add(jira_id)
                    continue

                deployment = Deployment(
                    jira_id=jira_id,
                    timestamp=timestamp,
                    project_id=project.id,
                    component_id=component.id if component else None,
                    environment=str(row_dict.get("Environment", "") or "").strip(),
                    vcs_url=str(row_dict.get("SVN/GIT URL", "") or "").strip(),
                    developer_name=str(row_dict.get("Developer Name", "") or "").strip(),
                    build_server=str(row_dict.get("Build Server", "") or "").strip(),
                    deploy_server=str(row_dict.get("Deploy Server", "") or "").strip(),
                    database_name=str(row_dict.get("Database Name", "") or "").strip(),
                    db_backup_location=str(row_dict.get("DB Backup Location", "") or "").strip(),
                    database_script=str(row_dict.get("Database Script", "") or "").strip(),
                    previous_build_backup=str(row_dict.get("Previous Build Backup", "") or "").strip(),
                    build_status=build_status_str,
                    deploy_status=deploy_status_str,
                    notes=str(row_dict.get("Notes", "") or "").strip(),
                    deployed_by=str(row_dict.get("Deployed By", "") or "").strip()
                )

                db.add(deployment)
                self._imported_jira_ids.add(jira_id)
                count += 1

            except Exception as e:
                logger.error(f"Error processing row {row_idx} in {file_path.name}: {e}")
                continue

        return count

    async def _parse_timestamp(self, timestamp_value: Any) -> datetime:
        """Parse timestamp from Excel cell.

        Handles multiple formats:
        - datetime object
        - String in various formats
        """
        if not timestamp_value:
            return datetime.utcnow()

        if isinstance(timestamp_value, datetime):
            return timestamp_value

        try:
            # Try common datetime formats
            formats = [
                "%d-%b-%Y %I:%M%p",
                "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
            ]

            timestamp_str = str(timestamp_value).strip()

            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue

            logger.warning(f"Could not parse timestamp: {timestamp_value}")
            return datetime.utcnow()

        except Exception as e:
            logger.warning(f"Error parsing timestamp {timestamp_value}: {e}")
            return datetime.utcnow()

    def _parse_status(self, status_value: Any) -> bool:
        """Parse status value from Excel cell.

        Treats various values as True:
        - "success", "Success", "SUCCESS"
        - "true", "True", "TRUE"
        - 1
        - "pass", "Pass", "PASS"

        Everything else is False
        """
        if not status_value:
            return False

        status_str = str(status_value).strip().lower()
        return status_str in ["success", "true", "1", "pass", "completed", "yes"]

    def _parse_status_string(self, status_value: Any) -> str:
        """Parse status value from Excel cell and return as string.

        Returns:
            "success" if value is truthy, "pending" otherwise
        """
        if not status_value:
            return "pending"

        status_str = str(status_value).strip().lower()
        if status_str in ["success", "true", "1", "pass", "completed", "yes"]:
            return "success"
        elif status_str in ["failed", "failure", "false", "0", "failed", "error"]:
            return "failed"
        else:
            return "pending"

    async def _get_project_by_name(
        self, db: AsyncSession, project_name: str
    ) -> Project | None:
        """Get project from database by name.

        Handles name variations:
        - Exact match
        - Replace spaces with underscores
        - Replace underscores with spaces
        - Case-insensitive match
        """
        if not project_name:
            return None

        try:
            # Try exact match first
            stmt = select(Project).where(Project.name == project_name)
            result = await db.execute(stmt)
            project = result.scalars().first()
            if project:
                return project

            # Try with spaces replaced by underscores
            name_underscore = project_name.replace(" ", "_")
            stmt = select(Project).where(Project.name == name_underscore)
            result = await db.execute(stmt)
            project = result.scalars().first()
            if project:
                return project

            # Try with underscores replaced by spaces
            name_space = project_name.replace("_", " ")
            stmt = select(Project).where(Project.name == name_space)
            result = await db.execute(stmt)
            project = result.scalars().first()
            if project:
                return project

            # Try case-insensitive match using LIKE
            stmt = select(Project).where(
                func.lower(Project.name) == func.lower(project_name)
            )
            result = await db.execute(stmt)
            project = result.scalars().first()
            if project:
                return project

            return None
        except Exception as e:
            logger.error(f"Error getting project by name '{project_name}': {e}")
            return None

    async def _get_component_by_name(
        self, db: AsyncSession, component_name: str, project_id: int | None = None
    ) -> Component | None:
        """Get component from database by name, optionally filtered by project.

        Handles name variations and partial matches.
        """
        if not component_name:
            return None

        try:
            # Try exact match first
            stmt = select(Component).where(Component.name == component_name)
            if project_id:
                stmt = stmt.where(Component.project_id == project_id)
            result = await db.execute(stmt)
            component = result.scalars().first()
            if component:
                return component

            # Try case-insensitive match
            stmt = select(Component).where(
                func.lower(Component.name) == func.lower(component_name)
            )
            if project_id:
                stmt = stmt.where(Component.project_id == project_id)
            result = await db.execute(stmt)
            component = result.scalars().first()
            if component:
                return component

            # Try partial match (component_name contains the DB name or vice versa)
            if project_id:
                stmt = select(Component).where(Component.project_id == project_id)
                result = await db.execute(stmt)
                components = result.scalars().all()
                component_name_lower = component_name.lower()
                for comp in components:
                    comp_name_lower = comp.name.lower()
                    if comp_name_lower in component_name_lower or component_name_lower in comp_name_lower:
                        return comp

            return None
        except Exception as e:
            logger.error(f"Error getting component by name '{component_name}': {e}")
            return None

    def check_migration_needed(self) -> bool:
        """Check if migration has already been done.

        Returns:
            True if migration is needed, False if already complete
        """
        return not self.migration_flag.exists()

    def mark_migration_complete(self) -> None:
        """Mark migration as complete by creating a flag file"""
        self.migration_flag.parent.mkdir(parents=True, exist_ok=True)
        self.migration_flag.touch()
        logger.info(f"Migration marked complete: {self.migration_flag}")

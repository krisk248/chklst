"""Excel service for reading and writing deployment data"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment


class ExcelService:
    """Service for managing Excel deployment files"""

    DEPLOYMENT_HEADERS = [
        "JIRA PATCH ID", "Timestamp", "Project Name", "Component Name",
        "Environment", "SVN/GIT URL", "Developer Name", "Build Server",
        "Deploy Server", "Database Name", "DB Backup Location",
        "Database Script", "Previous Build Backup", "Build Status",
        "Deploy Status", "Notes", "Deployed By"
    ]

    HISTORY_HEADERS = [
        "Timestamp", "Action", "Project", "Component",
        "JIRA ID", "User", "Details", "Status"
    ]

    def __init__(self, base_path: str = "reports"):
        """Initialize Excel service with base reports directory"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_month_folder(self, month: int, year: int) -> Path:
        """Get or create folder for month/year (e.g., 'reports/Nov_2025/')"""
        month_name = datetime(year, month, 1).strftime("%b_%Y")
        folder = self.base_path / month_name
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def get_project_file(self, project_name: str, month: int, year: int) -> Path:
        """Get path to project Excel file"""
        folder = self.get_month_folder(month, year)
        # Sanitize project name for file system
        safe_name = project_name.replace(" ", "_").replace("/", "_")
        return folder / f"{safe_name}.xlsx"

    def read_deployments(
        self,
        project_name: str,
        month: int,
        year: int
    ) -> List[Dict[str, Any]]:
        """Read all deployments from Excel file"""
        file_path = self.get_project_file(project_name, month, year)

        if not file_path.exists():
            return []

        wb = load_workbook(file_path)
        if "Deployments" not in wb.sheetnames:
            return []

        ws = wb["Deployments"]
        headers = [cell.value for cell in ws[1]]

        deployments = []
        for row in ws.iter_rows(min_row=2, values_only=False):
            # Skip empty rows
            if row[0].value is None:
                continue

            deployment = {
                header: row[i].value
                for i, header in enumerate(headers)
            }
            deployments.append(deployment)

        return deployments

    def read_all_monthly_deployments(
        self,
        month: int,
        year: int
    ) -> List[Dict[str, Any]]:
        """Read all deployments across all projects for a month"""
        folder = self.get_month_folder(month, year)
        all_deployments = []

        for file_path in folder.glob("*.xlsx"):
            project_name = file_path.stem
            deployments = self.read_deployments(project_name, month, year)
            all_deployments.extend(deployments)

        # Sort by timestamp (most recent first)
        all_deployments.sort(
            key=lambda x: x.get("Timestamp", ""),
            reverse=True
        )

        return all_deployments

    def save_deployment(self, deployment_data: Dict[str, Any]) -> bool:
        """Save deployment to Excel file (create if not exists)"""
        project_name = deployment_data["project_name"]
        timestamp = deployment_data["timestamp"]
        month = timestamp.month
        year = timestamp.year

        file_path = self.get_project_file(project_name, month, year)

        # Load existing workbook or create new one
        if file_path.exists():
            wb = load_workbook(file_path)
        else:
            wb = self._create_new_workbook()

        # Add deployment to Deployments sheet
        ws = wb["Deployments"]
        row_data = self._deployment_to_row(deployment_data)
        ws.append(row_data)

        # Add entry to History sheet
        ws_history = wb["History"]
        history_row = self._create_history_row(deployment_data, "CREATE")
        ws_history.append(history_row)

        # Save the workbook
        wb.save(file_path)
        return True

    def _create_new_workbook(self) -> Workbook:
        """Create new workbook with formatted sheets"""
        wb = Workbook()

        # Deployments sheet
        ws_deploy = wb.active
        ws_deploy.title = "Deployments"
        ws_deploy.append(self.DEPLOYMENT_HEADERS)
        self._style_header_row(ws_deploy, color="4a9eff")

        # History sheet
        ws_history = wb.create_sheet("History")
        ws_history.append(self.HISTORY_HEADERS)
        self._style_header_row(ws_history, color="FFA500")

        return wb

    def _style_header_row(
        self,
        ws,
        color: str = "4a9eff"
    ) -> None:
        """Style header row with color and formatting"""
        header_fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font

        # Freeze header row
        ws.freeze_panes = "A2"

        # Add auto-filter
        if ws.max_column > 0:
            ws.auto_filter.ref = ws.dimensions

    def _deployment_to_row(self, data: Dict[str, Any]) -> List[Any]:
        """Convert deployment dict to Excel row (17 columns)"""
        # Format timestamp
        timestamp = data.get("timestamp", "")
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.strftime("%d-%b-%Y %I:%M%p")
        else:
            timestamp_str = str(timestamp)

        # Convert boolean status to "Success" or "Failed"
        build_status = "Success" if data.get("build_status") else "Failed"
        deploy_status = "Success" if data.get("deploy_status") else "Failed"

        return [
            data.get("jira_id", ""),                    # 1. JIRA PATCH ID
            timestamp_str,                               # 2. Timestamp
            data.get("project_name", ""),               # 3. Project Name
            data.get("component_name", ""),             # 4. Component Name
            data.get("environment", ""),                # 5. Environment
            data.get("vcs_url", ""),                    # 6. SVN/GIT URL
            data.get("developer_name", ""),             # 7. Developer Name
            data.get("build_server", ""),               # 8. Build Server
            data.get("deploy_server", ""),              # 9. Deploy Server
            data.get("db_name", ""),                    # 10. Database Name
            data.get("db_backup_location", ""),         # 11. DB Backup Location
            data.get("db_script", ""),                  # 12. Database Script
            data.get("build_backup", ""),               # 13. Previous Build Backup
            build_status,                                # 14. Build Status
            deploy_status,                               # 15. Deploy Status
            data.get("notes", ""),                      # 16. Notes
            data.get("deployed_by", "")                 # 17. Deployed By
        ]

    def _create_history_row(
        self,
        data: Dict[str, Any],
        action: str
    ) -> List[Any]:
        """Create history row for audit log (8 columns)"""
        now = datetime.now()
        timestamp_str = now.strftime("%d-%b-%Y %I:%M%p")

        return [
            timestamp_str,                          # 1. Timestamp
            action,                                 # 2. Action
            data.get("project_name", ""),          # 3. Project
            data.get("component_name", ""),        # 4. Component
            data.get("jira_id", ""),               # 5. JIRA ID
            data.get("deployed_by", ""),           # 6. User
            f"{action} deployment",                # 7. Details
            "Success"                              # 8. Status
        ]

    def import_existing_data(self) -> Dict[str, Any]:
        """Import all existing Excel data and return summary"""
        imported = {
            "projects": set(),
            "deployments": 0,
            "errors": []
        }

        if not self.base_path.exists():
            return imported

        for month_folder in self.base_path.iterdir():
            if month_folder.is_dir() and month_folder.name != "pdfs":
                for excel_file in month_folder.glob("*.xlsx"):
                    try:
                        project_name = excel_file.stem
                        imported["projects"].add(project_name)

                        # Count deployments
                        wb = load_workbook(excel_file)
                        if "Deployments" in wb.sheetnames:
                            ws = wb["Deployments"]
                            # Count rows minus header
                            count = ws.max_row - 1
                            imported["deployments"] += count

                    except Exception as e:
                        imported["errors"].append({
                            "file": str(excel_file),
                            "error": str(e)
                        })

        imported["projects"] = list(imported["projects"])
        return imported

    def get_deployment_count(
        self,
        project_name: str,
        month: int,
        year: int
    ) -> int:
        """Get count of deployments for a project in a month"""
        file_path = self.get_project_file(project_name, month, year)

        if not file_path.exists():
            return 0

        try:
            wb = load_workbook(file_path)
            if "Deployments" in wb.sheetnames:
                ws = wb["Deployments"]
                # Subtract 1 for header row
                return max(0, ws.max_row - 1)
        except Exception:
            pass

        return 0

    def get_all_projects(self) -> List[str]:
        """Get list of all projects with Excel files"""
        projects = set()

        if not self.base_path.exists():
            return []

        for month_folder in self.base_path.iterdir():
            if month_folder.is_dir() and month_folder.name != "pdfs":
                for excel_file in month_folder.glob("*.xlsx"):
                    projects.add(excel_file.stem)

        return sorted(list(projects))

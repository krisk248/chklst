"""
Excel Manager for Monthly Deployment Tracking
Handles all Excel operations for deployment history
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExcelManager:
    """Manages Excel files for monthly deployment tracking"""
    
    # Excel column headers
    HEADERS = [
        "JIRA PATCH ID",
        "Timestamp",
        "Project Name",
        "Component Name",
        "Environment",
        "SVN/GIT URL",
        "Developer Name",
        "Build Server",
        "Deploy Server",
        "Database Name",
        "DB Backup Location",
        "Database Script",
        "Previous Build Backup",
        "Build Status",
        "Deploy Status",
        "Notes",
        "Deployed By"
    ]

    # History sheet headers
    HISTORY_HEADERS = [
        "Timestamp",
        "Action",
        "Project",
        "Component",
        "JIRA ID",
        "User",
        "Details",
        "Status"
    ]
    
    def __init__(self, base_path: str = "reports"):
        """Initialize Excel Manager with base reports path"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
    def _get_month_folder(self, month: int, year: int) -> Path:
        """Get or create month folder"""
        month_name = datetime(year, month, 1).strftime("%b_%Y")
        month_folder = self.base_path / month_name
        month_folder.mkdir(exist_ok=True)
        return month_folder
        
    def _get_excel_path(self, project_name: str, month: int, year: int) -> Path:
        """Get path to project's monthly Excel file"""
        month_folder = self._get_month_folder(month, year)
        return month_folder / f"{project_name}.xlsx"
        
    def _create_excel_file(self, filepath: Path) -> None:
        """Create new Excel file with Deployments and History sheets"""
        wb = Workbook()

        # Create Deployments sheet
        ws = wb.active
        ws.title = "Deployments"

        # Add headers
        for col, header in enumerate(self.HEADERS, 1):
            cell = ws.cell(row=1, column=col, value=header)
            # Header formatting
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Set column widths
        column_widths = [15, 20, 20, 20, 12, 40, 20, 20, 20, 20, 20, 30, 12, 12, 30, 20]
        for col, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        # Add borders to headers
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        for col in range(1, len(self.HEADERS) + 1):
            ws.cell(row=1, column=col).border = thin_border

        # Freeze header row
        ws.freeze_panes = "A2"

        # Add auto-filter
        ws.auto_filter.ref = f"A1:{get_column_letter(len(self.HEADERS))}1"

        # Create History sheet
        history_ws = wb.create_sheet(title="History")

        # Add history headers
        for col, header in enumerate(self.HISTORY_HEADERS, 1):
            cell = history_ws.cell(row=1, column=col, value=header)
            # Header formatting
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        # Set history column widths
        history_widths = [20, 30, 20, 20, 15, 20, 40, 15]
        for col, width in enumerate(history_widths, 1):
            history_ws.column_dimensions[get_column_letter(col)].width = width

        # Freeze history header row
        history_ws.freeze_panes = "A2"

        # Add auto-filter to history
        history_ws.auto_filter.ref = f"A1:{get_column_letter(len(self.HISTORY_HEADERS))}1"

        wb.save(filepath)

    def check_duplicate_deployment(self, project_name: str, deployment_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if deployment is a duplicate based on JIRA ID or time proximity

        Returns:
            Tuple of (is_duplicate: bool, duplicate_details: Optional[Dict])
        """
        try:
            # Get current month and year from deployment timestamp
            if 'timestamp' in deployment_data and deployment_data['timestamp']:
                deploy_time = datetime.strptime(deployment_data['timestamp'], "%d-%b-%Y %I:%M%p")
            else:
                deploy_time = datetime.now()

            month = deploy_time.month
            year = deploy_time.year

            # Get Excel file path
            excel_path = self._get_excel_path(project_name, month, year)

            # If file doesn't exist, no duplicates possible
            if not excel_path.exists():
                return False, None

            # Open workbook and get deployments sheet
            wb = openpyxl.load_workbook(excel_path, read_only=True)
            ws = wb['Deployments']

            # Get new deployment details
            new_jira_id = deployment_data.get('jira_patch_id', 'N/A')
            new_project = deployment_data.get('project_name', project_name)
            new_component = deployment_data.get('component_name', '')

            # Check last 10 rows for duplicates
            max_row = ws.max_row
            start_row = max(2, max_row - 9)  # Check last 10 rows, minimum row 2

            for row_num in range(start_row, max_row + 1):
                row = ws[row_num]

                # Skip empty rows
                if row[0].value is None:
                    continue

                existing_jira_id = row[0].value  # Column A: JIRA PATCH ID
                existing_timestamp = row[1].value  # Column B: Timestamp
                existing_project = row[2].value  # Column C: Project Name
                existing_component = row[3].value  # Column D: Component Name

                # Check 1: If JIRA ID is not N/A, check for exact JIRA ID match
                if new_jira_id != 'N/A' and existing_jira_id == new_jira_id:
                    if existing_project == new_project and existing_component == new_component:
                        wb.close()
                        return True, {
                            'row': row_num,
                            'jira_id': existing_jira_id,
                            'timestamp': existing_timestamp,
                            'project': existing_project,
                            'component': existing_component,
                            'reason': 'Same JIRA ID with same project and component'
                        }

                # Check 2: If JIRA ID is N/A, check for time proximity (within 5 minutes)
                if new_jira_id == 'N/A':
                    if existing_project == new_project and existing_component == new_component:
                        # Parse existing timestamp
                        if isinstance(existing_timestamp, str):
                            try:
                                existing_time = datetime.strptime(existing_timestamp, "%d-%b-%Y %I:%M%p")
                                time_diff = abs((deploy_time - existing_time).total_seconds())

                                # If within 5 minutes (300 seconds)
                                if time_diff <= 300:
                                    wb.close()
                                    return True, {
                                        'row': row_num,
                                        'jira_id': existing_jira_id,
                                        'timestamp': existing_timestamp,
                                        'project': existing_project,
                                        'component': existing_component,
                                        'reason': f'Same project and component within 5 minutes (time difference: {int(time_diff)} seconds)'
                                    }
                            except (ValueError, TypeError):
                                pass

            wb.close()
            return False, None

        except Exception as e:
            print(f"Error checking duplicate: {str(e)}")
            return False, None

    def log_history(self, project_name: str, action: str, deployment_data: Dict[str, Any],
                    details: str = "", status: str = "Success") -> bool:
        """
        Log an action to the History sheet

        Args:
            project_name: Name of the project
            action: Action performed (e.g., "Deployment Saved", "Duplicate Detected")
            deployment_data: Deployment data dictionary
            details: Additional details about the action
            status: Status of the action (Success/Warning/Error)
        """
        try:
            # Get current month and year
            if 'timestamp' in deployment_data and deployment_data['timestamp']:
                deploy_time = datetime.strptime(deployment_data['timestamp'], "%d-%b-%Y %I:%M%p")
            else:
                deploy_time = datetime.now()

            month = deploy_time.month
            year = deploy_time.year

            # Get Excel file path
            excel_path = self._get_excel_path(project_name, month, year)

            # If file doesn't exist, create it
            if not excel_path.exists():
                self._create_excel_file(excel_path)

            # Open workbook and get History sheet
            wb = openpyxl.load_workbook(excel_path)

            # Get or create History sheet
            if 'History' in wb.sheetnames:
                history_ws = wb['History']
            else:
                # Create History sheet if it doesn't exist (for older Excel files)
                history_ws = wb.create_sheet(title="History")
                # Add headers
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                for col, header in enumerate(self.HISTORY_HEADERS, 1):
                    cell = history_ws.cell(row=1, column=col, value=header)
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = thin_border

            # Find next empty row
            next_row = history_ws.max_row + 1

            # Prepare history entry
            history_data = [
                datetime.now().strftime("%d-%b-%Y %I:%M%p"),
                action,
                deployment_data.get('project_name', project_name),
                deployment_data.get('component_name', ''),
                deployment_data.get('jira_patch_id', 'N/A'),
                deployment_data.get('deployed_by', ''),
                details,
                status
            ]

            # Write to history sheet
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            for col, value in enumerate(history_data, 1):
                cell = history_ws.cell(row=next_row, column=col, value=value)
                cell.border = thin_border

                # Color code status column
                if col == 8:  # Status column
                    if status == 'Success':
                        cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                        cell.font = Font(color="006100")
                    elif status == 'Warning':
                        cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                        cell.font = Font(color="9C5700")
                    else:  # Error
                        cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                        cell.font = Font(color="9C0006")

            # Save workbook
            wb.save(excel_path)
            wb.close()

            return True

        except Exception as e:
            print(f"Error logging history: {str(e)}")
            return False

    def add_deployment(self, project_name: str, deployment_data: Dict[str, Any]) -> bool:
        """Add a deployment record to the monthly Excel file"""
        try:
            # Get current month and year from deployment timestamp
            if 'timestamp' in deployment_data and deployment_data['timestamp']:
                deploy_time = datetime.strptime(deployment_data['timestamp'], "%d-%b-%Y %I:%M%p")
            else:
                deploy_time = datetime.now()
                
            month = deploy_time.month
            year = deploy_time.year
            
            # Get Excel file path
            excel_path = self._get_excel_path(project_name, month, year)
            
            # Create file if it doesn't exist
            if not excel_path.exists():
                self._create_excel_file(excel_path)
                
            # Open workbook and get active sheet
            wb = openpyxl.load_workbook(excel_path)
            ws = wb.active
            
            # Find next empty row
            next_row = ws.max_row + 1
            
            # Prepare row data
            row_data = [
                deployment_data.get('jira_patch_id', 'N/A'),
                deployment_data.get('timestamp', datetime.now().strftime("%d-%b-%Y %I:%M%p")),
                deployment_data.get('project_name', project_name),
                deployment_data.get('component_name', ''),
                deployment_data.get('environment', 'QA'),
                deployment_data.get('vcs_url', ''),
                deployment_data.get('developer_name', ''),
                deployment_data.get('build_server', ''),
                deployment_data.get('deploy_server', ''),
                deployment_data.get('database_name', ''),
                deployment_data.get('db_backup_location', ''),
                deployment_data.get('database_script', 'N/A'),
                deployment_data.get('backup_location', ''),
                'Success' if deployment_data.get('build_status', False) else 'Failed',
                'Success' if deployment_data.get('deploy_status', False) else 'Failed',
                deployment_data.get('notes', ''),
                deployment_data.get('deployed_by', '')
            ]
            
            # Write data to Excel
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=next_row, column=col, value=value)
                
                # Add border
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                
                # Color code status columns
                if col == 13:  # Build Status
                    if value == 'Success':
                        cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                        cell.font = Font(color="006100")
                    else:
                        cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                        cell.font = Font(color="9C0006")
                        
                if col == 14:  # Deploy Status
                    if value == 'Success':
                        cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                        cell.font = Font(color="006100")
                    else:
                        cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                        cell.font = Font(color="9C0006")
                        
            # Update auto-filter range
            ws.auto_filter.ref = f"A1:{get_column_letter(len(self.HEADERS))}{next_row}"
            
            # Save workbook
            wb.save(excel_path)
            wb.close()

            # Log to history
            self.log_history(
                project_name,
                "Deployment Saved",
                deployment_data,
                f"Deployment record added successfully",
                "Success"
            )

            return True

        except Exception as e:
            print(f"Error adding deployment: {str(e)}")
            # Log error to history
            try:
                self.log_history(
                    project_name,
                    "Deployment Failed",
                    deployment_data,
                    f"Error: {str(e)}",
                    "Error"
                )
            except:
                pass
            return False
            
    def get_monthly_deployments(self, project_name: str, month: int, year: int) -> List[Dict[str, Any]]:
        """Get all deployments for a project in a specific month"""
        deployments = []
        excel_path = self._get_excel_path(project_name, month, year)
        
        if not excel_path.exists():
            return deployments
            
        try:
            wb = openpyxl.load_workbook(excel_path, read_only=True)
            ws = wb.active
            
            # Skip header row
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] is None:  # Skip empty rows
                    continue
                    
                deployment = {
                    'jira_patch_id': row[0],
                    'timestamp': row[1],
                    'project_name': row[2],
                    'component_name': row[3],
                    'environment': row[4],
                    'vcs_url': row[5],
                    'developer_name': row[6],
                    'build_server': row[7],
                    'deploy_server': row[8],
                    'database_name': row[9],
                    'db_backup_location': row[10],
                    'database_script': row[11],
                    'backup_location': row[12],
                    'build_status': row[13] == 'Success',
                    'deploy_status': row[14] == 'Success',
                    'notes': row[15],
                    'deployed_by': row[16]
                }
                deployments.append(deployment)
                
            wb.close()
            
        except Exception as e:
            print(f"Error reading deployments: {str(e)}")
            
        return deployments
        
    def get_all_monthly_deployments(self, month: int, year: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all deployments across all projects for a specific month"""
        all_deployments = {}
        month_folder = self._get_month_folder(month, year)
        
        if not month_folder.exists():
            return all_deployments
            
        # Read all Excel files in the month folder
        for excel_file in month_folder.glob("*.xlsx"):
            project_name = excel_file.stem
            deployments = self.get_monthly_deployments(project_name, month, year)
            if deployments:
                all_deployments[project_name] = deployments
                
        return all_deployments
        
    def get_deployment_stats(self, month: int, year: int) -> Dict[str, Any]:
        """Get deployment statistics for a month"""
        all_deployments = self.get_all_monthly_deployments(month, year)
        
        total_deployments = 0
        successful_builds = 0
        failed_builds = 0
        successful_deploys = 0
        failed_deploys = 0
        project_counts = {}
        component_counts = {'Frontend': 0, 'Backend': 0, 'Backoffice': 0}
        
        for project_name, deployments in all_deployments.items():
            project_counts[project_name] = len(deployments)
            
            for deployment in deployments:
                total_deployments += 1
                
                if deployment['build_status']:
                    successful_builds += 1
                else:
                    failed_builds += 1
                    
                if deployment['deploy_status']:
                    successful_deploys += 1
                else:
                    failed_deploys += 1
                    
                # Count by component type
                component = deployment.get('component_name', '')
                if 'Frontend' in component:
                    component_counts['Frontend'] += 1
                elif 'Backend' in component:
                    component_counts['Backend'] += 1
                elif 'Backoffice' in component:
                    component_counts['Backoffice'] += 1
                    
        return {
            'total_deployments': total_deployments,
            'successful_builds': successful_builds,
            'failed_builds': failed_builds,
            'successful_deploys': successful_deploys,
            'failed_deploys': failed_deploys,
            'build_success_rate': (successful_builds / total_deployments * 100) if total_deployments > 0 else 0,
            'deploy_success_rate': (successful_deploys / total_deployments * 100) if total_deployments > 0 else 0,
            'project_counts': project_counts,
            'component_counts': component_counts
        }
        
    def file_exists(self, project_name: str, month: int, year: int) -> bool:
        """Check if Excel file exists for a project in a specific month"""
        excel_path = self._get_excel_path(project_name, month, year)
        return excel_path.exists()
"""
Excel Manager for Monthly Deployment Tracking
Handles all Excel operations for deployment history
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
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
        "Database Script",
        "Backup Location",
        "Build Status",
        "Deploy Status",
        "Notes",
        "Deployed By"
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
        """Create new Excel file with headers and formatting"""
        wb = Workbook()
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
        
        wb.save(filepath)
        
    def add_deployment(self, project_name: str, deployment_data: Dict[str, Any]) -> bool:
        """Add a deployment record to the monthly Excel file"""
        try:
            # Get current month and year from deployment timestamp
            if 'timestamp' in deployment_data and deployment_data['timestamp']:
                deploy_time = datetime.strptime(deployment_data['timestamp'], "%Y-%m-%d %H:%M:%S")
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
                deployment_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                deployment_data.get('project_name', project_name),
                deployment_data.get('component_name', ''),
                deployment_data.get('environment', 'QA'),
                deployment_data.get('vcs_url', ''),
                deployment_data.get('developer_name', ''),
                deployment_data.get('build_server', ''),
                deployment_data.get('deploy_server', ''),
                deployment_data.get('database_name', ''),
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
            
            return True
            
        except Exception as e:
            print(f"Error adding deployment: {str(e)}")
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
                    'database_script': row[10],
                    'backup_location': row[11],
                    'build_status': row[12] == 'Success',
                    'deploy_status': row[13] == 'Success',
                    'notes': row[14],
                    'deployed_by': row[15]
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
"""Reports API routes"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from datetime import datetime
import calendar

from backend.database import get_db_session
from backend.services.excel_service import ExcelService
from backend.services.pdf_service import PDFReportService
from backend.services import deployment_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/excel")
async def export_excel(
    month: int,
    year: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Export deployments to Excel file"""
    # Validate month and year
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

    # Create Excel service
    excel_service = ExcelService()

    # Read all deployments for the month
    all_deployments = excel_service.read_all_monthly_deployments(month, year)

    # Create a temporary workbook with all data
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Deployments"

    # Add headers
    headers = excel_service.DEPLOYMENT_HEADERS
    ws.append(headers)

    # Style header row
    excel_service._style_header_row(ws)

    # Add data rows
    for deployment in all_deployments:
        row_data = [
            deployment.get("JIRA PATCH ID", ""),
            deployment.get("Timestamp", ""),
            deployment.get("Project Name", ""),
            deployment.get("Component Name", ""),
            deployment.get("Environment", ""),
            deployment.get("SVN/GIT URL", ""),
            deployment.get("Developer Name", ""),
            deployment.get("Build Server", ""),
            deployment.get("Deploy Server", ""),
            deployment.get("Database Name", ""),
            deployment.get("DB Backup Location", ""),
            deployment.get("Database Script", ""),
            deployment.get("Previous Build Backup", ""),
            deployment.get("Build Status", ""),
            deployment.get("Deploy Status", ""),
            deployment.get("Notes", ""),
            deployment.get("Deployed By", "")
        ]
        ws.append(row_data)

    # Save to bytes
    excel_bytes = BytesIO()
    wb.save(excel_bytes)
    excel_bytes.seek(0)

    # Generate filename
    month_name = datetime(year, month, 1).strftime("%b_%Y")
    filename = f"Deployments_{month_name}.xlsx"

    return StreamingResponse(
        iter([excel_bytes.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/pdf")
async def export_pdf(
    month: int,
    year: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Export deployments to PDF report"""
    # Validate month and year
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

    try:
        # Get deployments and stats
        deployments = await deployment_service.get_monthly_deployments(session, month, year)
        stats = await deployment_service.get_deployment_stats(session, month, year)

        # Convert deployments to dict format for PDF service
        deployment_list = []
        for dep in deployments:
            deployment_list.append({
                "jira_patch_id": dep.jira_id or "N/A",
                "timestamp": dep.timestamp.strftime("%d-%b-%Y %I:%M%p") if dep.timestamp else "N/A",
                "project_name": dep.project.name if dep.project else "Unknown",
                "component_name": dep.component.name if dep.component else "Unknown",
                "environment": dep.environment or "Unknown",
                "developer_name": dep.developer_name or "Unknown",
                "deployed_by": dep.deployed_by or "Unknown",
                "build_status": dep.build_status,
                "deploy_status": dep.deploy_status,
            })

        # Convert stats to required format
        pdf_stats = {
            "total": stats["total_deployments"],
            "successful": stats["successful_deployments"],
            "failed": stats["failed_deployments"],
            "success_rate": stats["success_rate"],
            "projects_count": len(stats["by_project"]),
            "components_count": 0,  # Will be calculated from deployments
            "by_project": stats["by_project"],
            "by_environment": stats["by_environment"],
        }

        # Count unique components
        components = set()
        for dep in deployment_list:
            if dep["component_name"] != "Unknown":
                components.add(dep["component_name"])
        pdf_stats["components_count"] = len(components)

        # Generate PDF
        pdf_service = PDFReportService()
        pdf_bytes = pdf_service.generate_report_bytes(
            month=month,
            year=year,
            deployments=deployment_list,
            stats=pdf_stats
        )

        # Generate filename
        month_name = calendar.month_name[month]
        filename = f"{month_name}_{year}_deployment_report.pdf"

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/stats")
async def get_monthly_stats(
    month: int,
    year: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get deployment statistics for a month"""
    # Validate month and year
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

    try:
        stats = await deployment_service.get_deployment_stats(session, month, year)

        return {
            "month": month,
            "year": year,
            "total": stats["total_deployments"],
            "successful": stats["successful_deployments"],
            "failed": stats["failed_deployments"],
            "success_rate": round(stats["success_rate"], 2),
            "by_project": stats["by_project"],
            "by_environment": stats["by_environment"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

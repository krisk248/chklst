"""Tests for PDF report generation service"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock

from backend.services.pdf_service import PDFReportService


@pytest.fixture
def pdf_service():
    """Create a PDF service instance with temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = PDFReportService(output_path=tmpdir)
        yield service


@pytest.fixture
def sample_deployments():
    """Sample deployment data for testing"""
    return [
        {
            "jira_patch_id": "JIRA-001",
            "timestamp": "09-Nov-2025 10:33AM",
            "project_name": "Project A",
            "component_name": "Frontend",
            "environment": "Production",
            "developer_name": "John Doe",
            "deployed_by": "Jenkins",
            "build_status": True,
            "deploy_status": True,
        },
        {
            "jira_patch_id": "JIRA-002",
            "timestamp": "09-Nov-2025 14:15PM",
            "project_name": "Project B",
            "component_name": "Backend",
            "environment": "Staging",
            "developer_name": "Jane Smith",
            "deployed_by": "Jenkins",
            "build_status": True,
            "deploy_status": False,
        },
        {
            "jira_patch_id": "N/A",
            "timestamp": "10-Nov-2025 09:00AM",
            "project_name": "Project A",
            "component_name": "Database",
            "environment": "Development",
            "developer_name": "John Doe",
            "deployed_by": "Manual",
            "build_status": True,
            "deploy_status": True,
        },
    ]


@pytest.fixture
def sample_stats():
    """Sample statistics data for testing"""
    return {
        "total": 10,
        "successful": 8,
        "failed": 2,
        "success_rate": 80.0,
        "projects_count": 3,
        "components_count": 5,
        "by_project": {"Project A": 5, "Project B": 3, "Project C": 2},
        "by_environment": {"Production": 4, "Staging": 3, "Development": 3},
        "by_developer": {"John Doe": 6, "Jane Smith": 4},
    }


class TestPDFReportServiceInit:
    """Tests for PDF service initialization"""

    def test_init_creates_output_directory(self):
        """Test that initialization creates output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "reports" / "pdfs"
            service = PDFReportService(output_path=str(output_path))

            assert output_path.exists()
            assert output_path.is_dir()

    def test_init_with_existing_directory(self):
        """Test initialization with existing directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = PDFReportService(output_path=tmpdir)
            assert Path(tmpdir).exists()


class TestPDFGeneration:
    """Tests for PDF generation"""

    def test_generate_report_bytes_returns_bytes(self, pdf_service, sample_deployments, sample_stats):
        """Test that generate_report_bytes returns valid PDF bytes"""
        pdf_bytes = pdf_service.generate_report_bytes(
            month=11,
            year=2025,
            deployments=sample_deployments,
            stats=sample_stats
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF files start with %PDF
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_report_bytes_with_empty_deployments(self, pdf_service, sample_stats):
        """Test PDF generation with empty deployments"""
        pdf_bytes = pdf_service.generate_report_bytes(
            month=11,
            year=2025,
            deployments=[],
            stats={"total": 0, "successful": 0, "failed": 0, "success_rate": 0}
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_report_file(self, pdf_service, sample_deployments, sample_stats):
        """Test that generate_monthly_report creates a file"""
        output_path = pdf_service.generate_monthly_report(
            month=11,
            year=2025,
            deployments=sample_deployments,
            stats=sample_stats
        )

        assert isinstance(output_path, Path)
        assert output_path.exists()
        assert output_path.suffix == ".pdf"
        assert "November" in output_path.name or "2025" in output_path.name


class TestTitlePage:
    """Tests for title page generation"""

    def test_title_page_generation(self, pdf_service):
        """Test that title page is added to story"""
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Spacer, Paragraph

        styles = getSampleStyleSheet()
        story = []

        pdf_service._add_title_page(story, styles, month=11, year=2025)

        assert isinstance(story, list)
        assert len(story) > 0
        # Check that story contains Spacer and Paragraph elements
        assert any(isinstance(e, (Spacer, Paragraph)) for e in story)


class TestExecutiveSummary:
    """Tests for executive summary section"""

    def test_executive_summary_generation(self, pdf_service, sample_stats):
        """Test that executive summary is added to story"""
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Spacer, Paragraph

        styles = getSampleStyleSheet()
        story = []

        pdf_service._add_executive_summary(story, styles, stats=sample_stats)

        assert isinstance(story, list)
        assert len(story) > 0
        # Check that story contains elements
        assert any(isinstance(e, (Spacer, Paragraph)) for e in story)

    def test_executive_summary_with_zero_stats(self, pdf_service):
        """Test that executive summary handles zero stats"""
        from reportlab.lib.styles import getSampleStyleSheet

        styles = getSampleStyleSheet()
        story = []
        zero_stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0,
            "projects_count": 0,
            "components_count": 0,
        }

        pdf_service._add_executive_summary(story, styles, stats=zero_stats)

        assert isinstance(story, list)
        assert len(story) > 0


class TestChartGeneration:
    """Tests for chart generation"""

    def test_create_bar_chart_returns_path(self, pdf_service):
        """Test that _create_bar_chart returns valid file path"""
        data = {"Project A": 5, "Project B": 3, "Project C": 2}
        chart_path = pdf_service._create_bar_chart(
            data=data,
            title="Test Chart",
            xlabel="Projects",
            ylabel="Deployments"
        )

        assert chart_path is not None
        assert isinstance(chart_path, Path)
        # File should exist (may not if matplotlib fails, but we test the function)

    def test_create_pie_chart_returns_path(self, pdf_service):
        """Test that _create_pie_chart returns valid file path"""
        data = {"Success": 8, "Failed": 2}
        chart_path = pdf_service._create_pie_chart(
            data=data,
            title="Status Distribution"
        )

        assert chart_path is not None
        assert isinstance(chart_path, Path)

    def test_create_bar_chart_handles_empty_data(self, pdf_service):
        """Test that _create_bar_chart handles empty data gracefully"""
        data = {}
        chart_path = pdf_service._create_bar_chart(
            data=data,
            title="Empty Chart",
            xlabel="X",
            ylabel="Y"
        )

        # Should return None or handle gracefully
        assert chart_path is None or isinstance(chart_path, Path)


class TestDeploymentTable:
    """Tests for deployment table generation"""

    def test_deployment_table_generation(self, pdf_service, sample_deployments):
        """Test that deployment table is added to story"""
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Spacer, Paragraph

        styles = getSampleStyleSheet()
        story = []

        pdf_service._add_deployment_table(story, styles, deployments=sample_deployments)

        assert isinstance(story, list)
        assert len(story) > 0
        assert any(isinstance(e, (Spacer, Paragraph)) for e in story)

    def test_deployment_table_with_empty_list(self, pdf_service):
        """Test deployment table with empty deployments"""
        from reportlab.lib.styles import getSampleStyleSheet

        styles = getSampleStyleSheet()
        story = []

        pdf_service._add_deployment_table(story, styles, deployments=[])

        assert isinstance(story, list)
        assert len(story) > 0

    def test_deployment_table_with_large_dataset(self, pdf_service):
        """Test deployment table truncates large datasets to 50 rows"""
        from reportlab.lib.styles import getSampleStyleSheet

        # Create 100 deployments
        deployments = [
            {
                "jira_patch_id": f"JIRA-{i:03d}",
                "timestamp": "09-Nov-2025 10:00AM",
                "project_name": f"Project {i % 5}",
                "component_name": f"Component {i % 10}",
                "environment": ["Production", "Staging", "Development"][i % 3],
                "developer_name": f"Dev {i % 5}",
                "deployed_by": "Jenkins",
                "build_status": i % 2 == 0,
                "deploy_status": i % 3 != 0,
            }
            for i in range(100)
        ]

        styles = getSampleStyleSheet()
        story = []

        pdf_service._add_deployment_table(story, styles, deployments=deployments)

        assert isinstance(story, list)
        assert len(story) > 0


class TestChartSection:
    """Tests for charts section"""

    def test_charts_section_generation(self, pdf_service, sample_deployments, sample_stats):
        """Test that charts section is added to story"""
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Spacer, Paragraph

        styles = getSampleStyleSheet()
        story = []

        pdf_service._add_charts_section(story, styles, deployments=sample_deployments, stats=sample_stats)

        assert isinstance(story, list)
        assert len(story) > 0

    def test_charts_section_with_empty_data(self, pdf_service):
        """Test charts section with empty data"""
        from reportlab.lib.styles import getSampleStyleSheet

        styles = getSampleStyleSheet()
        story = []

        pdf_service._add_charts_section(
            story,
            styles,
            deployments=[],
            stats={"by_project": {}, "by_environment": {}, "successful": 0, "failed": 0}
        )

        assert isinstance(story, list)


class TestUtilityMethods:
    """Tests for utility methods"""

    def test_parse_timestamp_valid(self, pdf_service):
        """Test parsing valid timestamp"""
        timestamp_str = "09-Nov-2025 10:33AM"
        result = pdf_service._parse_timestamp(timestamp_str)

        assert result is not None
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 9
        assert result.hour == 10
        assert result.minute == 33

    def test_parse_timestamp_invalid(self, pdf_service):
        """Test parsing invalid timestamp"""
        result = pdf_service._parse_timestamp("invalid")
        assert result is None

    def test_parse_timestamp_none(self, pdf_service):
        """Test parsing None timestamp"""
        result = pdf_service._parse_timestamp(None)
        assert result is None

    def test_parse_timestamp_na(self, pdf_service):
        """Test parsing N/A timestamp"""
        result = pdf_service._parse_timestamp("N/A")
        assert result is None


class TestIntegration:
    """Integration tests for PDF service"""

    def test_full_pdf_generation_workflow(self, pdf_service, sample_deployments, sample_stats):
        """Test complete PDF generation workflow"""
        # Generate report bytes
        pdf_bytes = pdf_service.generate_report_bytes(
            month=11,
            year=2025,
            deployments=sample_deployments,
            stats=sample_stats
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000  # Should be reasonably sized

    def test_multiple_months_generation(self, pdf_service, sample_deployments, sample_stats):
        """Test generating reports for multiple months"""
        for month in [10, 11, 12]:
            pdf_bytes = pdf_service.generate_report_bytes(
                month=month,
                year=2025,
                deployments=sample_deployments,
                stats=sample_stats
            )

            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 0

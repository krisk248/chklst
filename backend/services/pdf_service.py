"""PDF Report generation service for deployment statistics"""

import calendar
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
from io import BytesIO
import tempfile

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFReportService:
    """Generate PDF reports with comprehensive deployment statistics and charts"""

    def __init__(self, output_path: str = "reports/pdfs"):
        """Initialize PDF service with output directory"""
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(tempfile.gettempdir()) / "chklst_charts"
        self.temp_dir.mkdir(exist_ok=True)

    def generate_monthly_report(
        self,
        month: int,
        year: int,
        deployments: list,
        stats: dict
    ) -> Path:
        """Generate comprehensive monthly deployment report PDF"""
        try:
            month_name = calendar.month_name[month]
            output_file = self.output_path / f"{month_name}_{year}_deployment_report.pdf"

            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=A4,
                topMargin=15*mm,
                bottomMargin=15*mm,
                leftMargin=20*mm,
                rightMargin=20*mm
            )

            # Build content
            story = []
            styles = getSampleStyleSheet()

            # Add title page
            self._add_title_page(story, styles, month, year)
            story.append(PageBreak())

            # Add executive summary
            self._add_executive_summary(story, styles, stats)
            story.append(PageBreak())

            # Add charts section
            self._add_charts_section(story, styles, deployments, stats)
            story.append(PageBreak())

            # Add deployment table
            self._add_deployment_table(story, styles, deployments)

            # Build PDF
            doc.build(story)

            return output_file

        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            raise

    def generate_report_bytes(
        self,
        month: int,
        year: int,
        deployments: list,
        stats: dict
    ) -> bytes:
        """Generate PDF and return as bytes for streaming response"""
        try:
            buffer = BytesIO()

            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                topMargin=15*mm,
                bottomMargin=15*mm,
                leftMargin=20*mm,
                rightMargin=20*mm
            )

            # Build content
            story = []
            styles = getSampleStyleSheet()

            # Add all sections
            self._add_title_page(story, styles, month, year)
            story.append(PageBreak())
            self._add_executive_summary(story, styles, stats)
            story.append(PageBreak())
            self._add_charts_section(story, styles, deployments, stats)
            story.append(PageBreak())
            self._add_deployment_table(story, styles, deployments)

            doc.build(story)

            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            print(f"Error generating PDF bytes: {str(e)}")
            raise

    def _add_title_page(self, story, styles, month, year):
        """Add professional title page"""
        try:
            # Main title
            title_style = ParagraphStyle(
                'MainTitle',
                parent=styles['Title'],
                fontSize=28,
                textColor=colors.HexColor('#1a5490'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )

            title = Paragraph("DEPLOYMENT REPORT", title_style)
            story.append(Spacer(1, 50))
            story.append(title)

            # Month and year
            month_style = ParagraphStyle(
                'MonthYear',
                parent=styles['Normal'],
                fontSize=20,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )

            month_name = calendar.month_name[month]
            last_day = calendar.monthrange(year, month)[1]

            month_para = Paragraph(f"<b>Month:</b> {month_name} {year}", month_style)
            period_para = Paragraph(
                f"<b>Report Period:</b> 01-{month_name[:3]}-{year} to {last_day}-{month_name[:3]}-{year}",
                month_style
            )

            story.append(Spacer(1, 30))
            story.append(month_para)
            story.append(period_para)

            # Prepared by section
            story.append(Spacer(1, 80))

            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=8,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )

            story.append(Paragraph("<b>System:</b> chklst Deployment Tracker", info_style))
            story.append(Paragraph(f"<b>Generated On:</b> {datetime.now().strftime('%d-%b-%Y %I:%M%p')}", info_style))

        except Exception as e:
            print(f"Error adding title page: {str(e)}")

    def _add_executive_summary(self, story, styles, stats):
        """Add executive summary with highlights"""
        try:
            # Section title
            section_title = Paragraph("EXECUTIVE SUMMARY", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # Report Overview table
            overview_data = [
                ['Metric', 'Value'],
                ['Total Deployments', str(stats.get('total', 0))],
                ['Successful', str(stats.get('successful', 0))],
                ['Failed', str(stats.get('failed', 0))],
                ['Success Rate', f"{stats.get('success_rate', 0):.1f}%"],
                ['Projects', str(stats.get('projects_count', 0))],
                ['Components', str(stats.get('components_count', 0))],
            ]

            overview_table = Table(overview_data, colWidths=[3.5*inch, 2*inch])
            overview_table.setStyle(self._get_table_style())
            story.append(overview_table)

        except Exception as e:
            print(f"Error adding executive summary: {str(e)}")
            story.append(Paragraph(f"Error loading summary: {str(e)}", styles['Normal']))

    def _add_charts_section(self, story, styles, deployments, stats):
        """Add charts section with visualizations"""
        try:
            # Section title
            section_title = Paragraph("ANALYTICS", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # 1. Deployments by Project (Bar chart)
            if stats.get('by_project'):
                subsection = Paragraph("Deployments by Project", self._get_subsection_style(styles))
                story.append(subsection)
                story.append(Spacer(1, 8))

                chart_path = self._create_bar_chart(
                    stats['by_project'],
                    "Deployments by Project",
                    "Project",
                    "Count"
                )
                if chart_path:
                    story.append(Image(str(chart_path), width=5*inch, height=3*inch))
                    story.append(Spacer(1, 15))

            # 2. Status Distribution (Pie chart)
            status_data = {
                'Success': stats.get('successful', 0),
                'Failed': stats.get('failed', 0)
            }
            if sum(status_data.values()) > 0:
                subsection = Paragraph("Deployment Status", self._get_subsection_style(styles))
                story.append(subsection)
                story.append(Spacer(1, 8))

                chart_path = self._create_pie_chart(status_data, "Status Distribution")
                if chart_path:
                    story.append(Image(str(chart_path), width=4*inch, height=3*inch))
                    story.append(Spacer(1, 15))

            # 3. Environment Distribution
            if stats.get('by_environment'):
                subsection = Paragraph("Deployments by Environment", self._get_subsection_style(styles))
                story.append(subsection)
                story.append(Spacer(1, 8))

                chart_path = self._create_bar_chart(
                    stats['by_environment'],
                    "Deployments by Environment",
                    "Environment",
                    "Count"
                )
                if chart_path:
                    story.append(Image(str(chart_path), width=5*inch, height=3*inch))

        except Exception as e:
            print(f"Error adding charts section: {str(e)}")
            story.append(Paragraph(f"Error loading charts: {str(e)}", styles['Normal']))

    def _add_deployment_table(self, story, styles, deployments):
        """Add detailed deployment table"""
        try:
            # Section title
            section_title = Paragraph("DEPLOYMENT DETAILS", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            if not deployments:
                story.append(Paragraph("No deployments recorded for this period.", styles['Normal']))
                return

            # Table headers
            headers = ["Date", "JIRA ID", "Project", "Component", "Env", "Build", "Deploy"]
            table_data = [headers]

            # Limit to 50 rows for PDF
            for dep in deployments[:50]:
                row = [
                    dep.get('timestamp', 'N/A')[:10] if dep.get('timestamp') else 'N/A',
                    dep.get('jira_patch_id', 'N/A')[:15],
                    dep.get('project_name', 'N/A')[:15],
                    dep.get('component_name', 'N/A')[:12],
                    dep.get('environment', 'N/A')[:8],
                    '✓' if dep.get('build_status') else '✗',
                    '✓' if dep.get('deploy_status') else '✗'
                ]
                table_data.append(row)

            table = Table(table_data, colWidths=[1*inch, 1*inch, 1.2*inch, 1*inch, 0.7*inch, 0.5*inch, 0.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))

            story.append(table)

            if len(deployments) > 50:
                story.append(Spacer(1, 10))
                note = Paragraph(
                    f"<i>Note: Showing first 50 deployments out of {len(deployments)} total.</i>",
                    styles['Normal']
                )
                story.append(note)

        except Exception as e:
            print(f"Error adding deployment table: {str(e)}")
            story.append(Paragraph(f"Error loading table: {str(e)}", styles['Normal']))

    def _create_bar_chart(self, data: dict, title: str, xlabel: str, ylabel: str) -> Path:
        """Generate bar chart and return path to image"""
        try:
            if not data:
                return None

            plt.figure(figsize=(8, 4))
            plt.style.use('default')

            bars = plt.bar(list(data.keys()), list(data.values()), color='#1a5490')
            plt.title(title, fontsize=12, fontweight='bold')
            plt.xlabel(xlabel, fontweight='bold')
            plt.ylabel(ylabel, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            chart_path = self.temp_dir / f"bar_{title.replace(' ', '_')}.png"
            plt.savefig(str(chart_path), dpi=100, bbox_inches='tight')
            plt.close()

            return chart_path

        except Exception as e:
            print(f"Error creating bar chart: {str(e)}")
            plt.close()
            return None

    def _create_pie_chart(self, data: dict, title: str) -> Path:
        """Generate pie chart and return path to image"""
        try:
            if not data or sum(data.values()) == 0:
                return None

            plt.figure(figsize=(6, 4))
            plt.style.use('default')

            colors_list = ['#2ecc71', '#e74c3c']  # Green for success, red for failed
            plt.pie(list(data.values()), labels=list(data.keys()), autopct='%1.1f%%', colors=colors_list)
            plt.title(title, fontsize=12, fontweight='bold')
            plt.tight_layout()

            chart_path = self.temp_dir / f"pie_{title.replace(' ', '_')}.png"
            plt.savefig(str(chart_path), dpi=100, bbox_inches='tight')
            plt.close()

            return chart_path

        except Exception as e:
            print(f"Error creating pie chart: {str(e)}")
            plt.close()
            return None

    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime object"""
        try:
            if not timestamp_str or timestamp_str == 'N/A':
                return None
            # Format: "09-Nov-2025 10:33AM" or "09-Nov-2025 14:15PM"
            return datetime.strptime(timestamp_str, "%d-%b-%Y %I:%M%p")
        except Exception:
            return None

    def _get_section_style(self, styles):
        """Get section title style"""
        return ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

    def _get_subsection_style(self, styles):
        """Get subsection title style"""
        return ParagraphStyle(
            'SubsectionTitle',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )

    def _get_table_style(self):
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ])

    def cleanup_temp_files(self):
        """Clean up temporary chart files"""
        try:
            for file in self.temp_dir.glob("*.png"):
                file.unlink()
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")

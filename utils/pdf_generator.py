"""
Enhanced PDF Report Generator for Deployment Statistics
Creates comprehensive monthly PDF reports with detailed analytics
"""

import os
import calendar
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid threading warnings
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import tempfile


class PDFGenerator:
    """Generate enhanced PDF reports with comprehensive deployment statistics and charts"""

    def __init__(self, excel_manager):
        self.excel_manager = excel_manager
        self.temp_dir = Path(tempfile.gettempdir()) / "chklst_charts"
        self.temp_dir.mkdir(exist_ok=True)

    def generate_monthly_report(self, month: int, year: int) -> str:
        """Generate comprehensive monthly PDF report"""
        try:
            # Create output directory
            output_dir = Path("reports") / "pdfs"
            output_dir.mkdir(parents=True, exist_ok=True)

            month_name = calendar.month_name[month]
            output_file = output_dir / f"{month_name}_{year}_deployment_report.pdf"

            # Get data
            stats = self.excel_manager.get_deployment_stats(month, year)
            all_deployments = self.excel_manager.get_all_monthly_deployments(month, year)

            # Flatten all deployments
            flat_deployments = []
            for project_name, deployments in all_deployments.items():
                flat_deployments.extend(deployments)

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
            self._add_executive_summary(story, styles, stats, flat_deployments, month, year)
            story.append(PageBreak())

            # Add time-based analytics
            self._add_time_analytics(story, styles, flat_deployments, month, year)
            story.append(PageBreak())

            # Add developer analytics
            self._add_developer_analytics(story, styles, flat_deployments)
            story.append(PageBreak())

            # Add project analytics
            self._add_project_analytics(story, styles, all_deployments, stats)
            story.append(PageBreak())

            # Add component analytics
            self._add_component_analytics(story, styles, flat_deployments, month, year)
            story.append(PageBreak())

            # Add JIRA compliance
            self._add_jira_compliance(story, styles, flat_deployments, all_deployments, month, year)

            # Build PDF
            doc.build(story)

            return str(output_file)

        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
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

            title = Paragraph("TTS QA DEPLOYMENT REPORT", title_style)
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
            # Calculate first and last day
            last_day = calendar.monthrange(year, month)[1]

            month_para = Paragraph(f"<b>Month:</b> {month_name} {year}", month_style)
            period_para = Paragraph(f"<b>Report Period:</b> 01-{month_name[:3]}-{year} to {last_day}-{month_name[:3]}-{year}", month_style)

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

            story.append(Paragraph("<b>Prepared By:</b> Kannan Giridharan", info_style))
            story.append(Paragraph("<b>Team:</b> TTS DevSecOps Team", info_style))
            story.append(Paragraph("<b>Department:</b> IT Operations", info_style))
            story.append(Paragraph("<b>Organization:</b> TTS", info_style))

            # Generated on
            story.append(Spacer(1, 80))
            gen_time = datetime.now().strftime("%d-%b-%Y %I:%M%p")
            story.append(Paragraph(f"<b>Generated On:</b> {gen_time}", info_style))
            story.append(Paragraph("<b>Report Version:</b> 2.0", info_style))

        except Exception as e:
            print(f"Error adding title page: {str(e)}")

    def _add_executive_summary(self, story, styles, stats, flat_deployments, month, year):
        """Add executive summary with highlights"""
        try:
            # Section title
            section_title = Paragraph("📊 EXECUTIVE SUMMARY", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # Report Overview table
            overview_data = [
                ['Metric', 'Value'],
                ['Total Deployments', str(stats['total_deployments'])],
                ['Active Projects', str(len(stats.get('project_counts', {})))],
                ['Active Developers', str(len(set(d.get('developer_name', '') for d in flat_deployments if d.get('developer_name'))))],
                ['Components Deployed', str(len(set(d.get('component_name', '') for d in flat_deployments if d.get('component_name'))))],
                ['JIRA Compliance Rate', f"{self._calculate_jira_compliance(flat_deployments):.1f}%"],
            ]

            overview_table = Table(overview_data, colWidths=[3.5*inch, 2*inch])
            overview_table.setStyle(self._get_table_style())
            story.append(overview_table)
            story.append(Spacer(1, 20))

            # Monthly Highlights
            highlights_title = Paragraph("🎯 MONTHLY HIGHLIGHTS", self._get_subsection_style(styles))
            story.append(highlights_title)
            story.append(Spacer(1, 8))

            highlights = self._calculate_highlights(flat_deployments, stats)

            highlights_data = [
                ['Highlight', 'Details'],
                ['Most Active Project', highlights['most_active_project']],
                ['Most Active Developer', highlights['most_active_developer']],
                ['Busiest Deployment Day', highlights['busiest_day']],
                ['Peak Deployment Time', highlights['peak_time']],
                ['Most Deployed Component', highlights['most_deployed_component']],
            ]

            highlights_table = Table(highlights_data, colWidths=[2.5*inch, 3*inch])
            highlights_table.setStyle(self._get_table_style())
            story.append(highlights_table)

        except Exception as e:
            print(f"Error adding executive summary: {str(e)}")
            story.append(Paragraph(f"Error loading executive summary: {str(e)}", styles['Normal']))

    def _add_time_analytics(self, story, styles, flat_deployments, month, year):
        """Add time-based analytics section"""
        try:
            # Section title
            section_title = Paragraph("📅 TIME-BASED ANALYTICS", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # 1.1 Deployment Timeline
            subsection = Paragraph("Deployment Timeline", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            timeline_chart = self._create_timeline_chart(flat_deployments, month, year)
            if timeline_chart:
                story.append(Image(timeline_chart, width=6*inch, height=3*inch))
            story.append(Spacer(1, 15))

            # 1.2 Day of Week Analysis
            subsection = Paragraph("Day of Week Analysis", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            dow_chart = self._create_day_of_week_chart(flat_deployments, month, year)
            if dow_chart:
                story.append(Image(dow_chart, width=6*inch, height=3*inch))

            dow_stats = self._calculate_day_of_week_stats(flat_deployments)
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<b>Insight:</b> {dow_stats['insight']}", styles['Normal']))
            story.append(Spacer(1, 15))

            # 1.3 Time of Day Distribution
            subsection = Paragraph("Time of Day Distribution", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            tod_chart = self._create_time_of_day_chart(flat_deployments, month, year)
            if tod_chart:
                story.append(Image(tod_chart, width=5*inch, height=3.5*inch))
            story.append(Spacer(1, 15))

            # 1.4 Week-wise Breakdown
            subsection = Paragraph("Week-wise Breakdown", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            week_chart = self._create_week_wise_chart(flat_deployments, month, year)
            if week_chart:
                story.append(Image(week_chart, width=6*inch, height=3*inch))

        except Exception as e:
            print(f"Error adding time analytics: {str(e)}")
            story.append(Paragraph(f"Error loading time analytics: {str(e)}", styles['Normal']))

    def _add_developer_analytics(self, story, styles, flat_deployments):
        """Add developer analytics section"""
        try:
            # Section title
            section_title = Paragraph("👨‍💻 DEVELOPER ANALYTICS", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # 2.4 Developer vs Component Analysis
            subsection = Paragraph("Developer vs Component Analysis", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            dev_comp_data = self._calculate_developer_component_analysis(flat_deployments)

            table_data = [['Developer', 'Primary Component', 'Count', 'Secondary Component', 'Count']]

            for dev_name, data in list(dev_comp_data.items())[:10]:  # Top 10
                primary = data['components'][0] if len(data['components']) > 0 else ('N/A', 0)
                secondary = data['components'][1] if len(data['components']) > 1 else ('N/A', 0)

                table_data.append([
                    dev_name,
                    primary[0][:20],  # Truncate long names
                    str(primary[1]),
                    secondary[0][:20],
                    str(secondary[1])
                ])

            if len(table_data) > 1:
                dev_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 0.7*inch, 1.5*inch, 0.7*inch])
                dev_table.setStyle(self._get_table_style())
                story.append(dev_table)
            else:
                story.append(Paragraph("No developer data available.", styles['Normal']))

        except Exception as e:
            print(f"Error adding developer analytics: {str(e)}")
            story.append(Paragraph(f"Error loading developer analytics: {str(e)}", styles['Normal']))

    def _add_project_analytics(self, story, styles, all_deployments, stats):
        """Add project analytics section"""
        try:
            # Section title
            section_title = Paragraph("📁 PROJECT ANALYTICS", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # 3.2 Projects Missing JIRA Tracking
            subsection = Paragraph("Projects Missing JIRA Tracking", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            jira_tracking = self._calculate_project_jira_tracking(all_deployments)

            table_data = [['Project', 'Total', 'JIRA Tracked', 'N/A Count', 'N/A %']]

            for project, data in sorted(jira_tracking.items(), key=lambda x: x[1]['na_percentage'], reverse=True):
                table_data.append([
                    project[:25],
                    str(data['total']),
                    str(data['tracked']),
                    str(data['na_count']),
                    f"{data['na_percentage']:.1f}%"
                ])

            if len(table_data) > 1:
                jira_table = Table(table_data, colWidths=[2*inch, 0.8*inch, 1.2*inch, 1*inch, 0.8*inch])
                jira_table.setStyle(self._get_table_style())
                story.append(jira_table)
            story.append(Spacer(1, 20))

            # 3.3 Most Active vs Least Active Projects
            subsection = Paragraph("Most Active vs Least Active Projects", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            project_counts = stats.get('project_counts', {})
            sorted_projects = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)

            # Create side-by-side tables
            top_5 = sorted_projects[:5]
            bottom_5 = sorted_projects[-5:][::-1]  # Reverse to show least first

            table_data = [['Top 5 Most Active', 'Deploys', 'Bottom 5 Least Active', 'Deploys']]

            max_len = max(len(top_5), len(bottom_5))
            for i in range(max_len):
                top_project = top_5[i] if i < len(top_5) else ('', '')
                bottom_project = bottom_5[i] if i < len(bottom_5) else ('', '')

                table_data.append([
                    top_project[0][:20] if top_project[0] else '',
                    str(top_project[1]) if top_project[1] else '',
                    bottom_project[0][:20] if bottom_project[0] else '',
                    str(bottom_project[1]) if bottom_project[1] else ''
                ])

            if len(table_data) > 1:
                comparison_table = Table(table_data, colWidths=[2*inch, 0.8*inch, 2*inch, 0.8*inch])
                comparison_table.setStyle(self._get_table_style())
                story.append(comparison_table)

        except Exception as e:
            print(f"Error adding project analytics: {str(e)}")
            story.append(Paragraph(f"Error loading project analytics: {str(e)}", styles['Normal']))

    def _add_component_analytics(self, story, styles, flat_deployments, month, year):
        """Add component analytics section"""
        try:
            # Section title
            section_title = Paragraph("🧩 COMPONENT ANALYTICS", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # 4.2 Component Deployment Frequency
            subsection = Paragraph("Component Deployment Frequency", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            comp_chart = self._create_component_frequency_chart(flat_deployments, month, year)
            if comp_chart:
                story.append(Image(comp_chart, width=6*inch, height=3.5*inch))

            story.append(Spacer(1, 10))

            # Component frequency table
            comp_counts = Counter(d.get('component_name', 'Unknown') for d in flat_deployments if d.get('component_name'))
            total = len(flat_deployments)

            table_data = [['Component', 'Deployments', '% of Total']]

            for comp_name, count in comp_counts.most_common():
                percentage = (count / total * 100) if total > 0 else 0
                table_data.append([
                    comp_name[:30],
                    str(count),
                    f"{percentage:.1f}%"
                ])

            if len(table_data) > 1:
                comp_table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                comp_table.setStyle(self._get_table_style())
                story.append(comp_table)

        except Exception as e:
            print(f"Error adding component analytics: {str(e)}")
            story.append(Paragraph(f"Error loading component analytics: {str(e)}", styles['Normal']))

    def _add_jira_compliance(self, story, styles, flat_deployments, all_deployments, month, year):
        """Add JIRA compliance section"""
        try:
            # Section title
            section_title = Paragraph("🎫 JIRA COMPLIANCE TRACKING", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # 8.1 Overall JIRA Compliance
            subsection = Paragraph("Overall JIRA Tracking Compliance", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            compliance_rate = self._calculate_jira_compliance(flat_deployments)
            total = len(flat_deployments)
            tracked = sum(1 for d in flat_deployments if d.get('jira_patch_id', 'N/A') != 'N/A')
            na_count = total - tracked

            # Gauge chart
            gauge_chart = self._create_jira_gauge_chart(compliance_rate, month, year)
            if gauge_chart:
                story.append(Image(gauge_chart, width=4*inch, height=3*inch))

            story.append(Spacer(1, 10))

            # Compliance metrics
            comp_data = [
                ['Metric', 'Value'],
                ['Total Deployments', str(total)],
                ['With JIRA ID', f"{tracked} ({compliance_rate:.1f}%)"],
                ['Without JIRA (N/A)', f"{na_count} ({100-compliance_rate:.1f}%)"],
                ['Compliance Status', self._get_compliance_status(compliance_rate)]
            ]

            comp_table = Table(comp_data, colWidths=[2.5*inch, 2.5*inch])
            comp_table.setStyle(self._get_table_style())
            story.append(comp_table)

            story.append(Spacer(1, 20))

            # 8.2 Projects with Poor JIRA Compliance
            subsection = Paragraph("Projects with Poor JIRA Compliance (<70%)", self._get_subsection_style(styles))
            story.append(subsection)
            story.append(Spacer(1, 8))

            poor_compliance = self._get_poor_jira_compliance_projects(all_deployments)

            if poor_compliance:
                table_data = [['Project', 'Total', 'JIRA Tracked', 'Compliance %', 'Status']]

                for project, data in poor_compliance:
                    status = '🔴 Critical' if data['compliance'] < 50 else '🟡 Warning'
                    table_data.append([
                        project[:25],
                        str(data['total']),
                        str(data['tracked']),
                        f"{data['compliance']:.1f}%",
                        status
                    ])

                poor_table = Table(table_data, colWidths=[2*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                poor_table.setStyle(self._get_table_style())
                story.append(poor_table)
            else:
                story.append(Paragraph("✅ All projects have good JIRA compliance (≥70%)", styles['Normal']))

            # Add footer since this is the last page
            story.append(Spacer(1, 40))
            footer_text = f"Generated on {datetime.now().strftime('%d-%b-%Y %I:%M%p')} | TTS Deployment Tracking System | Report Version 2.0"
            footer = Paragraph(footer_text, self._get_footer_style(styles))
            story.append(footer)

        except Exception as e:
            print(f"Error adding JIRA compliance: {str(e)}")
            story.append(Paragraph(f"Error loading JIRA compliance: {str(e)}", styles['Normal']))

    def _add_red_flags(self, story, styles, flat_deployments, all_deployments):
        """Add red flags and attention required section"""
        try:
            # Section title
            section_title = Paragraph("⚠️ ATTENTION REQUIRED", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            red_flags = []

            # Check for low JIRA compliance projects
            poor_jira = self._get_poor_jira_compliance_projects(all_deployments, threshold=50)
            if poor_jira:
                red_flags.append(f"⚠️ <b>Projects with Low JIRA Compliance (&lt;50%):</b> {len(poor_jira)} project(s)")
                for project, data in poor_jira[:5]:
                    red_flags.append(f"   • {project}: {data['compliance']:.1f}% compliance")

            # Check for high deployment frequency (might indicate inefficiency)
            high_freq_devs = self._get_high_frequency_developers(flat_deployments, threshold=10)
            if high_freq_devs:
                red_flags.append(f"⚠️ <b>Developers with High Deployment Frequency (&gt;10/month):</b>")
                for dev, count in high_freq_devs[:5]:
                    red_flags.append(f"   • {dev}: {count} deployments (possible inefficiency indicator)")

            # Check for inactive projects
            inactive_projects = self._get_inactive_projects(all_deployments)
            if inactive_projects:
                red_flags.append(f"⚠️ <b>Inactive Projects (0 deployments):</b> {len(inactive_projects)} project(s)")

            # Check for deployments outside business hours
            after_hours = self._get_after_hours_deployments(flat_deployments)
            if after_hours['count'] > 0:
                percentage = (after_hours['count'] / len(flat_deployments) * 100) if len(flat_deployments) > 0 else 0
                red_flags.append(f"⚠️ <b>After-Hours Deployments:</b> {after_hours['count']} ({percentage:.1f}%) deployments outside 8AM-6PM")

            # Display red flags
            if red_flags:
                for flag in red_flags:
                    story.append(Paragraph(flag, styles['Normal']))
                    story.append(Spacer(1, 8))
            else:
                story.append(Paragraph("✅ No major red flags detected. All systems operating normally.", styles['Normal']))

        except Exception as e:
            print(f"Error adding red flags: {str(e)}")
            story.append(Paragraph(f"Error loading red flags: {str(e)}", styles['Normal']))

    def _add_deployment_log(self, story, styles, flat_deployments):
        """Add detailed deployment log"""
        try:
            # Section title
            section_title = Paragraph("📝 DETAILED DEPLOYMENT LOG", self._get_section_style(styles))
            story.append(section_title)
            story.append(Spacer(1, 12))

            # Sort by timestamp
            sorted_deployments = sorted(flat_deployments, key=lambda x: x.get('timestamp', ''), reverse=True)

            if not sorted_deployments:
                story.append(Paragraph("No deployments found for this month.", styles['Normal']))
                return

            # Create table
            table_data = [['Date & Time', 'JIRA ID', 'Project', 'Component', 'Developer', 'Deployed By', 'Env']]

            for deployment in sorted_deployments[:50]:  # Limit to 50 for PDF
                table_data.append([
                    deployment.get('timestamp', 'N/A')[:16],  # Truncate time
                    deployment.get('jira_patch_id', 'N/A')[:15],
                    deployment.get('project_name', '')[:15],
                    deployment.get('component_name', '')[:15],
                    deployment.get('developer_name', '')[:12],
                    deployment.get('deployed_by', '')[:12],
                    deployment.get('environment', '')[:5]
                ])

            deploy_table = Table(table_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 0.9*inch, 0.9*inch, 0.5*inch])
            deploy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))

            story.append(deploy_table)

            if len(sorted_deployments) > 50:
                story.append(Spacer(1, 10))
                note = Paragraph(f"<i>Note: Showing most recent 50 deployments out of {len(sorted_deployments)} total.</i>",
                               styles['Normal'])
                story.append(note)

            # Footer
            story.append(Spacer(1, 20))
            footer_text = f"Generated on {datetime.now().strftime('%d-%b-%Y %I:%M%p')} | TTS Deployment Tracking System | Report Version 2.0"
            footer = Paragraph(footer_text, self._get_footer_style(styles))
            story.append(footer)

        except Exception as e:
            print(f"Error adding deployment log: {str(e)}")
            story.append(Paragraph(f"Error loading deployment log: {str(e)}", styles['Normal']))

    # ==================== HELPER FUNCTIONS ====================

    def _get_section_style(self, styles):
        """Get section title style"""
        return ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )

    def _get_subsection_style(self, styles):
        """Get subsection title style"""
        return ParagraphStyle(
            'SubsectionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )

    def _get_footer_style(self, styles):
        """Get footer style"""
        return ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
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

    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime object"""
        try:
            if not timestamp_str or timestamp_str == 'N/A':
                return None
            # Format: "09-Nov-2025 10:33AM"
            return datetime.strptime(timestamp_str, "%d-%b-%Y %I:%M%p")
        except:
            return None

    def _calculate_jira_compliance(self, deployments):
        """Calculate JIRA compliance percentage"""
        try:
            total = len(deployments)
            if total == 0:
                return 0.0
            tracked = sum(1 for d in deployments if d.get('jira_patch_id', 'N/A') != 'N/A')
            return (tracked / total * 100)
        except:
            return 0.0

    def _get_compliance_status(self, rate):
        """Get compliance status based on rate"""
        if rate >= 90:
            return '🟢 Excellent'
        elif rate >= 70:
            return '🟡 Good'
        else:
            return '🔴 Needs Improvement'

    def _calculate_highlights(self, deployments, stats):
        """Calculate monthly highlights"""
        try:
            highlights = {
                'most_active_project': 'N/A',
                'most_active_developer': 'N/A',
                'busiest_day': 'N/A',
                'peak_time': 'N/A',
                'most_deployed_component': 'N/A'
            }

            if not deployments:
                return highlights

            # Most active project
            project_counts = stats.get('project_counts', {})
            if project_counts:
                most_active = max(project_counts.items(), key=lambda x: x[1])
                highlights['most_active_project'] = f"{most_active[0]} ({most_active[1]} deployments)"

            # Most active developer
            dev_counts = Counter(d.get('developer_name', 'Unknown') for d in deployments if d.get('developer_name'))
            if dev_counts:
                most_active_dev = dev_counts.most_common(1)[0]
                highlights['most_active_developer'] = f"{most_active_dev[0]} ({most_active_dev[1]} deployments)"

            # Busiest day
            day_counts = defaultdict(int)
            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt:
                    day_key = dt.strftime("%d-%b-%Y")
                    day_counts[day_key] += 1

            if day_counts:
                busiest = max(day_counts.items(), key=lambda x: x[1])
                highlights['busiest_day'] = f"{busiest[0]} ({busiest[1]} deployments)"

            # Peak time
            hour_counts = defaultdict(int)
            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt:
                    hour_counts[dt.hour] += 1

            if hour_counts:
                peak_hour = max(hour_counts.items(), key=lambda x: x[1])
                highlights['peak_time'] = f"{peak_hour[0]:02d}:00 - {peak_hour[0]+1:02d}:00 ({peak_hour[1]} deployments)"

            # Most deployed component
            comp_counts = Counter(d.get('component_name', 'Unknown') for d in deployments if d.get('component_name'))
            if comp_counts:
                most_deployed = comp_counts.most_common(1)[0]
                highlights['most_deployed_component'] = f"{most_deployed[0]} ({most_deployed[1]} deployments)"

            return highlights

        except Exception as e:
            print(f"Error calculating highlights: {str(e)}")
            return highlights

    def _calculate_day_of_week_stats(self, deployments):
        """Calculate day of week statistics"""
        try:
            dow_counts = defaultdict(int)
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt:
                    dow_counts[dt.weekday()] += 1

            if dow_counts:
                max_day = max(dow_counts.items(), key=lambda x: x[1])
                insight = f"Most deployments happen on {day_names[max_day[0]]} ({max_day[1]} deployments)"
            else:
                insight = "No deployment pattern detected"

            return {'counts': dow_counts, 'insight': insight}

        except Exception as e:
            print(f"Error calculating day of week stats: {str(e)}")
            return {'counts': {}, 'insight': 'Error calculating statistics'}

    def _calculate_developer_component_analysis(self, deployments):
        """Calculate developer component analysis"""
        try:
            dev_comp_map = defaultdict(lambda: defaultdict(int))

            for d in deployments:
                dev = d.get('developer_name', 'Unknown')
                comp = d.get('component_name', 'Unknown')
                if dev and comp:
                    dev_comp_map[dev][comp] += 1

            # Sort and format
            result = {}
            for dev, comps in dev_comp_map.items():
                sorted_comps = sorted(comps.items(), key=lambda x: x[1], reverse=True)
                result[dev] = {
                    'total': sum(comps.values()),
                    'components': sorted_comps
                }

            # Sort by total count
            result = dict(sorted(result.items(), key=lambda x: x[1]['total'], reverse=True))

            return result

        except Exception as e:
            print(f"Error calculating developer component analysis: {str(e)}")
            return {}

    def _calculate_project_jira_tracking(self, all_deployments):
        """Calculate JIRA tracking per project"""
        try:
            result = {}

            for project, deployments in all_deployments.items():
                total = len(deployments)
                tracked = sum(1 for d in deployments if d.get('jira_patch_id', 'N/A') != 'N/A')
                na_count = total - tracked
                na_percentage = (na_count / total * 100) if total > 0 else 0

                result[project] = {
                    'total': total,
                    'tracked': tracked,
                    'na_count': na_count,
                    'na_percentage': na_percentage
                }

            return result

        except Exception as e:
            print(f"Error calculating project JIRA tracking: {str(e)}")
            return {}

    def _get_poor_jira_compliance_projects(self, all_deployments, threshold=70):
        """Get projects with poor JIRA compliance"""
        try:
            poor_projects = []

            for project, deployments in all_deployments.items():
                total = len(deployments)
                tracked = sum(1 for d in deployments if d.get('jira_patch_id', 'N/A') != 'N/A')
                compliance = (tracked / total * 100) if total > 0 else 0

                if compliance < threshold:
                    poor_projects.append((project, {
                        'total': total,
                        'tracked': tracked,
                        'compliance': compliance
                    }))

            # Sort by compliance (lowest first)
            poor_projects.sort(key=lambda x: x[1]['compliance'])

            return poor_projects

        except Exception as e:
            print(f"Error getting poor JIRA compliance projects: {str(e)}")
            return []

    def _get_high_frequency_developers(self, deployments, threshold=10):
        """Get developers with high deployment frequency"""
        try:
            dev_counts = Counter(d.get('developer_name', 'Unknown') for d in deployments if d.get('developer_name'))
            high_freq = [(dev, count) for dev, count in dev_counts.items() if count > threshold]
            high_freq.sort(key=lambda x: x[1], reverse=True)
            return high_freq
        except Exception as e:
            print(f"Error getting high frequency developers: {str(e)}")
            return []

    def _get_inactive_projects(self, all_deployments):
        """Get projects with no deployments"""
        try:
            return [project for project, deployments in all_deployments.items() if len(deployments) == 0]
        except Exception as e:
            print(f"Error getting inactive projects: {str(e)}")
            return []

    def _get_after_hours_deployments(self, deployments):
        """Get deployments outside business hours (8AM-6PM)"""
        try:
            after_hours_count = 0

            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt:
                    if dt.hour < 8 or dt.hour >= 18:
                        after_hours_count += 1

            return {'count': after_hours_count}

        except Exception as e:
            print(f"Error getting after hours deployments: {str(e)}")
            return {'count': 0}

    # ==================== CHART GENERATION FUNCTIONS ====================

    def _create_timeline_chart(self, deployments, month, year):
        """Create deployment timeline chart"""
        try:
            plt.figure(figsize=(10, 5))

            # Count deployments per day
            day_counts = defaultdict(int)
            last_day = calendar.monthrange(year, month)[1]

            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt and dt.month == month and dt.year == year:
                    day_counts[dt.day] += 1

            # Prepare data
            days = list(range(1, last_day + 1))
            counts = [day_counts.get(day, 0) for day in days]

            # Plot
            plt.plot(days, counts, marker='o', linewidth=2, markersize=6, color='#3498db')
            plt.fill_between(days, counts, alpha=0.3, color='#3498db')

            plt.title(f'Daily Deployment Timeline - {calendar.month_name[month]} {year}',
                     fontsize=14, fontweight='bold')
            plt.xlabel('Day of Month', fontweight='bold')
            plt.ylabel('Number of Deployments', fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            chart_path = self.temp_dir / f"timeline_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"Error creating timeline chart: {str(e)}")
            plt.close()
            return None

    def _create_day_of_week_chart(self, deployments, month, year):
        """Create day of week analysis chart"""
        try:
            plt.figure(figsize=(10, 5))

            dow_counts = defaultdict(int)
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt:
                    dow_counts[dt.weekday()] += 1

            # Prepare data
            counts = [dow_counts.get(i, 0) for i in range(7)]

            # Plot
            bars = plt.bar(day_names, counts, color='#27ae60', alpha=0.7, edgecolor='#1e8449')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                            f'{int(height)}', ha='center', va='bottom', fontweight='bold')

            plt.title(f'Deployments by Day of Week - {calendar.month_name[month]} {year}',
                     fontsize=14, fontweight='bold')
            plt.xlabel('Day of Week', fontweight='bold')
            plt.ylabel('Number of Deployments', fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()

            chart_path = self.temp_dir / f"dow_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"Error creating day of week chart: {str(e)}")
            plt.close()
            return None

    def _create_time_of_day_chart(self, deployments, month, year):
        """Create time of day distribution chart"""
        try:
            plt.figure(figsize=(8, 8))

            # Categorize by time of day
            morning = 0  # 8AM-12PM
            afternoon = 0  # 12PM-5PM
            evening = 0  # 5PM-8PM
            night = 0  # 8PM-8AM

            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt:
                    hour = dt.hour
                    if 8 <= hour < 12:
                        morning += 1
                    elif 12 <= hour < 17:
                        afternoon += 1
                    elif 17 <= hour < 20:
                        evening += 1
                    else:
                        night += 1

            # Prepare data
            labels = ['Morning\n(8AM-12PM)', 'Afternoon\n(12PM-5PM)', 'Evening\n(5PM-8PM)', 'Night\n(8PM-8AM)']
            sizes = [morning, afternoon, evening, night]
            colors = ['#f39c12', '#3498db', '#9b59b6', '#34495e']
            explode = (0.05, 0.05, 0.05, 0.05)

            # Plot
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=True, startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})

            plt.title(f'Time of Day Distribution - {calendar.month_name[month]} {year}',
                     fontsize=14, fontweight='bold', pad=20)
            plt.axis('equal')
            plt.tight_layout()

            chart_path = self.temp_dir / f"tod_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"Error creating time of day chart: {str(e)}")
            plt.close()
            return None

    def _create_week_wise_chart(self, deployments, month, year):
        """Create week-wise breakdown chart"""
        try:
            plt.figure(figsize=(10, 5))

            # Group by week
            week_counts = defaultdict(int)

            for d in deployments:
                dt = self._parse_timestamp(d.get('timestamp'))
                if dt and dt.month == month and dt.year == year:
                    week_num = (dt.day - 1) // 7 + 1
                    week_counts[week_num] += 1

            # Prepare data
            weeks = sorted(week_counts.keys())
            week_labels = [f'Week {w}' for w in weeks]
            counts = [week_counts[w] for w in weeks]

            # Plot
            bars = plt.bar(week_labels, counts, color='#e74c3c', alpha=0.7, edgecolor='#c0392b')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                            f'{int(height)}', ha='center', va='bottom', fontweight='bold')

            plt.title(f'Week-wise Deployment Breakdown - {calendar.month_name[month]} {year}',
                     fontsize=14, fontweight='bold')
            plt.xlabel('Week', fontweight='bold')
            plt.ylabel('Number of Deployments', fontweight='bold')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()

            chart_path = self.temp_dir / f"week_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"Error creating week-wise chart: {str(e)}")
            plt.close()
            return None

    def _create_component_frequency_chart(self, deployments, month, year):
        """Create component frequency chart"""
        try:
            plt.figure(figsize=(10, 6))

            comp_counts = Counter(d.get('component_name', 'Unknown') for d in deployments if d.get('component_name'))

            if not comp_counts:
                plt.close()
                return None

            # Get top 10 components
            top_comps = comp_counts.most_common(10)
            comp_names = [comp[0][:20] for comp in top_comps]  # Truncate long names
            counts = [comp[1] for comp in top_comps]

            # Plot
            bars = plt.barh(comp_names, counts, color='#9b59b6', alpha=0.7, edgecolor='#7d3c98')

            # Add value labels
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 0.3, bar.get_y() + bar.get_height()/2.,
                        f'{int(width)}', ha='left', va='center', fontweight='bold')

            plt.title(f'Component Deployment Frequency - {calendar.month_name[month]} {year}',
                     fontsize=14, fontweight='bold')
            plt.xlabel('Number of Deployments', fontweight='bold')
            plt.ylabel('Component', fontweight='bold')
            plt.grid(axis='x', alpha=0.3)
            plt.tight_layout()

            chart_path = self.temp_dir / f"component_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"Error creating component frequency chart: {str(e)}")
            plt.close()
            return None

    def _create_jira_gauge_chart(self, compliance_rate, month, year):
        """Create JIRA compliance gauge chart"""
        try:
            fig, ax = plt.subplots(figsize=(8, 5))

            # Create gauge
            categories = ['0-50%', '50-70%', '70-90%', '90-100%']
            colors_gauge = ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60']

            # Draw semi-circle
            theta = np.linspace(0, np.pi, 100)

            # Background arc
            for i, (start, end, color) in enumerate([(0, 50, '#e74c3c'), (50, 70, '#f39c12'),
                                                       (70, 90, '#f1c40f'), (90, 100, '#27ae60')]):
                theta_range = np.linspace(np.pi * (1 - end/100), np.pi * (1 - start/100), 50)
                r_outer = 1.0
                r_inner = 0.7

                x_outer = r_outer * np.cos(theta_range)
                y_outer = r_outer * np.sin(theta_range)
                x_inner = r_inner * np.cos(theta_range)
                y_inner = r_inner * np.sin(theta_range)

                ax.fill_between(theta_range, r_inner, r_outer,
                               transform=ax.transData._b, color=color, alpha=0.7)

            # Draw needle
            needle_angle = np.pi * (1 - compliance_rate/100)
            needle_length = 0.65
            ax.plot([0, needle_length * np.cos(needle_angle)],
                   [0, needle_length * np.sin(needle_angle)],
                   'k-', linewidth=3)
            ax.plot(0, 0, 'ko', markersize=10)

            # Add text
            ax.text(0, -0.3, f'{compliance_rate:.1f}%',
                   ha='center', va='center', fontsize=24, fontweight='bold')
            ax.text(0, -0.45, 'JIRA Compliance',
                   ha='center', va='center', fontsize=12)

            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-0.6, 1.2)
            ax.axis('off')
            ax.set_aspect('equal')

            plt.title(f'JIRA Tracking Compliance - {calendar.month_name[month]} {year}',
                     fontsize=14, fontweight='bold', pad=20)
            plt.tight_layout()

            chart_path = self.temp_dir / f"jira_gauge_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            return str(chart_path)

        except Exception as e:
            print(f"Error creating JIRA gauge chart: {str(e)}")
            plt.close()
            return None

    def cleanup_temp_files(self):
        """Clean up temporary chart files"""
        try:
            for file in self.temp_dir.glob("*.png"):
                file.unlink()
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")


# Import numpy for gauge chart
try:
    import numpy as np
except ImportError:
    print("Warning: numpy not installed. Gauge chart may not work.")
    np = None


if __name__ == '__main__':
    # Test PDF generation
    from excel_manager import ExcelManager

    excel_manager = ExcelManager()
    pdf_gen = PDFGenerator(excel_manager)

    output_file = pdf_gen.generate_monthly_report(11, 2025)
    print(f"PDF generated: {output_file}")

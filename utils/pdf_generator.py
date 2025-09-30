"""
PDF Report Generator for Deployment Statistics
Creates monthly PDF reports with charts and statistics
"""

import os
import calendar
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
import tempfile


class PDFGenerator:
    """Generate PDF reports with deployment statistics and charts"""
    
    def __init__(self, excel_manager):
        self.excel_manager = excel_manager
        self.temp_dir = Path(tempfile.gettempdir()) / "chklst_charts"
        self.temp_dir.mkdir(exist_ok=True)
        
    def generate_monthly_report(self, month: int, year: int) -> str:
        """Generate comprehensive monthly PDF report"""
        # Create output directory
        output_dir = Path("reports") / "pdfs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        month_name = calendar.month_name[month]
        output_file = output_dir / f"{month_name}_{year}_deployment_report.pdf"
        
        # Get data
        stats = self.excel_manager.get_deployment_stats(month, year)
        all_deployments = self.excel_manager.get_all_monthly_deployments(month, year)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            topMargin=20*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center
            textColor=colors.darkblue
        )
        
        title = Paragraph(f"Deployment Report<br/>{month_name} {year}", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Executive Summary
        self._add_executive_summary(story, styles, stats)
        
        # Charts
        self._add_charts(story, styles, stats, month, year)
        
        # Detailed Statistics
        self._add_detailed_stats(story, styles, stats, all_deployments)
        
        # Deployment Details Table
        self._add_deployment_table(story, styles, all_deployments)
        
        # Build PDF
        doc.build(story)
        
        return str(output_file)
        
    def _add_executive_summary(self, story, styles, stats):
        """Add executive summary section"""
        # Section title
        section_title = Paragraph("📊 Executive Summary", styles['Heading2'])
        story.append(section_title)
        story.append(Spacer(1, 12))
        
        # Summary data
        summary_data = [
            ['Metric', 'Count', 'Percentage'],
            ['Total Deployments', str(stats['total_deployments']), '100%'],
            ['Successful Builds', str(stats['successful_builds']), f"{stats.get('build_success_rate', 0):.1f}%"],
            ['Failed Builds', str(stats['failed_builds']), f"{100 - stats.get('build_success_rate', 0):.1f}%"],
            ['Successful Deploys', str(stats['successful_deploys']), f"{stats.get('deploy_success_rate', 0):.1f}%"],
            ['Failed Deploys', str(stats['failed_deploys']), f"{100 - stats.get('deploy_success_rate', 0):.1f}%"],
            ['Active Projects', str(len(stats.get('project_counts', {}))), ''],
        ]
        
        # Create table
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Key insights
        insights_title = Paragraph("🔍 Key Insights", styles['Heading3'])
        story.append(insights_title)
        
        build_rate = stats.get('build_success_rate', 0)
        deploy_rate = stats.get('deploy_success_rate', 0)
        
        insights = []
        if build_rate >= 90:
            insights.append("✅ Excellent build success rate indicates stable code quality")
        elif build_rate >= 70:
            insights.append("⚠️ Good build success rate with room for improvement")
        else:
            insights.append("❌ Build success rate needs attention - consider code review improvements")
            
        if deploy_rate >= 90:
            insights.append("✅ Excellent deployment success rate indicates reliable deployment process")
        elif deploy_rate >= 70:
            insights.append("⚠️ Good deployment success rate with room for improvement")
        else:
            insights.append("❌ Deployment process needs review and improvement")
            
        if stats['total_deployments'] > 0:
            avg_per_project = stats['total_deployments'] / len(stats.get('project_counts', {1: 1}))
            if avg_per_project > 10:
                insights.append("📈 High deployment frequency indicates active development")
            elif avg_per_project > 5:
                insights.append("📊 Moderate deployment frequency")
            else:
                insights.append("📉 Low deployment frequency - consider more frequent releases")
        
        for insight in insights:
            story.append(Paragraph(f"• {insight}", styles['Normal']))
            
        story.append(Spacer(1, 20))
        
    def _add_charts(self, story, styles, stats, month, year):
        """Add charts to the PDF"""
        charts_title = Paragraph("📈 Charts & Analytics", styles['Heading2'])
        story.append(charts_title)
        story.append(Spacer(1, 12))
        
        # Success Rate Pie Chart
        if stats['total_deployments'] > 0:
            success_chart_path = self._create_success_pie_chart(stats, month, year)
            if success_chart_path:
                story.append(Image(success_chart_path, width=4*inch, height=3*inch))
                story.append(Spacer(1, 12))
        
        # Project Breakdown Bar Chart
        if stats.get('project_counts'):
            project_chart_path = self._create_project_bar_chart(stats, month, year)
            if project_chart_path:
                story.append(Image(project_chart_path, width=6*inch, height=3*inch))
                story.append(Spacer(1, 12))
        
        # Component Breakdown
        if stats.get('component_counts'):
            component_chart_path = self._create_component_chart(stats, month, year)
            if component_chart_path:
                story.append(Image(component_chart_path, width=4*inch, height=3*inch))
                story.append(Spacer(1, 20))
        
    def _create_success_pie_chart(self, stats, month, year):
        """Create success rate pie chart"""
        try:
            plt.figure(figsize=(8, 6))
            
            # Data for pie chart
            successful = stats['successful_deploys']
            failed = stats['failed_deploys']
            
            if successful + failed == 0:
                return None
                
            labels = ['Successful Deploys', 'Failed Deploys']
            sizes = [successful, failed]
            colors = ['#27ae60', '#e74c3c']
            explode = (0.1, 0)  # explode successful slice
            
            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90)
            
            plt.title(f'Deployment Success Rate - {calendar.month_name[month]} {year}', 
                     fontsize=14, fontweight='bold')
            plt.axis('equal')
            
            chart_path = self.temp_dir / f"success_pie_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"Error creating success pie chart: {e}")
            return None
            
    def _create_project_bar_chart(self, stats, month, year):
        """Create project deployment bar chart"""
        try:
            project_counts = stats.get('project_counts', {})
            if not project_counts:
                return None
                
            plt.figure(figsize=(12, 6))
            
            projects = list(project_counts.keys())
            counts = list(project_counts.values())
            
            # Create bar chart
            bars = plt.bar(projects, counts, color='#3498db', alpha=0.7, edgecolor='#2980b9')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            plt.title(f'Deployments by Project - {calendar.month_name[month]} {year}', 
                     fontsize=14, fontweight='bold')
            plt.xlabel('Projects', fontweight='bold')
            plt.ylabel('Number of Deployments', fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            
            chart_path = self.temp_dir / f"project_bar_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"Error creating project bar chart: {e}")
            return None
            
    def _create_component_chart(self, stats, month, year):
        """Create component breakdown chart"""
        try:
            component_counts = stats.get('component_counts', {})
            # Filter out zero counts
            component_counts = {k: v for k, v in component_counts.items() if v > 0}
            
            if not component_counts:
                return None
                
            plt.figure(figsize=(8, 6))
            
            labels = list(component_counts.keys())
            sizes = list(component_counts.values())
            colors = ['#f39c12', '#9b59b6', '#1abc9c'][:len(labels)]
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                   shadow=True, startangle=90)
            
            plt.title(f'Deployments by Component - {calendar.month_name[month]} {year}', 
                     fontsize=14, fontweight='bold')
            plt.axis('equal')
            
            chart_path = self.temp_dir / f"component_pie_{month}_{year}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"Error creating component chart: {e}")
            return None
            
    def _add_detailed_stats(self, story, styles, stats, all_deployments):
        """Add detailed statistics section"""
        details_title = Paragraph("📋 Detailed Statistics", styles['Heading2'])
        story.append(details_title)
        story.append(Spacer(1, 12))
        
        # Project breakdown
        project_title = Paragraph("Projects Performance", styles['Heading3'])
        story.append(project_title)
        
        project_data = [['Project', 'Deployments', 'Success Rate']]
        
        for project_name, deployments in all_deployments.items():
            total = len(deployments)
            successful = sum(1 for d in deployments if d.get('deploy_status', False))
            success_rate = (successful / total * 100) if total > 0 else 0
            
            project_data.append([
                project_name,
                str(total),
                f"{success_rate:.1f}%"
            ])
        
        if len(project_data) > 1:  # Has data beyond header
            project_table = Table(project_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(project_table)
        else:
            story.append(Paragraph("No deployment data available for this month.", styles['Normal']))
            
        story.append(Spacer(1, 20))
        
    def _add_deployment_table(self, story, styles, all_deployments):
        """Add detailed deployment table"""
        table_title = Paragraph("📝 Deployment Details", styles['Heading2'])
        story.append(table_title)
        story.append(Spacer(1, 12))
        
        # Flatten all deployments
        all_deploys = []
        for project_name, deployments in all_deployments.items():
            all_deploys.extend(deployments)
            
        # Sort by timestamp
        all_deploys.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit to recent 20 deployments for PDF
        recent_deploys = all_deploys[:20]
        
        if not recent_deploys:
            story.append(Paragraph("No deployments found for this month.", styles['Normal']))
            return
            
        # Create table data
        table_data = [['Date', 'Project', 'Component', 'Developer', 'Build', 'Deploy']]
        
        for deployment in recent_deploys:
            timestamp = deployment.get('timestamp', '')
            # Extract just date from timestamp
            date_str = timestamp.split(' ')[0] if timestamp else 'N/A'
            
            table_data.append([
                date_str,
                deployment.get('project_name', '')[:15],  # Truncate long names
                deployment.get('component_name', '')[:15],
                deployment.get('developer_name', '')[:15],
                '✓' if deployment.get('build_status') else '✗',
                '✓' if deployment.get('deploy_status') else '✗'
            ])
        
        # Create table
        deploy_table = Table(table_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch, 0.5*inch, 0.5*inch])
        deploy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightsteelblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(deploy_table)
        
        if len(all_deploys) > 20:
            note = Paragraph(f"<i>Note: Showing most recent 20 deployments out of {len(all_deploys)} total.</i>", 
                           styles['Normal'])
            story.append(Spacer(1, 12))
            story.append(note)
            
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,  # Center
            textColor=colors.grey
        )
        
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Deployment Tracking System"
        footer = Paragraph(footer_text, footer_style)
        story.append(footer)
        
    def cleanup_temp_files(self):
        """Clean up temporary chart files"""
        try:
            for file in self.temp_dir.glob("*.png"):
                file.unlink()
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")


if __name__ == '__main__':
    # Test PDF generation
    from excel_manager import ExcelManager
    
    excel_manager = ExcelManager()
    pdf_gen = PDFGenerator(excel_manager)
    
    output_file = pdf_gen.generate_monthly_report(12, 2024)
    print(f"PDF generated: {output_file}")
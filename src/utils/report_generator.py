"""
PDF Report Generator for Extraction Bot

Generates professional PDF reports summarizing the extraction process.
Reports are saved to: reports/YYYYMMDD_HHMMSS/extraction_report_YYYYMMDD_HHMMSS.pdf
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ExtractionReportGenerator:
    """Generates professional PDF reports for extraction runs."""
    
    def __init__(self, output_base_dir: str = "reports"):
        """
        Initialize the report generator.
        
        Args:
            output_base_dir: Base directory for storing reports
        """
        self.output_base_dir = output_base_dir
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d')
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#4a5568')
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=11,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.HexColor('#2d3748'),
            borderPadding=2
        ))
        
        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=2,
            textColor=colors.HexColor('#4a5568')
        ))
        
        # Success text style
        self.styles.add(ParagraphStyle(
            name='SuccessText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#276749')
        ))
        
        # Error text style
        self.styles.add(ParagraphStyle(
            name='ErrorText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#c53030')
        ))
        
    def generate_report(
        self,
        run_timestamp: str,
        overall_start_time: datetime,
        overall_end_time: datetime,
        portal_timings: Dict,
        portal_results: Dict,
        db_upload_success: bool,
        db_rows_inserted: int,
        db_upload_duration: float,
        db_upload_start: datetime,
        db_upload_end: datetime,
        total_duration: float,
        output_folder: str,
        portals_processed: List[str],
        deletion_details: Dict = None
    ) -> str:
        """
        Generate the extraction report PDF.
        
        Args:
            run_timestamp: Timestamp string for the run (YYYYMMDD_HHMMSS)
            overall_start_time: When extraction started
            overall_end_time: When extraction ended
            portal_timings: Dict of portal timing info
            portal_results: Dict of portal success/failure status
            db_upload_success: Whether DB upload succeeded
            db_rows_inserted: Number of rows inserted
            db_upload_duration: Duration of DB upload in seconds
            db_upload_start: When DB upload started
            db_upload_end: When DB upload ended
            total_duration: Total process duration in seconds
            output_folder: Path to extracted data folder
            portals_processed: List of portal names processed
            deletion_details: Dict with deletion info per portal {company: {rows_deleted, dropdown_names}}
            
        Returns:
            str: Path to generated PDF report
        """
        # Create report directory with timestamp
        report_dir = os.path.join(self.output_base_dir, run_timestamp)
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate PDF filename
        pdf_filename = f"extraction_report_{run_timestamp}.pdf"
        pdf_path = os.path.join(report_dir, pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build content
        story = []
        
        # === HEADER SECTION ===
        story.append(Paragraph("🤖 Extraction Bot Report", self.styles['ReportTitle']))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            self.styles['ReportSubtitle']
        ))
        story.append(Spacer(1, 5))
        
        # === RUN INFORMATION ===
        story.append(self._create_section_header("📋 Run Information"))
        
        run_info_data = [
            ['Run ID', run_timestamp],
            ['Start Time', overall_start_time.strftime('%Y-%m-%d %H:%M:%S')],
            ['End Time', overall_end_time.strftime('%Y-%m-%d %H:%M:%S')],
            ['Output Folder', output_folder],
            ['Portals Processed', ', '.join(portals_processed)]
        ]
        story.append(self._create_info_table(run_info_data))
        story.append(Spacer(1, 6))
        
        # === PORTAL EXTRACTION SUMMARY ===
        story.append(self._create_section_header("🔄 Portal Extraction Summary"))
        
        # Calculate success/failure counts
        success_count = sum(1 for p, r in portal_results.items() if r.get('success', False))
        failure_count = len(portal_results) - success_count
        
        summary_data = [
            ['Total Portals', str(len(portals_processed))],
            ['Successful', f"{success_count}"],
            ['Failed', f"{failure_count}"],
            ['Extraction Duration', self._format_duration(
                (overall_end_time - overall_start_time).total_seconds()
            )]
        ]
        story.append(self._create_info_table(summary_data, highlight_success=(1, 1), highlight_fail=(2, 1) if failure_count > 0 else None))
        story.append(Spacer(1, 6))
        
        # === PORTAL-WISE DETAILS ===
        story.append(self._create_section_header("📊 Portal-wise Details"))
        
        portal_table_data = [['Portal', 'Status', 'Duration', 'Start', 'End']]
        portal_status_colors = []  # Track which rows need color coding
        
        for portal_name in portals_processed:
            timing = portal_timings.get(portal_name, {})
            result = portal_results.get(portal_name, {})
            
            start_time = timing.get('start')
            end_time = timing.get('end')
            duration = timing.get('duration')
            
            is_success = result.get('success', False)
            status = "SUCCESS" if is_success else "FAILED"
            portal_status_colors.append(is_success)
            
            duration_str = self._format_duration(duration.total_seconds()) if duration else "N/A"
            start_str = start_time.strftime('%H:%M:%S') if start_time else "N/A"
            end_str = end_time.strftime('%H:%M:%S') if end_time else "N/A"
            
            portal_table_data.append([
                portal_name,
                status,
                duration_str,
                start_str,
                end_str
            ])
        
        story.append(self._create_portal_table(portal_table_data, portal_status_colors))
        story.append(Spacer(1, 6))
        
        # === ERROR DETAILS (if any) ===
        errors_exist = any(r.get('error') for r in portal_results.values())
        if errors_exist:
            story.append(self._create_section_header("⚠️ Error Details"))
            
            for portal_name, result in portal_results.items():
                if result.get('error'):
                    story.append(Paragraph(
                        f"<b>{portal_name}:</b> {result['error']}",
                        self.styles['ErrorText']
                    ))
                    story.append(Spacer(1, 2))
            
            story.append(Spacer(1, 4))
        
        # === DATABASE UPLOAD SUMMARY ===
        story.append(self._create_section_header("📤 Database Upload Summary"))
        
        db_status = "SUCCESS" if db_upload_success else "FAILED"
        db_data = [
            ['Status', db_status],
            ['Rows Inserted', f"{db_rows_inserted:,}"],
            ['Duration', self._format_duration(db_upload_duration)],
            ['Time', f"{db_upload_start.strftime('%H:%M:%S')} → {db_upload_end.strftime('%H:%M:%S')}"]
        ]
        story.append(self._create_info_table(db_data, highlight_success=(0, 1) if db_upload_success else None, highlight_fail=(0, 1) if not db_upload_success else None))
        story.append(Spacer(1, 6))
        
        # === DELETION DETAILS BY PORTAL ===
        if deletion_details and db_upload_success:
            story.append(self._create_section_header("🗑️ Deletion Details by Portal"))
            
            deletion_table_data = [['Portal', 'Rows Deleted', 'Dropdown Names Deleted']]
            
            for company, details in deletion_details.items():
                rows_deleted = details.get('rows_deleted', 0)
                dropdown_names = details.get('dropdown_names', [])
                dropdown_names_str = ', '.join(dropdown_names) if dropdown_names else 'None'
                
                deletion_table_data.append([
                    company,
                    str(rows_deleted),
                    dropdown_names_str
                ])
            
            story.append(self._create_deletion_table(deletion_table_data))
            story.append(Spacer(1, 6))
        
        # === COMPLETE PROCESS SUMMARY ===
        story.append(self._create_section_header("🏁 Complete Process Summary"))
        
        extraction_duration = (overall_end_time - overall_start_time).total_seconds()
        
        # Create a visual timeline table
        timeline_data = [
            ['Phase', 'Duration', 'Percentage'],
            ['API Extraction', self._format_duration(extraction_duration), 
             f"{(extraction_duration/total_duration)*100:.1f}%"],
            ['Database Upload', self._format_duration(db_upload_duration),
             f"{(db_upload_duration/total_duration)*100:.1f}%"],
            ['TOTAL', self._format_duration(total_duration), '100%']
        ]
        story.append(self._create_summary_table(timeline_data))
        story.append(Spacer(1, 10))
        
        # === FOOTER ===
        story.append(Paragraph(
            "─" * 80,
            self.styles['InfoText']
        ))
        story.append(Paragraph(
            f"Report generated by Extraction Bot v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=7,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#718096')
            )
        ))
        
        # Build PDF
        doc.build(story)
        
        return pdf_path
    
    def _create_section_header(self, text: str) -> Paragraph:
        """Create a styled section header."""
        return Paragraph(text, self.styles['SectionHeader'])
    
    def _create_info_table(self, data: List[List[str]], highlight_success=None, highlight_fail=None) -> Table:
        """Create a simple info table with two columns and optional color highlighting."""
        table = Table(data, colWidths=[100, 370])
        
        style = [
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d3748')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Add success highlighting (green background)
        if highlight_success:
            row, col = highlight_success
            style.append(('BACKGROUND', (col, row), (col, row), colors.HexColor('#c6f6d5')))
            style.append(('TEXTCOLOR', (col, row), (col, row), colors.HexColor('#276749')))
            style.append(('FONTNAME', (col, row), (col, row), 'Helvetica-Bold'))
        
        # Add fail highlighting (red background)
        if highlight_fail:
            row, col = highlight_fail
            style.append(('BACKGROUND', (col, row), (col, row), colors.HexColor('#fed7d7')))
            style.append(('TEXTCOLOR', (col, row), (col, row), colors.HexColor('#c53030')))
            style.append(('FONTNAME', (col, row), (col, row), 'Helvetica-Bold'))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_portal_table(self, data: List[List[str]], status_colors: List[bool] = None) -> Table:
        """Create a styled portal details table with color-coded status."""
        table = Table(data, colWidths=[90, 70, 60, 65, 65])
        
        style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Color-code status column based on success/failure
        if status_colors:
            for i, is_success in enumerate(status_colors):
                row_idx = i + 1  # Skip header row
                if is_success:
                    # Green for success
                    style.append(('BACKGROUND', (1, row_idx), (1, row_idx), colors.HexColor('#c6f6d5')))
                    style.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), colors.HexColor('#276749')))
                    style.append(('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'))
                else:
                    # Red for failure
                    style.append(('BACKGROUND', (1, row_idx), (1, row_idx), colors.HexColor('#fed7d7')))
                    style.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), colors.HexColor('#c53030')))
                    style.append(('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'))
        
        # Alternate row colors (except status column)
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#f7fafc')))
                style.append(('BACKGROUND', (2, i), (-1, i), colors.HexColor('#f7fafc')))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_deletion_table(self, data: List[List[str]]) -> Table:
        """Create a styled deletion details table."""
        table = Table(data, colWidths=[90, 70, 190])
        
        style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#744210')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fffaf0')))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_summary_table(self, data: List[List[str]]) -> Table:
        """Create a styled summary table."""
        table = Table(data, colWidths=[180, 100, 80])
        
        style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Total row (last row)
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#edf2f7')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        table.setStyle(TableStyle(style))
        return table
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to a readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"


def generate_extraction_report(
    run_timestamp: str,
    overall_start_time: datetime,
    overall_end_time: datetime,
    portal_timings: Dict,
    portal_results: Dict,
    db_upload_success: bool,
    db_rows_inserted: int,
    db_upload_duration: float,
    db_upload_start: datetime,
    db_upload_end: datetime,
    total_duration: float,
    output_folder: str,
    portals_processed: List[str],
    deletion_details: Dict = None
) -> str:
    """
    Convenience function to generate extraction report.
    
    Returns:
        str: Path to generated PDF report
    """
    generator = ExtractionReportGenerator()
    return generator.generate_report(
        run_timestamp=run_timestamp,
        overall_start_time=overall_start_time,
        overall_end_time=overall_end_time,
        portal_timings=portal_timings,
        portal_results=portal_results,
        db_upload_success=db_upload_success,
        db_rows_inserted=db_rows_inserted,
        db_upload_duration=db_upload_duration,
        db_upload_start=db_upload_start,
        db_upload_end=db_upload_end,
        total_duration=total_duration,
        output_folder=output_folder,
        portals_processed=portals_processed,
        deletion_details=deletion_details
    )

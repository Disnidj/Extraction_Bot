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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
        deletion_details: Dict = None,
        mapping_details: Dict = None
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
            mapping_details: Dict with mapping info {applied_mappings: {company: {portal_name: db_name}}, unmapped_names: {company: [names]}}
            
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
        story.append(Spacer(1, 8))
        
        # === COMPREHENSIVE EXECUTION SUMMARY ===
        story.append(self._create_section_header("📊 Execution Summary"))
        
        # Calculate success/failure counts
        success_count = sum(1 for p, r in portal_results.items() if r.get('success', False))
        failure_count = len(portal_results) - success_count
        extraction_duration = (overall_end_time - overall_start_time).total_seconds()
        
        # Merged comprehensive summary table with Paragraph wrapping for long values
        portals_text = ', '.join(portals_processed)
        portals_paragraph = Paragraph(portals_text, ParagraphStyle(
            name='PortalsListCell',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#2d3748'),
            leading=10
        ))
        
        output_folder_paragraph = Paragraph(output_folder, ParagraphStyle(
            name='OutputFolderCell',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#2d3748'),
            leading=10
        ))
        
        comprehensive_summary = [
            ['Run ID', run_timestamp],
            ['Start Time', overall_start_time.strftime('%Y-%m-%d %H:%M:%S')],
            ['End Time', overall_end_time.strftime('%Y-%m-%d %H:%M:%S')],
            ['Output Folder', output_folder_paragraph],
            ['Portals Processed', portals_paragraph],
            ['', ''],  # Separator row
            ['Total Portals', str(len(portals_processed))],
            ['Successful', f"{success_count}"],
            ['Failed', f"{failure_count}"],
            ['', ''],  # Separator row
            ['Extraction Duration', self._format_duration(extraction_duration)],
            ['Database Upload Duration', self._format_duration(db_upload_duration)],
            ['Total Execution Time', self._format_duration(total_duration)]
        ]
        story.append(self._create_comprehensive_summary_table(
            comprehensive_summary, 
            success_count, 
            failure_count
        ))
        story.append(Spacer(1, 8))
        
        # === PORTAL-WISE DETAILS ===
        story.append(self._create_section_header("� Portal-wise Extraction Details"))
        
        portal_table_data = [['Portal', 'Status', 'Duration', 'Start', 'End', 'Error']]
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
            
            # Wrap error message in Paragraph for proper text wrapping
            error_msg = result.get('error')
            if error_msg:
                error_display = Paragraph(error_msg, ParagraphStyle(
                    name='ErrorCellText',
                    parent=self.styles['Normal'],
                    fontSize=7,
                    textColor=colors.HexColor('#c53030'),
                    leading=9
                ))
            else:
                error_display = ''
            
            portal_table_data.append([
                portal_name,
                status,
                duration_str,
                start_str,
                end_str,
                error_display
            ])
        
        story.append(self._create_portal_table(portal_table_data, portal_status_colors))
        story.append(Spacer(1, 8))
        
        # === DATABASE UPLOAD SUMMARY ===
        story.append(self._create_section_header("📤 Database Upload Summary"))
        
        db_status = "SUCCESS" if db_upload_success else "FAILED"
        
        # Check if only_mapped_mode is enabled
        only_mapped_mode = mapping_details.get('only_mapped_mode', False) if mapping_details else False
        upload_mode = "ONLY MAPPED DROPDOWNS" if only_mapped_mode else "ALL DROPDOWNS"
        
        db_data = [
            ['Status', db_status],
            ['Upload Mode', upload_mode],
            ['Rows Inserted', f"{db_rows_inserted:,}"],
            ['Duration', self._format_duration(db_upload_duration)],
            ['Time', f"{db_upload_start.strftime('%H:%M:%S')} → {db_upload_end.strftime('%H:%M:%S')}"]
        ]
        story.append(self._create_info_table(db_data, highlight_success=(0, 1) if db_upload_success else None, highlight_fail=(0, 1) if not db_upload_success else None))
        
        # Add note about only mapped mode
        if only_mapped_mode and db_upload_success:
            story.append(Spacer(1, 3))
            story.append(Paragraph(
                "<i>ℹ️ Note: Only dropdowns with mappings in the database were uploaded. Unmapped dropdowns were skipped.</i>",
                ParagraphStyle(
                    name='ModeNote',
                    parent=self.styles['Normal'],
                    fontSize=7,
                    textColor=colors.HexColor('#2b6cb0'),
                    spaceAfter=4
                )
            ))
        story.append(Spacer(1, 6))
        
        # === DROPDOWN DATA REFRESH VALIDATION ===
        if deletion_details and mapping_details and mapping_details.get('inserted_dropdown_names') and db_upload_success:
            story.append(self._create_section_header("🔄 Dropdown Data Refresh Validation"))
            
            inserted_dropdowns = mapping_details.get('inserted_dropdown_names', {})
            only_mapped = mapping_details.get('only_mapped_mode', False)
            
            if only_mapped:
                story.append(Paragraph(
                    "<i>ℹ️ Only mapped dropdowns were processed (unmapped dropdowns were skipped)</i>",
                    ParagraphStyle(
                        name='RefreshModeNote',
                        parent=self.styles['Normal'],
                        fontSize=7,
                        textColor=colors.HexColor('#2b6cb0'),
                        spaceAfter=4
                    )
                ))
            
            # Compare deleted vs inserted for each portal
            validation_table_data = [['Portal', 'Refreshed Count', 'Deleted', 'Inserted', 'Status']]
            mismatches_found = False
            
            all_portals = set(deletion_details.keys()) | set(inserted_dropdowns.keys())
            
            for company in sorted(all_portals):
                deleted_names = set(deletion_details.get(company, {}).get('dropdown_names', []))
                inserted_names = set(inserted_dropdowns.get(company, []))
                
                deleted_count = len(deleted_names)
                inserted_count = len(inserted_names)
                
                # Refreshed count = successfully replaced dropdowns (intersection)
                refreshed_count = len(deleted_names & inserted_names)
                
                # Check if they match
                if deleted_names == inserted_names:
                    status = "✅ Match"
                else:
                    status = "⚠️ Mismatch"
                    mismatches_found = True
                
                validation_table_data.append([
                    company,
                    str(refreshed_count),
                    str(deleted_count),
                    str(inserted_count),
                    status
                ])
            
            story.append(self._create_validation_table(validation_table_data, all_portals, deletion_details, inserted_dropdowns))
            story.append(Spacer(1, 4))
            
            # If mismatches found, show detailed analysis
            if mismatches_found:
                story.append(Paragraph(
                    "<b>⚠️ MISMATCH DETAILS:</b>",
                    ParagraphStyle(
                        name='MismatchHeader',
                        parent=self.styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor('#c53030'),
                        spaceBefore=4,
                        spaceAfter=4
                    )
                ))
                
                for company in sorted(all_portals):
                    deleted_names = set(deletion_details.get(company, {}).get('dropdown_names', []))
                    inserted_names = set(inserted_dropdowns.get(company, []))
                    
                    if deleted_names != inserted_names:
                        # Find differences
                        only_deleted = deleted_names - inserted_names
                        only_inserted = inserted_names - deleted_names
                        
                        story.append(Paragraph(
                            f"<b>{company}:</b>",
                            ParagraphStyle(
                                name='MismatchCompany',
                                parent=self.styles['Normal'],
                                fontSize=8,
                                textColor=colors.HexColor('#2d3748'),
                                spaceBefore=3
                            )
                        ))
                        
                        if only_deleted:
                            story.append(Paragraph(
                                f"   ❌ Deleted but NOT inserted ({len(only_deleted)}): {', '.join(sorted(only_deleted))}",
                                ParagraphStyle(
                                    name='OnlyDeleted',
                                    parent=self.styles['Normal'],
                                    fontSize=7,
                                    textColor=colors.HexColor('#c53030'),
                                    leftIndent=15
                                )
                            ))
                        
                        if only_inserted:
                            story.append(Paragraph(
                                f"   ➕ Inserted but NOT deleted ({len(only_inserted)}): {', '.join(sorted(only_inserted))}",
                                ParagraphStyle(
                                    name='OnlyInserted',
                                    parent=self.styles['Normal'],
                                    fontSize=7,
                                    textColor=colors.HexColor('#d69e2e'),
                                    leftIndent=15
                                )
                            ))
                        
                        story.append(Spacer(1, 2))
                
                story.append(Spacer(1, 6))
            else:
                story.append(Paragraph(
                    "✅ All portals: Deleted and inserted dropdowns match perfectly!",
                    ParagraphStyle(
                        name='AllMatch',
                        parent=self.styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor('#276749'),
                        spaceBefore=3,
                        spaceAfter=6
                    )
                ))
            
            # Show complete dropdown lists for reference
            story.append(Spacer(1, 10))
            
            story.append(Paragraph(
                "<b>📋 Complete Dropdown Lists by Portal</b>",
                ParagraphStyle(
                    name='DropdownListHeader',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#2d3748'),
                    spaceBefore=4,
                    spaceAfter=6
                )
            ))
            
            for company in sorted(all_portals):
                dropdown_names = sorted(inserted_dropdowns.get(company, []))
                names_text = ', '.join(dropdown_names) if dropdown_names else 'None'
                story.append(Paragraph(
                    f"<b>{company}:</b> {names_text}",
                    ParagraphStyle(
                        name='DropdownListDetails',
                        parent=self.styles['Normal'],
                        fontSize=8,
                        alignment=TA_LEFT,
                        textColor=colors.HexColor('#4a5568'),
                        spaceAfter=3
                    )
                ))
            
            story.append(Spacer(1, 8))

        # === DROPDOWN MAPPING DETAILS BY PORTAL ===
        if mapping_details and mapping_details.get('applied_mappings') and db_upload_success:
            story.append(self._create_section_header("🔄 Dropdown Mapping Details by Portal"))
            
            applied_mappings = mapping_details.get('applied_mappings', {})
            unmapped_names = mapping_details.get('unmapped_names', {})
            only_mapped = mapping_details.get('only_mapped_mode', False)
            
            for company, mappings in applied_mappings.items():
                if mappings:
                    # Company header
                    story.append(Paragraph(
                        f"<b>📋 {company}</b> - {len(mappings)} mappings applied",
                        ParagraphStyle(
                            name='MappingCompanyHeader',
                            parent=self.styles['Normal'],
                            fontSize=9,
                            textColor=colors.HexColor('#2b6cb0'),
                            spaceBefore=6,
                            spaceAfter=4
                        )
                    ))
                    
                    # Mapping table
                    mapping_table_data = [['Portal Field Name', 'Database Field Name']]
                    for portal_name, db_name in sorted(mappings.items()):
                        # Truncate long names
                        portal_display = (portal_name[:50] + '...') if len(portal_name) > 53 else portal_name
                        db_display = (db_name[:35] + '...') if len(db_name) > 38 else db_name
                        mapping_table_data.append([portal_display, db_display])
                    
                    story.append(self._create_mapping_table(mapping_table_data))
                    story.append(Spacer(1, 2))
                    
                    # Unmapped fields count - indicate if they were skipped
                    company_unmapped = unmapped_names.get(company, [])
                    if company_unmapped:
                        unmapped_preview = ', '.join(company_unmapped[:5])
                        if len(company_unmapped) > 5:
                            unmapped_preview += f", ... (+{len(company_unmapped) - 5} more)"
                        skip_status = "SKIPPED - not uploaded" if only_mapped else "uploaded with original names"
                        story.append(Paragraph(
                            f"<i>⚠️ Unmapped fields ({len(company_unmapped)}) - {skip_status}: {unmapped_preview}</i>",
                            ParagraphStyle(
                                name='UnmappedText',
                                parent=self.styles['Normal'],
                                fontSize=7,
                                textColor=colors.HexColor('#c53030'),
                                spaceAfter=4
                            )
                        ))
                else:
                    skip_note = " - all records SKIPPED" if only_mapped else ""
                    story.append(Paragraph(
                        f"<b>{company}</b> - No mappings applied{skip_note}",
                        ParagraphStyle(
                            name='NoMappingText',
                            parent=self.styles['Normal'],
                            fontSize=8,
                            textColor=colors.HexColor('#718096'),
                            spaceBefore=4,
                            spaceAfter=4
                        )
                    ))

        # === FOOTER ===
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            "─" * 80,
            self.styles['InfoText']
        ))
        story.append(Paragraph(
            f"Report generated by Extraction Bot v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
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
    
    def _create_comprehensive_summary_table(self, data: List[List[str]], success_count: int, failure_count: int) -> Table:
        """Create comprehensive summary table with all execution details.
        
        Args:
            data: List of [label, value] pairs
            success_count: Number of successful portals
            failure_count: Number of failed portals
        
        Returns:
            Table: Styled comprehensive summary table
        """
        table = Table(data, colWidths=[180, 290])
        
        style = [
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d3748')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top alignment for wrapped text
        ]
        
        # Highlight separator rows (empty label rows)
        for i, row in enumerate(data):
            if row[0] == '':
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#cbd5e0')))
                style.append(('LINEABOVE', (0, i), (-1, i), 1.5, colors.HexColor('#a0aec0')))
        
        # Highlight success count (row 7 = "Successful")
        if success_count > 0:
            style.append(('BACKGROUND', (1, 7), (1, 7), colors.HexColor('#c6f6d5')))
            style.append(('TEXTCOLOR', (1, 7), (1, 7), colors.HexColor('#276749')))
            style.append(('FONTNAME', (1, 7), (1, 7), 'Helvetica-Bold'))
        
        # Highlight failure count if > 0 (row 8 = "Failed")
        if failure_count > 0:
            style.append(('BACKGROUND', (1, 8), (1, 8), colors.HexColor('#fed7d7')))
            style.append(('TEXTCOLOR', (1, 8), (1, 8), colors.HexColor('#c53030')))
            style.append(('FONTNAME', (1, 8), (1, 8), 'Helvetica-Bold'))
        
        # Highlight total execution time (last row)
        style.append(('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e6fffa')))
        style.append(('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#234e52')))
        style.append(('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'))
        style.append(('FONTSIZE', (0, -1), (-1, -1), 9))
        
        table.setStyle(TableStyle(style))
        return table
    
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
        """Create a styled portal details table with color-coded status and word-wrapped error column.
        
        Args:
            data: Table data where error column may contain Paragraph objects for text wrapping
            status_colors: List of booleans indicating success (True) or failure (False)
        """
        # Adjusted column widths to give more space to error column
        table = Table(data, colWidths=[85, 60, 55, 60, 60, 150])

        style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (4, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),  # Error column left-aligned
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top alignment for better wrapping
            ('PADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
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

        # Alternate row colors (except status & error columns)
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#f7fafc')))
                style.append(('BACKGROUND', (2, i), (4, i), colors.HexColor('#f7fafc')))

        table.setStyle(TableStyle(style))
        return table
    
    def _create_deletion_table(self, data: List) -> Table:
        """Create a compact deletion-summary table (one row per portal).

        This table intentionally only shows `Portal` and `Rows Deleted` so the full
        dropdown-name lists can be rendered separately as wrapped paragraphs that
        may span pages safely.
        """
        table = Table(data, colWidths=[220, 80])

        style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#744210')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

            # Borders and padding
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]

        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fffaf0')))

        table.setStyle(TableStyle(style))
        return table
    
    def _create_validation_table(self, data: List[List[str]], all_portals, deletion_details, inserted_dropdowns) -> Table:
        """Create a validation table comparing deleted vs inserted dropdowns.
        
        Args:
            data: Table data [['Portal', 'Refreshed Count', 'Deleted', 'Inserted', 'Status'], ...]
            all_portals: Set of all portal names
            deletion_details: Dict of deletion details
            inserted_dropdowns: Dict of inserted dropdown names
        
        Returns:
            Table: Styled validation table with color-coded status
        """
        table = Table(data, colWidths=[170, 85, 70, 70, 75])
        
        style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Borders and padding
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]
        
        # Color-code status column based on match/mismatch
        for i, company in enumerate(sorted(all_portals), start=1):
            deleted_names = set(deletion_details.get(company, {}).get('dropdown_names', []))
            inserted_names = set(inserted_dropdowns.get(company, []))
            
            if deleted_names == inserted_names:
                # Green for match
                style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#c6f6d5')))
                style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#276749')))
                style.append(('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'))
                
                # Highlight refreshed count in green too
                style.append(('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#276749')))
                style.append(('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'))
            else:
                # Red/Orange for mismatch
                style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#fed7d7')))
                style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#c53030')))
                style.append(('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'))
                
                # Also highlight the count columns if they differ
                deleted_count = len(deleted_names)
                inserted_count = len(inserted_names)
                if deleted_count != inserted_count:
                    style.append(('TEXTCOLOR', (2, i), (3, i), colors.HexColor('#c53030')))
                    style.append(('FONTNAME', (2, i), (3, i), 'Helvetica-Bold'))
        
        # Alternate row colors for portal name column
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#f7fafc')))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_mapping_table(self, data: List[List[str]]) -> Table:
        """Create a styled mapping table showing portal field names to database field names.
        
        Args:
            data: List of rows, first row is header ['Portal Field Name', 'Database Field Name']
        
        Returns:
            Table: Styled ReportLab table
        """
        table = Table(data, colWidths=[250, 200])
        
        style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            
            # Borders and padding
            ('PADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]
        
        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ebf8ff')))
        
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
    deletion_details: Dict = None,
    mapping_details: Dict = None
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
        deletion_details=deletion_details,
        mapping_details=mapping_details
    )

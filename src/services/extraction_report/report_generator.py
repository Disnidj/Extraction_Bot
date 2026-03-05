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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
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
        # Professional color palette
        self.colors = {
            'primary': colors.HexColor('#0047AB'),      # Cobalt Blue
            'primary_dark': colors.HexColor('#003380'), # Dark Blue
            'secondary': colors.HexColor('#2d3748'),    # Dark Gray
            'accent': colors.HexColor('#00A86B'),       # Jade Green
            'warning': colors.HexColor('#F59E0B'),      # Amber
            'danger': colors.HexColor('#DC2626'),       # Red
            'success': colors.HexColor('#059669'),      # Emerald
            'light_bg': colors.HexColor('#F8FAFC'),     # Light Gray
            'border': colors.HexColor('#E2E8F0'),       # Border Gray
            'text': colors.HexColor('#1E293B'),         # Text Dark
            'text_muted': colors.HexColor('#64748B'),   # Text Muted
        }
        
        # Title style - Professional and bold
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=self.colors['primary_dark'],
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=self.colors['text_muted']
        ))
        
        # Section header style - More prominent
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=14,
            spaceAfter=6,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            borderPadding=4,
            leftIndent=0,
            borderWidth=0,
            borderColor=self.colors['primary']
        ))
        
        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=2,
            textColor=self.colors['text_muted']
        ))
        
        # Success text style
        self.styles.add(ParagraphStyle(
            name='SuccessText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.colors['success']
        ))
        
        # Error text style
        self.styles.add(ParagraphStyle(
            name='ErrorText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.colors['danger']
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
        mapping_details: Dict = None,
        change_report = None,
        broker_details: Dict = None
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
            change_report: ChangeReport object with comparison results (new/modified/deleted records)
            broker_details: Dict with broker breakdown {broker_ids: [], broker_to_portals: {}, portal_details: {}}
            
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
        
        # === PROFESSIONAL HEADER SECTION ===
        # Top accent line
        story.append(HRFlowable(
            width="100%",
            thickness=3,
            color=self.colors['primary'],
            spaceBefore=0,
            spaceAfter=12
        ))
        
        story.append(Paragraph("EXTRACTION BOT", ParagraphStyle(
            name='BrandTitle',
            fontSize=24,
            alignment=TA_CENTER,
            textColor=self.colors['primary_dark'],
            fontName='Helvetica-Bold',
            spaceAfter=6,
            leading=28
        )))
        story.append(Paragraph("Automated Data Extraction Report", ParagraphStyle(
            name='BrandSubtitle',
            fontSize=11,
            alignment=TA_CENTER,
            textColor=self.colors['text_muted'],
            spaceAfter=4,
            leading=14
        )))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            self.styles['ReportSubtitle']
        ))
        
        # Divider line
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.colors['border'],
            spaceBefore=4,
            spaceAfter=12
        ))
        
        # === COMPREHENSIVE EXECUTION SUMMARY ===
        story.append(self._create_section_header("📊 Execution Summary"))
        
        # Calculate success/failure counts
        success_count = sum(1 for p, r in portal_results.items() if r.get('success', False))
        failure_count = len(portal_results) - success_count
        extraction_duration = (overall_end_time - overall_start_time).total_seconds()
        
        # Calculate retry statistics
        retry_count = sum(1 for p, r in portal_results.items() if r.get('attempts', 1) > 1)
        retry_success_count = sum(
            1 for p, r in portal_results.items() 
            if r.get('attempts', 1) > 1 and r.get('retry_success', False)
        )
        
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
        ]
        
        # Add retry info if any retries occurred
        if retry_count > 0:
            comprehensive_summary.extend([
                ['', ''],  # Separator
                ['Retry Attempts', f"{retry_count}"],
                ['Succeeded on Retry', f"{retry_success_count}"],
            ])
        
        comprehensive_summary.extend([
            ['', ''],  # Separator row
            ['Extraction Duration', self._format_duration(extraction_duration)],
            ['Database Upload Duration', self._format_duration(db_upload_duration)],
            ['Total Execution Time', self._format_duration(total_duration)]
        ])
        story.append(self._create_comprehensive_summary_table(
            comprehensive_summary, 
            success_count, 
            failure_count
        ))
        story.append(Spacer(1, 8))
        
        # === PORTAL-WISE DETAILS ===
        story.append(self._create_section_header("� Portal-wise Extraction Details"))
        
        portal_table_data = [['Portal', 'Status', 'Attempts', 'Duration', 'Start', 'End', 'Error']]
        portal_status_colors = []  # Track which rows need color coding
        portal_retry_status = []  # Track retry status for special coloring
        
        for portal_name in portals_processed:
            timing = portal_timings.get(portal_name, {})
            result = portal_results.get(portal_name, {})
            
            start_time = timing.get('start')
            end_time = timing.get('end')
            duration = timing.get('duration')
            
            is_success = result.get('success', False)
            attempts = result.get('attempts', 1)
            retry_success = result.get('retry_success', False)
            
            # Determine status text and color coding
            if is_success:
                if attempts > 1 and retry_success:
                    # Succeeded after retry - use yellow/warning color
                    status = "RETRY OK"
                    portal_status_colors.append('retry')
                    portal_retry_status.append(True)
                else:
                    # Succeeded on first attempt
                    status = "SUCCESS"
                    portal_status_colors.append('success')
                    portal_retry_status.append(False)
            else:
                # Failed (possibly after retry)
                status = "FAILED"
                portal_status_colors.append('failed')
                portal_retry_status.append(False)
            
            attempts_str = f"{attempts}" if attempts > 1 else "1"
            
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
                error_display = Paragraph(
                    "No errors",
                    ParagraphStyle(
                        name='NoErrorText',
                        parent=self.styles['Normal'],
                        fontSize=8,
                        textColor=self.colors['text_muted'],
                        alignment=TA_CENTER
                    )
                )
            
            # Wrap portal name in Paragraph for proper word wrapping
            portal_display = Paragraph(
                portal_name,
                ParagraphStyle(
                    name='PortalCellText',
                    parent=self.styles['Normal'],
                    fontSize=8,
                    textColor=colors.HexColor('#2d3748'),
                    leading=10,
                    wordWrap='CJK'  # Enable word wrapping
                )
            )
            
            portal_table_data.append([
                portal_display,  # Wrapped portal name
                status,
                attempts_str,
                duration_str,
                start_str,
                end_str,
                error_display
            ])
        
        story.append(self._create_portal_table(portal_table_data, portal_status_colors))
        story.append(Spacer(1, 8))
        
        # === RETRY DETAILS (if any retries occurred) ===
        retry_portals = [p for p in portals_processed if portal_results.get(p, {}).get('attempts', 1) > 1]
        if retry_portals:
            story.append(self._create_section_header("🔄 Retry Attempt Details"))
            
            retry_success_count = sum(
                1 for p in retry_portals 
                if portal_results.get(p, {}).get('retry_success', False)
            )
            retry_failed_count = len(retry_portals) - retry_success_count
            
            # Summary paragraph
            retry_summary_text = (
                f"<b>{len(retry_portals)} portal(s)</b> failed on first attempt and were automatically retried. "
                f"<b style='color:#276749'>{retry_success_count} succeeded</b> on second attempt, "
                f"<b style='color:#c53030'>{retry_failed_count} failed</b> again."
            )
            story.append(Paragraph(retry_summary_text, ParagraphStyle(
                name='RetrySummaryText',
                parent=self.styles['Normal'],
                fontSize=9,
                spaceAfter=6,
                textColor=colors.HexColor('#2d3748')
            )))
            
            # Retry details table
            retry_table_data = [['Portal', 'Attempt 1', 'Attempt 2', 'Final Result']]
            
            for portal_name in retry_portals:
                result = portal_results.get(portal_name, {})
                timing = portal_timings.get(portal_name, {})
                
                # First attempt info
                first_attempt = timing.get('first_attempt', {})
                first_dur = first_attempt.get('duration')
                first_info = self._format_duration(first_dur.total_seconds()) if first_dur else "N/A"
                
                # Create Paragraph for first attempt
                first_cell = Paragraph(
                    f"<b>❌ Failed</b><br/>{first_info}",
                    ParagraphStyle(
                        name='RetryAttempt1Cell',
                        parent=self.styles['Normal'],
                        fontSize=8,
                        textColor=colors.HexColor('#2d3748'),
                        leading=12,
                        alignment=1  # Center
                    )
                )
                
                # Retry attempt info
                retry_attempt = timing.get('retry_attempt', {})
                retry_dur = retry_attempt.get('duration')
                retry_success = result.get('retry_success', False)
                
                if retry_dur:
                    retry_status_icon = "✅ Success" if retry_success else "❌ Failed"
                    retry_info = self._format_duration(retry_dur.total_seconds())
                    retry_cell = Paragraph(
                        f"<b>{retry_status_icon}</b><br/>{retry_info}",
                        ParagraphStyle(
                            name='RetryAttempt2Cell',
                            parent=self.styles['Normal'],
                            fontSize=8,
                            textColor=colors.HexColor('#2d3748'),
                            leading=12,
                            alignment=1  # Center
                        )
                    )
                else:
                    retry_cell = Paragraph(
                        "Not retried",
                        ParagraphStyle(
                            name='NotRetriedCell',
                            parent=self.styles['Normal'],
                            fontSize=8,
                            textColor=colors.HexColor('#718096'),
                            alignment=1
                        )
                    )
                
                # Final result
                if result.get('success', False):
                    final_result = "RETRY OK"
                    final_color = colors.HexColor('#92400e')
                    final_bg = colors.HexColor('#fef3c7')
                else:
                    final_result = "FAILED"
                    final_color = colors.HexColor('#c53030')
                    final_bg = colors.HexColor('#fed7d7')
                
                retry_table_data.append([
                    portal_name,
                    first_cell,
                    retry_cell,
                    final_result
                ])
            
            # Create retry table
            retry_table = Table(retry_table_data, colWidths=[140, 110, 110, 110])
            retry_style = [
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]
            
            # Color code final results
            for i in range(len(retry_portals)):
                row_idx = i + 1
                result = portal_results.get(retry_portals[i], {})
                if result.get('success', False):
                    # Success after retry - yellow/amber
                    retry_style.append(('BACKGROUND', (3, row_idx), (3, row_idx), colors.HexColor('#fef3c7')))
                    retry_style.append(('TEXTCOLOR', (3, row_idx), (3, row_idx), colors.HexColor('#92400e')))
                    retry_style.append(('FONTNAME', (3, row_idx), (3, row_idx), 'Helvetica-Bold'))
                else:
                    # Failed even after retry - red
                    retry_style.append(('BACKGROUND', (3, row_idx), (3, row_idx), colors.HexColor('#fed7d7')))
                    retry_style.append(('TEXTCOLOR', (3, row_idx), (3, row_idx), colors.HexColor('#c53030')))
                    retry_style.append(('FONTNAME', (3, row_idx), (3, row_idx), 'Helvetica-Bold'))
            
            retry_table.setStyle(TableStyle(retry_style))
            story.append(retry_table)
            story.append(Spacer(1, 8))
        
        # === STAGING COMPARISON RESULTS ===
        # This shows the ACTUAL changes detected by comparing staging vs original table
        # NOT the old delete+insert counts (which are misleading)
        if change_report and db_upload_success:
            story.append(self._create_section_header("🔍 Staging Comparison Results"))
            
            # Calculate totals
            total_new = len(change_report.new_records)
            total_modified = len(change_report.modified_records)
            total_deleted = len(change_report.deleted_records)
            total_unchanged = change_report.unchanged_count
            total_changes = total_new + total_modified + total_deleted
            
            # Only show table if there are changes
            if total_changes > 0:
                # Add explanation
                story.append(Paragraph(
                    "<i>ℹ️ Shows actual changes detected by comparing new extraction against existing database</i>",
                    ParagraphStyle(
                        name='StagingNote',
                        parent=self.styles['Normal'],
                        fontSize=7,
                        textColor=colors.HexColor('#2b6cb0'),
                        spaceAfter=6
                    )
                ))
                
                # Build comparison table
                comparison_data = [['Portal', 'New Values', 'Modified', 'Deleted', 'Unchanged', 'Total Changes']]
                
                changes_by_company = change_report.get_changes_by_company()
                
                for company in sorted(changes_by_company.keys()):
                    data = changes_by_company[company]
                    new_count = len(data.get('new', []))
                    modified_count = len(data.get('modified', []))
                    deleted_count = len(data.get('deleted', []))
                    
                    # Just show the changes we know about
                    total_changes_company = new_count + modified_count + deleted_count
                    
                    comparison_data.append([
                        company,
                        str(new_count),
                        str(modified_count),
                        str(deleted_count),
                        '-',  # Not easily calculable per company
                        str(total_changes_company)
                    ])
                
                # Add totals row
                comparison_data.append([
                    '📊 TOTAL',
                    str(total_new),
                    str(total_modified),
                    str(total_deleted),
                    str(total_unchanged),
                    str(total_changes)
                ])
                
                story.append(self._create_staging_comparison_table(comparison_data))
                story.append(Spacer(1, 6))
            
            # Summary message
            if total_changes == 0:
                msg = "✅ <b>No changes detected</b> - Database already up to date!"
                msg_detail = f"<i>All {total_unchanged} records in the database match the extracted data. No updates needed.</i>"
            else:
                msg = f"✅ <b>{total_changes} changes applied</b> - Only modified data was updated"
                msg_detail = f"<i>New: {total_new}, Modified: {total_modified}, Deleted: {total_deleted}, Unchanged: {total_unchanged}</i>"
            
            story.append(Paragraph(
                msg,
                ParagraphStyle(
                    name='StagingSummary',
                    parent=self.styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#22543d'),
                    spaceBefore=6,
                    spaceAfter=2
                )
            ))
            
            story.append(Paragraph(
                msg_detail,
                ParagraphStyle(
                    name='StagingDetail',
                    parent=self.styles['Normal'],
                    fontSize=8,
                    textColor=colors.HexColor('#4a5568'),
                    spaceAfter=6
                )
            ))
            
            # === DETAILED DROPDOWN CHANGES ===
            # Show ALL specific dropdown values that changed (not just samples)
            if total_changes > 0:
                story.append(Spacer(1, 6))
                story.append(self._create_section_header("📋 Detailed Dropdown Changes"))
                
                # Add explanation
                story.append(Paragraph(
                    "<i>Complete list of all values that were added, modified, or removed from the database</i>",
                    ParagraphStyle(
                        name='DropdownChangesNote',
                        parent=self.styles['Normal'],
                        fontSize=7,
                        textColor=colors.HexColor('#4a5568'),
                        spaceAfter=6,
                        leftIndent=10
                    )
                ))
                
                # Get FULL summary with ALL values
                dropdown_summary = change_report.get_dropdown_change_summary(show_all=True)
                
                for company in sorted(dropdown_summary.keys()):
                    # Company subheader with box
                    story.append(Paragraph(
                        f"<b>▶ {company}</b>",
                        ParagraphStyle(
                            name='CompanySubheader',
                            parent=self.styles['Normal'],
                            fontSize=9,
                            textColor=colors.HexColor('#1a365d'),
                            backColor=colors.HexColor('#e2e8f0'),
                            spaceBefore=8,
                            spaceAfter=4,
                            leftIndent=5,
                            borderPadding=3
                        )
                    ))
                    
                    dropdowns = dropdown_summary[company]
                    for dropdown_name in sorted(dropdowns.keys()):
                        data = dropdowns[dropdown_name]
                        
                        # Build change description
                        changes_desc = []
                        if data['new_count'] > 0:
                            changes_desc.append(f"<font color='#276749'><b>+{data['new_count']} new</b></font>")
                        if data['modified_count'] > 0:
                            changes_desc.append(f"<font color='#2c5282'><b>~{data['modified_count']} modified</b></font>")
                        if data['deleted_count'] > 0:
                            changes_desc.append(f"<font color='#c05621'><b>-{data['deleted_count']} deleted</b></font>")
                        
                        # Dropdown name with counts
                        story.append(Paragraph(
                            f"• <b>{dropdown_name}</b>: {', '.join(changes_desc)}",
                            ParagraphStyle(
                                name='DropdownName',
                                parent=self.styles['Normal'],
                                fontSize=8,
                                leftIndent=15,
                                spaceBefore=4,
                                spaceAfter=2
                            )
                        ))
                        
                        # Show ALL values (not just samples)
                        # NEW VALUES - show all
                        if data['all_new']:
                            all_new_text = ', '.join(f'"{v}"' for v in data['all_new'])
                            story.append(Paragraph(
                                f"<font color='#276749'><b>New Values ({len(data['all_new'])}):</b> {all_new_text}</font>",
                                ParagraphStyle(
                                    name='NewValues',
                                    parent=self.styles['Normal'],
                                    fontSize=7,
                                    leftIndent=25,
                                    textColor=colors.HexColor('#276749'),
                                    spaceAfter=2
                                )
                            ))
                        
                        # DELETED VALUES - show all
                        if data['all_deleted']:
                            all_deleted_text = ', '.join(f'"{v}"' for v in data['all_deleted'])
                            story.append(Paragraph(
                                f"<font color='#c05621'><b>Deleted Values ({len(data['all_deleted'])}):</b> {all_deleted_text}</font>",
                                ParagraphStyle(
                                    name='DeletedValues',
                                    parent=self.styles['Normal'],
                                    fontSize=7,
                                    leftIndent=25,
                                    textColor=colors.HexColor('#c05621'),
                                    spaceAfter=2
                                )
                            ))
                        
                        # MODIFIED VALUES - show all with old → new
                        if data['all_modified']:
                            mod_texts = [f'"{mod["old"]}" → "{mod["new"]}"' for mod in data['all_modified']]
                            all_mod_text = ', '.join(mod_texts)
                            story.append(Paragraph(
                                f"<font color='#2c5282'><b>Modified Values ({len(data['all_modified'])}):</b> {all_mod_text}</font>",
                                ParagraphStyle(
                                    name='ModifiedValues',
                                    parent=self.styles['Normal'],
                                    fontSize=7,
                                    leftIndent=25,
                                    textColor=colors.HexColor('#2c5282'),
                                    spaceAfter=2
                                )
                            ))
        
        # === STAGING UPLOAD INFO ===
        story.append(self._create_section_header("📤 Staging Upload Info"))
        
        db_status = "SUCCESS" if db_upload_success else "FAILED"
        
        # Check if only_mapped_mode is enabled
        only_mapped_mode = mapping_details.get('only_mapped_mode', False) if mapping_details else False
        upload_mode = "ONLY MAPPED DROPDOWNS" if only_mapped_mode else "ALL DROPDOWNS"
        
        db_data = [
            ['Status', db_status],
            ['Upload Mode', upload_mode],
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
        
        # === BROKER BREAKDOWN (Multi-Broker Mode) ===
        if broker_details:
            from src.config.broker_config import get_broker_name
            
            broker_ids = broker_details.get('broker_ids', [])
            broker_to_portals = broker_details.get('broker_to_portals', {})
            
            if broker_ids and broker_to_portals:
                story.append(self._create_section_header("🏢 Multi-Broker Breakdown"))
                
                # Info text
                info_text = f"This extraction run processed data for <b>{len(broker_ids)} broker(s)</b>. Each portal's data was uploaded for all relevant brokers in a single batch operation."
                story.append(Paragraph(info_text, ParagraphStyle(
                    name='BrokerInfoText',
                    parent=self.styles['Normal'],
                    fontSize=8,
                    spaceAfter=6,
                    textColor=colors.HexColor('#4a5568')
                )))
                
                # Broker breakdown table
                broker_table_data = [['Broker', 'Portal Count', 'Portal Names']]
                
                for broker_id in broker_ids:
                    portals = broker_to_portals.get(broker_id, [])
                    broker_name = get_broker_name(broker_id)
                    portal_list = ', '.join(portals) if portals else 'None'
                    
                    broker_table_data.append([
                        f"Broker {broker_id}\n{broker_name}",
                        str(len(portals)),
                        portal_list
                    ])
                
                broker_table = Table(broker_table_data, colWidths=[120, 80, 260])
                broker_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
                ]))
                
                story.append(broker_table)
                story.append(Spacer(1, 10))
        
        # === DATABASE OPERATIONS SUMMARY ===
        story.append(self._create_section_header("📊 Database Operations Summary"))
        
        # Get data from change_report if available
        old_backups_removed = 0
        backup_records_created = 0
        staging_cleared = 0
        audit_records_logged = 0
        
        if change_report:
            old_backups_removed = getattr(change_report, 'old_backups_removed', 0)
            backup_records_created = getattr(change_report, 'backup_count', 0)
            staging_cleared = getattr(change_report, 'staging_cleared', 0)
            audit_records_logged = getattr(change_report, 'audit_records_logged', 0)
        
        total_changes = 0
        if change_report:
            total_changes = len(change_report.new_records) + len(change_report.modified_records) + len(change_report.deleted_records)
        
        # Get backup file info from change_report
        full_backup_file = None
        if change_report:
            full_backup_file = getattr(change_report, 'full_backup_file', None)
        
        # Create sentence-based summary style
        sentence_style = ParagraphStyle(
            name='SentenceText',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=12,
            textColor=colors.HexColor('#333333'),
            leftIndent=10,
            spaceAfter=4
        )
        
        # Section header style
        subheader_style = ParagraphStyle(
            name='SubheaderStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2b6cb0'),
            spaceBefore=6,
            spaceAfter=3,
            leftIndent=5
        )
        
        # === BACKUP INFORMATION ===
        story.append(Paragraph("💾 Backup Information:", subheader_style))
        
        if full_backup_file:
            # Extract just the filename from the path
            backup_filename = os.path.basename(full_backup_file)
            story.append(Paragraph(
                f"A full backup was created as <b>{backup_filename}</b> containing <b>{backup_records_created:,}</b> records "
                f"before applying any changes.", sentence_style))
        else:
            story.append(Paragraph(
                f"<b>{backup_records_created:,}</b> records were backed up to the backup table before applying changes.", 
                sentence_style))
        
        if old_backups_removed > 0:
            story.append(Paragraph(
                f"<b>{old_backups_removed:,}</b> old backup records (older than 7 days) were automatically cleaned up.", 
                sentence_style))
        
        story.append(Spacer(1, 4))
        
        # === STAGING OPERATIONS ===
        story.append(Paragraph("📥 Staging Operations:", subheader_style))
        
        story.append(Paragraph(
            f"The staging table was cleared of <b>{staging_cleared:,}</b> records from the previous run, "
            f"and <b>{db_rows_inserted:,}</b> new records were uploaded for comparison.", 
            sentence_style))
        
        story.append(Spacer(1, 4))
        
        # === COMPARISON & SYNC ===
        story.append(Paragraph("🔄 Comparison & Sync:", subheader_style))
        
        if total_changes > 0:
            story.append(Paragraph(
                f"Comparing staging data with the original table detected <b>{total_changes:,}</b> changes. "
                f"All changes have been applied successfully.", 
                sentence_style))
        else:
            story.append(Paragraph(
                "Comparison found no differences - the original table is already up to date.", 
                sentence_style))
        
        story.append(Spacer(1, 4))
        
        # === AUDIT TRAIL ===
        story.append(Paragraph("📝 Audit Trail:", subheader_style))
        
        if audit_records_logged > 0:
            story.append(Paragraph(
                f"<b>{audit_records_logged:,}</b> change records have been logged to the audit table for permanent history tracking.", 
                sentence_style))
        else:
            story.append(Paragraph(
                "No changes were made, so no audit records were logged.", 
                sentence_style))
        
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

        # === DROPDOWN NAMES INSERTED TO STAGING ===
        if mapping_details and mapping_details.get('inserted_dropdown_names') and db_upload_success:
            story.append(self._create_section_header("📝 Dropdown Names Inserted to Staging"))
            
            story.append(Paragraph(
                "<i>Complete list of dropdown field names uploaded to staging table for each portal</i>",
                ParagraphStyle(
                    name='InsertedDropdownsNote',
                    parent=self.styles['Normal'],
                    fontSize=7,
                    textColor=colors.HexColor('#4a5568'),
                    spaceAfter=6,
                    leftIndent=10
                )
            ))
            
            inserted_dropdowns = mapping_details.get('inserted_dropdown_names', {})
            
            for company in sorted(inserted_dropdowns.keys()):
                dropdown_list = inserted_dropdowns[company]
                if dropdown_list:
                    # Company header with count
                    story.append(Paragraph(
                        f"<b>▶ {company}</b> - <font color='#2b6cb0'>{len(dropdown_list)} dropdown types</font>",
                        ParagraphStyle(
                            name='InsertedCompanyHeader',
                            parent=self.styles['Normal'],
                            fontSize=9,
                            textColor=colors.HexColor('#1a365d'),
                            backColor=colors.HexColor('#ebf8ff'),
                            spaceBefore=6,
                            spaceAfter=3,
                            leftIndent=5,
                            borderPadding=3
                        )
                    ))
                    
                    # All dropdown names in comma-separated format
                    dropdown_text = ', '.join(f'"{d}"' for d in dropdown_list)
                    story.append(Paragraph(
                        dropdown_text,
                        ParagraphStyle(
                            name='DropdownList',
                            parent=self.styles['Normal'],
                            fontSize=7,
                            textColor=colors.HexColor('#2d3748'),
                            leftIndent=15,
                            spaceAfter=4
                        )
                    ))

        # === PROFESSIONAL FOOTER ===
        story.append(Spacer(1, 20))
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.colors['border'],
            spaceBefore=0,
            spaceAfter=8
        ))
        story.append(Paragraph(
            f"Extraction Bot v2.0  |  Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  Algospring AI",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=self.colors['text_muted']
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
            ('BACKGROUND', (0, 0), (0, -1), self.colors['light_bg']),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['secondary']),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            ('ROUNDEDCORNERS', [3, 3, 3, 3]),
        ]
        
        # Highlight separator rows (empty label rows)
        for i, row in enumerate(data):
            if row[0] == '':
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#E2E8F0')))
                style.append(('LINEABOVE', (0, i), (-1, i), 1.5, self.colors['border']))
        
        # Highlight success count (row 7 = "Successful")
        if success_count > 0:
            style.append(('BACKGROUND', (1, 7), (1, 7), colors.HexColor('#D1FAE5')))
            style.append(('TEXTCOLOR', (1, 7), (1, 7), self.colors['success']))
            style.append(('FONTNAME', (1, 7), (1, 7), 'Helvetica-Bold'))
        
        # Highlight failure count if > 0 (row 8 = "Failed")
        if failure_count > 0:
            style.append(('BACKGROUND', (1, 8), (1, 8), colors.HexColor('#FEE2E2')))
            style.append(('TEXTCOLOR', (1, 8), (1, 8), self.colors['danger']))
            style.append(('FONTNAME', (1, 8), (1, 8), 'Helvetica-Bold'))
        
        # Highlight total execution time (last row) - Professional blue accent
        style.append(('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#DBEAFE')))
        style.append(('TEXTCOLOR', (0, -1), (-1, -1), self.colors['primary']))
        style.append(('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'))
        style.append(('FONTSIZE', (0, -1), (-1, -1), 10))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_info_table(self, data: List[List[str]], highlight_success=None, highlight_fail=None) -> Table:
        """Create a simple info table with two columns and optional color highlighting."""
        table = Table(data, colWidths=[100, 370])
        
        style = [
            ('BACKGROUND', (0, 0), (0, -1), self.colors['light_bg']),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['secondary']),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping
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
    
    def _create_portal_table(self, data: List[List[str]], status_colors: List = None) -> Table:
        """Create a styled portal details table with color-coded status and word-wrapped error column.
        
        Args:
            data: Table data where error column may contain Paragraph objects for text wrapping
            status_colors: List of status indicators ('success', 'failed', 'retry')
        """
        # Adjusted column widths - wider Portal column to prevent overflow
        # Portal (100) | Status (70) | Attempts (48) | Duration (48) | Start (40) | End (40) | Error (128)
        table = Table(data, colWidths=[100, 70, 48, 48, 40, 40, 128])

        style = [
            # Header row - Professional dark blue
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (5, -1), 'CENTER'),  # Portal to End columns centered
            ('ALIGN', (6, 1), (6, -1), 'LEFT'),  # Error column left-aligned
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top alignment for better wrapping
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
            ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping
        ]

        # Color-code status column based on success/failure/retry
        if status_colors:
            for i, status_type in enumerate(status_colors):
                row_idx = i + 1  # Skip header row
                if status_type == 'success':
                    # Green for success on first attempt
                    style.append(('BACKGROUND', (1, row_idx), (1, row_idx), colors.HexColor('#D1FAE5')))
                    style.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), self.colors['success']))
                    style.append(('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'))
                elif status_type == 'retry':
                    # Yellow/orange for success after retry
                    style.append(('BACKGROUND', (1, row_idx), (1, row_idx), colors.HexColor('#FEF3C7')))
                    style.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), self.colors['warning']))
                    style.append(('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'))
                elif status_type == 'failed':
                    # Red for failure
                    style.append(('BACKGROUND', (1, row_idx), (1, row_idx), colors.HexColor('#FEE2E2')))
                    style.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), colors.HexColor('#c53030')))
                    style.append(('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'))

        # Alternate row colors (except status & error columns)
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#f7fafc')))
                style.append(('BACKGROUND', (2, i), (2, i), colors.HexColor('#f7fafc')))  # Attempts
                style.append(('BACKGROUND', (3, i), (5, i), colors.HexColor('#f7fafc')))  # Duration, Start, End

        table.setStyle(TableStyle(style))
        return table
    
    def _create_deletion_table(self, data: List) -> Table:
        """Create a compact deletion-summary table (one row per portal).

        This table intentionally only shows `Portal` and `Rows Deleted` so the full
        dropdown-name lists can be rendered separately as wrapped paragraphs that
        may span pages safely.
        """
        table = Table(data, colWidths=[340, 130])

        style = [
            # Header row - Amber/Orange for deletion context
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#B45309')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

            # Borders and padding
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]

        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FEF3C7')))

        table.setStyle(TableStyle(style))
        return table
    
    def _create_staging_comparison_table(self, data: List[List[str]]) -> Table:
        """Create a staging comparison table showing new/modified/deleted changes.
        
        Args:
            data: Table data [['Portal', 'New Values', 'Modified', 'Deleted', 'Unchanged', 'Total Changes'], ...]
                  Last row is totals row starting with '📊 TOTAL'
        
        Returns:
            Table: Styled staging comparison table with color-coded totals
        """
        # Column widths: [Portal, New, Modified, Deleted, Unchanged, Total]
        table = Table(data, colWidths=[130, 62, 62, 62, 75, 79])
        
        style = [
            # Header row - Professional blue
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Borders and padding
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
        ]
        
        # Totals row styling (last row)
        totals_row_idx = len(data) - 1
        style.extend([
            ('BACKGROUND', (0, totals_row_idx), (-1, totals_row_idx), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, totals_row_idx), (-1, totals_row_idx), colors.HexColor('#2d3748')),
            ('FONTNAME', (0, totals_row_idx), (-1, totals_row_idx), 'Helvetica-Bold'),
            ('FONTSIZE', (0, totals_row_idx), (-1, totals_row_idx), 9),
        ])
        
        # Alternate row colors for data rows (excluding header and totals)
        for i in range(1, totals_row_idx):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f7fafc')))
        
        # Highlight change columns if they have values > 0
        for i in range(1, totals_row_idx):
            row_data = data[i]
            
            # New values column (index 1) - green if > 0
            if row_data[1] != '0' and row_data[1] != '-':
                style.append(('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#276749')))
                style.append(('FONTNAME', (1, i), (1, i), 'Helvetica-Bold'))
            
            # Modified column (index 2) - blue if > 0
            if row_data[2] != '0' and row_data[2] != '-':
                style.append(('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#2c5282')))
                style.append(('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'))
            
            # Deleted column (index 3) - orange if > 0
            if row_data[3] != '0' and row_data[3] != '-':
                style.append(('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#c05621')))
                style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_mapping_table(self, data: List[List[str]]) -> Table:
        """Create a styled mapping table showing portal field names to database field names.
        
        Args:
            data: List of rows, first row is header ['Portal Field Name', 'Database Field Name']
        
        Returns:
            Table: Styled ReportLab table
        """
        table = Table(data, colWidths=[260, 210])
        
        style = [
            # Header row - Professional blue
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            
            # Borders and padding
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
        ]
        
        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#DBEAFE')))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _create_summary_table(self, data: List[List[str]]) -> Table:
        """Create a styled summary table."""
        table = Table(data, colWidths=[260, 105, 105])
        
        style = [
            # Header row - Professional dark blue
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary_dark']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            
            # Total row (last row) - Light blue accent
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#DBEAFE')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            
            # Data rows
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
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
    mapping_details: Dict = None,
    change_report = None,
    broker_details: Dict = None
) -> str:
    """
    Convenience function to generate extraction report.
    
    Args:
        change_report: ChangeReport object with comparison results (new/modified/deleted records)
    
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
        mapping_details=mapping_details,
        change_report=change_report,
        broker_details=broker_details
    )

"""
Extraction Report Email Notifier
Sends extraction success notifications with PDF report and HTML summary table
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
from .outlook_mailer import send_email_async


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format"""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {remaining_seconds}s"
    else:
        return f"{remaining_seconds}s"


def _build_change_report_html(change_report) -> str:
    """Build HTML section for data change report.
    
    Args:
        change_report: ChangeReport object with comparison results
        
    Returns:
        str: HTML string for the change report section
    """
    if not change_report:
        return ""
    
    total_changes = len(change_report.new_records) + len(change_report.modified_records) + len(change_report.deleted_records)
    
    if total_changes == 0:
        # No changes detected
        return '''
        <div style="margin-bottom: 20px;">
            <div style="font-weight: 600; color: #0066cc; margin-bottom: 10px; font-size: 15px; border-bottom: 2px solid #0066cc; padding-bottom: 5px;">
                📊 Staging Comparison Results
            </div>
            <div style="background-color: #d4edda; padding: 12px; border-radius: 6px; border-left: 3px solid #28a745;">
                <p style="margin: 0; color: #155724; font-weight: 600; font-size: 13px;">✅ No changes detected</p>
                <p style="margin: 5px 0 0 0; color: #155724; font-size: 12px;">All extracted data matches the existing records in the database.</p>
            </div>
        </div>
        '''
    
    # Build change summary rows
    new_count = len(change_report.new_records)
    mod_count = len(change_report.modified_records)
    del_count = len(change_report.deleted_records)
    unchanged_count = change_report.unchanged_count
    
    # Build portal-wise breakdown rows
    changes_by_company = change_report.get_changes_by_company()
    portal_rows = ""
    for company, data in sorted(changes_by_company.items()):
        c_new = len(data.get('new', []))
        c_mod = len(data.get('modified', []))
        c_del = len(data.get('deleted', []))
        c_total = c_new + c_mod + c_del
        portal_rows += f'''
        <tr>
            <td style="padding: 6px; border-bottom: 1px solid #ddd; color: #333333; font-size: 12px;">{company}</td>
            <td style="padding: 6px; border-bottom: 1px solid #ddd; text-align: center; color: #28a745; font-weight: 600; font-size: 12px;">{c_new if c_new > 0 else '-'}</td>
            <td style="padding: 6px; border-bottom: 1px solid #ddd; text-align: center; color: #d69e2e; font-weight: 600; font-size: 12px;">{c_mod if c_mod > 0 else '-'}</td>
            <td style="padding: 6px; border-bottom: 1px solid #ddd; text-align: center; color: #dc3545; font-weight: 600; font-size: 12px;">{c_del if c_del > 0 else '-'}</td>
            <td style="padding: 6px; border-bottom: 1px solid #ddd; text-align: center; font-weight: 600; font-size: 12px;">{c_total}</td>
        </tr>
        '''
    
    # Check for subtle changes (whitespace/case)
    subtle_changes = [r for r in change_report.modified_records if r.difference_type in ('WHITESPACE_CHANGE', 'INTERNAL_WHITESPACE', 'CASE_CHANGE')]
    subtle_warning = ""
    if subtle_changes:
        subtle_warning = f'''
        <div style="margin-top: 10px; background-color: #fff3cd; padding: 8px; border-radius: 6px; border-left: 3px solid #d69e2e;">
            <p style="margin: 0; color: #856404; font-weight: 600; font-size: 12px;">⚠️ Subtle Changes Detected ({len(subtle_changes)} records)</p>
            <p style="margin: 3px 0 0 0; color: #856404; font-size: 11px;">Some records have whitespace or case differences that may need review.</p>
        </div>
        '''
    
    # Build dropdown-level changes section
    dropdown_changes_html = ""
    try:
        dropdown_summary = change_report.get_dropdown_change_summary()
        if dropdown_summary:
            dropdown_rows = ""
            for company in sorted(dropdown_summary.keys()):
                dropdowns = dropdown_summary[company]
                # Portal header
                dropdown_rows += f'''
                <tr style="background-color: #e2e8f0;">
                    <td colspan="4" style="padding: 6px; font-weight: 600; color: #2b6cb0; border-bottom: 1px solid #cbd5e0; font-size: 12px;">{company}</td>
                </tr>
                '''
                for dropdown_name in sorted(dropdowns.keys()):
                    data = dropdowns[dropdown_name]
                    new_c = data['new_count']
                    del_c = data['deleted_count']
                    mod_c = data['modified_count']
                    
                    # Build samples
                    samples = []
                    if data.get('sample_new'):
                        sample_vals = ", ".join(str(v) for v in data['sample_new'][:2])
                        more = f" (+{new_c - 2})" if new_c > 2 else ""
                        samples.append(f'<span style="color: #276749;">New: {sample_vals}{more}</span>')
                    if data.get('sample_deleted'):
                        sample_vals = ", ".join(str(v) for v in data['sample_deleted'][:2])
                        more = f" (+{del_c - 2})" if del_c > 2 else ""
                        samples.append(f'<span style="color: #c53030;">Del: {sample_vals}{more}</span>')
                    if data.get('sample_modified'):
                        mod = data['sample_modified'][0]
                        samples.append(f'<span style="color: #c05621;">Mod: {str(mod["old"])}→{str(mod["new"])}</span>')
                    
                    sample_html = "<br>".join(samples) if samples else "-"
                    
                    dropdown_rows += f'''
                    <tr>
                        <td style="padding: 5px 6px 5px 18px; border-bottom: 1px solid #eee; color: #333; font-size: 11px;">{dropdown_name}</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; text-align: center; color: #276749; font-size: 11px;">{'+' + str(new_c) if new_c > 0 else '-'}</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; text-align: center; color: #c53030; font-size: 11px;">{'-' + str(del_c) if del_c > 0 else '-'}</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-size: 10px;">{sample_html}</td>
                    </tr>
                    '''
            
            dropdown_changes_html = f'''
            <div style="margin-top: 15px;">
                <div style="font-weight: 600; color: #4a5568; margin-bottom: 8px; font-size: 13px;">🔍 Dropdown Value Changes:</div>
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <thead>
                        <tr>
                            <th style="background-color: #667eea; color: white; padding: 6px; text-align: left; font-size: 12px;">Dropdown</th>
                            <th style="background-color: #667eea; color: white; padding: 6px; text-align: center; width: 45px; font-size: 12px;">New</th>
                            <th style="background-color: #667eea; color: white; padding: 6px; text-align: center; width: 45px; font-size: 12px;">Del</th>
                            <th style="background-color: #667eea; color: white; padding: 6px; text-align: left; font-size: 12px;">Sample Values</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dropdown_rows}
                    </tbody>
                </table>
            </div>
            '''
    except Exception:
        # Fallback if get_dropdown_change_summary doesn't exist
        dropdown_changes_html = ""
    
    # Build detailed dropdown changes section (showing ALL values, not just samples)
    detailed_dropdown_html = ""
    try:
        dropdown_summary_full = change_report.get_dropdown_change_summary(show_all=True)
        if dropdown_summary_full and total_changes > 0:
            detailed_rows = ""
            for company in sorted(dropdown_summary_full.keys()):
                dropdowns = dropdown_summary_full[company]
                # Company header
                detailed_rows += f'''
                <div style="background-color: #e2e8f0; padding: 8px; margin-top: 12px; margin-bottom: 6px; border-left: 3px solid #2b6cb0; font-size: 12px; font-weight: 600; color: #2b6cb0;">
                    ▶ {company}
                </div>
                '''
                for dropdown_name in sorted(dropdowns.keys()):
                    data = dropdowns[dropdown_name]
                    
                    # Build change description
                    changes_desc = []
                    if data['new_count'] > 0:
                        changes_desc.append(f"<span style='color: #276749; font-weight: 600;'>+{data['new_count']} new</span>")
                    if data['modified_count'] > 0:
                        changes_desc.append(f"<span style='color: #2c5282; font-weight: 600;'>~{data['modified_count']} modified</span>")
                    if data['deleted_count'] > 0:
                        changes_desc.append(f"<span style='color: #c05621; font-weight: 600;'>-{data['deleted_count']} deleted</span>")
                    
                    # Dropdown name with counts
                    detailed_rows += f'''
                    <div style="margin-left: 15px; margin-bottom: 8px; margin-top: 6px;">
                        <div style="font-size: 11px; font-weight: 600; color: #333; margin-bottom: 3px;">
                            • {dropdown_name}: {', '.join(changes_desc)}
                        </div>
                    '''
                    
                    # Show ALL new values
                    if data.get('all_new'):
                        all_new_text = ', '.join(f'"{v}"' for v in data['all_new'])
                        detailed_rows += f'''
                        <div style="margin-left: 25px; font-size: 10px; color: #276749; margin-bottom: 2px;">
                            <b>New Values ({len(data['all_new'])}):</b> {all_new_text}
                        </div>
                        '''
                    
                    # Show ALL deleted values
                    if data.get('all_deleted'):
                        all_deleted_text = ', '.join(f'"{v}"' for v in data['all_deleted'])
                        detailed_rows += f'''
                        <div style="margin-left: 25px; font-size: 10px; color: #c05621; margin-bottom: 2px;">
                            <b>Deleted Values ({len(data['all_deleted'])}):</b> {all_deleted_text}
                        </div>
                        '''
                    
                    # Show ALL modified values
                    if data.get('all_modified'):
                        mod_texts = [f'"{mod["old"]}" → "{mod["new"]}"' for mod in data['all_modified']]
                        all_mod_text = ', '.join(mod_texts)
                        detailed_rows += f'''
                        <div style="margin-left: 25px; font-size: 10px; color: #2c5282; margin-bottom: 2px;">
                            <b>Modified Values ({len(data['all_modified'])}):</b> {all_mod_text}
                        </div>
                        '''
                    
                    detailed_rows += '</div>'
            
            detailed_dropdown_html = f'''
            <div style="margin-top: 15px;">
                <div style="font-weight: 600; color: #4a5568; margin-bottom: 8px; font-size: 13px;">📋 Detailed Dropdown Changes</div>
                <div style="font-size: 10px; color: #666; font-style: italic; margin-bottom: 8px; margin-left: 10px;">
                    Complete list of all values that were added, modified, or removed from the database
                </div>
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 6px; border: 1px solid #e0e0e0;">
                    {detailed_rows}
                </div>
            </div>
            '''
    except Exception:
        detailed_dropdown_html = ""
    
    return f'''
    <div style="margin-bottom: 20px;">
        <div style="font-weight: 600; color: #0066cc; margin-bottom: 10px; font-size: 15px; border-bottom: 2px solid #0066cc; padding-bottom: 5px;">
            📊 Staging Comparison Results
        </div>
        
        <!-- Change Summary Cards -->
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 12px;">
            <tr>
                <td style="background: #c6f6d5; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #9ae6b4; width: 25%;">
                    <div style="font-size: 20px; font-weight: bold; color: #276749;">➕ {new_count}</div>
                    <div style="font-size: 11px; color: #276749;">NEW</div>
                </td>
                <td style="width: 4px;"></td>
                <td style="background: #fef3c7; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #f6e05e; width: 25%;">
                    <div style="font-size: 20px; font-weight: bold; color: #744210;">✏️ {mod_count}</div>
                    <div style="font-size: 11px; color: #744210;">MODIFIED</div>
                </td>
                <td style="width: 4px;"></td>
                <td style="background: #fed7d7; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #fc8181; width: 25%;">
                    <div style="font-size: 20px; font-weight: bold; color: #c53030;">🗑️ {del_count}</div>
                    <div style="font-size: 11px; color: #c53030;">DELETED</div>
                </td>
                <td style="width: 4px;"></td>
                <td style="background: #e2e8f0; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #cbd5e0; width: 25%;">
                    <div style="font-size: 20px; font-weight: bold; color: #4a5568;">✓ {unchanged_count}</div>
                    <div style="font-size: 11px; color: #4a5568;">UNCHANGED</div>
                </td>
            </tr>
        </table>
        
        <!-- Portal-wise Breakdown -->
        <div style="font-weight: 600; color: #4a5568; margin-bottom: 8px; font-size: 13px;">Changes by Portal:</div>
        <table style="width: 100%; border-collapse: collapse; margin-top: 5px;">
            <thead>
                <tr>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: left; font-size: 12px;">Portal</th>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: center; font-size: 12px;">New</th>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: center; font-size: 12px;">Modified</th>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: center; font-size: 12px;">Deleted</th>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: center; font-size: 12px;">Total</th>
                </tr>
            </thead>
            <tbody>
                {portal_rows}
            </tbody>
        </table>
        
        {dropdown_changes_html}
        
        {detailed_dropdown_html}
        
        {subtle_warning}
    </div>
    '''


def _build_broker_breakdown_html(broker_details: Dict) -> str:
    """
    Build HTML for broker breakdown section.
    Shows which portals are assigned to which brokers.
    
    Args:
        broker_details: Dict with broker_ids, broker_to_portals, portal_details
        
    Returns:
        str: HTML string for broker breakdown section
    """
    if not broker_details:
        return ""
    
    from src.config.broker_config import get_broker_name
    
    broker_ids = broker_details.get('broker_ids', [])
    broker_to_portals = broker_details.get('broker_to_portals', {})
    
    if not broker_ids or not broker_to_portals:
        return ""
    
    # Build broker rows
    broker_rows = ""
    for broker_id in broker_ids:
        portals = broker_to_portals.get(broker_id, [])
        broker_name = get_broker_name(broker_id)
        portal_list = ', '.join(portals) if portals else 'None'
        
        broker_rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #333333; font-size: 12px; font-weight: 600;">
                Broker {broker_id} - {broker_name}
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center; color: #0066cc; font-weight: 600; font-size: 12px;">
                {len(portals)}
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #555555; font-size: 11px;">
                {portal_list}
            </td>
        </tr>
        """
    
    return f'''
    <div style="margin-bottom: 20px;">
        <div style="font-weight: 600; color: #0066cc; margin-bottom: 10px; font-size: 15px; border-bottom: 2px solid #0066cc; padding-bottom: 5px;">
            🏢 Multi-Broker Breakdown
        </div>
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
            <p style="margin: 0; color: #495057; font-size: 11px; font-style: italic;">
                This extraction run processed data for {len(broker_ids)} broker(s). Each portal's data was uploaded for all relevant brokers.
            </p>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-top: 5px;">
            <thead>
                <tr>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: left; font-size: 12px;">Broker</th>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: center; width: 80px; font-size: 12px;">Portals</th>
                    <th style="background-color: #4a5568; color: white; padding: 8px; text-align: left; font-size: 12px;">Portal Names</th>
                </tr>
            </thead>
            <tbody>
                {broker_rows}
            </tbody>
        </table>
    </div>
    '''


def _build_database_operations_html(change_report) -> str:
    """
    Build HTML for detailed database operations section.
    Shows all database operations as clean bullet points.
    """
    if not change_report:
        return ""
    
    old_backups_removed = getattr(change_report, 'old_backups_removed', 0)
    backup_records_created = getattr(change_report, 'backup_count', 0)
    staging_cleared = getattr(change_report, 'staging_cleared', 0)
    staging_uploaded = getattr(change_report, 'staging_count', 0)
    audit_records_logged = getattr(change_report, 'audit_records_logged', 0)
    
    total_changes = len(change_report.new_records) + len(change_report.modified_records) + len(change_report.deleted_records)
    status_text = "Changes applied" if total_changes > 0 else "No changes needed"
    
    return f'''
    <div style="margin-bottom: 20px;">
        <div style="font-weight: 600; color: #0066cc; margin-bottom: 10px; font-size: 15px; border-bottom: 2px solid #0066cc; padding-bottom: 5px;">
            💾 Database Operations Summary
        </div>
        
        <!-- Operations as bullet points -->
        <div style="background-color: #f8f9fa; padding: 12px; border-radius: 6px; margin-top: 8px;">
            <ul style="margin: 0; padding-left: 20px; list-style-type: disc;">
                <li style="padding: 4px 0; color: #495057; font-size: 12px;">
                    <span style="color: #666;">Old backups removed (>7 days):</span> 
                    <span style="font-weight: 600; color: {"#dc3545" if old_backups_removed > 0 else "#6c757d"};">{old_backups_removed:,}</span>
                </li>
                <li style="padding: 4px 0; color: #495057; font-size: 12px;">
                    <span style="color: #666;">New backup records created:</span> 
                    <span style="font-weight: 600; color: #28a745;">{backup_records_created:,}</span>
                </li>
                <li style="padding: 4px 0; color: #495057; font-size: 12px;">
                    <span style="color: #666;">Old staging data cleared:</span> 
                    <span style="font-weight: 600; color: {"#dc3545" if staging_cleared > 0 else "#6c757d"};">{staging_cleared:,}</span>
                </li>
                <li style="padding: 4px 0; color: #495057; font-size: 12px;">
                    <span style="color: #666;">New staging records uploaded:</span> 
                    <span style="font-weight: 600; color: #0066cc;">{staging_uploaded:,}</span>
                </li>
                <li style="padding: 4px 0; color: #495057; font-size: 12px;">
                    <span style="color: #666;">Total changes detected:</span> 
                    <span style="font-weight: 600; color: {"#28a745" if total_changes > 0 else "#6c757d"};">{total_changes:,}</span>
                </li>
                <li style="padding: 4px 0; color: #495057; font-size: 12px;">
                    <span style="color: #666;">Status:</span> 
                    <span style="font-weight: 600; color: #28a745;">{"✅ " + status_text}</span>
                </li>
                <li style="padding: 4px 0; color: #495057; font-size: 12px;">
                    <span style="color: #666;">Audit records logged:</span> 
                    <span style="font-weight: 600; color: #6f42c1;">{audit_records_logged:,}</span>
                    <span style="font-style: italic; color: #6c757d;"> (For permanent change history)</span>
                </li>
            </ul>
        </div>
    </div>
    '''


def build_extraction_summary_email(
    run_timestamp: str,
    overall_start_time: datetime,
    overall_end_time: datetime,
    portal_results: Dict[str, bool],
    portal_timings: Dict,
    db_upload_success: bool,
    db_rows_inserted: int,
    db_upload_duration: float,
    total_duration: float,
    portals_processed: List[str],
    pdf_report_path: str = None,
    change_report = None,
    broker_details: Dict = None,
) -> str:
    """Build professional HTML email body for extraction completion notification.
    
    Args:
        run_timestamp: Timestamp of the extraction run
        overall_start_time: Start time of the extraction
        overall_end_time: End time of the extraction
        portal_results: Dictionary mapping portal names to success status
        portal_timings: Dictionary with timing information for each portal
        db_upload_success: Whether database upload was successful
        db_rows_inserted: Number of rows inserted into database
        db_upload_duration: Duration of database upload in seconds
        total_duration: Total duration of the process in seconds
        portals_processed: List of portal names that were processed
        pdf_report_path: Path to the PDF report (for display in email)
        change_report: ChangeReport object with comparison results (new/modified/deleted records)
        
    Returns:
        str: HTML formatted email body
    """
    
    # Calculate statistics
    successful_portals = [name for name, result in portal_results.items() if result.get('success', False)]
    failed_portals = [name for name, result in portal_results.items() if not result.get('success', False)]
    success_rate = (len(successful_portals) / len(portal_results) * 100) if portal_results else 0
    
    # Determine overall status
    overall_status = "✅ SUCCESS" if db_upload_success and not failed_portals else "⚠️ COMPLETED WITH ISSUES"
    status_color = "#28a745" if db_upload_success and not failed_portals else "#ffc107"
    
    # Build portal table rows
    portal_rows = ""
    for portal_name in portals_processed:
        timing = portal_timings.get(portal_name, {})
        result_dict = portal_results.get(portal_name, {})
        success = result_dict.get('success', False)
        error_msg = result_dict.get('error', None)
        
        status_icon = "✅" if success else "❌"
        status_text = "Success" if success else "Failed"
        status_bg = "#d4edda" if success else "#f8d7da"
        
        duration = timing.get('duration')
        duration_str = format_duration(duration.total_seconds()) if duration else "N/A"
        
        start_time = timing.get('start')
        end_time = timing.get('end')
        time_range = f"{start_time.strftime('%H:%M:%S')} → {end_time.strftime('%H:%M:%S')}" if start_time and end_time else "N/A"
        
        # Build error row if portal failed
        error_row = ""
        if not success and error_msg:
            error_row = f"""
                <tr>
                    <td colspan="4" style="padding: 6px 8px 8px 30px; border-bottom: 1px solid #ddd; background-color: #fff3cd; color: #856404; font-size: 11px; font-style: italic;">
                        ⚠️ Error: {error_msg}
                    </td>
                </tr>"""
        
        portal_rows += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: {'0' if error_row else '1px solid #ddd'}; color: #333333; font-size: 13px; word-wrap: break-word; word-break: break-word; max-width: 200px;">{status_icon} {portal_name}</td>
                    <td style="padding: 8px; border-bottom: {'0' if error_row else '1px solid #ddd'}; background-color: {status_bg}; font-weight: 600; color: #333333; font-size: 13px;">{status_text}</td>
                    <td style="padding: 8px; border-bottom: {'0' if error_row else '1px solid #ddd'}; color: #333333; font-size: 13px;">{duration_str}</td>
                    <td class="time-range" style="padding: 8px; border-bottom: {'0' if error_row else '1px solid #ddd'}; font-size: 12px; color: #333333;">{time_range}</td>
                </tr>{error_row}"""
    
    # Build the HTML email
    html = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333333; line-height: 1.6; margin: 0; padding: 0; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #ddd; border-top: none; }}
            .summary-box {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px; 
                           border-left: 4px solid {status_color}; }}
            .section {{ margin-bottom: 30px; }}
            .section-title {{ font-weight: bold; color: #0066cc; margin-bottom: 15px; font-size: 18px; 
                             border-bottom: 2px solid #0066cc; padding-bottom: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background-color: #5a6c7d; color: white; padding: 12px; text-align: left; font-weight: bold; }}
            td {{ padding: 12px; border-bottom: 1px solid #ddd; color: #333333; }}
            .footer {{ text-align: center; color: #777; font-size: 12px; margin-top: 30px; 
                      padding-top: 20px; border-top: 1px solid #ddd; }}
            
            /* Mobile Responsive Styles */
            @media only screen and (max-width: 600px) {{
                .container {{ padding: 10px !important; }}
                .header {{ padding: 20px !important; border-radius: 0 !important; }}
                .header h1 {{ font-size: 22px !important; }}
                .content {{ padding: 15px !important; border-radius: 0 !important; }}
                .summary-box {{ padding: 15px !important; }}
                .section-title {{ font-size: 16px !important; }}
                table {{ font-size: 13px !important; }}
                th, td {{ padding: 8px !important; }}
                th {{ font-size: 12px !important; }}
                /* Stack columns on mobile */
                .stats-card {{ display: block !important; width: 100% !important; margin-bottom: 10px !important; }}
                /* Make portal timing text smaller */
                .time-range {{ font-size: 10px !important; }}
            }}
        </style>
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333333; line-height: 1.6; margin: 0; padding: 0;">
        <div style="max-width: 700px; margin: 0 auto; padding: 15px;">
            <div style="background: {status_color}; color: white; padding: 12px 15px; text-align: center; border-radius: 4px 4px 0 0;">
                <h1 style="margin: 0; font-size: 18px; color: white; font-weight: 600;">{overall_status}</h1>
                <p style="margin: 4px 0 0 0; font-size: 11px; color: white; opacity: 0.9;">Run ID: {run_timestamp}</p>
            </div>
            
            <div style="background-color: #ffffff; padding: 20px; border: 1px solid #ddd; border-top: none; color: #333333;">
                <!-- Overall Summary -->
                <div style="background-color: #f8f9fa; padding: 8px; border-radius: 4px; margin-bottom: 15px; border-left: 3px solid {status_color};">
                    <table style="width: 100%; border-collapse: collapse; margin: 0;">
                        <tr>
                            <td style="padding: 3px; border: none; font-weight: 600; color: #555555; font-size: 11px;">📅 Execution Date:</td>
                            <td style="padding: 3px; border: none; text-align: right; color: #333333; font-size: 11px;">{overall_start_time.strftime('%B %d, %Y')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 3px; border: none; font-weight: 600; color: #555555; font-size: 11px;">⏰ Start Time:</td>
                            <td style="padding: 3px; border: none; text-align: right; color: #333333; font-size: 11px;">{overall_start_time.strftime('%H:%M:%S')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 3px; border: none; font-weight: 600; color: #555555; font-size: 11px;">🏁 End Time:</td>
                            <td style="padding: 3px; border: none; text-align: right; color: #333333; font-size: 11px;">{overall_end_time.strftime('%H:%M:%S')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 3px; border: none; font-weight: 600; color: #555555; font-size: 11px;">⏱️ Total Duration:</td>
                            <td style="padding: 3px; border: none; text-align: right; color: #333333; font-size: 11px;"><strong>{format_duration(total_duration)}</strong></td>
                        </tr>
                    </table>
                </div>
                
                <!-- Statistics Cards - Using Table for Email Compatibility -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                    <tr>
                        <td style="background: #f8f9fa; padding: 8px; border-radius: 4px; text-align: center; border: 1px solid #e0e0e0; width: 33%;">
                            <div style="font-size: 20px; font-weight: bold; color: {status_color}; margin-bottom: 2px;">{len(portals_processed)}</div>
                            <div style="font-size: 10px; color: #666666;">Portals Processed</div>
                        </td>
                        <td style="width: 8px;"></td>
                        <td style="background: #f8f9fa; padding: 8px; border-radius: 4px; text-align: center; border: 1px solid #e0e0e0; width: 33%;">
                            <div style="font-size: 20px; font-weight: bold; color: #28a745; margin-bottom: 2px;">{len(successful_portals)}</div>
                            <div style="font-size: 10px; color: #666666;">Successful</div>
                        </td>
                        <td style="width: 8px;"></td>
                        <td style="background: #f8f9fa; padding: 8px; border-radius: 4px; text-align: center; border: 1px solid #e0e0e0; width: 33%;">
                            <div style="font-size: 20px; font-weight: bold; color: #dc3545; margin-bottom: 2px;">{len(failed_portals)}</div>
                            <div style="font-size: 10px; color: #666666;">Failed</div>
                        </td>
                    </tr>
                </table>
                
                <!-- Portal Results Table -->
                <div style="margin-bottom: 20px;">
                    <div style="font-weight: 600; color: #0066cc; margin-bottom: 10px; font-size: 15px; border-bottom: 2px solid #0066cc; padding-bottom: 5px;">
                        📊 Portal Extraction Results
                    </div>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 8px;">
                        <thead>
                            <tr>
                                <th style="background-color: #5a6c7d; color: white; padding: 8px; text-align: left; font-weight: bold; font-size: 13px;">Portal Name</th>
                                <th style="background-color: #5a6c7d; color: white; padding: 8px; text-align: left; font-weight: bold; font-size: 13px;">Status</th>
                                <th style="background-color: #5a6c7d; color: white; padding: 8px; text-align: left; font-weight: bold; font-size: 13px;">Duration</th>
                                <th style="background-color: #5a6c7d; color: white; padding: 8px; text-align: left; font-weight: bold; font-size: 13px;">Time Range</th>
                            </tr>
                        </thead>
                        <tbody>
                            {portal_rows}
                        </tbody>
                    </table>
                </div>
                
                <!-- Broker Breakdown (Multi-Broker Mode) -->
                {_build_broker_breakdown_html(broker_details) if broker_details else ''}
                
                <!-- Database Operations Summary -->
                {_build_database_operations_html(change_report) if change_report else ''}
                
                <!-- Data Change Report Section (Staging Summary) -->
                {_build_change_report_html(change_report) if change_report else ''}
                
                <!-- Failed Portals Details (if any) -->
                {f'''
                <div style="margin-bottom: 20px;">
                    <div style="font-weight: 600; color: #dc3545; margin-bottom: 10px; font-size: 15px; border-bottom: 2px solid #dc3545; padding-bottom: 5px;">
                        ⚠️ Failed Portal Details
                    </div>
                    <div style="background-color: #f8d7da; padding: 12px; border-radius: 6px; border-left: 3px solid #dc3545;">
                        <table style="width: 100%; border-collapse: collapse; margin: 0;">
                            {"".join([f'''
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid #f5c6cb; font-weight: 600; color: #721c24; width: 30%; font-size: 13px;">❌ {portal_name}</td>
                                <td style="padding: 8px; border-bottom: 1px solid #f5c6cb; color: #721c24; font-size: 12px;">{portal_results[portal_name].get('error', 'Unknown error')}</td>
                            </tr>
                            ''' for portal_name in failed_portals])}
                        </table>
                    </div>
                </div>
                ''' if failed_portals else ''}
                
                <div style="text-align: center; color: #777777; font-size: 11px; margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
                    <p style="color: #777777; margin: 3px 0;"><strong>Automated Data Extraction System</strong></p>
                    <p style="color: #777777; margin: 3px 0;">This is an automated notification from the Insurance Portal Extraction Bot.</p>
                    <p style="color: #777777; margin: 3px 0;">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
                    <p style="margin-top: 8px; font-size: 10px; color: #999999;">
                        For questions or issues, please contact the Development Team.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


async def send_extraction_success_notification(
    run_timestamp: str,
    overall_start_time: datetime,
    overall_end_time: datetime,
    portal_results: Dict[str, Dict],
    portal_timings: Dict,
    db_upload_success: bool,
    db_rows_inserted: int,
    db_upload_duration: float,
    total_duration: float,
    portals_processed: List[str],
    pdf_report_path: str = None,
    recipients_to: List[str] = None,
    recipients_cc: List[str] = None,
    logger: Optional[logging.Logger] = None,
    change_report = None,    broker_details: Dict = None,) -> bool:
    """Send extraction completion notification email with PDF report.
    
    Args:
        run_timestamp: Timestamp of the extraction run
        overall_start_time: Start time of the extraction
        overall_end_time: End time of the extraction
        portal_results: Dictionary mapping portal names to result dictionaries with 'success' and 'error' keys
        portal_timings: Dictionary with timing information for each portal
        db_upload_success: Whether database upload was successful
        db_rows_inserted: Number of rows inserted into database
        db_upload_duration: Duration of database upload in seconds
        total_duration: Total duration of the process in seconds
        portals_processed: List of portal names that were processed
        pdf_report_path: Path to the PDF report to attach
        recipients_to: List of TO recipients (developers)
        recipients_cc: List of CC recipients (BA team)
        logger: Optional logger instance
        change_report: ChangeReport object with comparison results (new/modified/deleted records)
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    # Build email subject
    failed_portals = [name for name, result in portal_results.items() if not result.get('success', False)]
    if db_upload_success and not failed_portals:
        subject = f"✅ Extraction Complete - {run_timestamp} - All Portals Successful"
    else:
        subject = f"⚠️ Extraction Complete - {run_timestamp} - {len(failed_portals)} Portal(s) Failed"
    
    # Build email body
    body = build_extraction_summary_email(
        run_timestamp=run_timestamp,
        overall_start_time=overall_start_time,
        overall_end_time=overall_end_time,
        portal_results=portal_results,
        portal_timings=portal_timings,
        db_upload_success=db_upload_success,
        db_rows_inserted=db_rows_inserted,
        db_upload_duration=db_upload_duration,
        total_duration=total_duration,
        portals_processed=portals_processed,
        pdf_report_path=pdf_report_path,
        change_report=change_report,
        broker_details=broker_details,
    )
    
    # Prepare attachments
    attachments = []
    if pdf_report_path and Path(pdf_report_path).exists():
        attachments.append(Path(pdf_report_path))
    
    # Send email
    try:
        success = await send_email_async(
            subject=subject,
            body=body,
            to=recipients_to or [],
            cc=recipients_cc or [],
            attachments=attachments if attachments else None,
            logger=logger,
        )
        return success
    except Exception as e:
        if logger:
            logger.error(f"Failed to send extraction notification email: {e}")
        else:
            print(f"❌ Failed to send extraction notification email: {e}")
        return False

"""
Standalone Email Service Usage Examples
Shows how to use the email notification service independently from the extraction bot
"""
import asyncio
from pathlib import Path
from datetime import datetime
from src.services.email_notifications.outlook_mailer import send_email_async, send_email_sync


# ============================================================================
# EXAMPLE 1: Simple Text Email (Async)
# ============================================================================
async def example_simple_email():
    """Send a simple text email"""
    success = await send_email_async(
        subject="Simple Test Email",
        body="Hello!\n\nThis is a simple text email.\n\nBest regards,\nBot",
        to=["recipient@company.com"],
    )
    return success


# ============================================================================
# EXAMPLE 2: HTML Email with Styling (Async)
# ============================================================================
async def example_html_email():
    """Send an HTML formatted email with styling"""
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; }
            .content { padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Important Notification</h1>
            </div>
            <div class="content">
                <h2>Process Completed</h2>
                <p>Your automated process has completed successfully.</p>
                <ul>
                    <li>Start Time: 10:00 AM</li>
                    <li>End Time: 10:45 AM</li>
                    <li>Records Processed: 1,542</li>
                </ul>
                <p>Thank you!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success = await send_email_async(
        subject="📊 Process Completion Report",
        body=html_content,
        to=["recipient@company.com"],
        cc=["manager@company.com"],
    )
    return success


# ============================================================================
# EXAMPLE 3: Email with Attachments (Async)
# ============================================================================
async def example_email_with_attachments():
    """Send an email with multiple attachments"""
    success = await send_email_async(
        subject="Report - Data Extract 2026-02-23",
        body="<h2>Daily Extract Report</h2><p>Please find attached the daily extraction reports.</p>",
        to=["recipient@company.com"],
        cc=["team@company.com"],
        attachments=[
            Path("reports/extraction_report.pdf"),
            Path("reports/summary.xlsx"),
        ]
    )
    return success


# ============================================================================
# EXAMPLE 4: Using Custom Azure AD Credentials (Async)
# ============================================================================
async def example_custom_credentials():
    """Send email using custom Azure AD app credentials"""
    success = await send_email_async(
        subject="Custom Auth Email",
        body="This email uses custom Azure AD credentials",
        to=["recipient@company.com"],
        client_id="YOUR_CLIENT_ID",
        tenant_id="YOUR_TENANT_ID",
        cache_path="config/custom_token_cache.json"
    )
    return success


# ============================================================================
# EXAMPLE 5: Synchronous Email (Non-Async Context)
# ============================================================================
def example_sync_email():
    """Send email from non-async code using the synchronous wrapper"""
    success = send_email_sync(
        subject="Sync Email Test",
        body="This email is sent from synchronous (non-async) code",
        to=["recipient@company.com"],
    )
    return success


# ============================================================================
# EXAMPLE 6: Email with Error Handling and Logging
# ============================================================================
async def example_with_logging():
    """Send email with proper error handling and logging"""
    import logging
    
    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    try:
        success = await send_email_async(
            subject="Email with Logging",
            body="Check the logs to see detailed email sending progress",
            to=["recipient@company.com"],
            logger=logger,  # Pass logger for detailed output
        )
        
        if success:
            logger.info("Email sent successfully!")
        else:
            logger.error("Email sending failed")
            
        return success
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


# ============================================================================
# EXAMPLE 7: Batch Email Sending
# ============================================================================
async def example_batch_emails():
    """Send multiple emails in batch"""
    recipients = [
        {"email": "dev1@company.com", "name": "Developer 1"},
        {"email": "dev2@company.com", "name": "Developer 2"},
        {"email": "dev3@company.com", "name": "Developer 3"},
    ]
    
    results = []
    
    for recipient in recipients:
        html_body = f"""
        <html>
        <body>
            <h2>Hello {recipient['name']}!</h2>
            <p>This is a personalized email sent to you.</p>
            <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        try:
            success = await send_email_async(
                subject=f"Personal Report for {recipient['name']}",
                body=html_body,
                to=[recipient['email']],
            )
            results.append((recipient['name'], success))
            
            # Small delay between emails to avoid rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Failed to send to {recipient['name']}: {e}")
            results.append((recipient['name'], False))
    
    # Print summary
    print("\nBatch Email Results:")
    for name, success in results:
        status = "✅ Sent" if success else "❌ Failed"
        print(f"  {name}: {status}")
    
    return results


# ============================================================================
# EXAMPLE 8: Error Notification Email
# ============================================================================
async def example_error_notification():
    """Send an error notification email with stack trace"""
    error_info = {
        "process": "Data Extraction",
        "error_message": "Connection timeout to database",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "stack_trace": "Traceback (most recent call last):\n  File...",
    }
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: monospace; }}
            .error-header {{ background-color: #dc3545; color: white; padding: 20px; border-radius: 5px; }}
            .error-content {{ padding: 20px; background-color: #f8d7da; border: 1px solid #dc3545; margin-top: 10px; }}
            .stack-trace {{ background-color: #2b2b2b; color: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="error-header">
            <h1>❌ Process Error Alert</h1>
        </div>
        <div class="error-content">
            <h2>Error Details</h2>
            <p><strong>Process:</strong> {error_info['process']}</p>
            <p><strong>Timestamp:</strong> {error_info['timestamp']}</p>
            <p><strong>Error Message:</strong> {error_info['error_message']}</p>
            <h3>Stack Trace:</h3>
            <div class="stack-trace">
                <pre>{error_info['stack_trace']}</pre>
            </div>
        </div>
    </body>
    </html>
    """
    
    success = await send_email_async(
        subject=f"🚨 ERROR ALERT - {error_info['process']} Failed",
        body=html_body,
        to=["devops@company.com", "support@company.com"],
    )
    return success


# ============================================================================
# EXAMPLE 9: Daily Summary Report
# ============================================================================
async def example_daily_summary():
    """Send a daily summary report email"""
    summary_data = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "total_processed": 1542,
        "successful": 1498,
        "failed": 44,
        "success_rate": 97.1,
        "processing_time": "2h 15m",
    }
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 8px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #e0e0e0; }}
            .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
            .stat-label {{ font-size: 14px; color: #666; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Daily Processing Summary</h1>
            <p>{summary_data['date']}</p>
        </div>
        
        <div style="padding: 20px;">
            <h2>Overview</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{summary_data['total_processed']:,}</div>
                    <div class="stat-label">Total Processed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #28a745;">{summary_data['successful']:,}</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #dc3545;">{summary_data['failed']}</div>
                    <div class="stat-label">Failed</div>
                </div>
            </div>
            
            <h3>Performance Metrics</h3>
            <ul>
                <li><strong>Success Rate:</strong> {summary_data['success_rate']}%</li>
                <li><strong>Total Processing Time:</strong> {summary_data['processing_time']}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    success = await send_email_async(
        subject=f"📊 Daily Summary - {summary_data['date']}",
        body=html_body,
        to=["management@company.com"],
        cc=["team@company.com"],
    )
    return success


# ============================================================================
# RUN EXAMPLES
# ============================================================================
async def run_all_examples():
    """Run all examples (for testing)"""
    print("Running all email examples...\n")
    
    print("1. Simple Email...")
    # await example_simple_email()
    
    print("2. HTML Email...")
    # await example_html_email()
    
    print("3. Email with Attachments...")
    # await example_email_with_attachments()
    
    print("4. Custom Credentials...")
    # await example_custom_credentials()
    
    print("5. Sync Email...")
    # example_sync_email()
    
    print("6. Email with Logging...")
    # await example_with_logging()
    
    print("7. Batch Emails...")
    # await example_batch_emails()
    
    print("8. Error Notification...")
    # await example_error_notification()
    
    print("9. Daily Summary...")
    # await example_daily_summary()
    
    print("\nAll examples completed!")


if __name__ == "__main__":
    # Uncomment the examples you want to test
    print("Email Service Usage Examples")
    print("=" * 70)
    print("Uncomment the examples in run_all_examples() to test them")
    print("=" * 70)
    
    # asyncio.run(run_all_examples())

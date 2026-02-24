# Email Notifications Module

This module handles automated email notifications for extraction bot completion reports.

## 📁 Files

- **`outlook_mailer.py`** - Core email functionality using Microsoft Graph API with OAuth
- **`extraction_notifier.py`** - Builds and sends extraction completion notifications
- **`__init__.py`** - Package initialization and exports

## 🚀 Usage

```python
from src.services.email_notifications import send_extraction_success_notification

# Send extraction completion notification
await send_extraction_success_notification(
    run_timestamp="20260223_143022",
    overall_start_time=start_time,
    overall_end_time=end_time,
    portal_results=portal_results,
    portal_timings=portal_timings,
    db_upload_success=True,
    db_rows_inserted=1542,
    db_upload_duration=12.5,
    total_duration=390,
    portals_processed=["Medgulf", "Takaful"],
    pdf_report_path="reports/extraction_report.pdf",
    recipients_to=["dev@company.com"],
    recipients_cc=["ba@company.com"],
)
```

## 📧 Features

- ✅ OAuth-based authentication (Microsoft Graph API)
- ✅ Automatic token refresh
- ✅ Professional HTML email templates
- ✅ PDF report attachments
- ✅ Portal statistics and timing tables
- ✅ Database upload status

## ⚙️ Configuration

See `config.yaml` for email notification settings:
- Enable/disable notifications
- Configure recipients (TO/CC)
- Set OAuth credentials

## 📖 Documentation

See `EMAIL_NOTIFICATION_SETUP.md` in the project root for:
- Setup instructions
- Azure AD app configuration
- Troubleshooting guide
- Testing procedures

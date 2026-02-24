"""
Email Notifications Module
Handles extraction completion notifications via Microsoft Outlook
"""

from .outlook_mailer import send_email_async, send_email_sync, get_valid_access_token
from .extraction_notifier import send_extraction_success_notification

__all__ = [
    'send_email_async',
    'send_email_sync',
    'get_valid_access_token',
    'send_extraction_success_notification',
]

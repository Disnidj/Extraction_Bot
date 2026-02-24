"""
Microsoft Outlook Email Service using Graph API with OAuth Authentication
Handles automatic token refresh and email sending with attachments
"""
from __future__ import annotations
import os
import base64
from pathlib import Path
from typing import Dict, Optional, Sequence
import requests
import logging


class OutlookTokenManager:
    """Manages OAuth tokens for Microsoft Graph API with automatic refresh"""
    
    def __init__(self, client_id: str, tenant_id: str, cache_path: str):
        import msal
        
        self.config = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "scope": ["https://graph.microsoft.com/Mail.Send"],
            "authority": f"https://login.microsoftonline.com/{tenant_id}"
        }
        self.cache_path = cache_path
        self.app = msal.PublicClientApplication(
            self.config["client_id"],
            authority=self.config["authority"],
            token_cache=msal.SerializableTokenCache()
        )
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load token cache from file"""
        try:
            cache_file = Path(self.cache_path)
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = f.read()
                    if cache_data:
                        self.app.token_cache.deserialize(cache_data)
        except FileNotFoundError:
            pass  # No cache exists yet
        except Exception as e:
            print(f"Warning: Failed to load token cache: {e}")
    
    def _save_cache(self) -> None:
        """Save token cache to file"""
        try:
            cache_file = Path(self.cache_path)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = self.app.token_cache.serialize()
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(cache_data)
        except Exception as e:
            print(f"Warning: Failed to save token cache: {e}")
    
    def get_token(self, force_refresh: bool = False) -> str:
        """Get a valid access token, refreshing if necessary"""
        if not force_refresh:
            # Try silent token acquisition first
            accounts = self.app.get_accounts()
            if accounts:
                result = self.app.acquire_token_silent(
                    self.config["scope"],
                    account=accounts[0]
                )
                if result and "access_token" in result:
                    self._save_cache()
                    return result["access_token"]

        # If we get here, we need to do interactive auth
        print("\n🔐 Authentication Required: Please login in the browser window...")
        result = self.app.acquire_token_interactive(scopes=self.config["scope"])
        if "access_token" in result:
            self._save_cache()
            print("✅ Authentication successful!")
            return result["access_token"]
        else:
            error = result.get("error", "Unknown error")
            error_desc = result.get("error_description", "No description")
            raise ValueError(f"Authentication failed: {error} - {error_desc}")


# Global token manager instance
_token_manager = None


def get_token_manager(client_id: str = None, tenant_id: str = None, cache_path: str = None) -> OutlookTokenManager:
    """Get or create the token manager instance"""
    global _token_manager
    
    if _token_manager is None:
        # Use provided values or fall back to environment variables
        client_id = client_id or os.getenv("OUTLOOK_CLIENT_ID", "1ac522e4-707b-4dc8-b7c7-ba88bc4d0e6f")
        tenant_id = tenant_id or os.getenv("OUTLOOK_TENANT_ID", "a3dfb5e4-789f-427f-ada4-9481ec87a98e")
        cache_path = cache_path or os.getenv("OUTLOOK_TOKEN_CACHE", "config/outlook_token_cache.json")
        
        _token_manager = OutlookTokenManager(client_id, tenant_id, cache_path)
    
    return _token_manager


def get_valid_access_token(force_refresh: bool = False, **kwargs) -> str:
    """Get a valid access token using the token manager with automatic refresh support.
    
    Args:
        force_refresh: If True, skip cache and force token refresh
        **kwargs: Optional client_id, tenant_id, cache_path for initialization
        
    Returns:
        A valid access token string
        
    Raises:
        ValueError: If token acquisition fails
    """
    manager = get_token_manager(
        client_id=kwargs.get('client_id'),
        tenant_id=kwargs.get('tenant_id'),
        cache_path=kwargs.get('cache_path')
    )
    return manager.get_token(force_refresh=force_refresh)


async def send_email_async(
    *,
    subject: str,
    body: str,
    to: Optional[Sequence[str]] = None,
    cc: Optional[Sequence[str]] = None,
    bcc: Optional[Sequence[str]] = None,
    attachments: Optional[Sequence[Path]] = None,
    logger: Optional[logging.Logger] = None,
    client_id: str = None,
    tenant_id: str = None,
    cache_path: str = None,
) -> bool:
    """Send email using Microsoft Graph API with automatic token refresh.

    This function will:
    1. Get a valid access token, refreshing if needed
    2. Send the email using Graph API
    3. If the token is expired, refresh it and retry automatically
    4. Handle up to 2 retries for token expiration

    Args:
        subject: Email subject line
        body: Email body text (supports HTML)
        to: List of recipient email addresses
        cc: List of CC recipient email addresses
        bcc: List of BCC recipient email addresses
        attachments: List of file paths to attach
        logger: Optional logger for status/debug messages
        client_id: Azure AD app client ID (optional, uses env var if not provided)
        tenant_id: Azure AD tenant ID (optional, uses env var if not provided)
        cache_path: Path to token cache file (optional, uses default if not provided)

    Returns:
        bool: True if email sent successfully, False otherwise

    Raises:
        ValueError: If token acquisition fails
        RuntimeError: If email sending fails after retries
    """
    
    # Get token with auto-refresh
    try:
        token = get_valid_access_token(
            client_id=client_id,
            tenant_id=tenant_id,
            cache_path=cache_path
        )
    except ValueError as e:
        if logger:
            logger.error(f"Failed to get access token: {e}")
        else:
            print(f"❌ Failed to get access token: {e}")
        raise
        
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    
    # Build recipients lists
    to_list = [{"emailAddress": {"address": addr}} for addr in (to or [])]
    cc_list = [{"emailAddress": {"address": addr}} for addr in (cc or [])]
    bcc_list = [{"emailAddress": {"address": addr}} for addr in (bcc or [])]
    
    # Prepare attachments if any
    attachment_list = []
    if attachments:
        for att in attachments:
            p = Path(att).resolve()
            if not p.exists():
                if logger:
                    logger.warning(f"Attachment not found: {p}")
                continue
            try:
                # Read file and encode to base64
                data = p.read_bytes()
                b64_data = base64.b64encode(data).decode()
                attachment_list.append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": p.name,
                    "contentBytes": b64_data
                })
                if logger:
                    logger.info(f"Added attachment: {p.name} ({len(data) / 1024:.1f} KB)")
            except Exception as e:
                if logger:
                    logger.warning(f"Failed to attach file {p}: {e}")

    # Auto-detect content type
    content_type = "Text"
    if any(tag in body for tag in ["<html>", "<table", "<h1>", "<h2>", "<h3>", "<div>", "<p>", "<br>"]):
        content_type = "HTML"
    
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": content_type, 
                "content": body
            },
            "toRecipients": to_list,
            "ccRecipients": cc_list,
            "bccRecipients": bcc_list,
            "attachments": attachment_list
        },
        "saveToSentItems": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json" 
    }
    
    if logger:
        to_str = ", ".join(to or [])
        logger.info(f"📧 Sending email to: {to_str}")
        logger.info(f"   Subject: {subject}")
        if attachments:
            logger.info(f"   Attachments: {len([p for p in attachments if Path(p).exists()])} file(s)")
    else:
        print(f"\n📧 Sending email to: {', '.join(to or [])}")
        print(f"   Subject: {subject}")
    
    # Try sending with auto-retry on token expiration
    max_retries = 2
    for attempt in range(max_retries):
        resp = requests.post(url, headers=headers, json=message)
        
        if resp.status_code in (200, 202):
            if logger:
                logger.info(f"✅ Email sent successfully!")
            else:
                print(f"✅ Email sent successfully!")
            return True
            
        # Check if token expired
        if resp.status_code == 401 and "InvalidAuthenticationToken" in resp.text:
            if attempt < max_retries - 1:  # Don't refresh on last attempt
                if logger:
                    logger.warning("Token expired, refreshing and retrying...")
                else:
                    print("⚠️ Token expired, refreshing and retrying...")
                try:
                    # Force token refresh and update headers
                    token = get_valid_access_token(
                        force_refresh=True,
                        client_id=client_id,
                        tenant_id=tenant_id,
                        cache_path=cache_path
                    )
                    headers["Authorization"] = f"Bearer {token}"
                    continue
                except Exception as e:
                    if logger:
                        logger.error(f"Token refresh failed: {e}")
                    else:
                        print(f"❌ Token refresh failed: {e}")
                    break

        # Non-token error or max retries reached
        error = f"Failed to send mail. HTTP {resp.status_code}: {resp.text}"
        if logger:
            logger.error(error)
        else:
            print(f"❌ {error}")
        raise RuntimeError(error)
    
    return False


def send_email_sync(
    *,
    subject: str,
    body: str,
    to: Optional[Sequence[str]] = None,
    cc: Optional[Sequence[str]] = None,
    bcc: Optional[Sequence[str]] = None,
    attachments: Optional[Sequence[Path]] = None,
    logger: Optional[logging.Logger] = None,
    client_id: str = None,
    tenant_id: str = None,
    cache_path: str = None,
) -> bool:
    """Synchronous wrapper for send_email_async.
    
    Use this when calling from non-async code.
    For all parameters, see send_email_async documentation.
    """
    import asyncio
    
    # Check if we're already in an event loop
    try:
        loop = asyncio.get_running_loop()
        # We're in an async context, create a new thread to avoid issues
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                send_email_async(
                    subject=subject,
                    body=body,
                    to=to,
                    cc=cc,
                    bcc=bcc,
                    attachments=attachments,
                    logger=logger,
                    client_id=client_id,
                    tenant_id=tenant_id,
                    cache_path=cache_path
                )
            )
            return future.result()
    except RuntimeError:
        # No event loop running, we can use asyncio.run directly
        return asyncio.run(
            send_email_async(
                subject=subject,
                body=body,
                to=to,
                cc=cc,
                bcc=bcc,
                attachments=attachments,
                logger=logger,
                client_id=client_id,
                tenant_id=tenant_id,
                cache_path=cache_path
            )
        )

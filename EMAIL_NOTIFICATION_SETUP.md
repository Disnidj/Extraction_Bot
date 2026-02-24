# Email Notification Service - Setup Guide

## 📧 Overview

This email notification service automatically sends extraction completion reports to your development and BA teams after each successful extraction run. It includes:

- **Professional HTML Summary Email** - Beautiful table showing portal results, timing, and database statistics
- **PDF Report Attachment** - Detailed extraction report automatically attached
- **OAuth Authentication** - Secure Microsoft Graph API integration with automatic token refresh
- **Easy Configuration** - Simple YAML-based setup for recipients and credentials

---

## 🎯 What Your Senior Dev Sent You

The **Email sending - Demo user** folder contains:

1. **`mailer.py`** - Core email module using Microsoft Graph API with OAuth authentication
2. **`send_email.py`** - Helper wrapper functions (reference implementation)
3. **`outlook_token_cache.json`** - Token cache for maintaining authentication sessions

This is a **working template** that has been adapted and integrated into your extraction bot.

---

## 🚀 Quick Start

### Step 1: Install Required Package

```bash
pip install msal
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Recipients

Edit `config.yaml` and update the email recipients:

```yaml
extraction_notifications:
  enabled: true  # Set to false to disable emails
  recipients:
    to_recipients:
      - "recipient1@company.com"
      - "recipient2@company.com"
    cc_recipients:
      - "cc1@company.com"
      - "cc2@company.com"
```

### Step 3: First Run Authentication

On the **first run**, you'll need to authenticate:

1. Run your extraction bot as normal
2. After extraction completes, a browser window will pop up
3. Login with your Microsoft 365 account (the one you want to send emails FROM)
4. Grant permissions when prompted
5. Token will be saved and future runs will be automatic! ✅

**Note:** You only need to do this ONCE. After that, the system uses the cached token.

---

## 🔐 Authentication Details

### Using Demo Credentials (Quick Test)

The demo credentials from your senior dev are already configured and will work out-of-the-box:

- **Client ID**: `1ac522e4-707b-4dc8-b7c7-ba88bc4d0e6f`
- **Tenant ID**: `a3dfb5e4-789f-427f-ada4-9481ec87a98e`
- **Token Cache**: `config/outlook_token_cache.json`

Just authenticate once with your Microsoft account and you're done!

### Using Your Organization's Azure AD App (Production)

For production use, you should register your own Azure AD application:

#### Create Azure AD App:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Name: "Extraction Bot Email Service"
5. Supported account types: **Accounts in this organizational directory only**
6. Redirect URI: **Public client/native** → `http://localhost`
7. Click **Register**

#### Configure API Permissions:

1. In your app, go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Delegated permissions**
3. Add these permissions:
   - `Mail.Send`
   - `Mail.ReadWrite` (optional, for sent items)
   - `User.Read`
4. Click **Grant admin consent** (if you're admin)

#### Get Your Credentials:

1. Go to **Overview** tab
2. Copy **Application (client) ID**
3. Copy **Directory (tenant) ID**

#### Update Config:

Edit `config.yaml`:

```yaml
extraction_notifications:
  outlook:
    client_id: "YOUR_CLIENT_ID_HERE"
    tenant_id: "YOUR_TENANT_ID_HERE"
    token_cache_path: "config/outlook_token_cache.json"
```

---

## 📊 Email Content

### What the Email Contains:

✅ **Header Section**
- Overall success/failure status
- Run timestamp and ID

✅ **Summary Box**
- Execution date and time
- Total duration

✅ **Statistics Cards**
- Total portals processed
- Successful extractions
- Failed extractions

✅ **Portal Results Table**
| Portal Name | Status | Duration | Time Range |
|------------|--------|----------|------------|
| Medgulf | ✅ Success | 2m 15s | 10:30:15 → 10:32:30 |
| Takaful | ✅ Success | 1m 45s | 10:32:35 → 10:34:20 |
| Orient | ❌ Failed | 0m 30s | 10:34:25 → 10:34:55 |

✅ **Database Upload Status**
- Upload success/failure
- Rows inserted
- Upload duration

✅ **PDF Report Attachment**
- Detailed extraction report automatically attached

---

## 🎨 Email Preview

The email is sent as **professional HTML** with:
- Color-coded status indicators (green for success, red for failures)
- Responsive table design
- Modern styling with gradients and cards
- Mobile-friendly layout

**Sample Subject Lines:**
- `✅ Extraction Complete - 20260223_143022 - All Portals Successful`
- `⚠️ Extraction Complete - 20260223_143022 - 2 Portal(s) Failed`

---

## 🔧 Configuration Options

### Enable/Disable Email Notifications

In `config.yaml`:

```yaml
extraction_notifications:
  enabled: true  # Set to false to disable all email notifications
```

When disabled, the extraction will run normally but skip sending emails.

### Change Recipients

You can specify different recipients for TO and CC:

```yaml
extraction_notifications:
  recipients:
    to_recipients:  # Primary recipients
      - "team-lead@company.com"
      - "developer@company.com"
    cc_recipients:  # Carbon copy recipients
      - "manager@company.com"
      - "analyst@company.com"
```

### Token Cache Location

By default, tokens are cached in `config/outlook_token_cache.json`. To change:

```yaml
extraction_notifications:
  outlook:
    token_cache_path: "custom/path/token_cache.json"
```

---

## 🐛 Troubleshooting

### Problem: Authentication popup keeps appearing

**Solution:** 
- Check if the token cache file exists at `config/outlook_token_cache.json`
- Make sure the account you're logging in with has permission to send emails
- Verify the token cache file has write permissions

### Problem: "Invalid client" error

**Solution:**
- Double-check your `client_id` in `config.yaml`
- Verify the Azure AD app registration is active
- Ensure redirect URI is set to `http://localhost`

### Problem: "Insufficient privileges" error

**Solution:**
- In Azure Portal, check API permissions in your app
- Make sure `Mail.Send` permission is granted
- Click "Grant admin consent for [Your Org]"

### Problem: Email not sending but no errors

**Solution:**
- Check if `enabled: true` in `config.yaml`
- Verify recipient email addresses are valid
- Check if PDF report was generated successfully
- Look in the logs for detailed error messages

### Problem: Token expired errors

**Solution:**
- The system should auto-refresh tokens, but if it fails:
- Delete the `config/outlook_token_cache.json` file
- Run the bot again and re-authenticate

---

## 📁 File Structure

```
Extraction_Bot/
├── config.yaml                          # Main configuration
├── config/
│   └── outlook_token_cache.json        # OAuth token cache (auto-created)
├── src/
│   ├── services/
│   │   └── email_service/
│   │       ├── outlook_mailer.py       # Core email functionality
│   │       └── extraction_notifier.py   # Extraction-specific email builder
│   └── utils/
│       └── load_yaml.py                # Config loader (updated)
└── main.py                              # Main script (integrated)
```

---

## 🔄 How It Works

1. **Extraction Completes** → PDF report is generated
2. **Configuration Check** → Reads `config.yaml` for enabled status and recipients
3. **Token Management** → Checks for cached token, uses it or prompts for authentication
4. **Email Building** → Creates HTML summary with statistics and timing
5. **Attachment** → Attaches the PDF report
6. **Sending** → Sends via Microsoft Graph API
7. **Auto-Retry** → If token expires, automatically refreshes and retries

---

## 🎓 Using the Service Manually

You can also use the email service in other parts of your code:

```python
from src.services.email_service.outlook_mailer import send_email_async
from pathlib import Path

# Send a custom email
await send_email_async(
    subject="Test Email",
    body="<h1>Hello!</h1><p>This is a test email.</p>",
    to=["recipient@company.com"],
    cc=["cc@company.com"],
    attachments=[Path("report.pdf")],
    logger=logger  # optional
)
```

---

## 📝 Testing

### Test Email Configuration

Create a simple test script:

```python
import asyncio
from src.services.email_service.outlook_mailer import send_email_async

async def test_email():
    success = await send_email_async(
        subject="Test - Extraction Bot Email Service",
        body="<h2>Test Email</h2><p>If you receive this, email service is working!</p>",
        to=["your-email@company.com"],
    )
    print(f"Email sent: {success}")

asyncio.run(test_email())
```

Run it:
```bash
python test_email_service.py
```

---

## 🔒 Security Notes

1. **Token Cache Security**: The `outlook_token_cache.json` file contains authentication tokens. 
   - ✅ Already added to `.gitignore` 
   - ⚠️ Never commit this file to Git
   - 🔐 Keep it in a secure location

2. **Client Secret**: If you use a confidential client (not recommended for this use case), never commit secrets.

3. **Service Account**: Consider using a dedicated service account for sending emails rather than personal accounts.

---

## 🎉 Success!

That's it! Your extraction bot now automatically sends professional email notifications to your team after each run.

**Questions?** Check the troubleshooting section or contact your senior dev.

---

**Version:** 1.0  
**Last Updated:** February 23, 2026  
**Author:** Extraction Bot Team

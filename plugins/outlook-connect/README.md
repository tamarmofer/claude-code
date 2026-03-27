# Outlook Connect Plugin

Connect Claude Code to Microsoft Outlook for email and calendar management via the Microsoft Graph API.

## Features

| Command | Description |
|---------|-------------|
| `/outlook-connect:auth` | Authenticate with Microsoft Outlook using device code flow |
| `/outlook-connect:read-emails` | Read recent emails from your inbox |
| `/outlook-connect:send-email` | Compose and send emails |
| `/outlook-connect:search-emails` | Search emails by keyword, sender, or date |
| `/outlook-connect:calendar` | View and manage calendar events |

### Agent

| Agent | Description |
|-------|-------------|
| `email-analyzer` | Analyze emails, extract action items, and prioritize your inbox |

## Setup

### 1. Register an Azure App

1. Go to the [Azure App Registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps) portal
2. Click **New registration**
3. Name: "Claude Code Outlook" (or any name you prefer)
4. Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
5. Click **Register**

### 2. Configure Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Delegated permissions**
3. Add the following permissions:
   - `Mail.Read` - Read user mail
   - `Mail.Send` - Send mail as the user
   - `Calendars.Read` - Read user calendars
   - `Calendars.ReadWrite` - Read and write user calendars
4. Under **Authentication**, enable **Allow public client flows**

### 3. Authenticate

Run `/outlook-connect:auth` and follow the prompts to authenticate via device code flow.

Alternatively, if you already have a token, set it directly:

```bash
export OUTLOOK_ACCESS_TOKEN="your_access_token_here"
```

## Usage Examples

```
/outlook-connect:read-emails 5
/outlook-connect:read-emails 10 SentItems
/outlook-connect:send-email user@example.com
/outlook-connect:search-emails quarterly report
/outlook-connect:calendar today
/outlook-connect:calendar week
/outlook-connect:calendar create
```

## Security Notes

- Access tokens are stored only in environment variables, never written to files
- Tokens expire after approximately 1 hour
- The `/send-email` command always confirms with you before sending
- The `/calendar create` command always confirms event details before creating

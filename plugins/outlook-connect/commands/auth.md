---
description: Authenticate with Microsoft Outlook via device code flow
allowed-tools: Bash(curl:*), AskUserQuestion
---

# Authenticate with Microsoft Outlook

## Your Task

Help the user authenticate with Microsoft Graph API using the OAuth 2.0 device code flow, which is ideal for CLI environments.

### Steps

1. Ask the user for their **Azure App Client ID**. If they don't have one, guide them:
   - Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
   - Click "New registration"
   - Name: "Claude Code Outlook" (or any name)
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: leave blank (not needed for device code flow)
   - After registration, copy the **Application (client) ID**
   - Under "API permissions", add: `Mail.Read`, `Mail.Send`, `Calendars.Read`, `Calendars.ReadWrite`
   - Under "Authentication", enable "Allow public client flows"

2. Initiate device code flow:

```bash
curl -s -X POST \
  "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=<CLIENT_ID>&scope=https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.Send https://graph.microsoft.com/Calendars.ReadWrite offline_access"
```

3. Display the `user_code` and `verification_uri` to the user. Ask them to:
   - Open the verification URL in a browser
   - Enter the code shown
   - Sign in and grant permissions

4. Poll for the token:

```bash
curl -s -X POST \
  "https://login.microsoftonline.com/common/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=<CLIENT_ID>&grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=<DEVICE_CODE>"
```

5. Once the token is obtained, instruct the user to set it:
   ```bash
   export OUTLOOK_ACCESS_TOKEN="<access_token>"
   ```

6. Confirm authentication by fetching user profile:
   ```bash
   curl -s -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
     "https://graph.microsoft.com/v1.0/me?\$select=displayName,mail"
   ```

7. Display the authenticated user's name and email.

### Important

- Never store tokens in files - only use environment variables
- Remind the user that tokens expire (typically after 1 hour) and they may need to re-authenticate

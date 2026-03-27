---
description: Compose and send an email via Outlook
argument-hint: "[recipient email]"
allowed-tools: Bash(curl:*), AskUserQuestion
---

# Send Outlook Email

## Prerequisites

You need a valid Microsoft Graph API access token with `Mail.Send` permission.
The token should be set as the environment variable `OUTLOOK_ACCESS_TOKEN`.

## Your Task

Compose and send an email via the Microsoft Graph API.

Arguments: $ARGUMENTS

### Steps

1. Check if `OUTLOOK_ACCESS_TOKEN` is set. If not, ask the user to provide it.
2. Gather email details. If not provided in arguments, ask the user for:
   - **To**: Recipient email address(es) - comma-separated for multiple
   - **Subject**: Email subject line
   - **Body**: Email body content (plain text or HTML)
   - **CC** (optional): CC recipients
3. Confirm the email details with the user before sending.
4. Send the email using the Microsoft Graph API:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/me/sendMail" \
  -d '{
    "message": {
      "subject": "<subject>",
      "body": {
        "contentType": "Text",
        "content": "<body>"
      },
      "toRecipients": [
        { "emailAddress": { "address": "<recipient>" } }
      ]
    }
  }'
```

5. Report success or failure to the user.

### Important

- ALWAYS confirm the email content with the user before sending
- Never send an email without explicit user approval
- Sanitize any special characters in the JSON payload

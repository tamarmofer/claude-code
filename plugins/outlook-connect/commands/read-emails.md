---
description: Read recent emails from your Outlook inbox
argument-hint: "[number of emails] [folder name]"
allowed-tools: Bash(curl:*), Read, AskUserQuestion
---

# Read Outlook Emails

## Prerequisites

You need a valid Microsoft Graph API access token. If the user has not provided one, ask them to:

1. Register an app at https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
2. Grant `Mail.Read` permission
3. Obtain an access token via OAuth 2.0 authorization code flow or device code flow
4. Set the token as the environment variable `OUTLOOK_ACCESS_TOKEN`

## Your Task

Read emails from the user's Outlook inbox using the Microsoft Graph API.

Arguments: $ARGUMENTS

### Steps

1. Check if `OUTLOOK_ACCESS_TOKEN` is set. If not, ask the user to provide it.
2. Parse the arguments:
   - First argument (optional): number of emails to fetch (default: 10)
   - Second argument (optional): folder name (default: "Inbox")
3. Fetch emails using the Microsoft Graph API:

```bash
curl -s -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/me/mailFolders/{folder}/messages?\$top={count}&\$select=subject,from,receivedDateTime,bodyPreview,isRead&\$orderby=receivedDateTime%20desc"
```

4. Present the emails in a clear, readable format:
   - Show subject, sender, date/time, read status, and a preview of the body
   - Number each email for easy reference
5. Ask the user if they want to read the full body of any specific email.

---
description: Search Outlook emails by keyword, sender, or date
argument-hint: "<search query>"
allowed-tools: Bash(curl:*), AskUserQuestion
---

# Search Outlook Emails

## Prerequisites

You need a valid Microsoft Graph API access token with `Mail.Read` permission.
The token should be set as the environment variable `OUTLOOK_ACCESS_TOKEN`.

## Your Task

Search for emails in the user's Outlook mailbox using the Microsoft Graph API.

Arguments: $ARGUMENTS

### Steps

1. Check if `OUTLOOK_ACCESS_TOKEN` is set. If not, ask the user to provide it.
2. Parse the search query from arguments. If no query is provided, ask the user what they want to search for.
3. Search emails using the Microsoft Graph API:

```bash
curl -s -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/me/messages?\$search=\"<query>\"&\$top=20&\$select=subject,from,receivedDateTime,bodyPreview,isRead&\$orderby=receivedDateTime%20desc"
```

4. Present matching emails in a clear format:
   - Subject, sender, date, read status, body preview
   - Number results for easy reference
5. Offer to read the full content of any specific result.

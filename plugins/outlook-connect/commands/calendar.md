---
description: View and manage Outlook calendar events
argument-hint: "[today|week|create]"
allowed-tools: Bash(curl:*), AskUserQuestion
---

# Outlook Calendar

## Prerequisites

You need a valid Microsoft Graph API access token with `Calendars.Read` and `Calendars.ReadWrite` permissions.
The token should be set as the environment variable `OUTLOOK_ACCESS_TOKEN`.

## Your Task

View or manage calendar events via the Microsoft Graph API.

Arguments: $ARGUMENTS

### Steps

1. Check if `OUTLOOK_ACCESS_TOKEN` is set. If not, ask the user to provide it.
2. Determine the action from arguments:
   - **today** (default): Show today's events
   - **week**: Show this week's events
   - **create**: Create a new calendar event

### View Events

Fetch events using the Microsoft Graph API:

```bash
curl -s -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: outlook.timezone=\"<user_timezone>\"" \
  "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=<start>&endDateTime=<end>&\$select=subject,start,end,location,organizer,isAllDay&\$orderby=start/dateTime"
```

Present events in a clear timeline format showing:
- Time range (or "All Day")
- Event subject
- Location (if any)
- Organizer

### Create Event

If the user wants to create an event, gather:
- **Subject**: Event title
- **Start**: Start date and time
- **End**: End date and time
- **Location** (optional): Event location
- **Body** (optional): Event description
- **Attendees** (optional): Email addresses of attendees

Confirm details with the user, then create:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $OUTLOOK_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/me/events" \
  -d '{
    "subject": "<subject>",
    "start": { "dateTime": "<start>", "timeZone": "UTC" },
    "end": { "dateTime": "<end>", "timeZone": "UTC" },
    "location": { "displayName": "<location>" },
    "attendees": [
      { "emailAddress": { "address": "<email>" }, "type": "required" }
    ]
  }'
```

### Important

- ALWAYS confirm event creation details with the user before sending
- Use appropriate timezone handling

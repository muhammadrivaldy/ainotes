# Google Calendar Integration - Implementation Plan

## Overview

Add Google Calendar integration to create reminders from conversations. This requires upgrading the OAuth flow to support Calendar API access and storing OAuth tokens.

---

## Current State Analysis

**Authentication Flow:**

- Uses simplified Google OAuth with ID tokens only
- Frontend: `@react-oauth/google` library
- Backend: Manual JWT decoding (no token verification)
- Storage: Only user profile data (no OAuth tokens)
- Scopes: Only default (profile, email) - **no Calendar access**

**Critical Gap:** Current flow doesn't request or store OAuth tokens needed for Calendar API access.

---

## Required Architecture Changes

### Phase 1: Upgrade OAuth Flow

**Current:** Client-side ID token flow
**Needed:** Server-side authorization code flow with token storage

#### 1.1 Backend OAuth Endpoints

Create new OAuth flow in `backend/auth.py`:

```python
# New endpoints needed:
@app.get("/auth/google/authorize")
# Redirect user to Google consent screen with calendar scopes

@app.get("/auth/google/callback")
# Handle OAuth callback, exchange code for tokens, store tokens

@app.post("/auth/google/refresh")
# Refresh expired access tokens
```

**Required scopes:**

- `https://www.googleapis.com/auth/calendar.events` (create/edit events)
- `openid`, `email`, `profile` (existing)

#### 1.2 Database Schema Updates

Extend `User` model in `backend/models.py`:

```python
class User(SQLModel, table=True):
    # Existing fields...
    google_access_token: Optional[str] = None      # Encrypted
    google_refresh_token: Optional[str] = None     # Encrypted
    token_expiry: Optional[datetime] = None
```

**Security:** Encrypt tokens using `cryptography` library before storage.

#### 1.3 Dependencies

Add to `backend/requirements.txt`:

```text
google-auth>=2.16.0
google-api-python-client>=2.70.0
google-auth-oauthlib>=1.0.0
cryptography>=41.0.0
```

### Phase 2: Google Calendar Service

Create `backend/calendar_service.py`:

```python
class GoogleCalendarService:
    def __init__(self, user: User):
        # Load tokens, build Calendar API client

    def create_reminder(self, title: str, description: str, datetime: str):
        # Create calendar event

    def list_upcoming_events(self, max_results: int = 10):
        # Get upcoming calendar events
```

### Phase 3: Backend API Endpoints

Add to `backend/main.py`:

```python
@app.post("/calendar/reminder")
# Create a calendar reminder
# Input: { title, description, datetime }
# Returns: { event_id, link }

@app.get("/calendar/events")
# Get upcoming events
# Returns: List of events

@app.get("/calendar/status")
# Check if Calendar is connected
# Returns: { connected: bool, needs_reauth: bool }
```

### Phase 4: Frontend Changes

#### 4.1 Update OAuth Initialization

**Option A: Server-Redirect (Recommended)**

- Remove `<GoogleLogin>` component
- Add button that redirects to backend `/auth/google/authorize`
- Backend handles full OAuth flow
- Callback returns to frontend with JWT

**Option B: Keep React OAuth**

- Configure `@react-oauth/google` for authorization code flow
- Request additional scopes
- Send authorization code to backend (not ID token)

#### 4.2 Calendar UI Components

**Create new components:**

- `frontend/src/components/calendar/ReminderDialog.jsx` - Modal to create reminders
- `frontend/src/components/calendar/CalendarButton.jsx` - Trigger button in chat
- `frontend/src/pages/CalendarPage.jsx` - View upcoming events (optional)

**Integration points:**

- Add "Create Reminder" button in chat interface
- Parse dates/times from AI responses
- Show confirmation after reminder created

---

## Implementation Sequence

### Step 1: Backend OAuth Flow (3-4 hours)

1. Install dependencies
2. Create OAuth authorize/callback endpoints
3. Add token encryption utilities
4. Update User model with token fields
5. Migrate database

### Step 2: Google Calendar Service (2-3 hours)

1. Create `calendar_service.py`
2. Implement token refresh logic
3. Add Calendar API methods (create event, list events)
4. Error handling for revoked tokens

### Step 3: Backend API Endpoints (1-2 hours)

1. Add `/calendar/reminder` endpoint
2. Add `/calendar/events` endpoint
3. Add `/calendar/status` endpoint
4. Test with curl/Postman

### Step 4: Frontend OAuth Update (2-3 hours)

1. Update LoginPage for new OAuth flow
2. Handle OAuth callback
3. Update AuthContext to track Calendar connection status

### Step 5: Frontend Calendar UI (3-4 hours)

1. Create ReminderDialog component
2. Add calendar button to chat interface
3. Integrate with ChatPage
4. Show success/error messages

---

## Key Design Decisions Needed

### 1. **OAuth Flow Approach**

- **Option A:** Full server-side (backend redirects)
  - Pros: More secure, full control, easier token management
  - Cons: Requires page redirect, more complex
- **Option B:** Hybrid (React OAuth + backend token storage)
  - Pros: Better UX, no page redirect
  - Cons: More complex frontend, security considerations

### 2. **Calendar Reminder Trigger**

- **Option A:** Manual button - User clicks "Create Reminder" button
- **Option B:** AI-suggested - AI detects dates/times and suggests reminders
- **Option C:** Automatic - AI automatically creates reminders for detected dates

### 3. **Token Storage Security**

- Encrypt tokens in database using `cryptography.fernet`
- Store encryption key in environment variable
- Rotate keys periodically

### 4. **Scope Permissions**

- Start with `calendar.events` (read/write events only)
- Can upgrade to full `calendar` scope later if needed

---

## Files to Create/Modify

| File                                                  | Action                                 |
| ----------------------------------------------------- | -------------------------------------- |
| `backend/auth.py`                                     | Add OAuth authorize/callback endpoints |
| `backend/models.py`                                   | Add token fields to User model         |
| `backend/calendar_service.py`                         | New file - Google Calendar API wrapper |
| `backend/main.py`                                     | Add calendar endpoints                 |
| `backend/requirements.txt`                            | Add Google API dependencies            |
| `backend/.env.example`                                | Add calendar-related env vars          |
| `frontend/src/pages/LoginPage.jsx`                    | Update OAuth flow                      |
| `frontend/src/components/calendar/ReminderDialog.jsx` | New file                               |
| `frontend/src/pages/ChatPage.jsx`                     | Integrate calendar button              |

---

## Testing Plan

1. **OAuth Flow:** Verify consent screen shows calendar scope
2. **Token Storage:** Confirm tokens encrypted in database
3. **Token Refresh:** Test with expired tokens
4. **Calendar API:** Create test reminder, verify in Google Calendar
5. **Error Handling:** Test with revoked tokens, API errors
6. **UI:** Test reminder creation from chat interface

---

## Security Considerations

1. **Token Encryption:** Use Fernet symmetric encryption
2. **Token Expiry:** Check expiry before each API call
3. **Scope Minimization:** Only request needed calendar scopes
4. **Error Messages:** Don't leak token details in errors
5. **Rate Limiting:** Respect Google Calendar API quotas
6. **Token Revocation:** Handle when user revokes access

---

## User Decisions

1. **OAuth flow:** Server-redirect (backend handles full OAuth)
2. **Reminder trigger:** AI-suggested (AI detects dates/times and suggests creating reminders)
3. **Initial scope:** Calendar events only (`calendar.events` scope)

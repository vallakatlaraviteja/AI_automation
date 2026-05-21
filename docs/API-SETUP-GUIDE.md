# API Setup Guide — How to Get Every Credential

## Purpose of 4 Emails

We use 4 different email accounts to create multiple accounts on each service. This escapes free-tier subscription limits — giving us 4x capacity on every service for $0.

**Example emails you might use:**
- email1@gmail.com
- email2@gmail.com
- email3@gmail.com
- email4@gmail.com

---

## 1. GROQ API Keys (AI — Primary)

**What it does:** Fastest AI for scoring jobs + generating emails
**Free limit:** 14,400 requests/day per key
**With 4 keys:** 57,600/day

### How to get:

```
1. Go to: https://console.groq.com
2. Click "Sign Up" (use email1@gmail.com)
3. Verify your email
4. After login → left sidebar → click "API Keys"
5. Click "Create API Key"
6. Give it a name (e.g., "job-automation")
7. Copy the key (starts with: gsk_...)
8. Save it somewhere safe

Repeat with email2, email3, email4 → you get 4 keys
```

### Where it goes in the workflow:
```javascript
groqKeys: [
  "gsk_KEY_FROM_EMAIL1",
  "gsk_KEY_FROM_EMAIL2",
  "gsk_KEY_FROM_EMAIL3",
  "gsk_KEY_FROM_EMAIL4"
]
```

---

## 2. NVIDIA NIM API Keys (AI — Second)

**What it does:** Free AI models (80+), same format as Groq
**Free limit:** ~40 requests/minute per key (~14,400/day)
**With 4 keys:** ~57,600/day
**Model we use:** meta/llama-3.3-70b-instruct

### How to get:

```
1. Go to: https://developer.nvidia.com
2. Click "Join" → create NVIDIA Developer account (use email1@gmail.com)
3. Verify email
4. Go to: https://build.nvidia.com
5. Sign in with your NVIDIA account
6. Search for: "llama-3.3-70b-instruct" (by Meta)
7. Click on the model
8. Click "Get API Key" (or "Build with this NIM")
9. Copy the key (starts with: nvapi-...)

Repeat with email2, email3, email4 → you get 4 keys
```

### Where it goes in the workflow:
```javascript
nvidiaKeys: [
  "nvapi-KEY_FROM_EMAIL1",
  "nvapi-KEY_FROM_EMAIL2",
  "nvapi-KEY_FROM_EMAIL3",
  "nvapi-KEY_FROM_EMAIL4"
]
```

---

## 3. GEMINI / Google AI Studio Keys (AI — Backup)

**What it does:** Quality AI backup (Google's model)
**Free limit:** 1,000 requests/day per key
**With 4 keys:** 4,000/day
**Model:** gemini-1.5-flash

### How to get:

```
1. Go to: https://aistudio.google.com
2. Sign in with Google account (use email1@gmail.com)
3. Click "Get API Key" (left sidebar or top area)
4. Click "Create API Key in new project" (or select existing project)
5. Copy the key (starts with: AIza...)

Repeat with email2, email3, email4 → you get 4 keys
```

### Where it goes in the workflow:
```javascript
geminiKeys: [
  "AIza_KEY_FROM_EMAIL1",
  "AIza_KEY_FROM_EMAIL2",
  "AIza_KEY_FROM_EMAIL3",
  "AIza_KEY_FROM_EMAIL4"
]
```

---

## 4. RapidAPI Keys (for JSearch — LinkedIn+Indeed aggregator)

**What it does:** Searches jobs from LinkedIn, Indeed, Google Jobs — all in one API
**Free limit:** 500 requests/month per account
**With 4 keys:** 2,000/month

### How to get:

```
1. Go to: https://rapidapi.com
2. Click "Sign Up" (use email1@gmail.com)
3. Verify email
4. Go to: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
5. Click "Subscribe to Test" → select FREE plan (Basic)
6. Accept terms
7. Your key is shown in the code examples on the page
   OR: go to top-right avatar → "My Apps" → "default-application" → "Security" → copy key

Repeat with email2, email3, email4 → you get 4 keys
```

### Where it goes in the workflow:
```javascript
rapidApiKeys: [
  "RAPIDAPI_KEY_FROM_EMAIL1",
  "RAPIDAPI_KEY_FROM_EMAIL2",
  "RAPIDAPI_KEY_FROM_EMAIL3",
  "RAPIDAPI_KEY_FROM_EMAIL4"
]
```

---

## 5. Findwork API Keys (tech startup jobs)

**What it does:** Finds tech/startup jobs
**Free limit:** 50 requests/month per account
**With 4 keys:** 200/month

### How to get:

```
1. Go to: https://findwork.dev
2. Click "Sign Up" or "Register"
3. Create account (use email1@gmail.com)
4. Verify email
5. Go to: https://findwork.dev/developers/ (or REST API in top menu)
6. Your API key is shown on the page (dots = hidden, click eye icon to show)
7. Click copy icon to copy the key

Repeat with email2, email3, email4 → you get 4 keys
```

### Where it goes in the workflow:
```javascript
findworkKeys: [
  "FINDWORK_KEY_FROM_EMAIL1",
  "FINDWORK_KEY_FROM_EMAIL2",
  "FINDWORK_KEY_FROM_EMAIL3",
  "FINDWORK_KEY_FROM_EMAIL4"
]
```

---

## 6. Gmail OAuth (for sending application emails)

**What it does:** Lets the workflow send emails from user's Gmail
**This is for TESTING only** — in production, users connect via frontend

### How to set up in n8n:

```
Step A: Create Google Cloud Project

1. Go to: https://console.cloud.google.com
2. Click "Select a project" (top bar) → "New Project"
3. Name it (e.g., "Job Automation")
4. Click "Create"

Step B: Enable Gmail API

1. In Google Cloud Console → left menu → "APIs & Services" → "Library"
2. Search: "Gmail API"
3. Click "Gmail API" → click "Enable"

Step C: Create OAuth Credentials

1. Go to: "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. If asked for consent screen:
   - User Type: External
   - App name: "Job Automation"
   - User support email: your email
   - Developer email: your email
   - Save and Continue (skip scopes, skip test users)
   - Back to Dashboard
4. Now create OAuth Client:
   - Application type: "Web application"
   - Name: "n8n OAuth"
   - Authorized redirect URIs: 
     YOUR_N8N_URL/rest/oauth2-credential/callback
     (e.g., http://localhost:5678/rest/oauth2-credential/callback)
   - Click "Create"
5. Copy: Client ID + Client Secret

Step D: Add to n8n

1. In n8n: go to Credentials → Add New
2. Search: "Gmail OAuth2 API"
3. Paste: Client ID + Client Secret
4. Click "Sign in with Google" → authorize your Gmail account
5. Done! Select this credential on all Gmail nodes.
```

### Which nodes need Gmail credentials:

**User's Gmail (for sending applications to recruiters):**
- "Send Application Email"
- "Send Follow-up Email"
- "Send Speculative Email"

**Bot Gmail (for sending notifications to user — "AI Jobs Assistant"):**
- "Send Job Digest Email"
- "Send Outreach Summary Email"
- "Limit Notification Email"
- "Send Follow-up Summary Email"

For testing: use ONE Gmail credential on ALL 7 nodes. Separate later.

---

## 7. Supabase (Database — for later)

**Not needed for testing.** Will be added when we build the frontend/backend.

---

## Summary — What you need minimum for testing:

| Service | Minimum keys | How long to get |
|---------|-------------|-----------------|
| Groq | 1 key | 2 minutes |
| NVIDIA | 1 key | 3 minutes |
| Gemini | 1 key | 2 minutes |
| RapidAPI | 1 key | 3 minutes |
| Findwork | 1 key | 2 minutes |
| Gmail OAuth | 1 credential | 10 minutes |

**Total setup time: ~20 minutes**

For production (4x capacity): create 4 accounts on each = ~1 hour total.

---

## Where to put all keys:

In n8n, double-click the **"Backend Config"** node and replace placeholders:

```javascript
const config = {
  groqKeys: ["gsk_YOUR_KEY_1", "gsk_YOUR_KEY_2", "gsk_YOUR_KEY_3", "gsk_YOUR_KEY_4"],
  nvidiaKeys: ["nvapi-YOUR_KEY_1", "nvapi-YOUR_KEY_2", "nvapi-YOUR_KEY_3", "nvapi-YOUR_KEY_4"],
  nvidiaDailyLimit: 14400,
  geminiKeys: ["AIza_YOUR_KEY_1", "AIza_YOUR_KEY_2", "AIza_YOUR_KEY_3", "AIza_YOUR_KEY_4"],
  rapidApiKeys: ["YOUR_RAPID_1", "YOUR_RAPID_2", "YOUR_RAPID_3", "YOUR_RAPID_4"],
  findworkKeys: ["YOUR_FINDWORK_1", "YOUR_FINDWORK_2", "YOUR_FINDWORK_3", "YOUR_FINDWORK_4"],
  groqDailyLimit: 14400,
  geminiDailyLimit: 1000,
  rapidApiMonthlyLimit: 500,
  findworkMonthlyLimit: 50,
  userEmailDailyLimit: 50,
  scoreThreshold: 60,
  freshnessMaxDays: 14
};
return [{ json: config }];
```

---

## After all keys are set:

1. Click "Trigger: 8AM Job Discovery" → Execute manually
2. Watch data flow through nodes
3. Check if jobs are found and scored
4. If errors → screenshot and we'll fix

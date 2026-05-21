# MASTER PLAN — AI Job Automation SaaS

## What This Is

An automated job hunting service. Users give email + resume → system finds relevant jobs, scores them with AI, sends impressive application emails. $0 cost.

---

## The Box Model

```
INPUT (user provides — 30 seconds):
  • 1 Gmail account (OAuth click "Allow")
  • 1 Resume (PDF or Drive link)
  • Preferences: role, skills, location

THE BOX (your backend — user never sees):
  • AI: Groq ×4 + NVIDIA NIM ×4 + Gemini ×4 (forward-only rotation)
  • Job APIs: 8 verified sources (5 unlimited + 3 with 4-email trick)
  • Database: Supabase ×4 (persistent, multi-user)
  • Hosting: Koyeb (always-on, free)
  • Notifications: Bot Gmail ("AI Jobs Assistant" — your name hidden)

OUTPUT (user gets — daily, automatically):
  • All jobs shown in tiers (strong/good/partial/stretch)
  • Application emails sent from THEIR Gmail (impressive, specific)
  • Skills gap analysis (what to learn)
  • Speculative outreach to companies without exact match
  • Auto follow-up day 3-5 (one-time, not desperate)
```

---

## The 4-Email Trick (Core Strategy)

Every free-tier service has limits. We create 4 accounts and rotate forward-only:

| Service | 1 account | 4 accounts | Purpose |
|---------|-----------|------------|---------|
| Groq AI | 14,400/day | 57,600/day | Job scoring + email gen (PRIMARY) |
| NVIDIA NIM | ~14,400/day | ~57,600/day | Same as Groq (SECOND) |
| Gemini/Google AI Studio | 1,000/day | 4,000/day | Quality backup (THIRD) |
| RapidAPI/JSearch | 500/month | 2,000/month | LinkedIn+Indeed aggregator |
| Findwork.dev | 50/month | 200/month | Tech startup jobs |
| Supabase | 500MB | 2GB | Database |

**Rule:** key1 → key2 → key3 → key4 → STOP. Never backward. Reset at midnight.

**Total AI capacity:** ~119,200 calls/day = ~850 users FREE

---

## AI Rotation Chain

```
Groq key1 → key2 → key3 → key4 (57,600/day, fastest — 300 tok/s)
  ↓ all exhausted
NVIDIA NIM key1 → key2 → key3 → key4 (~57,600/day, OpenAI-compatible)
  ↓ all exhausted
Gemini key1 → key2 → key3 → key4 (4,000/day, quality backup)
  ↓ all exhausted
FALLBACK: keyword-based scoring (no AI needed, still works)
```

### NVIDIA NIM Details:
- URL: https://integrate.api.nvidia.com/v1/chat/completions
- Format: OpenAI-compatible (same as Groq!)
- Model: meta/llama-3.1-70b-instruct
- Rate limit: ~40 RPM per account
- Sign up: developer.nvidia.com → build.nvidia.com
- 4-email trick: 4 accounts = 4 API keys

### Groq Details:
- URL: https://api.groq.com/openai/v1/chat/completions
- Model: llama-3.1-70b-versatile
- Rate limit: 14,400/day per key
- Sign up: console.groq.com

### Gemini Details:
- URL: https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
- Sign up: aistudio.google.com
- Rate limit: 1,000/day per key

---

## Job Discovery (8 Verified APIs)

### FREE (no key, unlimited):

| # | API | Endpoint | What it finds | Keyword search? |
|---|-----|----------|---------------|-----------------|
| 1 | Remotive | remotive.com/api/remote-jobs?search={keywords} | Remote tech jobs | ✅ Yes |
| 2 | Arbeitnow | arbeitnow.com/api/job-board-api?search={keywords} | EU/remote, from ATS | ✅ Yes |
| 3 | Himalayas | himalayas.app/jobs/api?q={keywords} | High-quality remote + salary | ✅ Yes |
| 4 | RemoteJobs.org | remotejobs.org/api/jobs?limit=20 | General remote | ❌ (AI filters) |
| 5 | Jobicy | jobicy.com/api/v2/remote-jobs?count=20 | Remote tech | ❌ (AI filters) |

### 4-EMAIL TRICK (key rotation):

| # | API | Endpoint | What it finds | Free limit | ×4 |
|---|-----|----------|---------------|-----------|-----|
| 6 | JSearch (RapidAPI) | jsearch.p.rapidapi.com/search | LinkedIn+Indeed+Google Jobs | 500/month | 2,000/month |
| 7 | Findwork.dev | findwork.dev/api/jobs/?search={keywords} | Tech startups | 50/month | 200/month |
| 8 | The Muse | themuse.com/api/public/jobs | Enterprise companies | Unlimited | Same |

### PHASE 3 (add after deployment):

| # | API | What | Notes |
|---|-----|------|-------|
| 9 | JobSpy (self-hosted) | LinkedIn+Indeed+Glassdoor+ZipRecruiter | Python scraper, run on server |
| 10 | Apify LinkedIn | LinkedIn jobs without login | 48 runs/month free (×4 = 192) |

### DEAD APIs (DO NOT USE):
- ❌ GitHub Jobs — shut down April 2021
- ❌ USAJobs — US-citizenship required
- ❌ Adzuna — requires approval
- ❌ RemoteOK — now requires paid key

---

## Daily Flow (Per User)

### 8:00 AM — Job Discovery

```
1. Parse resume → extract skills, projects, experience
2. Use keywords to search 8 APIs (not random!)
3. Auto-extract emails from descriptions (careers@, hr@, hiring@)
4. Deduplicate (same job from multiple APIs)
5. Freshness filter: skip >14 days, prioritize <48hr
6. AI Score 0-100 (using resume data vs job description)
7. Categorize into tiers (nothing hidden):
   ⭐ 80-100: STRONG → email sent
   ✅ 60-79:  GOOD → email sent
   📋 40-59:  PARTIAL → shown (tailor resume?)
   📚 20-39:  STRETCH → shown (learning)
8. Skills Gap Analysis: what companies want that user doesn't have
9. Store for outreach + send digest email to user
```

### 9:00 AM — Email Outreach

```
FOR SCORE ≥60 (has recruiter email):
  AI generates IMPRESSIVE direct application email:
  - Eye-catching subject (NOT "Application for [Role]")
  - References specific JD requirement + specific resume project
  - Professional but has personality
  - Resume context included
  - Sent FROM user's Gmail (their identity)
  - CC to user (they see what was sent)
  - 50/day limit → STOP

FOR SCORE 30-59 (speculative outreach):
  AI generates impressive open application:
  - Shows what user BRINGS (value-first)
  - Specific to that COMPANY
  - "Here's what I do well, consider me for current/future roles"
  - Max 5 speculative/day
  - One-time per company (never repeated)
```

### 10:00 AM — Follow-up (day 3-5)

```
  Jobs emailed 3-5 days ago, no reply:
  - SHORT follow-up (50-80 words max)
  - NOT desperate. Confident check-in.
  - ONE time only per job. NEVER again.
  - Max 5 follow-ups/day
```

### Midnight — Daily Reset

```
  Reset: Groq/NVIDIA/Gemini counters
  Reset: email counter (50/day)
  Clean: old jobs (>14 days)
  Monthly: reset RapidAPI/Findwork counters (1st of month)
```

---

## Email Quality Rules

ALL emails must be:
- ❌ NOT: "Dear Hiring Manager, I am writing to express my interest..."
- ❌ NOT: "I hope this email finds you well..."
- ❌ NOT: Generic subjects like "Application for [Role]"
- ✅ YES: Eye-catching subject referencing specific skill/achievement
- ✅ YES: Opens with something about THEIR company/role
- ✅ YES: References user's actual project that proves competence
- ✅ YES: Confident, personality-driven, makes recruiter think "this person gets it"
- ✅ YES: Every word earns its place (150-200 words max)

---

## Notifications (Bot Email, NOT your name)

All notifications sent from "AI Jobs Assistant" (one of your 4 Gmail accounts):
- Daily Job Digest (shows ALL tiers + skills gap + portal links)
- Outreach Summary ("applied to X jobs")
- Follow-up Summary ("checked in on X applications")
- Limit Notification ("50/day reached, continues tomorrow")

**Your personal name NEVER appears to users.**

---

## Multi-User Safety

- Each user gets their own n8n workflow with own staticData
- Shared backend (Groq/NVIDIA/Gemini/RapidAPI/Findwork) serves ALL users via rotation
- User's Gmail is isolated (their own OAuth token, their own 50/day limit)
- No conflicts between users. Period.

---

## Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| AI (primary) | Groq (4 keys) | Fastest (300 tok/s), highest free limit |
| AI (second) | NVIDIA NIM (4 keys) | Same format, 80+ models, free |
| AI (backup) | Gemini (4 keys) | Quality backup |
| Database | Supabase (4 accounts) | Auth + DB + storage, persistent |
| Hosting | Koyeb | Always-on free (no sleeping) |
| Workflow | n8n (self-hosted) | Visual automation, Code nodes |
| Jobs | 8 APIs (5 free + 3 rotated) | Maximum coverage |
| Notifications | Bot Gmail | Free, no Telegram dependency |
| User outreach | User's own Gmail | Their identity, 50/day |

---

## Capacity (All Free)

| Service | Total capacity | Per-user usage | Max users |
|---------|---------------|---------------|-----------|
| Groq (4 keys) | 57,600/day | ~80 calls | ~700 |
| NVIDIA (4 keys) | ~57,600/day | ~80 calls | ~700 |
| Gemini (4 keys) | 4,000/day | ~10 calls | ~400 |
| **AI Total** | **~119,200/day** | **~140/user** | **~850** |
| RapidAPI (4 keys) | 2,000/month | ~30/month | ~65 |
| Supabase (4 accounts) | 2GB | ~10MB/month | ~200 |
| Koyeb hosting | 512MB RAM | ~10MB/user | ~50 |

**Bottleneck:** Koyeb at ~50 users. First upgrade: Koyeb paid ($7/mo).

---

## Build Phases

### Phase 1 ✅ DONE (workflow engine)
- 55 nodes, 0 errors, fully wired
- 8 job APIs (verified alive)
- AI rotation (Groq + Gemini, forward-only)
- Tiered categorization (all jobs shown)
- Skills Gap Analysis
- Direct application emails (impressive, specific)
- Speculative outreach (partial matches)
- Auto follow-up (day 3-5, one-time)
- Bot email notifications
- Daily reset
- Resume drives everything
- Email extraction from descriptions
- Freshness filter (<48hr priority)

### Phase 1.5 ⬜ NEXT
- Add NVIDIA NIM to rotation (Groq → NVIDIA → Gemini)
- Add Supabase for persistence (replace staticData)

### Phase 2 ⬜
- Frontend (user input form)
- Backend (multi-user management)
- Deploy to Koyeb

### Phase 3 ⬜
- Add JobSpy (LinkedIn+Indeed+Glassdoor scraper)
- Add Apify LinkedIn scraper
- Paid tier ($9-19/month)
- Application tracking dashboard
- Resume optimization AI
- Interview prep AI

---

## Revenue Model

### Free Tier (launch):
- 50 emails/day (user's Gmail limit)
- 8 job sources
- AI scoring + impressive emails
- Skills gap analysis
- Speculative outreach

### Paid Tier ($9-19/month, when income starts):
- Priority job delivery (<1 hour of posting)
- More follow-ups
- Advanced analytics
- Resume optimization
- Cover letter generation
- LinkedIn message drafts

---

## What Makes This NOT Collapse

| Risk | Prevention |
|------|-----------|
| API dies | Health check: auto-skip + alert. Other APIs still work. |
| AI key exhausted | Forward-only: Groq → NVIDIA → Gemini → fallback scoring. |
| User Gmail hits 50/day | STOP. No overflow. Tomorrow continues. |
| Multiple users overwhelm | Rotation spreads load. ~850 users capacity. |
| Expired job postings | Freshness filter: skip >14 days. |
| Server restarts | Supabase (persistent). Koyeb (always-on). |
| Bad emails (bounces) | Track in DB. Skip next time. |
| n8n crashes | Auto-restart on Koyeb. |

---

## Accounts to Create (One-Time Setup)

| # | Service | Sign up at | How many | Purpose |
|---|---------|-----------|----------|---------|
| 1-4 | Groq | console.groq.com | 4 accounts | AI scoring + email gen |
| 5-8 | NVIDIA | developer.nvidia.com → build.nvidia.com | 4 accounts | AI backup |
| 9-12 | Google AI Studio | aistudio.google.com | 4 accounts | AI quality backup |
| 13-16 | RapidAPI | rapidapi.com (subscribe JSearch) | 4 accounts | Job aggregator |
| 17-20 | Findwork | findwork.dev | 4 accounts | Tech startup jobs |
| 21-24 | Supabase | supabase.com | 4 accounts | Database |
| 25 | Koyeb | koyeb.com | 1 account | Hosting |
| 26 | Gmail (bot) | gmail.com | 1 account | "AI Jobs Assistant" notifications |

**Total: 26 accounts. All free. One-time setup.**

---

## File Structure

```
AI_automation/
├── workflow/
│   └── job-automation.json     ← THE ENGINE (55 nodes, imports into n8n)
├── web/
│   ├── index.html              ← FRONTEND (user sign-up form)
│   └── api/
│       └── server.js           ← BACKEND (multi-user, Supabase)
├── deploy/
│   ├── Dockerfile              ← For Koyeb
│   └── koyeb.yaml              ← Koyeb config
├── docs/
│   └── MASTER-PLAN.md          ← THIS FILE
├── verify.py                   ← Workflow verification script
└── README.md                   ← Quick overview
```

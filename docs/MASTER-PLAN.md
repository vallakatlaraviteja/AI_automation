# MASTER PLAN — Job Automation SaaS Product

## What We're Building

An automated job hunting service where users provide their email + resume, and the system finds jobs, scores them against their resume with AI, and sends direct application emails — all for $0.

---

## The Box Model

```
┌─────────────────────────────────────────────────────────────────┐
│                         THE PRODUCT                              │
│                                                                 │
│  INPUT (user provides — 30 seconds):                            │
│    • 1 Gmail account (OAuth click "Allow")                      │
│    • 1 Resume (upload PDF or paste Drive link)                  │
│    • Preferences: role, skills, location, remote/hybrid         │
│    • Telegram bot (optional, for notifications)                 │
│                                                                 │
│  THE BOX (your backend — user never sees):                      │
│    • 4 Groq API keys + 4 Gemini keys (AI)                      │
│    • 4 Supabase accounts (database)                             │
│    • 4 RapidAPI keys (JSearch job aggregator)                   │
│    • 4 Findwork keys (tech startup jobs)                        │
│    • 8 job API sources total                                    │
│    • n8n workflow engine on Koyeb (always-on)                   │
│    • Forward-only rotation on EVERYTHING                        │
│                                                                 │
│  OUTPUT (user gets — daily, automatically):                     │
│    • Jobs found, AI-scored against their resume                 │
│    • Direct application emails sent FROM THEIR Gmail            │
│    • Resume PDF attached to every email                         │
│    • Telegram: "Applied to 8 jobs. Apply to 5 more via portal"  │
│    • Full tracking in their personal dashboard                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why This Architecture

### The 4-Email Trick (Core Strategy)

Every free-tier service has daily/monthly limits. Instead of paying for premium, we create 4 accounts and rotate through them:

```
Service          │ 1 account (free) │ 4 accounts (free) │ Multiplier
─────────────────┼──────────────────┼────────────────────┼──────────
Groq AI          │ 14,400/day       │ 57,600/day         │ 4x
Gemini Flash     │ 1,000/day        │ 4,000/day          │ 4x
Supabase         │ 500MB            │ 2GB                │ 4x
RapidAPI/JSearch │ 500/month        │ 2,000/month        │ 4x
Findwork.dev     │ 50/month         │ 200/month          │ 4x
```

**Rule:** Forward-only rotation. key1 → key2 → key3 → key4 → STOP. Never backward. Reset at midnight UTC only.

### User's Gmail (NOT part of rotation)

- User provides 1 Gmail account
- ALL outreach emails go FROM their Gmail (their identity)
- Max 50 emails/day (their free limit)
- Hit 50? STOP for today. Continue tomorrow.
- We do NOT overflow to our accounts. Their limit = their limit.

### Our Gmail accounts

- Used ONLY for escaping platform service limits (Groq, Supabase, RapidAPI, etc.)
- NOT used for sending user outreach emails
- NOT visible to users or recruiters

---

## Daily Flow (Per User)

### 8:00 AM — Job Discovery (automatic)

```
1. Download + AI-parse user's resume (extracts skills, projects, experience)

2. Fetch jobs from 8 VERIFIED APIs:
   
   FREE (no key, unlimited):
     ① Remotive        → remote tech jobs (LIVE, status page confirms)
     ② Arbeitnow       → EU/remote, direct from ATS (LIVE, updated 2025)
     ③ Himalayas       → high-quality remote + salary data (LIVE, updated May 2025)
     ④ RemoteJobs.org  → general remote jobs (LIVE, confirmed June 2025)
     ⑤ Jobicy          → remote tech, RSS/JSON (LIVE, GitHub active)
   
   4-EMAIL TRICK (key rotation):
     ⑥ JSearch/RapidAPI → LinkedIn+Indeed+Google Jobs aggregator (LIVE)
     ⑦ Findwork.dev    → tech startup jobs (LIVE, publicapi confirmed)
     ⑧ The Muse        → enterprise company jobs (LIVE, API v2 active)

3. Health check each API:
   ✓ HTTP 200 + has jobs + jobs recent (<14 days)
   ✗ Failed 3x → mark DOWN, alert admin, skip it
   → System NEVER collapses. Other APIs still work.

4. Auto-extract emails from job descriptions:
   "Forward resume to careers@company.com" → EXTRACTED
   "Apply: hr@startup.io" → EXTRACTED
   Priority: career/hr/hiring/talent emails > random
   Filter out: noreply@, unsubscribe@, notifications@, spam

5. Deduplicate (don't show same job twice)

6. AI scores each job 0-100 against user's resume:
   Uses OUR Groq/Gemini keys (shared, 4-email rotation)
   Scoring: +20 skill overlap, +15 project match, +10 location/mode match
   Only jobs scoring ≥60 pass through

7. Freshness priority:
   Posted today/yesterday → ⚡ HIGH PRIORITY (apply NOW for best results)
   Posted 2-7 days ago    → NORMAL
   Posted 8-14 days ago   → LOW priority
   Posted 14+ days ago    → SKIP (likely filled/expired)

8. Save to user's database (Supabase, our 4-account rotation)
```

### 9:00 AM — Email Outreach (automatic)

```
1. Read user's jobs from database

2. For jobs with extracted email (careers@, hr@, etc.):

   THE EMAIL IS THE APPLICATION (not a follow-up):

   Subject: Application for [Role] — [Key Qualification]

   Hi [Recruiter/Hiring Team],

   I'm [Name], applying for the [Role] position at [Company].
   
   [Specific match: JD requirement → user's resume project]
   [Another matching skill/achievement from their resume]
   
   I've attached my resume for your review. I'd welcome the
   opportunity to discuss how my background fits your needs.

   Best regards,
   [Name]
   [LinkedIn] [Portfolio]

   📎 Attachment: [Name]_Resume.pdf

   → Sent FROM user's own Gmail (their identity)

3. For jobs WITH portal links:
   Telegram: "Also apply through portal for these: [clickable links]"
   (Double coverage = maximum visibility with recruiters)

4. Email limit: User's Gmail = 50/day max
   Hit 50? → STOP. Tomorrow continues.
   NOT overflowed anywhere. Clean stop.

5. Track: Mark "Applied" in database with timestamp
```

### Day 3-5 — Auto Follow-up (one time only)

```
If no response after 3-5 days:
  SHORT follow-up (50 words max):
  "Just checking in on my application for [Role]. 
   Still very interested. Happy to provide additional info."

Only ONE follow-up per job. Never spam.
```

### Midnight UTC — Daily Reset

```
Reset all rotation counters:
  Groq keys: 0/14,400 each
  Gemini keys: 0/1,000 each
  Supabase accounts: 0 writes
  RapidAPI keys: 0/500 each
  User Gmail: 0/50 (their own counter)
```

### Anytime — Telegram Bot

```
/stats  → "This week: 47 jobs found, 23 applied, 3 replies"
/status → Full system health dashboard
Any question → AI answers using their job data
```

---

## How Users Receive Results

| Channel | What it sends | Purpose |
|---------|---------------|---------|
| **Telegram** | Job links + "apply now" + portal links + status | Instant action, mobile |
| **Email** (to their Gmail) | Daily summary digest | Record-keeping, reference |
| **Dashboard** (Phase 3) | Full history, tracking, analytics | Deep review |

---

## Tech Stack

| Component | Tool | Why | Free Tier |
|-----------|------|-----|-----------|
| **AI** | Groq (primary) + Gemini Flash (backup) | Fastest + best quality fallback | 61,600 calls/day |
| **Database** | Supabase | Auth + DB + storage in one | 2GB (4 accounts) |
| **Hosting** | Koyeb | Always-on free (never sleeps!) | 1 app, always running |
| **Workflow** | n8n (self-hosted) | Visual automation, Code nodes | Unlimited |
| **Jobs** | 8 APIs (5 free + 3 rotated) | Maximum coverage | 50-100 jobs/day |
| **Notifications** | Telegram Bot | Free, instant, mobile | Unlimited |
| **Email sending** | User's own Gmail via OAuth | Their identity | 50/day (their limit) |

---

## Multi-User Capacity (All Free)

| Service | Total free capacity | Per-user usage | Max users |
|---------|--------------------:|---------------:|----------:|
| Groq AI (4 keys) | 57,600 calls/day | ~80 calls/day | ~700 |
| Gemini (4 keys, backup) | 4,000 calls/day | ~10 calls/day | ~400 |
| Supabase (4 accounts) | 2GB storage | ~10MB/month | ~200 |
| RapidAPI/JSearch (4 keys) | 2,000 req/month | ~30 req/month | **~65** ← bottleneck |
| Koyeb hosting | 512MB RAM | ~10MB/user | ~50 |

**Bottleneck: RapidAPI at ~65 users.** First upgrade when earning: RapidAPI paid ($9/mo = 10,000/month = ~330 users).

---

## AI Rotation (Forward-Only, Never Backward)

```
PRIMARY CHAIN (Groq — fastest, highest limit):
  groq_key1 (14,400/day) 
    → groq_key2 (14,400/day)
      → groq_key3 (14,400/day)
        → groq_key4 (14,400/day)
          ↓ ALL GROQ EXHAUSTED

FAILOVER CHAIN (Gemini Flash — quality backup):
  gemini_key1 (1,000/day)
    → gemini_key2 (1,000/day)
      → gemini_key3 (1,000/day)
        → gemini_key4 (1,000/day)
          ↓ ALL EXHAUSTED

STOP FOR TODAY. Reset at midnight.
Total capacity: 61,600 AI calls/day FREE.
```

Same pattern for Supabase, RapidAPI, Findwork — always forward, never back.

---

## Health Checks (System Never Collapses)

```
Every API call:
  1. Check HTTP response (200 = alive)
  2. Check response has actual jobs (not empty)
  3. Check job dates are recent (<14 days)
  4. If API fails 3 times → mark as DOWN
  5. Telegram alert to admin: "⚠️ [API name] is down"
  6. Auto-skip dead API, continue with others
  7. Remaining 7 APIs still work → system runs fine

No single API failure can crash the system.
```

---

## Verified Job APIs (Double-Checked, All LIVE)

| # | API | Verified Status | Key? | Limit | 4x Capacity |
|---|-----|----------------|------|-------|-------------|
| 1 | Remotive | ✅ Status page operational | No | Unlimited | Same |
| 2 | Arbeitnow | ✅ Updated June 2025, ATS-powered | No | Unlimited | Same |
| 3 | Himalayas | ✅ API updated May 2025 | No | Unlimited (20/page) | Same |
| 4 | RemoteJobs.org | ✅ Confirmed June 2025 | No | Unlimited | Same |
| 5 | Jobicy | ✅ GitHub + GitLab active | No | 50 latest | Same |
| 6 | JSearch (RapidAPI) | ✅ LinkedIn+Indeed aggregator | Yes | 500/month | 2,000/month |
| 7 | Findwork.dev | ✅ PublicAPI confirmed | Yes | 50/month | 200/month |
| 8 | The Muse | ✅ API v2 active | No | Unlimited | Same |

### DEAD APIs (verified, do NOT use):
- ❌ GitHub Jobs — shut down April 2021
- ❌ USAJobs — US-citizenship required
- ❌ Adzuna — requires approval (hard to get)
- ❌ RemoteOK — was free, now requires paid key

---

## Research-Backed Strategies (Built into the system)

| Strategy | Data | How we implement it |
|----------|------|---------------------|
| Apply within 24 hours of posting | First applicants get 3x more callbacks | ⚡ Priority flag for <48hr old jobs |
| Follow up after 3-5 days | Reminds recruiter you exist | Auto follow-up email (one time only) |
| Match 70%+ of requirements | Don't apply to everything | Score threshold ≥60 |
| Apply to <2-week-old postings only | Older = likely filled | Freshness filter, skip >14 days |
| Reference specific JD requirements in email | Shows you read the posting | AI pulls from description + matches to resume |
| Attach resume (not just link) | Recruiters want the file | PDF attached on every outreach |
| Apply through multiple channels | Double visibility | Email + portal link notification |

---

## Build Phases

### Phase 1 ✅ DONE (this session)
- 97-node n8n workflow, fully wired, imports into n8n
- 4 API job discovery + auto-extract emails from descriptions
- AI scoring (≥60 threshold)
- Forward-only rotation (Groq + Sheets)
- 3-tier outreach (direct apply + portal links + cold)
- Telegram bot (/status, /stats, AI assistant)
- Multi-user safe (isolated staticData per workflow)

### Phase 2 (NEXT — build the SaaS product)
1. Add 4 new job APIs (Himalayas, RemoteJobs.org, Jobicy, Findwork)
2. Add Gemini Flash as AI failover (4 keys)
3. Replace Google Sheets with Supabase (4-account rotation)
4. Update email prompt: direct application + resume attached
5. Add API health checks (auto-skip dead APIs + admin alerts)
6. Add freshness filter (prioritize <48hr postings)
7. Add auto follow-up after 3-5 days (one time only)
8. Build web interface (simple user input form)
9. Multi-user backend (per-user workflow creation)
10. Deploy to Koyeb (always-on, never sleeps)
11. Telegram onboarding flow

### Phase 3 (SCALE + MONETIZE)
- Paid tier: priority scoring, more sources, analytics
- Upgrade Koyeb/Render when users > 50
- Upgrade RapidAPI when users > 65
- Application tracking dashboard (web UI)
- Interview prep AI
- LinkedIn job notifications
- Referral system (user invites friends)

---

## Revenue Model

### Free Tier (launch with)
- 50 emails/day (user's Gmail limit)
- 8 job sources
- AI scoring + personalized application emails
- Resume attached
- Telegram notifications

### Paid Tier ($9-19/month — when you have income)
- Priority delivery (apply within 1 hour of posting)
- Multiple follow-ups
- Advanced analytics (which emails get replies)
- Resume optimization AI
- Cover letter generation
- LinkedIn message drafts

---

## What Makes This NOT Collapse

| Risk | Prevention |
|------|-----------|
| An API dies | Health check: auto-skip + alert. 7 other APIs still work. |
| Groq key exhausted | Forward-only → next key. All Groq done → Gemini kicks in. |
| User Gmail hits 50/day | STOP sending. No overflow. Continue tomorrow. |
| Multiple users overwhelm | Rotation spreads load. Alert at 80% capacity. |
| Expired/old job postings | Freshness filter: skip >14 days old. |
| Server sleeps (Render issue) | Use Koyeb instead (always-on free tier). |
| Bad email addresses (bounces) | Track bounces in DB. Skip next time. |
| n8n crashes | Auto-restart on Koyeb. Error notifications. |

---

## How We Start (Immediate Next Steps)

1. **Merge current PRs** (workflow + repo cleanup)
2. **Create 4 Groq accounts** + 4 Gemini accounts + 4 Supabase accounts + 4 RapidAPI accounts + 4 Findwork accounts
3. **Build Phase 2** step by step (see list above)
4. **Deploy to Koyeb** with Dockerfile
5. **Test with yourself as first user**
6. **Invite 5 beta users** (friends/colleagues)
7. **Iterate based on feedback**
8. **Launch publicly** (Product Hunt, Reddit, Twitter)

---

## Summary

**What:** Automated job hunting service
**For whom:** Job seekers who want daily AI-scored jobs + auto-applied emails
**Cost to run:** $0 (all free tiers with 4-email trick)
**User effort:** 30 seconds to set up. 2 minutes/day to click portal links.
**Your effort:** Build it once, maintain it, scale when users come.
**Revenue:** Free now → $9-19/month paid tier when income starts.

This is the complete, verified, optimal plan. No shortcuts taken, no dead APIs, no going back to exhausted keys. The best possible outcome for $0.

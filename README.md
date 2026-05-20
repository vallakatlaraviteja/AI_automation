# AI Job Automation

**Users give email + resume → System finds jobs, scores with AI, sends applications. $0 cost.**

## The One File

```
workflow/job-automation.json → Import into n8n
```

## Architecture

```
INPUT:  User's Gmail + Resume + Preferences (30 sec setup)
BOX:    Your Groq×4 + Gemini×4 + Supabase×4 + 8 Job APIs (invisible)
OUTPUT: Daily scored jobs + auto application emails + Telegram alerts
```

## How It Works

- **8 AM**: Fetch jobs from 8 APIs → AI score against resume → filter ≥60 → notify user
- **9 AM**: Send direct application emails from user's Gmail (resume attached)
- **Midnight**: Reset all rotation counters

## Key Principles

- **4-email trick**: Every service with limits gets 4 accounts (4x free capacity)
- **Forward-only rotation**: key1→2→3→4→STOP. Never backward. Reset at midnight.
- **User's Gmail only**: All outreach from THEIR email. Your keys are backend only.
- **Health checks**: If an API dies, system continues with the others.

## Build Steps

1. ✅ Workflow JSON (job discovery + scoring) — DONE
2. ⬜ Add email outreach (direct application + resume)
3. ⬜ Add remaining APIs (JSearch, Findwork, RemoteJobs.org)
4. ⬜ Add Supabase database
5. ⬜ Frontend (user input form)
6. ⬜ Backend (multi-user management)
7. ⬜ Deploy to Koyeb

## Full Documentation

See: [docs/MASTER-PLAN.md](docs/MASTER-PLAN.md)

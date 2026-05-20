#!/usr/bin/env python3
"""Build the complete n8n job-automation workflow JSON."""
import json
import uuid

def uid():
    return str(uuid.uuid4())

# Pre-generate all node IDs
IDS = {}
node_names = [
    'trigger1_schedule', 'backend_config', 'user_profile', 'ai_key_rotation',
    'download_resume', 'parse_resume_ai',
    'fetch_remotive', 'fetch_arbeitnow', 'fetch_himalayas', 'fetch_remotejobs',
    'fetch_jobicy', 'fetch_jsearch', 'fetch_findwork', 'fetch_themuse',
    'parse_remotive', 'parse_arbeitnow', 'parse_himalayas', 'parse_remotejobs',
    'parse_jobicy', 'parse_jsearch', 'parse_findwork', 'parse_themuse',
    'merge_all_jobs', 'deduplicate_jobs', 'freshness_filter',
    'ai_score_jobs', 'filter_score', 'store_jobs', 'prepare_telegram',
    'send_telegram_digest', 'trigger2_schedule', 'get_jobs_outreach',
    'check_email_limit', 'limit_reached', 'generate_email', 'send_email',
    'track_email', 'outreach_summary', 'send_outreach_telegram',
    'limit_notification', 'trigger3_schedule', 'daily_reset'
]
for n in node_names:
    IDS[n] = uid()

nodes = []


# ============================================================
# TRIGGER 1: Schedule at 8 AM UTC (Job Discovery)
# ============================================================
nodes.append({
    "parameters": {
        "rule": {
            "interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]
        }
    },
    "id": IDS['trigger1_schedule'],
    "name": "Trigger: 8AM Job Discovery",
    "type": "n8n-nodes-base.scheduleTrigger",
    "typeVersion": 1.2,
    "position": [0, 0]
})

# Step 1: Backend Config
backend_config_code = '''
const config = {
  groqKeys: [
    "gsk_GROQ_KEY_1_PLACEHOLDER",
    "gsk_GROQ_KEY_2_PLACEHOLDER",
    "gsk_GROQ_KEY_3_PLACEHOLDER",
    "gsk_GROQ_KEY_4_PLACEHOLDER"
  ],
  geminiKeys: [
    "GEMINI_KEY_1_PLACEHOLDER",
    "GEMINI_KEY_2_PLACEHOLDER",
    "GEMINI_KEY_3_PLACEHOLDER",
    "GEMINI_KEY_4_PLACEHOLDER"
  ],
  rapidApiKeys: [
    "RAPIDAPI_KEY_1_PLACEHOLDER",
    "RAPIDAPI_KEY_2_PLACEHOLDER",
    "RAPIDAPI_KEY_3_PLACEHOLDER",
    "RAPIDAPI_KEY_4_PLACEHOLDER"
  ],
  findworkKeys: [
    "FINDWORK_KEY_1_PLACEHOLDER",
    "FINDWORK_KEY_2_PLACEHOLDER",
    "FINDWORK_KEY_3_PLACEHOLDER",
    "FINDWORK_KEY_4_PLACEHOLDER"
  ],
  groqDailyLimit: 14400,
  geminiDailyLimit: 1000,
  rapidApiMonthlyLimit: 500,
  findworkMonthlyLimit: 50,
  userEmailDailyLimit: 50,
  scoreThreshold: 60,
  freshnessMaxDays: 14
};
return [{ json: config }];
'''


nodes.append({
    "parameters": {
        "jsCode": backend_config_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['backend_config'],
    "name": "Backend Config",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [220, 0]
})

# Step 2: User Profile
user_profile_code = '''
const userProfile = {
  name: "YOUR_NAME",
  email: "your.email@gmail.com",
  skills: ["JavaScript", "TypeScript", "React", "Node.js", "Python", "AWS"],
  keywords: "software engineer remote",
  resumeUrl: "https://drive.google.com/file/d/YOUR_FILE_ID/view",
  telegramChatId: "YOUR_TELEGRAM_CHAT_ID",
  linkedinUrl: "https://linkedin.com/in/yourprofile",
  portfolioUrl: "https://yourportfolio.com",
  currentRole: "Software Engineer",
  experience: "3 years"
};
return [{ json: userProfile }];
'''

nodes.append({
    "parameters": {
        "jsCode": user_profile_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['user_profile'],
    "name": "User Profile",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [440, 200]
})


# Step 3: AI Key Rotation Manager
ai_rotation_code = '''
const staticData = this.getWorkflowStaticData('global');
const config = $input.first().json;

const today = new Date().toISOString().split('T')[0];

// Initialize if new day or first run
if (!staticData.rotationDate || staticData.rotationDate !== today) {
  staticData.rotationDate = today;
  staticData.groqIndex = 0;
  staticData.geminiIndex = 0;
  staticData.groqCounts = [0, 0, 0, 0];
  staticData.geminiCounts = [0, 0, 0, 0];
  staticData.rapidApiIndex = 0;
  staticData.findworkIndex = 0;
  staticData.rapidApiCounts = [0, 0, 0, 0];
  staticData.findworkCounts = [0, 0, 0, 0];
  staticData.aiCallsToday = 0;
}

// Forward-only AI rotation: groq1->2->3->4 then gemini1->2->3->4 then exhausted
let aiKey = null;
let aiProvider = 'exhausted';
let aiUrl = '';
let aiModel = '';

// Try Groq keys first (forward only)
for (let i = staticData.groqIndex; i < 4; i++) {
  if (staticData.groqCounts[i] < config.groqDailyLimit) {
    aiKey = config.groqKeys[i];
    aiProvider = 'groq';
    aiUrl = 'https://api.groq.com/openai/v1/chat/completions';
    aiModel = 'llama-3.1-70b-versatile';
    staticData.groqIndex = i;
    break;
  }
  staticData.groqIndex = i + 1;
}

// If all Groq exhausted, try Gemini (forward only)
if (aiProvider === 'exhausted') {
  for (let i = staticData.geminiIndex; i < 4; i++) {
    if (staticData.geminiCounts[i] < config.geminiDailyLimit) {
      aiKey = config.geminiKeys[i];
      aiProvider = 'gemini';
      aiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';
      aiModel = 'gemini-1.5-flash';
      staticData.geminiIndex = i;
      break;
    }
    staticData.geminiIndex = i + 1;
  }
}

// RapidAPI key rotation (forward only)
let rapidApiKey = null;
for (let i = staticData.rapidApiIndex; i < 4; i++) {
  if (staticData.rapidApiCounts[i] < config.rapidApiMonthlyLimit) {
    rapidApiKey = config.rapidApiKeys[i];
    staticData.rapidApiIndex = i;
    break;
  }
  staticData.rapidApiIndex = i + 1;
}

// Findwork key rotation (forward only)
let findworkKey = null;
for (let i = staticData.findworkIndex; i < 4; i++) {
  if (staticData.findworkCounts[i] < config.findworkMonthlyLimit) {
    findworkKey = config.findworkKeys[i];
    staticData.findworkIndex = i;
    break;
  }
  staticData.findworkIndex = i + 1;
}

return [{ json: {
  aiKey, aiProvider, aiUrl, aiModel,
  rapidApiKey, findworkKey,
  groqIndex: staticData.groqIndex,
  geminiIndex: staticData.geminiIndex,
  rapidApiIndex: staticData.rapidApiIndex,
  findworkIndex: staticData.findworkIndex,
  ...config
}}];
'''

nodes.append({
    "parameters": {
        "jsCode": ai_rotation_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['ai_key_rotation'],
    "name": "AI Key Rotation Manager",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [440, -200]
})


# Step 4: Download Resume
nodes.append({
    "parameters": {
        "url": "={{$('User Profile').item.json.resumeUrl.replace('https://drive.google.com/file/d/', 'https://drive.google.com/uc?export=download&id=').replace('/view', '').replace(/\\/view.*$/, '')}}",
        "options": {
            "response": {"response": {"responseFormat": "file"}}
        }
    },
    "id": IDS['download_resume'],
    "name": "Download Resume",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [660, 200]
})

# Step 5: Parse Resume with AI
parse_resume_code = '''
const staticData = this.getWorkflowStaticData('global');
const rotation = $('AI Key Rotation Manager').first().json;
const resumeText = $input.first().json.data || $input.first().json.body || "Resume content unavailable";

let parsed = { skills: [], experience: [], projects: [], achievements: [] };

if (rotation.aiProvider === 'exhausted') {
  // Fallback: return user profile skills
  const profile = $('User Profile').first().json;
  parsed.skills = profile.skills || [];
  return [{ json: parsed }];
}

const prompt = `Parse this resume and extract structured data. Return ONLY valid JSON with these fields:
- skills: array of technical skills
- experience: array of {role, company, duration, highlights}
- projects: array of {name, description, technologies}
- achievements: array of strings

Resume text:
${resumeText}`;

let response;
try {
  if (rotation.aiProvider === 'groq') {
    response = await this.helpers.httpRequest({
      method: 'POST',
      url: rotation.aiUrl,
      headers: {
        'Authorization': `Bearer ${rotation.aiKey}`,
        'Content-Type': 'application/json'
      },
      body: {
        model: rotation.aiModel,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.1,
        max_tokens: 2000
      }
    });
    const content = response.choices[0].message.content;
    const jsonMatch = content.match(/\\{[\\s\\S]*\\}/);
    if (jsonMatch) parsed = JSON.parse(jsonMatch[0]);
  } else if (rotation.aiProvider === 'gemini') {
    response = await this.helpers.httpRequest({
      method: 'POST',
      url: `${rotation.aiUrl}?key=${rotation.aiKey}`,
      headers: { 'Content-Type': 'application/json' },
      body: {
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.1, maxOutputTokens: 2000 }
      }
    });
    const content = response.candidates[0].content.parts[0].text;
    const jsonMatch = content.match(/\\{[\\s\\S]*\\}/);
    if (jsonMatch) parsed = JSON.parse(jsonMatch[0]);
  }
  // Increment AI counter
  if (rotation.aiProvider === 'groq') {
    staticData.groqCounts[staticData.groqIndex]++;
  } else {
    staticData.geminiCounts[staticData.geminiIndex]++;
  }
  staticData.aiCallsToday++;
} catch (e) {
  // Fallback to user profile
  const profile = $('User Profile').first().json;
  parsed.skills = profile.skills || [];
}

return [{ json: parsed }];
'''

nodes.append({
    "parameters": {
        "jsCode": parse_resume_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_resume_ai'],
    "name": "Parse Resume with AI",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [880, 200]
})


# Step 6: Fetch 8 Job APIs (httpRequest nodes)
# 1. Fetch Remotive
nodes.append({
    "parameters": {
        "url": "https://remotive.com/api/remote-jobs?limit=20",
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_remotive'],
    "name": "Fetch Remotive",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [880, -600]
})

# 2. Fetch Arbeitnow
nodes.append({
    "parameters": {
        "url": "https://www.arbeitnow.com/api/job-board-api",
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_arbeitnow'],
    "name": "Fetch Arbeitnow",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [880, -400]
})

# 3. Fetch Himalayas
nodes.append({
    "parameters": {
        "url": "https://himalayas.app/jobs/api?limit=20",
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_himalayas'],
    "name": "Fetch Himalayas",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [880, -200]
})

# 4. Fetch RemoteJobs.org
nodes.append({
    "parameters": {
        "url": "https://remotejobs.org/api/jobs?limit=20",
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_remotejobs'],
    "name": "Fetch RemoteJobs.org",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [880, 0]
})

# 5. Fetch Jobicy
nodes.append({
    "parameters": {
        "url": "https://jobicy.com/api/v2/remote-jobs?count=20",
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_jobicy'],
    "name": "Fetch Jobicy",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1100, -600]
})


# 6. Fetch JSearch (RapidAPI)
nodes.append({
    "parameters": {
        "url": "https://jsearch.p.rapidapi.com/search",
        "sendQuery": True,
        "queryParameters": {
            "parameters": [
                {"name": "query", "value": "={{$('User Profile').item.json.keywords}}"},
                {"name": "num_pages", "value": "1"},
                {"name": "date_posted", "value": "week"}
            ]
        },
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "X-RapidAPI-Key", "value": "={{$('AI Key Rotation Manager').item.json.rapidApiKey}}"},
                {"name": "X-RapidAPI-Host", "value": "jsearch.p.rapidapi.com"}
            ]
        },
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_jsearch'],
    "name": "Fetch JSearch",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1100, -400]
})

# 7. Fetch Findwork
nodes.append({
    "parameters": {
        "url": "https://findwork.dev/api/jobs/",
        "sendHeaders": True,
        "headerParameters": {
            "parameters": [
                {"name": "Authorization", "value": "=Token {{$('AI Key Rotation Manager').item.json.findworkKey}}"}
            ]
        },
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_findwork'],
    "name": "Fetch Findwork",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1100, -200]
})

# 8. Fetch The Muse
nodes.append({
    "parameters": {
        "url": "https://www.themuse.com/api/public/jobs?page=1&descending=true",
        "options": {"timeout": 15000}
    },
    "id": IDS['fetch_themuse'],
    "name": "Fetch The Muse",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [1100, 0]
})


# Helper: email extraction function used in all parsers
email_extract_fn = '''
function extractEmails(text) {
  if (!text) return { recruiterEmail: null, recruiterName: null };
  const emailRegex = /[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}/g;
  const allEmails = (text.match(emailRegex) || [])
    .map(e => e.toLowerCase())
    .filter(e => !e.match(/noreply|unsubscribe|notifications|mailer-daemon|no-reply/))
    .filter(e => !e.match(/\\.(png|jpg|jpeg|gif|svg|webp)$/));
  
  if (allEmails.length === 0) return { recruiterEmail: null, recruiterName: null };
  
  // Priority: career/hr/hiring/talent/recruit keywords
  const priority = allEmails.find(e => e.match(/career|hr|hiring|talent|recruit|jobs|apply|people/));
  const chosen = priority || allEmails[0];
  const namePart = chosen.split('@')[0].replace(/[._]/g, ' ');
  return { recruiterEmail: chosen, recruiterName: namePart };
}
'''

# Step 7: Parse each API response (Code nodes)
# Parse Remotive
parse_remotive_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobs = (data.jobs || []).map(job => {{
    const emails = extractEmails(job.description || '');
    return {{
      source: 'remotive',
      jobTitle: job.title || '',
      company: job.company_name || '',
      location: job.candidate_required_location || 'Remote',
      workMode: 'remote',
      description: (job.description || '').substring(0, 1000),
      applyUrl: job.url || '',
      postedDate: job.publication_date || '',
      jobId: `remotive_${{job.id || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'remotive' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'remotive', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_remotive_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_remotive'],
    "name": "Parse Remotive",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1320, -600]
})


# Parse Arbeitnow
parse_arbeitnow_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobs = (data.data || []).map(job => {{
    const emails = extractEmails(job.description || '');
    return {{
      source: 'arbeitnow',
      jobTitle: job.title || '',
      company: job.company_name || '',
      location: job.location || 'Remote',
      workMode: job.remote ? 'remote' : 'hybrid',
      description: (job.description || '').substring(0, 1000),
      applyUrl: job.url || '',
      postedDate: job.created_at || '',
      jobId: `arbeitnow_${{job.slug || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'arbeitnow' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'arbeitnow', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_arbeitnow_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_arbeitnow'],
    "name": "Parse Arbeitnow",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1320, -400]
})

# Parse Himalayas
parse_himalayas_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobs = (data.jobs || []).map(job => {{
    const emails = extractEmails(job.description || '');
    return {{
      source: 'himalayas',
      jobTitle: job.title || '',
      company: job.companyName || job.company_name || '',
      location: job.location || 'Remote',
      workMode: 'remote',
      description: (job.description || '').substring(0, 1000),
      applyUrl: job.applicationUrl || job.url || '',
      postedDate: job.pubDate || job.postedDate || '',
      jobId: `himalayas_${{job.id || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'himalayas' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'himalayas', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_himalayas_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_himalayas'],
    "name": "Parse Himalayas",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1320, -200]
})


# Parse RemoteJobs.org
parse_remotejobs_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobsArr = Array.isArray(data) ? data : (data.jobs || data.data || []);
  const jobs = jobsArr.map(job => {{
    const emails = extractEmails(job.description || '');
    return {{
      source: 'remotejobs',
      jobTitle: job.title || '',
      company: job.company || job.company_name || '',
      location: job.location || 'Remote',
      workMode: 'remote',
      description: (job.description || '').substring(0, 1000),
      applyUrl: job.url || job.apply_url || '',
      postedDate: job.date || job.created_at || '',
      jobId: `remotejobs_${{job.id || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'remotejobs' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'remotejobs', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_remotejobs_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_remotejobs'],
    "name": "Parse RemoteJobs",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1320, 0]
})

# Parse Jobicy
parse_jobicy_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobs = (data.jobs || []).map(job => {{
    const emails = extractEmails(job.jobDescription || '');
    return {{
      source: 'jobicy',
      jobTitle: job.jobTitle || '',
      company: job.companyName || '',
      location: job.jobGeo || 'Remote',
      workMode: 'remote',
      description: (job.jobDescription || '').substring(0, 1000),
      applyUrl: job.url || '',
      postedDate: job.pubDate || '',
      jobId: `jobicy_${{job.id || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'jobicy' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'jobicy', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_jobicy_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_jobicy'],
    "name": "Parse Jobicy",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1540, -600]
})


# Parse JSearch
parse_jsearch_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobs = (data.data || []).map(job => {{
    const desc = job.job_description || '';
    const emails = extractEmails(desc);
    return {{
      source: 'jsearch',
      jobTitle: job.job_title || '',
      company: job.employer_name || '',
      location: job.job_city ? `${{job.job_city}}, ${{job.job_country}}` : (job.job_country || 'Remote'),
      workMode: job.job_is_remote ? 'remote' : 'onsite',
      description: desc.substring(0, 1000),
      applyUrl: job.job_apply_link || '',
      postedDate: job.job_posted_at_datetime_utc || '',
      jobId: `jsearch_${{job.job_id || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'jsearch' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'jsearch', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_jsearch_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_jsearch'],
    "name": "Parse JSearch",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1540, -400]
})

# Parse Findwork
parse_findwork_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobs = (data.results || []).map(job => {{
    const desc = job.text || job.description || '';
    const emails = extractEmails(desc);
    return {{
      source: 'findwork',
      jobTitle: job.role || '',
      company: job.company_name || '',
      location: job.location || 'Remote',
      workMode: job.remote ? 'remote' : 'onsite',
      description: desc.substring(0, 1000),
      applyUrl: job.url || '',
      postedDate: job.date_posted || '',
      jobId: `findwork_${{job.id || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'findwork' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'findwork', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_findwork_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_findwork'],
    "name": "Parse Findwork",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1540, -200]
})


# Parse The Muse
parse_themuse_code = f'''
{email_extract_fn}
try {{
  const data = $input.first().json;
  const jobs = (data.results || []).map(job => {{
    const desc = job.contents || '';
    const emails = extractEmails(desc);
    const loc = job.locations && job.locations.length > 0 ? job.locations[0].name : 'Remote';
    return {{
      source: 'themuse',
      jobTitle: job.name || '',
      company: job.company ? job.company.name : '',
      location: loc,
      workMode: loc.toLowerCase().includes('remote') ? 'remote' : 'onsite',
      description: desc.substring(0, 1000),
      applyUrl: job.refs ? job.refs.landing_page : '',
      postedDate: job.publication_date || '',
      jobId: `themuse_${{job.id || ''}}`,
      recruiterEmail: emails.recruiterEmail,
      recruiterName: emails.recruiterName
    }};
  }});
  return jobs.length > 0 ? jobs.map(j => ({{ json: j }})) : [{{ json: {{ empty: true, source: 'themuse' }} }}];
}} catch (e) {{
  return [{{ json: {{ empty: true, source: 'themuse', error: e.message }} }}];
}}
'''

nodes.append({
    "parameters": {
        "jsCode": parse_themuse_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['parse_themuse'],
    "name": "Parse The Muse",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1540, 0]
})


# Step 9: Merge All Jobs
merge_code = '''
const allItems = $input.all();
const jobs = allItems
  .map(item => item.json)
  .filter(j => !j.empty && j.jobTitle);
  
if (jobs.length === 0) {
  return [{ json: { empty: true, message: "No jobs found from any API" } }];
}

return jobs.map(j => ({ json: j }));
'''

nodes.append({
    "parameters": {
        "jsCode": merge_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['merge_all_jobs'],
    "name": "Merge All Jobs",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1760, -300]
})

# Step 10: Deduplicate
dedup_code = '''
const staticData = this.getWorkflowStaticData('global');
if (!staticData.seenJobs) staticData.seenJobs = {};

const items = $input.all();
const unique = [];

for (const item of items) {
  if (item.json.empty) continue;
  const key = (item.json.jobTitle + item.json.company).toLowerCase().replace(/\\s+/g, '');
  if (!staticData.seenJobs[key]) {
    staticData.seenJobs[key] = Date.now();
    unique.push(item);
  }
}

// Clean old entries (>7 days)
const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
for (const key of Object.keys(staticData.seenJobs)) {
  if (staticData.seenJobs[key] < weekAgo) {
    delete staticData.seenJobs[key];
  }
}

if (unique.length === 0) {
  return [{ json: { empty: true, message: "All jobs are duplicates" } }];
}
return unique;
'''

nodes.append({
    "parameters": {
        "jsCode": dedup_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['deduplicate_jobs'],
    "name": "Deduplicate Jobs",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1980, -300]
})


# Step 11: Freshness Filter
freshness_code = '''
const config = $('Backend Config').first().json;
const maxDays = config.freshnessMaxDays || 14;
const items = $input.all();
const filtered = [];

for (const item of items) {
  if (item.json.empty) continue;
  
  const postedDate = item.json.postedDate;
  if (!postedDate) {
    // No date available - keep it with NORMAL priority
    item.json.priority = 'NORMAL';
    filtered.push(item);
    continue;
  }
  
  const posted = new Date(postedDate);
  const now = new Date();
  const diffDays = Math.floor((now - posted) / (1000 * 60 * 60 * 24));
  
  if (diffDays > maxDays) continue; // Skip old jobs
  
  // Set priority
  if (diffDays <= 2) item.json.priority = 'HIGH';
  else if (diffDays <= 7) item.json.priority = 'NORMAL';
  else item.json.priority = 'LOW';
  
  item.json.ageDays = diffDays;
  filtered.push(item);
}

if (filtered.length === 0) {
  return [{ json: { empty: true, message: "All jobs too old" } }];
}
return filtered;
'''

nodes.append({
    "parameters": {
        "jsCode": freshness_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['freshness_filter'],
    "name": "Freshness Filter",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [2200, -300]
})

# Step 12: AI Score Jobs (runOnceForEachItem)
ai_score_code = '''
const staticData = this.getWorkflowStaticData('global');
const rotation = $('AI Key Rotation Manager').first().json;
const userProfile = $('User Profile').first().json;
const resume = $('Parse Resume with AI').first().json;
const job = $input.item.json;

if (job.empty) return [{ json: { ...job, score: 0, matchReason: 'empty' } }];
if (rotation.aiProvider === 'exhausted') {
  // Fallback: simple keyword matching
  const skills = (userProfile.skills || []).map(s => s.toLowerCase());
  const desc = (job.description || '').toLowerCase();
  let score = 0;
  skills.forEach(s => { if (desc.includes(s)) score += 15; });
  score = Math.min(score, 100);
  return [{ json: { ...job, score, matchReason: 'keyword-fallback' } }];
}

const prompt = `Score this job match 0-100 for the candidate. Return ONLY JSON: {"score": number, "matchReason": "brief reason"}

Job: ${job.jobTitle} at ${job.company}
Description: ${(job.description || '').substring(0, 500)}
Location: ${job.location} | Mode: ${job.workMode}

Candidate Skills: ${userProfile.skills.join(', ')}
Experience: ${userProfile.experience}
Resume Skills: ${(resume.skills || []).join(', ')}
Resume Projects: ${(resume.projects || []).map(p => p.name || p).join(', ')}

Scoring: +20 skill overlap, +15 project match, +10 location match, +10 seniority match, +10 fresh posting`;

try {
  let content = '';
  if (rotation.aiProvider === 'groq') {
    const resp = await this.helpers.httpRequest({
      method: 'POST',
      url: rotation.aiUrl,
      headers: { 'Authorization': `Bearer ${rotation.aiKey}`, 'Content-Type': 'application/json' },
      body: { model: rotation.aiModel, messages: [{ role: 'user', content: prompt }], temperature: 0.1, max_tokens: 200 }
    });
    content = resp.choices[0].message.content;
    staticData.groqCounts[staticData.groqIndex]++;
  } else {
    const resp = await this.helpers.httpRequest({
      method: 'POST',
      url: `${rotation.aiUrl}?key=${rotation.aiKey}`,
      headers: { 'Content-Type': 'application/json' },
      body: { contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.1, maxOutputTokens: 200 } }
    });
    content = resp.candidates[0].content.parts[0].text;
    staticData.geminiCounts[staticData.geminiIndex]++;
  }
  staticData.aiCallsToday++;
  
  const jsonMatch = content.match(/\\{[\\s\\S]*?\\}/);
  if (jsonMatch) {
    const result = JSON.parse(jsonMatch[0]);
    return [{ json: { ...job, score: result.score || 0, matchReason: result.matchReason || '' } }];
  }
  return [{ json: { ...job, score: 50, matchReason: 'parse-error' } }];
} catch (e) {
  return [{ json: { ...job, score: 50, matchReason: `error: ${e.message}` } }];
}
'''

nodes.append({
    "parameters": {
        "jsCode": ai_score_code,
        "mode": "runOnceForEachItem"
    },
    "id": IDS['ai_score_jobs'],
    "name": "AI Score Jobs",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [2420, -300]
})


# Step 13: Filter Score >= 60 (IF node)
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": ""},
            "conditions": [
                {
                    "id": uid(),
                    "leftValue": "={{ $json.score }}",
                    "rightValue": "={{ $('Backend Config').item.json.scoreThreshold }}",
                    "operator": {"type": "number", "operation": "gte"}
                }
            ],
            "combinator": "and"
        }
    },
    "id": IDS['filter_score'],
    "name": "Filter Score >= 60",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [2640, -300]
})

# Step 14: Store Jobs for Outreach
store_jobs_code = '''
const staticData = this.getWorkflowStaticData('global');
if (!staticData.discoveredJobs) staticData.discoveredJobs = [];

const items = $input.all();
const today = new Date().toISOString().split('T')[0];

for (const item of items) {
  const job = item.json;
  if (job.empty) continue;
  
  job.discoveredAt = today;
  job.emailed = false;
  staticData.discoveredJobs.push(job);
}

// Cap at 500 (rolling window)
if (staticData.discoveredJobs.length > 500) {
  staticData.discoveredJobs = staticData.discoveredJobs.slice(-500);
}

return [{ json: { 
  stored: items.length, 
  totalInQueue: staticData.discoveredJobs.length,
  today: today
}}];
'''

nodes.append({
    "parameters": {
        "jsCode": store_jobs_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['store_jobs'],
    "name": "Store Jobs for Outreach",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [2860, -300]
})

# Step 15: Prepare Telegram Summary
prepare_telegram_code = '''
const stored = $input.first().json;
const allItems = $('AI Score Jobs').all();
const highPriority = allItems.filter(i => i.json.priority === 'HIGH' && i.json.score >= 60);
const totalScored = allItems.filter(i => !i.json.empty).length;
const passed = allItems.filter(i => i.json.score >= 60).length;

let msg = `🔍 *Job Discovery Report*\\n\\n`;
msg += `📊 Found: ${totalScored} jobs | Passed: ${passed} (score ≥60)\\n`;
msg += `💾 Stored for outreach: ${stored.stored} | Queue: ${stored.totalInQueue}\\n\\n`;

if (highPriority.length > 0) {
  msg += `⚡ *HIGH PRIORITY (posted <2 days):*\\n`;
  highPriority.slice(0, 5).forEach((item, i) => {
    const j = item.json;
    msg += `${i+1}. ${j.jobTitle} @ ${j.company} (${j.score}/100)\\n`;
    if (j.applyUrl) msg += `   → ${j.applyUrl}\\n`;
  });
  if (highPriority.length > 5) msg += `   ...and ${highPriority.length - 5} more\\n`;
}

msg += `\\n✅ Outreach will begin at 9:00 AM UTC`;
return [{ json: { message: msg } }];
'''

nodes.append({
    "parameters": {
        "jsCode": prepare_telegram_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['prepare_telegram'],
    "name": "Prepare Telegram Summary",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [3080, -300]
})

# Step 16: Send Telegram Digest
nodes.append({
    "parameters": {
        "chatId": "={{$('User Profile').item.json.telegramChatId}}",
        "text": "={{$json.message}}",
        "additionalFields": {"parse_mode": "Markdown"}
    },
    "id": IDS['send_telegram_digest'],
    "name": "Send Telegram Digest",
    "type": "n8n-nodes-base.telegram",
    "typeVersion": 1.2,
    "position": [3300, -300],
    "credentials": {"telegramApi": {"id": "1", "name": "Telegram Bot"}}
})


# ============================================================
# TRIGGER 2: Schedule at 9 AM UTC (Email Outreach)
# ============================================================
nodes.append({
    "parameters": {
        "rule": {
            "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
        }
    },
    "id": IDS['trigger2_schedule'],
    "name": "Trigger: 9AM Email Outreach",
    "type": "n8n-nodes-base.scheduleTrigger",
    "typeVersion": 1.2,
    "position": [0, 600]
})

# Step 17: Get Jobs for Outreach
get_jobs_code = '''
const staticData = this.getWorkflowStaticData('global');
const today = new Date().toISOString().split('T')[0];

if (!staticData.discoveredJobs || staticData.discoveredJobs.length === 0) {
  return [{ json: { empty: true, message: "No jobs in queue" } }];
}

// Filter: has recruiterEmail AND not already emailed today
const available = staticData.discoveredJobs.filter(job => 
  job.recruiterEmail && !job.emailed
);

if (available.length === 0) {
  return [{ json: { empty: true, message: "No jobs with email available" } }];
}

return available.map(j => ({ json: j }));
'''

nodes.append({
    "parameters": {
        "jsCode": get_jobs_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['get_jobs_outreach'],
    "name": "Get Jobs for Outreach",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [440, 600]
})

# Step 18: Check Email Limit
check_limit_code = '''
const staticData = this.getWorkflowStaticData('global');
const config = $('Backend Config').first().json;
const today = new Date().toISOString().split('T')[0];

if (!staticData.emailsSent) staticData.emailsSent = {};
if (!staticData.emailsSent[today]) {
  staticData.emailsSent[today] = { count: 0, jobIds: [] };
}

const sent = staticData.emailsSent[today].count;
const limit = config.userEmailDailyLimit || 50;
const remaining = limit - sent;

if (remaining <= 0) {
  return [{ json: { limitReached: true, sent, limit } }];
}

// Slice jobs to fit remaining limit
const items = $input.all().filter(i => !i.json.empty);
const toSend = items.slice(0, remaining);

return toSend.map(item => ({
  json: { ...item.json, limitReached: false, emailsSentToday: sent, dailyLimit: limit }
}));
'''

nodes.append({
    "parameters": {
        "jsCode": check_limit_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['check_email_limit'],
    "name": "Check Email Limit",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [660, 600]
})


# Step 19: Limit Reached? (IF node)
nodes.append({
    "parameters": {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": ""},
            "conditions": [
                {
                    "id": uid(),
                    "leftValue": "={{ $json.limitReached }}",
                    "rightValue": True,
                    "operator": {"type": "boolean", "operation": "true"}
                }
            ],
            "combinator": "and"
        }
    },
    "id": IDS['limit_reached'],
    "name": "Limit Reached?",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.2,
    "position": [880, 600]
})

# Step 20: AI Generate Application Email (runOnceForEachItem)
generate_email_code = '''
const staticData = this.getWorkflowStaticData('global');
const rotation = $('AI Key Rotation Manager').first().json;
const userProfile = $('User Profile').first().json;
const resume = $('Parse Resume with AI').first().json;
const job = $input.item.json;

if (job.empty || !job.recruiterEmail) {
  return [{ json: { skip: true } }];
}

// Generate email with AI or fallback
let emailSubject = `Application for ${job.jobTitle} at ${job.company}`;
let emailBody = '';

if (rotation.aiProvider !== 'exhausted') {
  const prompt = `Write a DIRECT job application email (150-200 words). This is NOT a follow-up.

Job: ${job.jobTitle} at ${job.company}
Description: ${(job.description || '').substring(0, 400)}

Candidate: ${userProfile.name}
Skills: ${userProfile.skills.join(', ')}
Experience: ${userProfile.experience}
Resume highlights: ${(resume.projects || []).slice(0, 2).map(p => p.name || p).join(', ')}
LinkedIn: ${userProfile.linkedinUrl}
Portfolio: ${userProfile.portfolioUrl}

Instructions:
- Start with "Hi [Hiring Team/Recruiter Name],"
- First paragraph: State you're applying for the role, mention one specific JD requirement you match
- Second paragraph: Reference a project from resume that proves competence
- Close: Express enthusiasm, mention resume is attached
- Sign off with name + LinkedIn + Portfolio
- Keep it 150-200 words, professional but warm
- Do NOT say "I saw your posting on..." or "I hope this email finds you..."

Return format:
Subject: [subject line]

[email body]`;

  try {
    let content = '';
    if (rotation.aiProvider === 'groq') {
      const resp = await this.helpers.httpRequest({
        method: 'POST',
        url: rotation.aiUrl,
        headers: { 'Authorization': `Bearer ${rotation.aiKey}`, 'Content-Type': 'application/json' },
        body: { model: rotation.aiModel, messages: [{ role: 'user', content: prompt }], temperature: 0.7, max_tokens: 500 }
      });
      content = resp.choices[0].message.content;
      staticData.groqCounts[staticData.groqIndex]++;
    } else {
      const resp = await this.helpers.httpRequest({
        method: 'POST',
        url: `${rotation.aiUrl}?key=${rotation.aiKey}`,
        headers: { 'Content-Type': 'application/json' },
        body: { contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.7, maxOutputTokens: 500 } }
      });
      content = resp.candidates[0].content.parts[0].text;
      staticData.geminiCounts[staticData.geminiIndex]++;
    }
    staticData.aiCallsToday++;
    
    // Parse subject and body
    const subjectMatch = content.match(/Subject:\\s*(.+)/i);
    if (subjectMatch) {
      emailSubject = subjectMatch[1].trim();
      emailBody = content.replace(/Subject:.+\\n?\\n?/i, '').trim();
    } else {
      emailBody = content.trim();
    }
  } catch (e) {
    // Fallback template
    emailBody = `Hi Hiring Team,\\n\\nI am writing to apply for the ${job.jobTitle} position at ${job.company}. With ${userProfile.experience} of experience in ${userProfile.skills.slice(0, 3).join(', ')}, I believe I would be a strong fit for this role.\\n\\nI have attached my resume for your review. I would welcome the opportunity to discuss how my background aligns with your needs.\\n\\nBest regards,\\n${userProfile.name}\\n${userProfile.linkedinUrl}\\n${userProfile.portfolioUrl}`;
  }
} else {
  // AI exhausted - simple template
  emailBody = `Hi Hiring Team,\\n\\nI am writing to apply for the ${job.jobTitle} position at ${job.company}. With ${userProfile.experience} of experience in ${userProfile.skills.slice(0, 3).join(', ')}, I believe I would be a strong fit for this role.\\n\\nI have attached my resume for your review. I would welcome the opportunity to discuss how my background aligns with your needs.\\n\\nBest regards,\\n${userProfile.name}\\n${userProfile.linkedinUrl}\\n${userProfile.portfolioUrl}`;
}

return [{ json: { 
  ...job, 
  emailSubject, 
  emailBody, 
  sendTo: job.recruiterEmail,
  ccEmail: userProfile.email
}}];
'''

nodes.append({
    "parameters": {
        "jsCode": generate_email_code,
        "mode": "runOnceForEachItem"
    },
    "id": IDS['generate_email'],
    "name": "AI: Generate Application Email",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1100, 800]
})


# Step 21: Send Application Email (Gmail node)
nodes.append({
    "parameters": {
        "sendTo": "={{$json.sendTo}}",
        "subject": "={{$json.emailSubject}}",
        "message": "={{$json.emailBody}}",
        "options": {
            "ccList": "={{$json.ccEmail}}"
        }
    },
    "id": IDS['send_email'],
    "name": "Send Application Email",
    "type": "n8n-nodes-base.gmail",
    "typeVersion": 2.1,
    "position": [1320, 800],
    "credentials": {"gmailOAuth2": {"id": "1", "name": "User Gmail OAuth"}}
})

# Step 22: Track Email Sent
track_email_code = '''
const staticData = this.getWorkflowStaticData('global');
const today = new Date().toISOString().split('T')[0];

if (!staticData.emailsSent) staticData.emailsSent = {};
if (!staticData.emailsSent[today]) {
  staticData.emailsSent[today] = { count: 0, jobIds: [] };
}

const job = $input.item.json;
staticData.emailsSent[today].count++;
staticData.emailsSent[today].jobIds.push(job.jobId);

// Mark job as emailed in discoveredJobs
if (staticData.discoveredJobs) {
  const idx = staticData.discoveredJobs.findIndex(j => j.jobId === job.jobId);
  if (idx >= 0) {
    staticData.discoveredJobs[idx].emailed = true;
    staticData.discoveredJobs[idx].emailedAt = new Date().toISOString();
  }
}

return [{ json: { 
  ...job, 
  emailSent: true, 
  emailCount: staticData.emailsSent[today].count 
}}];
'''

nodes.append({
    "parameters": {
        "jsCode": track_email_code,
        "mode": "runOnceForEachItem"
    },
    "id": IDS['track_email'],
    "name": "Track Email Sent",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1540, 800]
})

# Step 23: Outreach Summary
outreach_summary_code = '''
const staticData = this.getWorkflowStaticData('global');
const today = new Date().toISOString().split('T')[0];
const todayStats = staticData.emailsSent ? staticData.emailsSent[today] : { count: 0 };
const config = $('Backend Config').first().json;

const items = $input.all();
const sentCount = items.length;

let msg = `📧 *Email Outreach Complete*\\n\\n`;
msg += `✅ Sent: ${sentCount} application emails\\n`;
msg += `📊 Total today: ${todayStats.count}/${config.userEmailDailyLimit}\\n\\n`;

items.slice(0, 5).forEach((item, i) => {
  const j = item.json;
  msg += `${i+1}. ${j.jobTitle} @ ${j.company}\\n`;
  msg += `   → ${j.recruiterEmail}\\n`;
});

if (items.length > 5) msg += `   ...and ${items.length - 5} more\\n`;
msg += `\\n💡 Each email is a direct application with resume context.`;

return [{ json: { message: msg } }];
'''

nodes.append({
    "parameters": {
        "jsCode": outreach_summary_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['outreach_summary'],
    "name": "Outreach Summary",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [1760, 800]
})


# Step 24: Send Outreach Telegram
nodes.append({
    "parameters": {
        "chatId": "={{$('User Profile').item.json.telegramChatId}}",
        "text": "={{$json.message}}",
        "additionalFields": {"parse_mode": "Markdown"}
    },
    "id": IDS['send_outreach_telegram'],
    "name": "Send Outreach Telegram",
    "type": "n8n-nodes-base.telegram",
    "typeVersion": 1.2,
    "position": [1980, 800],
    "credentials": {"telegramApi": {"id": "1", "name": "Telegram Bot"}}
})

# Step 25: Limit Notification
nodes.append({
    "parameters": {
        "chatId": "={{$('User Profile').item.json.telegramChatId}}",
        "text": "=⚠️ *Daily Email Limit Reached*\n\nSent: {{$json.sent}}/{{$json.limit}} emails today.\nOutreach paused until tomorrow.\n\n💡 Remaining jobs saved in queue for tomorrow.",
        "additionalFields": {"parse_mode": "Markdown"}
    },
    "id": IDS['limit_notification'],
    "name": "Limit Notification",
    "type": "n8n-nodes-base.telegram",
    "typeVersion": 1.2,
    "position": [1100, 400],
    "credentials": {"telegramApi": {"id": "1", "name": "Telegram Bot"}}
})


# ============================================================
# TRIGGER 3: Schedule at Midnight UTC (Daily Reset)
# ============================================================
nodes.append({
    "parameters": {
        "rule": {
            "interval": [{"field": "cronExpression", "expression": "0 0 * * *"}]
        }
    },
    "id": IDS['trigger3_schedule'],
    "name": "Trigger: Midnight Reset",
    "type": "n8n-nodes-base.scheduleTrigger",
    "typeVersion": 1.2,
    "position": [0, 1200]
})

# Step 26: Daily Reset
daily_reset_code = '''
const staticData = this.getWorkflowStaticData('global');
const today = new Date().toISOString().split('T')[0];

// Reset AI counters
staticData.rotationDate = today;
staticData.groqIndex = 0;
staticData.geminiIndex = 0;
staticData.groqCounts = [0, 0, 0, 0];
staticData.geminiCounts = [0, 0, 0, 0];
staticData.aiCallsToday = 0;

// Reset email counter (keep history)
if (!staticData.emailsSent) staticData.emailsSent = {};
staticData.emailsSent[today] = { count: 0, jobIds: [] };

// Clean old email history (keep 7 days)
const keys = Object.keys(staticData.emailsSent);
const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
keys.forEach(k => { if (k < weekAgo) delete staticData.emailsSent[k]; });

// Keep discoveredJobs (rolling window) but clean >14 day old
if (staticData.discoveredJobs) {
  const cutoff = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  staticData.discoveredJobs = staticData.discoveredJobs.filter(j => 
    !j.discoveredAt || j.discoveredAt >= cutoff
  );
}

// Reset RapidAPI monthly counters on 1st of month
const dayOfMonth = new Date().getDate();
if (dayOfMonth === 1) {
  staticData.rapidApiIndex = 0;
  staticData.findworkIndex = 0;
  staticData.rapidApiCounts = [0, 0, 0, 0];
  staticData.findworkCounts = [0, 0, 0, 0];
}

return [{ json: { 
  message: "Daily reset complete",
  date: today,
  discoveredJobsCount: (staticData.discoveredJobs || []).length
}}];
'''

nodes.append({
    "parameters": {
        "jsCode": daily_reset_code,
        "mode": "runOnceForAllItems"
    },
    "id": IDS['daily_reset'],
    "name": "Daily Reset",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [220, 1200]
})


# ============================================================
# CONNECTIONS
# ============================================================
connections = {
    "Trigger: 8AM Job Discovery": {
        "main": [[{"node": "Backend Config", "type": "main", "index": 0}]]
    },
    "Backend Config": {
        "main": [[
            {"node": "AI Key Rotation Manager", "type": "main", "index": 0},
            {"node": "User Profile", "type": "main", "index": 0},
            {"node": "Get Jobs for Outreach", "type": "main", "index": 0}
        ]]
    },
    "User Profile": {
        "main": [[{"node": "Download Resume", "type": "main", "index": 0}]]
    },
    "Download Resume": {
        "main": [[{"node": "Parse Resume with AI", "type": "main", "index": 0}]]
    },
    "AI Key Rotation Manager": {
        "main": [[
            {"node": "Fetch Remotive", "type": "main", "index": 0},
            {"node": "Fetch Arbeitnow", "type": "main", "index": 0},
            {"node": "Fetch Himalayas", "type": "main", "index": 0},
            {"node": "Fetch RemoteJobs.org", "type": "main", "index": 0},
            {"node": "Fetch Jobicy", "type": "main", "index": 0},
            {"node": "Fetch JSearch", "type": "main", "index": 0},
            {"node": "Fetch Findwork", "type": "main", "index": 0},
            {"node": "Fetch The Muse", "type": "main", "index": 0}
        ]]
    },
    "Fetch Remotive": {
        "main": [[{"node": "Parse Remotive", "type": "main", "index": 0}]]
    },
    "Fetch Arbeitnow": {
        "main": [[{"node": "Parse Arbeitnow", "type": "main", "index": 0}]]
    },
    "Fetch Himalayas": {
        "main": [[{"node": "Parse Himalayas", "type": "main", "index": 0}]]
    },
    "Fetch RemoteJobs.org": {
        "main": [[{"node": "Parse RemoteJobs", "type": "main", "index": 0}]]
    },
    "Fetch Jobicy": {
        "main": [[{"node": "Parse Jobicy", "type": "main", "index": 0}]]
    },
    "Fetch JSearch": {
        "main": [[{"node": "Parse JSearch", "type": "main", "index": 0}]]
    },
    "Fetch Findwork": {
        "main": [[{"node": "Parse Findwork", "type": "main", "index": 0}]]
    },
    "Fetch The Muse": {
        "main": [[{"node": "Parse The Muse", "type": "main", "index": 0}]]
    },
    "Parse Remotive": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Parse Arbeitnow": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Parse Himalayas": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Parse RemoteJobs": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Parse Jobicy": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Parse JSearch": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Parse Findwork": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Parse The Muse": {
        "main": [[{"node": "Merge All Jobs", "type": "main", "index": 0}]]
    },
    "Merge All Jobs": {
        "main": [[{"node": "Deduplicate Jobs", "type": "main", "index": 0}]]
    },
    "Deduplicate Jobs": {
        "main": [[{"node": "Freshness Filter", "type": "main", "index": 0}]]
    },
    "Freshness Filter": {
        "main": [[{"node": "AI Score Jobs", "type": "main", "index": 0}]]
    },
    "AI Score Jobs": {
        "main": [[{"node": "Filter Score >= 60", "type": "main", "index": 0}]]
    },
    "Filter Score >= 60": {
        "main": [
            [{"node": "Store Jobs for Outreach", "type": "main", "index": 0}],
            []
        ]
    },
    "Store Jobs for Outreach": {
        "main": [[{"node": "Prepare Telegram Summary", "type": "main", "index": 0}]]
    },
    "Prepare Telegram Summary": {
        "main": [[{"node": "Send Telegram Digest", "type": "main", "index": 0}]]
    },
    "Trigger: 9AM Email Outreach": {
        "main": [[{"node": "Backend Config", "type": "main", "index": 0}]]
    },
    "Get Jobs for Outreach": {
        "main": [[{"node": "Check Email Limit", "type": "main", "index": 0}]]
    },
    "Check Email Limit": {
        "main": [[{"node": "Limit Reached?", "type": "main", "index": 0}]]
    },
    "Limit Reached?": {
        "main": [
            [{"node": "Limit Notification", "type": "main", "index": 0}],
            [{"node": "AI: Generate Application Email", "type": "main", "index": 0}]
        ]
    },
    "AI: Generate Application Email": {
        "main": [[{"node": "Send Application Email", "type": "main", "index": 0}]]
    },
    "Send Application Email": {
        "main": [[{"node": "Track Email Sent", "type": "main", "index": 0}]]
    },
    "Track Email Sent": {
        "main": [[{"node": "Outreach Summary", "type": "main", "index": 0}]]
    },
    "Outreach Summary": {
        "main": [[{"node": "Send Outreach Telegram", "type": "main", "index": 0}]]
    },
    "Trigger: Midnight Reset": {
        "main": [[{"node": "Daily Reset", "type": "main", "index": 0}]]
    }
}


# ============================================================
# BUILD FINAL WORKFLOW JSON
# ============================================================
workflow = {
    "name": "Job Automation - Discovery + Outreach + Reset",
    "nodes": nodes,
    "connections": connections,
    "settings": {
        "executionOrder": "v1",
        "saveManualExecutions": True,
        "callerPolicy": "workflowsFromSameOwner"
    },
    "pinData": {},
    "active": False
}

# ============================================================
# VALIDATION
# ============================================================
print("=" * 60)
print("WORKFLOW VALIDATION")
print("=" * 60)

# Get all node names
node_names_set = {n["name"] for n in nodes}
print(f"\nTotal nodes: {len(nodes)}")

# Count edges
edge_count = 0
dangling = []
for source_name, conn_data in connections.items():
    if source_name not in node_names_set:
        dangling.append(f"SOURCE NOT FOUND: {source_name}")
    if "main" in conn_data:
        for output_group in conn_data["main"]:
            for edge in output_group:
                edge_count += 1
                target = edge["node"]
                if target not in node_names_set:
                    dangling.append(f"TARGET NOT FOUND: {target} (from {source_name})")

print(f"Total edges: {edge_count}")
print(f"Dangling references: {len(dangling)}")
if dangling:
    for d in dangling:
        print(f"  ❌ {d}")
else:
    print("  ✅ All connection references are valid!")

# Check all Code nodes have mode
code_nodes_without_mode = []
for n in nodes:
    if n["type"] == "n8n-nodes-base.code":
        if "mode" not in n["parameters"]:
            code_nodes_without_mode.append(n["name"])

if code_nodes_without_mode:
    print(f"\n❌ Code nodes missing 'mode': {code_nodes_without_mode}")
else:
    print(f"\n✅ All Code nodes have 'mode' set")

# Check all IDs are UUIDs
import re
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
bad_ids = [n["name"] for n in nodes if not uuid_pattern.match(n["id"])]
if bad_ids:
    print(f"❌ Non-UUID IDs: {bad_ids}")
else:
    print(f"✅ All node IDs are valid UUIDs")

# Check top-level keys
allowed_keys = {"name", "nodes", "connections", "settings", "pinData", "active"}
actual_keys = set(workflow.keys())
if actual_keys == allowed_keys:
    print(f"✅ Top-level keys correct: {sorted(actual_keys)}")
else:
    extra = actual_keys - allowed_keys
    missing = allowed_keys - actual_keys
    if extra: print(f"❌ Extra keys: {extra}")
    if missing: print(f"❌ Missing keys: {missing}")

# Write to file
import os
os.makedirs('/projects/sandbox/AI_automation/workflow', exist_ok=True)
output_path = '/projects/sandbox/AI_automation/workflow/job-automation.json'
with open(output_path, 'w') as f:
    json.dump(workflow, f, indent=2)

file_size = os.path.getsize(output_path)
print(f"\n📁 File saved: {output_path}")
print(f"📏 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
print(f"\n{'=' * 60}")
print("BUILD COMPLETE")
print(f"{'=' * 60}")

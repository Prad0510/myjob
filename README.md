# MyJob

**MyJob** is an automated job discovery and matching system that continuously collects internship and job opportunities from multiple sources, normalizes them into a common format, stores them in PostgreSQL, evaluates them against a candidate profile, and sends notifications for relevant opportunities.

The project is being developed as a personal **job monitoring and intelligent matching system**, with an upcoming unsupervised ML layer for discovering job and skill patterns from the collected market data.

---

## 🚀 Current Workflow

```text
Candidate Resume
      ↓
Resume Parser
      ↓
Candidate Profile
      ↓
                    ┌── Lever
                    ├── Greenhouse
Job Sources ────────┼── Ashby
                    ├── SmartRecruiters
                    └── Career Pages
                           ↓
                    Raw Job Data
                           ↓
                     Normalization
                           ↓
                      PostgreSQL
                           ↓
                 Eligibility Filtering
                           ↓
                    Job Matching
                           ↓
                    Match Score
                           ↓
                  Telegram Notification
```

The system also maintains the lifecycle of jobs by detecting whether previously collected jobs are still active or have disappeared from their source.

---

## ✨ Features Implemented

### 1. Resume Parsing

The system extracts candidate information from a resume PDF using **PyMuPDF**.

The parsed profile currently contains:

* Name
* Skills
* Education
* Experience
* Projects
* Target job roles

The profile is stored as:

```text
data/processed/candidate_profile.json
```

Example target roles:

```text
Python Developer
Backend Developer
Software Engineer
Data Engineer
Java Developer
```

---

### 2. Multi-Source Job Collection

MyJob supports multiple job collection mechanisms.

#### Lever

Uses the Lever public postings API.

```text
Source: Lever
Example company: Aleph
```

The collector retrieves:

* Job title
* Company
* Location
* Description
* Employment type
* Application URL
* Source job ID

---

#### Greenhouse

Uses the Greenhouse public job board API.

```text
Source: Greenhouse
Example company: Vercel
```

The collector retrieves job postings and their associated metadata.

---

#### Ashby

Uses the Ashby public posting API.

```text
Source: Ashby
Example company: Linear
```

The current integration successfully collected **31 Linear jobs** in a single synchronization run.

---

#### SmartRecruiters

Uses the SmartRecruiters public API.

The current integration successfully detects existing jobs and updates them instead of creating duplicate records.

---

#### Career Page Collector

MyJob also supports collecting jobs directly from company career pages using structured **JSON-LD JobPosting** data.

An AdEngage career page integration successfully collected multiple positions, including:

* Python Developer Intern
* Business Operations Intern
* HR Recruiter and Admin
* SEO & PPC Intern
* Social Media Marketing Intern
* Video Editing Intern
* Graphics Intern
* Sales Executive
* Client Servicing Executive

and other available positions.

---

## 🔄 Job Normalization

Different job sources provide different data formats.

MyJob converts these different formats into a common `RawJob → Job` representation.

```text
Source-specific job
        ↓
     RawJob
        ↓
 Job Normalizer
        ↓
Normalized Job
```

The normalized job contains fields such as:

```text
title
company
location
description
skills
experience_required
employment_type
application_method
application_url
source
source_type
source_job_id
fingerprint
source_company
```

HTML descriptions are cleaned before storage.

---

## 🗄️ PostgreSQL Database

PostgreSQL is used as the main persistent storage layer.

### Jobs

The `jobs` table stores normalized job postings.

Important fields include:

```text
id
source_job_id
title
company
location
description
skills
experience_required
employment_type
application_url
source
source_type
fingerprint
status
first_seen_at
last_seen_at
closed_at
source_company
missed_runs
```

---

### Job Matching

The `job_matches` table stores the matching results between the candidate and jobs.

It contains:

```text
match_score
matched_skills
missing_skills
role_score
skill_score
experience_score
semantic_score
application_url
```

Each job has a unique matching record.

---

### Collection Runs

The `collection_runs` table records every collection attempt.

It tracks:

```text
source
source_company
started_at
finished_at
jobs_found
success
error_message
```

This allows failed collection runs to be distinguished from genuinely missing jobs.

---

## ♻️ Job Lifecycle Tracking

MyJob does not immediately mark a job as closed when it disappears from one collection run.

Instead, it uses consecutive missed runs.

```text
Job found
   ↓
missed_runs = 0
   ↓
Job missing once
   ↓
missed_runs = 1
   ↓
Job missing again
   ↓
status = closed
```

A job is therefore marked **closed only after two consecutive successful collection runs in which it is not found**.

If the job appears again:

```text
status → active
missed_runs → 0
closed_at → NULL
```

Failed collection runs do not cause jobs to be closed.

This prevents temporary API failures from being interpreted as job closures.

---

## 🧠 Matching Engine

MyJob currently uses a hybrid matching system.

The structured matching score combines:

```text
Skill Score
Role Score
Experience Score
```

with the current weighting:

```text
Structured Score
    ↓
50% Skill
30% Role
20% Experience
```

A semantic similarity component is also included:

```text
Semantic Score
    ↓
Skill similarity
Experience similarity
Project similarity
```

The final score combines structured and semantic matching.

```text
Final Score
    =
80% Structured Score
+
20% Semantic Score
```

The current default notification threshold is:

```text
75%
```

Jobs are classified as eligible/uncertain before matching, preventing obviously unrelated roles from being treated as strong matches.

---

## 📱 Telegram Notifications

When a newly collected job crosses the configured match threshold, MyJob can send a Telegram notification.

The notification includes information such as:

```text
Job title
Company
Match percentage
Skill score
Role score
Experience score
Semantic score
Application URL
```

This allows relevant opportunities to be surfaced automatically without manually checking every job source.

---

## ⚙️ Automated Job Monitoring

MyJob is designed to run continuously rather than requiring manual execution.

The scheduler currently runs a synchronization cycle every **6 hours**.

```text
Scheduler
    ↓
Job Source Registry
    ↓
Collect jobs
    ↓
Normalize
    ↓
Insert / Update
    ↓
Lifecycle detection
    ↓
Evaluate new jobs
    ↓
Telegram notification
    ↓
Wait 6 hours
    ↓
Repeat
```

The scheduler is configured to run automatically through **Windows Task Scheduler**.

---

## 📊 Current Job Sources

| Source          | Example         | Status    |
| --------------- | --------------- | --------- |
| Lever           | Aleph           | ✅ Working |
| Greenhouse      | Vercel          | ✅ Working |
| Ashby           | Linear          | ✅ Working |
| SmartRecruiters | SmartRecruiters | ✅ Working |
| Career Page     | AdEngage        | ✅ Working |

The system is designed so additional companies can be added through the source registry without rewriting the core synchronization pipeline.

---

## 📁 Project Structure

```text
myjob/
│
├── src/
│   ├── api/
│   │
│   ├── resume/
│   │   ├── pdf_parser.py
│   │   └── candidate_profile.py
│   │
│   ├── collectors/
│   │   ├── lever/
│   │   ├── greenhouse/
│   │   ├── ashby/
│   │   ├── smartrecruiters/
│   │   └── career_page/
│   │
│   ├── normalization/
│   │   ├── raw_job.py
│   │   ├── job.py
│   │   ├── html_cleaner.py
│   │   └── job_normalizer.py
│   │
│   ├── matching/
│   │   ├── job_matcher.py
│   │   └── eligibility_filter.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── job_repository.py
│   │   ├── match_repository.py
│   │   ├── collection_repository.py
│   │   ├── job_lifecycle.py
│   │   └── evaluate_jobs.py
│   │
│   ├── notifications/
│   │   └── telegram.py
│   │
│   └── jobs/
│       ├── registry.py
│       ├── sync.py
│       └── scheduler.py
│
├── data/
│   ├── raw/
│   └── processed/
│       └── candidate_profile.json
│
├── tests/
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

### Programming

* Python 3.13
* SQL

### Data Processing

* PyMuPDF
* Pandas
* NumPy
* BeautifulSoup

### Machine Learning / Matching

* Scikit-learn
* Sentence Transformers
* Cosine similarity

### Database

* PostgreSQL
* psycopg2

### Job Sources

* Lever API
* Greenhouse API
* Ashby API
* SmartRecruiters API
* Company career pages

### Notifications

* Telegram Bot API

### Automation

* Python scheduler
* Windows Task Scheduler

### Development

* Git
* GitHub
* VS Code

---

## 🔐 Environment Variables

Create a `.env` file containing the database and notification configuration.

Example:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=myjob
DATABASE_USER=postgres
DATABASE_PASSWORD=YOUR_POSTGRES_PASSWORD

TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_CHAT_ID

MATCH_THRESHOLD=75
```

Do not commit `.env` to GitHub.

---

## ▶️ Running MyJob

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the job synchronization:

```powershell
python -m src.jobs.sync
```

Run the automated scheduler:

```powershell
python -m src.jobs.scheduler
```

The scheduler performs a synchronization every 6 hours.

---

## 🔍 Example Synchronization

A typical synchronization performs:

```text
Syncing Ashby: Linear
Found 31 jobs

Inserted: 31
Updated: 0
Seen: 31
Missed: 0
Closed: 0
```

Existing jobs are updated rather than duplicated:

```text
Syncing SmartRecruiters: SmartRecruiters
Found 1 jobs

Inserted: 0
Updated: 1
Seen: 1
Missed: 0
Closed: 0
```

---

## 🧪 Current Development Status

### Completed

* [x] Resume PDF parsing
* [x] Candidate profile generation
* [x] PostgreSQL database
* [x] Job normalization
* [x] Job fingerprinting
* [x] Lever integration
* [x] Greenhouse integration
* [x] Ashby integration
* [x] SmartRecruiters integration
* [x] Career page integration
* [x] Job insertion/updating
* [x] Duplicate prevention
* [x] Job lifecycle tracking
* [x] Collection run tracking
* [x] Eligibility filtering
* [x] Structured job matching
* [x] Semantic matching
* [x] Match threshold
* [x] Telegram notifications
* [x] Automated 6-hour synchronization
* [x] Windows Task Scheduler integration

### 🚧 Next Phase — Machine Learning

The next major component is an **unsupervised job market intelligence layer**.

Planned pipeline:

```text
Collected Jobs
      ↓
Skill Feature Extraction
      ↓
Job × Skill Matrix
      ↓
Feature Engineering
      ↓
PCA
      ↓
K-Means / HDBSCAN
      ↓
Job Clusters
      ↓
UMAP Visualization
      ↓
Skill & Cluster Analysis
```

The ML layer will be used to discover patterns such as:

* Groups of similar job roles
* Common skill combinations
* Job/skill clusters
* Emerging combinations of technical skills
* Similarity between different job-market segments

This will eventually allow MyJob to move beyond simple candidate-to-job matching toward **data-driven job market intelligence**.

---

## 🎯 Long-Term Goal

The long-term goal of MyJob is to create an automated system that continuously understands the job market and connects it with a candidate's profile.

```text
                    ┌─────────────────────┐
                    │    Job Market       │
                    └──────────┬──────────┘
                               ↓
                    Automated Collection
                               ↓
                         Job Database
                               ↓
                  ┌────────────┴────────────┐
                  ↓                         ↓
          Job Matching                ML Analysis
                  ↓                         ↓
        Candidate Relevance        Market Patterns
                  └────────────┬────────────┘
                               ↓
                         Notifications
                               ↓
                         Candidate
```

MyJob is therefore being developed as more than a job scraper: it is intended to become an **automated job discovery, matching, monitoring, and job-market intelligence system**.

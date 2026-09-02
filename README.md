# MyJob

MyJob is a resume-to-job matching system.

## Goal

MyJob extracts information from a candidate's resume, collects job
postings from available sources, normalizes the job data, calculates
job-resume similarity, and notifies the candidate when a job exceeds
the configured match threshold.

## Pipeline

Resume PDF
→ Resume Parser
→ Candidate Profile
→ Job Collectors
→ Job Normalizer
→ PostgreSQL
→ Matching Engine
→ Match Score
→ Notification

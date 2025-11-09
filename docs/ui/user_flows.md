# User Flows — AI Job Application Assistant

This document describes the primary user journeys in text and simple ASCII diagrams.

## 1. New user: Find matches and review

Steps:
1. Open app -> Land on Input Form
2. Fill out personal details, preferences, upload resume
3. Click "Find Matches"
4. Backend returns scored job list
5. User reviews results, opens job detail, reads tips
6. User saves jobs to tracker or exports to Excel

ASCII flow:

[Input Form] --(submit)--> [Processing/Scoring] --(results)--> [Results Dashboard]
[Results Dashboard] --(open)--> [Job Detail]
[Job Detail] --(save)--> [Application Tracker]

## 2. Track application progress

Steps:
1. From Results Dashboard, user clicks "Save to Tracker"
2. In Tracker, user updates Status -> Applied/Interview/Offer/Rejected
3. User adds notes and follow-up dates

ASCII flow:

[Results Dashboard] --(save)--> [Application Tracker] --(update status)--> [Status Changed]

## 3. Resume optimization loop

Steps:
1. System extracts keywords from resume and job descriptions
2. Shows missing keywords and suggestions in Job Detail
3. User edits resume externally and re-uploads
4. System re-evaluates matches

## Edge cases
- Missing resume: system should still run keyword matching on provided job titles and user inputs
- Large resume files (>5MB): show warning and request reduced size or plain-text upload
- No matches found: suggest broadening location/salary/job-title filters

## Acceptance criteria
- Each flow has clear CTAs and fallback paths
- Flows are represented both in textual steps and clickable mockups (next step)

# Wireframes — AI Job Application Assistant

This file contains low-fidelity wireframes and notes for the major screens.

## Screens

1. Input / Setup Form
   - Fields: Full name, Location (city, remote preference), Desired salary range, Preferred job titles (multi-select), Job types (Remote/Onsite/Hybrid), Resume upload (PDF/DOCX)
   - CTA: "Find Matches"

   ASCII sketch (low-fi):

   +-----------------------------------------+
   | AI Job Application Assistant            |
   | [Logo]                                  |
   |-----------------------------------------|
   | Name: [______________]                  |
   | Location: [______________] [Remote v]   |
   | Desired Salary: [min] - [max]           |
   | Job Titles: [tag1, tag2, ...] (+ add)   |
   | Job Types: [ ] Remote  [ ] Onsite  [ ] Hybrid |
   | Resume: [Choose file]  (PDF/DOCX)       |
   | [Find Matches]                          |
   +-----------------------------------------+

2. Results Dashboard (compact list + details panel)
   - Header with search filters (sort by score, salary, location)
   - Left: List of job matches with score badge and colored highlight (Red/Yellow/White)
   - Right: Detail panel showing job description, company, apply link, resume tips

   ASCII layout:
   +-----------------+--------------------------------+
   | Filters / Search| Job Detail                      |
   | [filters]       | Title:                          |
   |                 | Company:                        |
   |                 | Score: [85] (Green)             |
   | Job List        | Description: ...                |
   +-----------------+--------------------------------+

3. Application Tracker
   - Columns: Job Title | Company | Applied Date | Status | Notes | Actions
   - Status tags: Applied, Interview, Offer, Rejected, Pending

## Component notes
- Use clear call-to-action colors for primary actions
- Score color mapping: Green (>=80), Yellow (50-79), Red (<50)
- Provide inline resume improvement tips in detail panel

## Next steps
- Convert these low-fidelity wireframes to clickable mockups (Figma/Sketch)
- Add high-fidelity visual styles in `frontend/README.md` or `frontend` mockup files

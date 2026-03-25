# Engineering Impact Plan

## Goal

Build a local, offline-first pipeline that fetches GitHub pull request data for `PostHog/posthog`, scores engineers over the last 90 days, and writes a frontend-ready `dashboard.json`.

## Constraints

- No FastAPI in the critical path
- Keep code simple and human-readable
- Preserve the existing merged PR JSON shape as closely as possible
- Use GitHub GraphQL first for speed
- Use REST only where it is the cleanest tradeoff, mainly PR files for exact area extraction

## Output Targets

1. `backend/data/pull_requests.json`
   - Raw fetched data
   - Includes merged PR records and summary counts for true merge-rate calculation
2. `backend/data/dashboard.json`
   - Final scored payload for the frontend

## Fetch Design

### GraphQL-first ingestion

Use repository PR pagination instead of search where possible.

### Tier 1: GraphQL PR metadata

For merged PRs, fetch in paginated GraphQL passes:

- number
- title
- url
- author login and avatar
- createdAt
- mergedAt
- mergedBy
- additions
- deletions
- changedFiles
- reviews
- review requests or participants only if needed later

Stop paging once a page is fully older than the 90-day cutoff.

### Tier 2: REST file metadata

Use REST only for PR files so we can derive exact `top_level_areas`.

- `GET /repos/{owner}/{repo}/pulls/{number}/files`

This gives us a hybrid model:

- GraphQL for PR metadata and reviews
- REST for file paths only

### True merge-rate support

We need a real KPI, so the fetch step must also count closed PRs in the same 90-day window.

Recommended definition:

- denominator: PRs closed in the last 90 days
- numerator: PRs merged in the last 90 days

This keeps the KPI aligned with the merged subset used for scoring.

## Raw Fetch Output

`backend/data/pull_requests.json` should contain:

- `summary`
  - repo
  - windowDays
  - generatedAt
  - closedPrs
  - mergedPrs
  - graphqlPagesFetched
  - restFileRequests
- `pullRequests`
  - array of merged PRs with the existing shape:
    - number
    - title
    - url
    - author_login
    - author_avatar
    - created_at
    - merged_at
    - merged
    - changed_files_count
    - top_level_areas
    - reviews

## Scoring Model

### Weighted metrics

- merged PRs: `0.35`
- meaningful merged PRs: `0.45`
- reviews given: `0.20`

Normalize only these three ranking metrics.

### Supporting metrics

- unique areas touched
- unique authors reviewed
- median time to merge in hours

Display these raw.

### Meaningful PR rule

Keep this simple and explainable:

- +1 if `changed_files_count >= 5`
- +1 if `len(top_level_areas) >= 2`
- +1 if `review_count >= 2`
- meaningful if total score is at least 2

## Dashboard Output

`backend/data/dashboard.json` should match the expected frontend contract:

- `summary`
- `topEngineers`
- `engineerDetails`
- `methodology`

The ranking should include only the top 5 engineers, with detailed evidence and rationale for each.

## Representative PR selection

For each ranked engineer, choose 3 representative PRs using a simple depth heuristic based on:

- changed files
- area breadth
- review count

Each PR should include a short `whyItMatters` explanation.

## Validation

After implementation:

1. Run a quick GitHub auth check
2. Run the fetch script
3. Run the dashboard builder
4. Validate that request usage is meaningfully lower than the old REST-heavy flow by logging:
   - GraphQL pages fetched
   - REST file requests
   - merged PRs processed

## Implementation Order

1. Refactor `backend/app/github_client.py` for GraphQL-first ingestion
2. Rewrite `backend/app/fetch_pull_requests.py`
3. Implement `backend/app/schema.py`, `backend/app/utils.py`, and `backend/app/scoring.py`
4. Add a dashboard builder script
5. Validate the end-to-end output

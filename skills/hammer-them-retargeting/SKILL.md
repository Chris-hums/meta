---
name: hammer-them-retargeting
description: Execution framework for building, launching, and troubleshooting a "Hammer Them" content retargeting campaign in Meta Ads Manager for a weekly cold webinar funnel (registration → webinar → sales call). Use this whenever the user mentions "Hammer Them," webinar retargeting, backend selling systems, pre-framing leads before a sales call, one-ad-per-ad-set structures, 3-second video view exclusions, or asks how to stop salespeople from having to sell on calls. Also use it to diagnose an underperforming webinar/call show rate or close rate, to size budget/audiences for a webinar funnel retargeting campaign, or to review an existing Meta campaign against this playbook's structure (ABO vs CBO, bid caps, quadrant content mix, frequency targets). Trigger even if the user just says "set up the hammer them" or "why isn't my webinar retargeting working" without naming the framework explicitly.
---

# Hammer Them Retargeting (Webinar Funnel)

## What this is

The Hammer Them is a paid Meta Ads content-retargeting campaign that runs
between the two leak points of a **weekly cold webinar funnel**:
registration → webinar attendance, and call booking → sales call. It is one
of four backend selling systems (the other three — confirmation page
breakout videos, a value-dense email sequence, and setter/SDR outreach —
are free and should run alongside it). The point isn't more leads; it's
pre-framing the leads already in the pipe so thoroughly that every
question, objection, and expectation is handled before the sales call. Done
right, the salesperson stops selling and starts collecting — "turn
salespeople into cashiers."

Use this skill to: answer questions about the strategy, walk a user
step-by-step through setting it up for their specific funnel, or diagnose
an existing campaign against the IF/THEN logic and pitfalls below. Where a
detail depends on the user's numbers (registrant volume, audience size,
content inventory, sales-cycle length), ask rather than assume — the right
setup branches hard on those inputs.

## The two windows

Everything in this framework hangs off two distinct gaps where cold
webinar prospects go cold:

| | Window 1: Registration → Attendance | Window 2: Call Booking → Sales Call |
|---|---|---|
| Starts | Opt-in form submission | Call booked (during or after webinar) |
| Ends | They attend the webinar | They show up to the call |
| Typical length | 1–7 days (avg 3–5 for a weekly live webinar) | 1–7 days |
| Purpose | Keep registrants from forgetting why they signed up | Pre-frame bookers so they arrive sold, not skeptical |
| Metric it moves | Webinar show rate (target 30%+ cold) | Call show rate (target 70%+), close rate (target 35–40%+) |

Window-shape logic:
- Live weekly webinar → Window 1 averages 3–5 days.
- Automated/evergreen webinar → Window 1 shrinks (same/next-day); less critical.
- Automated webinar + call booked immediately after → Window 1 nearly collapses; put budget/content into Window 2.
- Calls booked live in-webinar → Window 2 starts the moment the webinar ends.
- Calls booked via post-webinar email → Window 2 starts at the booking-page submission; track via a website custom audience on that confirmation URL.

## How to use this skill

1. **New setup** — ask for the inputs that change the plan (see below), then
   walk the user through `references/campaign-setup.md` (objective, ABO vs
   CBO, bid strategy, audiences, the one-ad-per-ad-set structure with
   3-second exclusions, placements), `references/content-quadrants.md`
   (what content to produce and in what mix), and
   `references/frequency-budget-timing.md` (frequency targets, starting
   budget, scaling, and the free layers it must run alongside). Finish with
   `references/execution-checklist.md`, in order. If the Window 2 (call
   booker) audience is or could be sourced from a server-side automation
   (a booking webhook, CRM, or workflow tool) rather than a browser pixel
   on a confirmation page, see `references/capi-server-side-integration.md`
   — it's the stronger pattern and worth defaulting to over the pure
   URL-based version in `campaign-setup.md`.
2. **Diagnosing an existing campaign** — start from
   `references/troubleshooting-and-kpis.md`: the 11 "things to look out
   for" catch the most common ways this breaks silently (Audience Network
   creeping back on, exclusions not populated, content that's diverse in
   format but not message, subtracting from a working campaign), and the
   measurement section gives the IF/THEN logic for what a stalled or
   partially-moving metric actually means.
3. **Quick questions** — answer directly from this file and the IF/THEN
   tables in the references; don't make the user read the whole framework
   for one number.
4. **Building it programmatically via the Marketing API** (not just
   walking a human through Ads Manager) — see
   `references/marketing-api-build-notes.md` for confirmed request shapes
   (Custom Audience rule JSON, ABO campaign creation, the 3-second
   exclusion audience pattern) and the batch-endpoint approach for
   creating many ad sets/ads at once without burning rate limit.

Key inputs to get from the user before sizing anything:
- Weekly registrant volume (drives campaign count and starting budget — see `references/campaign-setup.md` and `references/frequency-budget-timing.md`)
- Webinar type: live weekly vs. automated/evergreen, and whether calls book in-webinar or via email follow-up (drives window shape above)
- Content inventory: how many short-form pieces exist, any long-form (podcasts/interviews 10+ min)? (25 minimum per campaign, 30–50 ideal — see `references/content-quadrants.md`)
- Front-end cold acquisition spend, if any (Hammer Them budget is typically 10–20% of it)
- Any known negative online reputation (Reddit threads, bad reviews) — changes the objection-content requirement

## Non-negotiables (the load-bearing rules)

These are the parts of the framework that are easy to "optimize" away and
shouldn't be:

- **One ad per ad set, minimum 25 ad sets per campaign.** Never combine
  multiple pieces of content in one ad set.
- **ABO, not CBO.** CBO concentrates spend on 1–3 ad sets and starves the
  rest, which breaks the forced-distribution mechanism the whole structure
  depends on.
- **Bid caps, not cost caps.** Engagement objectives have no cost-per-result
  anchor for a cost cap to work against.
- **Audience Network off, always** — and re-check it after every edit or
  duplication; Meta's UI can silently re-enable it.
- **Objection content (Quadrant 4) is the heaviest slice — 40% minimum**
  for cold webinar traffic. If there's no objection-handling content yet,
  don't launch; generate it first.
- **Never subtract content from a working campaign.** If show rate or close
  rate improved, one specific piece may be carrying the lift — pulling it
  to "clean up" is the single most common mistake people make after early
  success.
- **The campaign runs continuously**, not paused between weekly webinars —
  there's always someone in Window 1 or Window 2.

Full detail, exact numbers, and every IF/THEN branch live in
`references/`. Read the relevant file before advising on that part of the
setup rather than relying on memory of the summary above.

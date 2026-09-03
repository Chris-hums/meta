# Building It via the Meta Marketing API (Confirmed Mechanics)

Notes from actually provisioning a Hammer Them window via the Marketing API
(Graph API v21.0) against a live ad account, rather than clicking through
Ads Manager. Useful if a future session has a System User access token
with `ads_management` scope and is asked to build/replicate a window
programmatically instead of walking a human through the UI.

## Discovering the account and pixel

- `GET /me` on the token identifies it (name/id) — confirm it's the
  expected system user before doing anything else.
- `GET /me/adaccounts?fields=id,name,account_status,currency` lists every
  ad account the token can reach. A business can run several
  (`act_...`) — don't assume which one owns the pixel in question.
- `GET /act_<id>/adspixels?fields=id,name` lists the pixels owned by a
  specific ad account — use it to confirm which account a known pixel ID
  belongs to before creating anything there.
- `GET /me/permissions` lists granted scopes on a user access token. For a
  System User token this can come back differently; `/me` succeeding plus
  `/me/adaccounts` returning real accounts is a good enough liveness check.

## Reading what already exists before building

Before creating anything, `GET /act_<id>/customaudiences` and
`GET /act_<id>/campaigns` (and each campaign's `/adsets` and `/ads`).
This account may already have a Hammer Them window built — reading the
existing structure gives you the *exact* working `rule` JSON, targeting
shape, bid strategy, and optimization goal this business actually runs,
which beats reconstructing it from the abstract framework in
`campaign-setup.md`. Mirror what's live and proven rather than the
generic defaults when both are available — e.g. this account runs
`bid_strategy: LOWEST_COST_WITHOUT_CAP` with
`optimization_goal: OFFSITE_CONVERSIONS` against a `PURCHASE` custom
event on the pixel (optimizing retargeting spend toward purchases, not
just impressions/engagement) rather than the plain Engagement-objective
bid-cap setup the general framework describes. Both are legitimate; match
whichever this specific account already runs for consistency.

## Custom Audience from a pixel event (validated request)

```
POST /act_<AD_ACCOUNT_ID>/customaudiences
name=<name>
description=<description>
rule={"inclusions":{"operator":"or","rules":[{"event_sources":[{"type":"pixel","id":"<PIXEL_ID>"}],"retention_seconds":<seconds>,"filter":{"operator":"and","filters":[{"field":"event","operator":"eq","value":"<EVENT_NAME>"}]}}]}}
access_token=<token>
```

- Do **not** pass `subtype` on creation in v21.0 — the API rejects it
  (`error_subcode 1870053`, "not supported in the current API version").
  It's inferred from the rule and comes back correctly on read (e.g.
  `"subtype": "WEBSITE"`).
- `retention_seconds` is just days × 86400 (14 days = 1209600).
- `operator: "eq"` for the event filter (not `"="`) — confirmed from a
  live, populated audience already running in the account.
- A newly created audience's `approximate_count_lower_bound` sits at the
  platform's floor (e.g. 20) until the underlying event actually fires
  for real people — this is expected for a not-yet-live or freshly wired
  server-side event and isn't itself a sign of a problem.
- The same `event_sources`/`filter` pattern with `"type": "page"` and
  `field: "video_id"` + `field: "video_view_time", operator: "gte", value: 3`
  is exactly the 3-second video-view exclusion audience from
  `campaign-setup.md` Step 3 — confirmed against ~27 live examples in one
  account, one per piece of content, named `3sec — [description]`.

## Campaign creation (ABO)

```
POST /act_<AD_ACCOUNT_ID>/campaigns
name=<name>
objective=<e.g. OUTCOME_SALES>
buying_type=AUCTION
special_ad_categories=[]
is_adset_budget_sharing_enabled=false
status=PAUSED
```

`is_adset_budget_sharing_enabled` is **required** once you're not passing
a campaign-level budget — omit it and creation fails
(`error_subcode 4834011`). Set it `false` for a true ABO setup (no
campaign budget optimization/sharing), matching the "ABO, not CBO" rule
in `campaign-setup.md`.

## Ad sets and ads at scale — use the batch endpoint

Replicating a 25–50-ad-set structure one call at a time is slow and
burns rate limit. Use the Graph API batch endpoint instead:

```
POST https://graph.facebook.com/v21.0/
access_token=<token>
batch=[{"method":"POST","relative_url":"act_<id>/adsets","body":"<urlencoded ad set params>"}, ...]
```

Up to ~50 sub-requests per batch call. Build the array of ad set bodies
in one pass (mirroring an existing window's targeting/budget/bid config,
swapping in the new window's `custom_audiences` and the matching
`excluded_custom_audiences`), submit one batch call, then read back the
new ad set IDs from the batch response (`json.loads(response['body'])['id']`
for each item, in the same order submitted) to build the follow-up ad
batch.

**Creative is reusable — don't re-upload.** An ad's `creative` is just a
reference (`{"creative_id": "<id>"}`); the same creative object can be
attached to a new ad in a different ad set or campaign without
recreating it. If a new window is launching with the *same* content
pool as an existing one (e.g. reusing Window 1's videos for a freshly
wired Window 2 before window-specific content exists), pull each
existing ad's `creative.id` and reuse it directly — `GET .../ads?fields=id,name,adset_id,creative`
on the source campaign gives you the full adset→creative mapping in one
call.

**Build everything `status: PAUSED`** (campaign, ad sets, and ads) when
provisioning programmatically and spend approval hasn't explicitly been
given — it creates the full structure with zero spend risk, and a human
reviews and flips it active. Note that a paused *campaign* means nothing
spends regardless of ad set/ad status, but setting all three levels to
PAUSED is cheap insurance and avoids any ambiguity when someone reviews
the account later.

## Field-expansion gotcha

`GET .../adsets?fields=...,targeting{...}` or `...,creative{id}` (curly-brace
sub-field syntax) silently returned nothing for `targeting`/`creative` in
testing — the field just didn't come back. Requesting the plain field
name (`targeting`, `creative`) without sub-selection returned the full
nested object correctly. If a nested-field expansion comes back empty,
retry with the bare field name before assuming the object has no data.

## Ongoing frequency monitoring (n8n + a scheduled check-in)

To watch frequency on running Hammer Them campaigns without re-deriving
Marketing API calls each time: build a small n8n workflow (Manual Trigger
→ HTTP Request per campaign hitting `/{campaign_id}/insights?level=adset&fields=adset_name,frequency,reach,impressions,spend&date_preset=last_3d`,
using the stored Meta credential → a Code node that aggregates
avg/min/max frequency and flags ad sets outside the 10–25 range) and
invoke it on a schedule via `mcp__n8n__execute_workflow` (executionMode
`manual`, which runs the current saved version regardless of whether the
workflow itself is published/active — no need to activate it in n8n at
all if the invocation is always external).

Two gotchas hit while building this:
- **`setNodeCredential` / `addNode` with `credentials` both failed** to
  attach an `httpQueryAuth` generic-auth credential to an `httpRequest`
  node via the n8n MCP server's `update_workflow` tool, even though the
  exact same node type + credential type combination already works fine
  when configured by hand in the n8n UI (and even after removing/re-adding
  the node with credentials inlined). Treat this as a known gap in that
  MCP tool for this credential type — don't burn time retrying it several
  ways. The workaround is a one-time manual step: open the workflow in
  the n8n UI and pick the credential from each HTTP Request node's
  credential dropdown directly.
- **A Claude Code Remote Routine (`create_trigger`) that self-binds to
  the current session warned "this trigger stores no MCP connectors, so
  the sessions it fires will run without connector tools."** In testing
  this appeared to refer to claude.ai-style OAuth connectors (Gmail,
  Slack-as-connector — the set `ListConnectors` returns), not
  environment-configured MCP servers like n8n (which don't show up in
  `ListConnectors` at all and are wired into the environment itself). A
  self-bound Routine firing into the *same* session should still have
  n8n available. Unconfirmed until a real firing is observed, though —
  if a scheduled check-in comes back unable to reach n8n tools, that's
  the thing to revisit, and the fallback is moving the schedule into n8n
  itself (its own Schedule Trigger node) with delivery straight to Slack
  instead of round-tripping through a Claude session at all — more
  robust regardless, since it doesn't depend on any Claude session being
  reachable.

## Content-reuse caveat

Reusing an existing window's content pool to stand up a new window fast
(get the audience/campaign live today) trades off against
`content-quadrants.md`'s guidance that content should be
window-specific — Window 2 (call bookers) ideally runs call-specific
objection/expectation content, not webinar-attendance content. Treat a
reused-content build as a functional placeholder to get retargeting
flowing immediately, and flag it explicitly as a follow-up: swap in
window-specific content (per the quadrant weighting) once it exists,
rather than leaving the reused set as permanent.

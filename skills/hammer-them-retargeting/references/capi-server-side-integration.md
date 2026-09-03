# Server-Side CAPI Events for Window 2 (Call Bookers)

An alternative to the URL-based website custom audience described in
`campaign-setup.md` Step 2 for Window 2. Instead of relying on the Meta
Pixel firing in-browser on a booking confirmation page (which breaks under
ad blockers, iOS tracking restrictions, or a booking tool that doesn't
load your pixel), fire the "booked a call" event **server-side** from
whatever automation already handles the booking — the calendar webhook,
the CRM, the workflow tool — straight to Meta's Conversions API.

This is generally the *better* source for Window 2 in a modern setup: it's
not dependent on the browser, it's not blockable, and it lets you hash and
send exact identity data (email, phone, name) rather than relying on
cookie-based matching.

## The pattern

1. **Filter before you send.** Whatever triggers the event (a Calendly
   webhook, a Calendly/Acuity/HubSpot booking, etc.) should already be
   doing real-sales-call detection — same logic that gates your other
   booked-call automations (Slack alerts, CRM rows). Route the CAPI event
   off that same filtered node so test bookings, support calls, and
   onboarding calls never enter the Window 2 audience. Sending noise into
   this audience is worse than sending nothing — it dilutes targeting with
   people who were never actually sales prospects.

2. **Normalize and hash identity fields.** Meta requires SHA-256 hashes,
   lowercase where applicable, no extra whitespace:
   - `em` — email, trimmed + lowercased before hashing
   - `ph` — phone, digits only; for a 10-digit US number, prepend country
     code `1` before hashing (adjust if the business isn't US-only)
   - `fn` / `ln` — first/last name, lowercased, split from a full-name
     field

3. **Send the event.**
   ```
   POST https://graph.facebook.com/v21.0/{PIXEL_ID}/events
   {
     "data": [{
       "event_name": "Schedule",
       "event_time": <unix timestamp>,
       "action_source": "system_generated",
       "user_data": { "em": ["<hash>"], "ph": ["<hash>"], "fn": ["<hash>"], "ln": ["<hash>"] },
       "custom_data": { ... whatever's useful for later segmentation, e.g. lead source, rep assigned ... }
     }]
   }
   ```
   - `event_name: "Schedule"` is the right choice for "booked a call" — it's
     one of Meta's standard events, which keeps it eligible for standard
     optimization/reporting rather than requiring a custom-conversion setup.
   - `action_source: "system_generated"` is correct for a fully backend
     trigger with no direct user browser action in the same request (as
     opposed to `"website"` or `"phone_call"`).
   - Auth: use a **stored credential** for the access token (e.g. an HTTP
     query-auth credential in your automation tool), never a token
     hardcoded into the workflow — it's a long-lived system-user token and
     leaks are hard to walk back.

4. **Verify before building the audience.** Book a real or test call, then
   check **Meta Events Manager → Pixel → Test Events** to confirm the
   `Schedule` event lands and check its match-quality score. Do this
   before building the Custom Audience in Ads Manager — a low match score
   means fewer people actually get matched into the audience, and it's
   worth fixing the hashing/normalization first.

5. **Build the Custom Audience in Ads Manager** from the `Schedule` event
   once it's verified, same retention logic as the URL-based version (14
   days default, 7 if calls happen within 3 days of booking).

## What this does and doesn't give you

- **Gives you:** identity-based audience matching (email/phone/name
  hashes) good enough to build the Window 2 retargeting audience the
  Hammer Them needs.
- **Doesn't give you, unless you add it:** `fbc`/`fbp` (click ID / browser
  ID). Without capturing `fbclid` from the ad click and threading it
  through the landing page → booking tool → into this event, Meta can't
  attribute a given booking back to the specific ad/campaign that drove
  it. That's an ad-attribution/optimization gap, not an audience-building
  one — the Hammer Them retargeting campaign works fine without it. Only
  chase this if the goal shifts to optimizing the front-end acquisition
  campaign off booked-call conversions, not just retargeting people who
  already booked.
- **If you later add browser-side Pixel events for the same action**
  (e.g. a confirmation-page pixel fires *in addition* to this
  server-side event), pass a shared `event_id` on both so Meta
  deduplicates them instead of double-counting the same booking.

## Reference implementation

n8n workflow `CC - Booked Call Alert (Webhook)` — built off a Calendly
webhook that already logs booked calls to Slack/Sheets/Supabase/CRM. Two
nodes hang off its existing booking-row/filter node:
- `Meta CAPI - Build Payload` (Code node) — normalizes, hashes, and shapes the payload as above
- `Meta CAPI - Send Event` (HTTP Request node) — POSTs it, auth via a stored generic query-auth credential holding the CAPI access token

Worth copying this pattern (filtered trigger → hash/build payload → POST
with a stored credential) for Window 1 too, if the webinar registration
flow has an equivalent server-side hook to fire off.

# Campaign Setup: Objective, Structure, Audiences, Ad Sets, Placements

Covers Steps 1–4 of the framework. Read `content-quadrants.md` for what
content to put in the ad sets built here, and
`frequency-budget-timing.md` for budget sizing.

## Step 1: Campaign objective and structure

**Objective**
- Short-form content (reels, shorts, under 3 minutes) → **Engagement** objective.
- Long-form content (podcasts, full interviews, 10+ min clips) exists too → add a **second, parallel** campaign with **Video Views** objective for long-form only.
- All content is short-form → Engagement only, one set of campaigns.

**Campaign count** — one campaign per window, two total for a standard weekly cold webinar funnel:
- Campaign A: "Hammer Them — Webinar Registrants" (engagement, Window 1 audience)
- Campaign B: "Hammer Them — Call Bookers" (engagement, Window 2 audience)
- If long-form content exists → Campaign C: "Hammer Them — Long Form" (video views, both audiences combined)

**IF/THEN on campaign count by weekly registrant volume:**
| Weekly registrants | Structure |
|---|---|
| Under 100 | Consolidate both windows into ONE campaign, one combined warm audience. Two campaigns at this volume underperform from insufficient audience size each. |
| 100–500 | Two campaigns (Window 1 / Window 2 separately), modest budgets ($10–30/day each). |
| 500+ | All three campaigns if long-form exists, else two. Budget scales proportionally. |

**Budget type: ABO, not CBO.** Ad Set Budget Optimization, always. Campaign
Budget Optimization concentrates spend on 1–3 ad sets and starves the rest
— it destroys the forced-distribution mechanism that makes
one-ad-per-ad-set work (see Step 3 below). This holds even when Meta's UI
nudges toward CBO.

**Bid strategy: bid caps, not cost caps.** Engagement objectives have no
cost-per-result to anchor a cost cap against — cost caps only make sense on
direct-response objectives (purchase, lead, sales). If the platform forces
a minimum bid, set the cap at that minimum and manage frequency through
budget instead.

## Step 2: Audience targeting

**Window 1 — Webinar Registrants** (website custom audience)
- Source: registration thank-you / confirmation page URL
- Retention: 14 days default (full weekly cycle)
  - Daily/twice-weekly webinars → 7 days
  - Monthly webinars → 30 days

**Window 2 — Call Bookers** (website custom audience)
- Source: call-booking confirmation/thank-you page URL (Typeform, Calendly, etc.)
- If booking happens inside the webinar platform with no separate URL → build the audience from a pixel event (Lead or CompleteRegistration) instead
- Retention: 14 days default; 7 days if calls happen within 3 days of booking
- **Stronger alternative: a server-side Conversions API (CAPI) event fired straight from the booking automation**, instead of relying on the Pixel loading on a confirmation page. See `capi-server-side-integration.md` for the pattern (SHA-256 hashed identity match, event filtering, what it does and doesn't give you) and a working n8n reference implementation.

**Supplementary audiences (add to both windows):**
- 25%+ video viewers of a front-end ad video
- Page engagers (IG/FB engagement in last 30 days)
- Email list upload, if the CRM captures emails at opt-in and the list is current
- 50%+ replay watchers, if replays are available — these are the hottest pre-framed leads and can run on a smaller budget slice since they need less hammering

**IF/THEN on audience size:**
| Total warm audience (both windows) | Structure |
|---|---|
| Under 1,000 | Consolidate into one combined audience, one campaign. |
| 1,000–10,000 | Two campaigns fine; $20–50/day each. |
| 10,000+ | Two campaigns minimum, three with long-form; budget scales up. |

- Large registrant base (10,000+) but low call-booking volume (under 100/week) → weight budget toward Window 2 (call bookers) — higher intent, more lift per dollar there.

**Exclusions:**
- Always exclude existing customers/purchasers from both warm audiences.
- Running a parallel cold direct-response acquisition campaign → exclude the Hammer Them warm audience from it to prevent overlap.
- Someone is in both Window 1 and Window 2 (registered AND already booked) → exclude Window 2 (call bookers) from the Window 1 campaign. They're further down the funnel; give them the higher-intent Window 2 content, not Window 1's.

## Step 3: Ad set structure — one ad per ad set

**Core rule, non-negotiable:** every ad set contains exactly ONE ad. No
exceptions, no multi-ad ad sets.

**Ad set count:**
- Minimum 25 ad sets (25 pieces of content) per campaign.
- Ideal 30–50 per campaign.
- Running Window 1 + Window 2 as two campaigns → need 25–50 *unique* pieces per campaign, i.e. 50–100 total minimum. Don't launch under 25 per campaign — generate more content first if short.

**Audience targeting inside each ad set:** every ad set in a campaign uses
the *exact same* warm audience from Step 2. The only thing that varies
between ad sets is the exclusion.

**The 3-second video view exclusion mechanism (critical).** Each ad set
excludes a 3-second video-view audience of the specific video inside that
ad set. Build:
1. Meta Ads Manager → Audiences → Create Audience → Custom Audience → Video
2. Select the specific video for that ad set
3. Threshold: "3 second views"
4. Name convention: `3sec — [Video Name/Description]`
5. Repeat for every piece of content in the campaign
6. On each ad set, add the matching 3-second audience under Exclusions

**Result:** once someone watches 3 seconds of a given piece, they never see
it again — they cycle through the other 24–49 pieces instead. This forced
distribution is what makes sure every piece of content actually reaches
people instead of the platform hammering the same one repeatedly.

**IF/THEN on exclusions:**
- Static image (no video) → exclude via a website custom audience of the linked landing page, or a post-engagement audience.
- Carousel → post-engagement audience as the exclusion.
- Video posted only as an IG reel (not cross-posted to FB) → the 3-second audience only populates from IG data; restrict that ad set to IG placements (Step 4).
- 3-second audience has fewer than 20 people at launch → it may not be selectable as an exclusion yet. Launch anyway; add the exclusion once it populates (typically 24–48 hrs). Set a reminder to check back at 48 hours.
- Two campaigns with different content in each → build separate 3-second audiences per campaign's content; don't reuse an exclusion across campaigns unless the same video appears in both.

## Step 4: Placements

**Defaults:**
- Content cross-posted to FB and IG → Automatic Placements (or manually: FB Feed, IG Feed, IG Reels, IG Stories).
- IG-only content → remove Facebook placements entirely; IG Feed, IG Reels, IG Stories only.
- **Always remove Audience Network — no exceptions, and re-check after every campaign edit.** It serves content on low-quality third-party apps and generates junk engagement.

**IF/THEN by content format:**
| Content | Placements |
|---|---|
| Reel with IG-only licensed audio | IG placements only |
| 9:16 vertical (reel/short) | IG Reels + IG Stories; don't force into FB Feed (displays poorly) |
| 16:9 horizontal (YouTube/podcast clip) | FB Feed + IG Feed; exclude IG Reels/Stories (horizontal performs poorly there) |
| 1:1 square | FB Feed, IG Feed, IG Reels |

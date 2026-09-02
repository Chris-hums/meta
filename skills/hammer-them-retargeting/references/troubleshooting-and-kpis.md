# Things to Look Out For, Measurement, and KPIs

Flag anything matching the list below before proceeding with setup or
scaling. Use the measurement section to diagnose a campaign that isn't
moving the numbers it should.

## Things to look out for

1. **Related media / auto-generated content.** Meta sometimes auto-pulls
   "related media" into ad sets. Check every ad set after creation and
   after every duplication/edit; remove anything auto-pulled that wasn't
   intentionally placed — it dilutes the one-ad-per-ad-set structure and
   breaks forced distribution.

2. **Audience Network.** Confirm it's OFF, every time, without exception.
   Meta can re-enable it on duplication or edits.

3. **Learning phase.** ABO with 25+ ad sets at low budget means each ad set
   may get very little spend and stay in learning phase — this is expected
   and fine for a content/engagement campaign. Do **not** switch to CBO to
   escape it; the forced distribution from one-ad-per-ad-set matters more
   than exiting learning phase. This isn't a problem the way it would be on
   a purchase campaign.

4. **Exclusion population delay.** 3-second video-view audiences take
   24–48 hours to populate after an ad goes live. During that window the
   exclusion isn't active yet and people may see the same piece twice —
   acceptable for the first 48 hours. After that, verify every exclusion
   is active (set a reminder).

5. **Content quality vs. quantity.** 50 pieces that all say the same thing
   is 1 piece of content in 50 formats. Audit for *message* diversity, not
   just format diversity, before loading a campaign.

6. **Email deliverability.** Open rates below 40% on the 3–6/day sequence
   usually mean deliverability (domain reputation, SPF/DKIM/DMARC, sender
   burnout from over-sending to webinar lists) — not content quality. Signs
   of a burned domain: landing in spam/promotions, open rates that were
   50%+ dropping to 20% or below. Fix: rotate to a fresh sending domain,
   verify authentication records, reserve the primary domain for warm
   sequences and use a secondary for broadcast blasts.

7. **Subtraction warning.** If the campaign is working (show rate, close
   rate, or sales-team-reported lead quality improved), do **not** remove
   pieces to "optimize" — one specific video may be carrying the lift, and
   removing it can collapse the improvement. Add more content if needed;
   never pull pieces from a working system. This is the most common
   mistake people make after early success.

8. **Placement audit after changes.** Every duplication, edit, or budget
   adjustment is an opportunity for Meta's UI to silently re-enable
   placements or Audience Network you'd turned off — re-audit every time.

9. **Negative online reputation (cold-webinar specific).** If the business
   or personal brand has negative search results (Reddit threads, bad
   reviews, Trustpilot, Ripoff Report), cold registrants *will* search
   between registration and the call. Proactively address known issues in
   Quadrant 4 content rather than let the prospect find it first, and add
   a due-diligence video to the confirmation page that frames it honestly.
   Don't create a Trustpilot profile that doesn't already exist — it just
   opens a new surface for negative reviews.

10. **Audience overlap between windows.** Someone in both Window 1 and
    Window 2 audiences should only be in Window 2 — exclude call bookers
    from the Window 1 campaign. They're further down the funnel and need
    call-specific objection content, not webinar-specific.

11. **Webinar fatigue on warm audiences.** Running warm-audience webinars
    (monthly, for existing leads) alongside the cold funnel? Don't target
    the same warm audience with the Hammer Them for both simultaneously —
    warm audiences fatigue faster. Run separate campaigns or exclude warm
    webinar registrants from the cold Hammer Them.

## Measurement and KPIs

**Record these baselines before launch:**
- Webinar show rate (% of registrants who attend)
- Call show rate (% of booked calls that show up)
- Call close rate (% of shown-up calls that close)
- Sales team qualitative feedback ("are the leads pre-framed or cold?")
- Email open rate and click rate

**Leading indicator — check first, within 7 days.** The first sign the
Hammer Them is working is *not* show rate — it's salespeople reporting
leads are higher quality and easier to close. Check in with closers at day
7. If they say "leads are so good now" / "these people already know what
we do" → it's working; don't change anything yet.

**Secondary indicators — check at 14 days:**
- Webinar show rate → target upward toward 30%+
- Call show rate → target upward toward 70%+
- Call close rate → target upward toward 35–40%+
- Email open rate → target 40%+ sustained

**IF/THEN measurement logic:**
- Salespeople say leads are better but show rate hasn't moved → keep
  running. Show rate is a lagging indicator that follows lead-quality
  improvement — the framing is working even if this metric lags.
- Show rate improved but close rate didn't → content is getting people to
  show up but not pre-framing them to *buy*. Audit for objection content
  (Quadrant 4) — likely missing or under-weighted.
- Neither improved after 14 days → audit content against the four
  quadrants; the problem is content quality/mapping, not budget or
  frequency. Check specifically: are the objection pieces addressing the
  objections the sales team *actually* hears on calls, or generic ones?
- Show rate improved but webinar attendance didn't → Window 2 (call show
  rate) is working but Window 1 content may not be addressing
  webinar-attendance-specific objections (e.g. "I don't have time for a
  90-minute webinar," "I'll just watch the replay," "I already know this
  stuff") — audit Window 1 content specifically.

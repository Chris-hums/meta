# Execution Checklist (Follow in Order)

Walk through this in order when setting up a new Hammer Them campaign.
Each numbered item links back to the reference file with the full detail
if a decision is needed.

1. Confirm this is a **weekly cold** webinar funnel (not warm-audience, not evergreen — if different, adjust the window shapes per `../SKILL.md#the-two-windows` first).
2. Confirm campaign objective is Engagement (add Video Views for long-form). See `campaign-setup.md`.
3. Confirm **ABO**, not CBO.
4. Confirm **bid caps**, not cost caps.
5. Build Window 1 warm audience: website custom audience from the webinar registration confirmation page URL, 14-day retention.
6. Build Window 2 warm audience: website custom audience from the call-booking confirmation page URL, 14-day retention (or pixel-event-based if booking happens inside the webinar platform).
7. Add supplementary audiences: 25%+ video viewers, page engagers, email list upload, 50%+ replay watchers (if replays exist).
8. Exclude existing customers/purchasers from both audiences.
9. Exclude Window 2 (call bookers) from the Window 1 campaign to prevent overlap.
10. Confirm audience size and set budget per registrant volume (`frequency-budget-timing.md`, Step 7).
11. Create Campaign A: "Hammer Them — Webinar Registrants" (Window 1), 25–50 ad sets.
12. Create Campaign B: "Hammer Them — Call Bookers" (Window 2), 25–50 ad sets.
13. If long-form content exists, create Campaign C: "Hammer Them — Long Form" (video views objective).
14. Apply the same warm audience to every ad set within each campaign.
15. Create a 3-second video-view audience for every piece of content in every campaign.
16. Apply each 3-second view audience as the exclusion on its matching ad set.
17. Confirm Audience Network is OFF on every campaign.
18. Confirm placements match content format (9:16 → reels/stories, 16:9 → feed only, 1:1 → feed/reels).
19. Audit all content against the four quadrants (10% questions / 20% second-layer / 30% expectations / 40% objections) — `content-quadrants.md`.
20. Confirm objection content (Quadrant 4) is the heaviest slice — 40% minimum for cold webinar traffic.
21. Confirm the email sequence is running in parallel (3–6/day depending on window length).
22. Confirm the confirmation page has breakout videos (the free layer complementing the Hammer Them).
23. Confirm setter/SDR outreach is running (text + call between booking and call).
24. Record baseline metrics: webinar show rate, call show rate, close rate, email open rate, sales team feedback.
25. Launch campaigns.
26. Wait 48 hours for 3-second view exclusion audiences to populate.
27. Verify all exclusions are active after 48 hours (set a reminder).
28. Let it run 7 days minimum before adjusting anything.
29. Check sales team feedback at 7 days (leading indicator).
30. Check show rate and close rate at 14 days (secondary indicators).
31. Metrics improved → scale budget 20–30%, run another 7 days.
32. Metrics didn't improve → audit content against the four quadrants (do NOT increase budget, do NOT change frequency — audit content first).
33. Do not subtract content from a working campaign.
34. Re-audit placements, Audience Network, and related media after every edit or duplication.
35. Monitor audience size weekly — below 500 active, reduce budget proportionally.
36. If negative online reputation exists, confirm objection content addresses known issues and the confirmation page has a due-diligence video.

See `troubleshooting-and-kpis.md` for the full detail behind steps 26–36
and the measurement logic for steps 29–32.

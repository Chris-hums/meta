#!/usr/bin/env python3
"""
Fix a "Hammer Them" retargeting campaign built on the wrong objective
(Awareness, Purchase/Sales, Traffic, etc.) by rebuilding it under
OUTCOME_ENGAGEMENT — the objective the Hammer Them framework calls for.

Why this is needed
-------------------
Meta does not allow changing a campaign's `objective` after creation, and
changing an ad set's `optimization_goal` after creation is blocked whenever
it requires a different `attribution_spec` (Meta's error: "Attribution
window update is no longer supported after adset creation. Please create
a new adset instead."). So the only fix is: create new campaign(s) with
the correct objective, recreate each ad set with POST_ENGAGEMENT +
ABO + a bid cap, recreate each ad pointing at the SAME existing creative
(no new content needed), activate, then pause the old campaign(s).

What this script does, end to end
----------------------------------
1. For each OLD_CAMPAIGN_ID: fetch every ad set (targeting, daily_budget,
   destination_type, is_dynamic_creative) and each ad set's single ad +
   creative id. (Assumes the Hammer Them "one ad per ad set" structure —
   see the framework doc. If an ad set has >1 ad, it's flagged and
   skipped rather than guessed at.)
2. Create ONE new campaign per OLD_CAMPAIGN_ID, objective=OUTCOME_ENGAGEMENT,
   ABO (is_adset_budget_sharing_enabled=False), PAUSED.
3. Recreate every ad set under the matching new campaign:
     optimization_goal = POST_ENGAGEMENT
     billing_event      = IMPRESSIONS
     bid_strategy        = LOWEST_COST_WITH_BID_CAP
     bid_amount           = BID_CAP_CENTS (tune per account/auction —
                             see "Finding your bid cap" below)
     targeting            = copied as-is (this preserves the existing
                             warm audience AND any per-ad-set exclusions,
                             e.g. the Hammer Them 3-second-view exclusion
                             mechanism — nothing about that changes)
     daily_budget         = copied as-is
   promoted_object and attribution_spec are deliberately dropped —
   Engagement doesn't optimize toward a pixel event, so neither applies.
4. Recreate the single ad in each new ad set, reusing the SAME creative_id
   (no re-upload, no lost engagement/comments on the underlying post).
5. Activate every new ad set + ad, activate the new campaign(s).
6. Pause (not delete) the old campaign(s) — never delete live history.

Finding your bid cap
---------------------
There's no universal right answer for `bid_amount` (it's a real-money bid
cap in the account's minor currency unit, e.g. cents for USD). This
script's default (50 = $0.50) worked on one account's Engagement/
POST_ENGAGEMENT test but auction dynamics vary by account, geography, and
competition. Before a full run, do what this script's `--test-bid` mode
does: try creating ONE throwaway ad set at your candidate bid, see if
Meta accepts it, delete it, then commit to that value for the real run.
Meta will reject a bid that's below its enforced floor with a specific
error naming the minimum — raise BID_CAP_CENTS and retry if you see that.

Safety
------
- Everything is created PAUSED first. Nothing spends until the final
  activation step, which you can comment out to review in Ads Manager
  before going live.
- Resumable: progress is cached to RESULTS_CACHE_PATH, so re-running after
  a rate limit (Meta error code 17) or a crash picks up where it left off
  instead of duplicating ad sets.
- Old campaigns are PAUSED, never deleted, at the end.

Usage
-----
    export META_ACCESS_TOKEN=...            # System User token
    python3 fix_hammer_them_objective.py

Edit the CONFIG block below for the account/campaigns you're fixing.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from meta_ads.client import GraphClient, GraphAPIError  # noqa: E402

# ============================== CONFIG ===================================

AD_ACCOUNT_ID = "act_XXXXXXXXXXXXXXX"  # e.g. "act_1222452979529550"

# One entry per old campaign you're fixing. `new_name` is the replacement
# campaign's name. Add as many as you have (e.g. Window 1 + Window 2).
OLD_CAMPAIGNS = [
    {"old_campaign_id": "1202XXXXXXXXXXXXX", "new_name": "Hammer Them — Webinar Registrants"},
    {"old_campaign_id": "1202XXXXXXXXXXXXX", "new_name": "Hammer Them — Call Bookers"},
]

BID_CAP_CENTS = 50  # $0.50 — verify with --test-bid before a real run
PACE_SECONDS = 1.3  # delay between API calls; raise if you hit rate limits
NAME_SUFFIX = " (ENG)"  # appended to each rebuilt ad set's name

RESULTS_CACHE_PATH = "hammer_them_eng_rebuild_results.json"
CONFIGS_CACHE_PATH = "hammer_them_old_adset_configs.json"
AD_MAP_CACHE_PATH = "hammer_them_old_ad_map.json"

ACTIVATE_WHEN_DONE = True  # flip to False to leave everything PAUSED for review
PAUSE_OLD_CAMPAIGNS_WHEN_DONE = True

# =========================================================================


def get_client() -> GraphClient:
    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set META_ACCESS_TOKEN in your environment first.")
    return GraphClient(access_token=token)


def load_cache(path: str) -> dict:
    try:
        return json.load(open(path))
    except FileNotFoundError:
        return {}


def save_cache(path: str, data: dict) -> None:
    json.dump(data, open(path, "w"), indent=2)


def fetch_old_adset_ids(client: GraphClient, campaign_id: str) -> list[str]:
    r = client.get(
        f"{campaign_id}/adsets",
        params={
            "fields": "id",
            "filtering": json.dumps(
                [{"field": "adset.effective_status", "operator": "IN", "value": ["ACTIVE", "PAUSED"]}]
            ),
            "limit": 200,
        },
    )
    return [a["id"] for a in r.get("data", [])]


def batch_fetch_adset_configs(client: GraphClient, adset_ids: list[str]) -> dict:
    fields = "id,name,campaign_id,daily_budget,destination_type,targeting,is_dynamic_creative"
    configs = {}
    batch = [{"method": "GET", "relative_url": f"{aid}?fields={fields}"} for aid in adset_ids]
    for i in range(0, len(batch), 25):
        chunk = batch[i : i + 25]
        r = client.post("", data={"batch": json.dumps(chunk)})
        for sub in r:
            body = json.loads(sub["body"])
            if "id" in body:
                configs[body["id"]] = body
        time.sleep(PACE_SECONDS)
    return configs


def batch_fetch_ads(client: GraphClient, adset_ids: list[str]) -> dict:
    ad_map = {}
    batch = [
        {"method": "GET", "relative_url": f"{aid}/ads?fields=id,name,creative{{id}}"} for aid in adset_ids
    ]
    for i in range(0, len(batch), 25):
        chunk = batch[i : i + 25]
        r = client.post("", data={"batch": json.dumps(chunk)})
        for aid, sub in zip(adset_ids[i : i + 25], r):
            body = json.loads(sub["body"])
            ad_map[aid] = body.get("data", [])
        time.sleep(PACE_SECONDS)
    return ad_map


def test_bid_cap(client: GraphClient, campaign_id: str, sample_cfg: dict, bid_cents: int) -> bool:
    """Create + immediately delete one throwaway ad set to check a bid cap works."""
    try:
        r = client.post(
            f"{AD_ACCOUNT_ID}/adsets",
            data={
                "campaign_id": campaign_id,
                "name": f"BID-CAP-TEST-{bid_cents}",
                "status": "PAUSED",
                "daily_budget": sample_cfg["daily_budget"],
                "optimization_goal": "POST_ENGAGEMENT",
                "billing_event": "IMPRESSIONS",
                "destination_type": sample_cfg["destination_type"],
                "targeting": json.dumps(sample_cfg["targeting"]),
                "is_dynamic_creative": sample_cfg["is_dynamic_creative"],
                "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
                "bid_amount": bid_cents,
            },
        )
        client.post(r["id"], data={"status": "DELETED"})
        print(f"  bid_amount={bid_cents}: OK")
        return True
    except GraphAPIError as e:
        print(f"  bid_amount={bid_cents}: REJECTED — {e.user_title or e}")
        return False


def rebuild(client: GraphClient) -> None:
    results = load_cache(RESULTS_CACHE_PATH)
    all_configs = load_cache(CONFIGS_CACHE_PATH)
    all_ad_map = load_cache(AD_MAP_CACHE_PATH)

    new_campaign_ids: dict[str, str] = {}
    old_to_new_campaign: dict[str, str] = {}

    for entry in OLD_CAMPAIGNS:
        old_campaign_id = entry["old_campaign_id"]
        new_name = entry["new_name"]

        print(f"\n=== {new_name} (replacing {old_campaign_id}) ===")

        old_adset_ids = fetch_old_adset_ids(client, old_campaign_id)
        print(f"  {len(old_adset_ids)} ad sets found")

        missing_cfg = [a for a in old_adset_ids if a not in all_configs]
        if missing_cfg:
            all_configs.update(batch_fetch_adset_configs(client, missing_cfg))
            save_cache(CONFIGS_CACHE_PATH, all_configs)

        missing_ads = [a for a in old_adset_ids if a not in all_ad_map]
        if missing_ads:
            all_ad_map.update(batch_fetch_ads(client, missing_ads))
            save_cache(AD_MAP_CACHE_PATH, all_ad_map)

        multi_ad = {a: all_ad_map[a] for a in old_adset_ids if len(all_ad_map.get(a, [])) != 1}
        if multi_ad:
            print(f"  WARNING: {len(multi_ad)} ad set(s) don't have exactly 1 ad — skipping them:")
            for aid, ads in multi_ad.items():
                print(f"    {aid}: {len(ads)} ads")
            old_adset_ids = [a for a in old_adset_ids if a not in multi_ad]

        # Create the replacement campaign once per old campaign.
        camp_key = f"new_campaign::{old_campaign_id}"
        if camp_key not in results:
            r = client.post(
                f"{AD_ACCOUNT_ID}/campaigns",
                data={
                    "name": new_name,
                    "objective": "OUTCOME_ENGAGEMENT",
                    "status": "PAUSED",
                    "special_ad_categories": json.dumps([]),
                    "is_adset_budget_sharing_enabled": False,
                },
            )
            results[camp_key] = r["id"]
            save_cache(RESULTS_CACHE_PATH, results)
            print(f"  new campaign created: {r['id']}")
        new_campaign_id = results[camp_key]
        new_campaign_ids[new_name] = new_campaign_id
        old_to_new_campaign[old_campaign_id] = new_campaign_id

        for old_aid in old_adset_ids:
            entry_key = old_aid
            adset_entry = results.get(entry_key, {})
            if adset_entry.get("new_adset_id") and adset_entry.get("new_ad_id"):
                continue

            cfg = all_configs[old_aid]
            old_ad = all_ad_map[old_aid][0]
            creative_id = old_ad["creative"]["id"]

            try:
                if "new_adset_id" not in adset_entry:
                    r = client.post(
                        f"{AD_ACCOUNT_ID}/adsets",
                        data={
                            "campaign_id": new_campaign_id,
                            "name": cfg["name"] + NAME_SUFFIX,
                            "status": "PAUSED",
                            "daily_budget": cfg["daily_budget"],
                            "optimization_goal": "POST_ENGAGEMENT",
                            "billing_event": "IMPRESSIONS",
                            "destination_type": cfg["destination_type"],
                            "targeting": json.dumps(cfg["targeting"]),
                            "is_dynamic_creative": cfg["is_dynamic_creative"],
                            "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
                            "bid_amount": BID_CAP_CENTS,
                        },
                    )
                    adset_entry["new_adset_id"] = r["id"]
                    results[entry_key] = adset_entry
                    save_cache(RESULTS_CACHE_PATH, results)

                if "new_ad_id" not in adset_entry:
                    ad = client.post(
                        f"{AD_ACCOUNT_ID}/ads",
                        data={
                            "name": old_ad["name"],
                            "adset_id": adset_entry["new_adset_id"],
                            "creative": json.dumps({"creative_id": creative_id}),
                            "status": "PAUSED",
                        },
                    )
                    adset_entry["new_ad_id"] = ad["id"]
                    results[entry_key] = adset_entry
                    save_cache(RESULTS_CACHE_PATH, results)

                print(f"  OK {old_aid} -> adset {adset_entry['new_adset_id']}, ad {adset_entry['new_ad_id']}")

            except GraphAPIError as e:
                adset_entry["error"] = str(e)
                results[entry_key] = adset_entry
                save_cache(RESULTS_CACHE_PATH, results)
                if e.code == 17:  # rate limited — back off and retry this one next run
                    print(f"  RATE LIMITED on {old_aid}, back off and re-run the script to resume")
                    time.sleep(30)
                else:
                    print(f"  FAIL {old_aid}: {e}")

            time.sleep(PACE_SECONDS)

    total = sum(1 for k, v in results.items() if isinstance(v, dict) and v.get("new_adset_id") and v.get("new_ad_id"))
    print(f"\nRebuilt {total} ad sets across {len(OLD_CAMPAIGNS)} campaign(s).")

    if not ACTIVATE_WHEN_DONE:
        print("ACTIVATE_WHEN_DONE is False — everything left PAUSED for you to review in Ads Manager.")
        return

    print("\nActivating new ad sets, ads, and campaigns...")
    for k, v in results.items():
        if isinstance(v, dict) and v.get("new_adset_id") and v.get("new_ad_id"):
            client.post(v["new_ad_id"], data={"status": "ACTIVE"})
            time.sleep(PACE_SECONDS)
            client.post(v["new_adset_id"], data={"status": "ACTIVE"})
            time.sleep(PACE_SECONDS)
    for new_campaign_id in new_campaign_ids.values():
        client.post(new_campaign_id, data={"status": "ACTIVE"})
        time.sleep(PACE_SECONDS)

    if PAUSE_OLD_CAMPAIGNS_WHEN_DONE:
        print("Pausing old campaign(s)...")
        for entry in OLD_CAMPAIGNS:
            client.post(entry["old_campaign_id"], data={"status": "PAUSED"})
            time.sleep(PACE_SECONDS)

    print("\nDone. New campaign IDs:")
    for name, cid in new_campaign_ids.items():
        print(f"  {name}: {cid}")
    print(
        "\nIMPORTANT: if any scheduled triggers/automation reference the OLD "
        "campaign/ad set IDs, update them to the new ones printed above."
    )


if __name__ == "__main__":
    client = get_client()

    if "--test-bid" in sys.argv:
        # Quick standalone check: does BID_CAP_CENTS clear the auction floor?
        # Uses the first old campaign's first ad set as a config template.
        old_campaign_id = OLD_CAMPAIGNS[0]["old_campaign_id"]
        adset_ids = fetch_old_adset_ids(client, old_campaign_id)
        sample_cfg = batch_fetch_adset_configs(client, adset_ids[:1])[adset_ids[0]]
        # Uses the OLD campaign as the container for the throwaway test ad
        # set (it's deleted immediately after) so no new campaign is needed
        # just to test a bid value.
        test_bid_cap(client, old_campaign_id, sample_cfg, BID_CAP_CENTS)
        sys.exit(0)

    rebuild(client)

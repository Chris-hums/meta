"""Command-line interface for managing the Trade Covenant Meta ad account.

Usage examples:
    python -m meta_ads.cli validate
    python -m meta_ads.cli account info
    python -m meta_ads.cli campaigns list --status ACTIVE,PAUSED
    python -m meta_ads.cli campaigns create --name "Fall Promo" --objective OUTCOME_TRAFFIC --daily-budget 2000
    python -m meta_ads.cli campaigns activate 12345678
    python -m meta_ads.cli insights account --date-preset last_7d --format table
"""
from __future__ import annotations

import json
import sys
from typing import Optional

import click

from . import adsets as adsets_mod
from . import ads as ads_mod
from . import campaigns as campaigns_mod
from . import creatives as creatives_mod
from . import insights as insights_mod
from .client import GraphAPIError, GraphClient
from .config import ConfigError, load_config
from .output import print_json, print_table


def _client() -> tuple[GraphClient, str]:
    cfg = load_config()
    return GraphClient(cfg.access_token, api_version=cfg.api_version), cfg.ad_account_id


def _emit(data, fmt: str, columns: Optional[list[str]] = None) -> None:
    if fmt == "json":
        print_json(data)
    else:
        rows = data if isinstance(data, list) else [data]
        print_table(rows, columns)


def _parse_status_list(value: Optional[str]) -> Optional[list[str]]:
    return [s.strip().upper() for s in value.split(",")] if value else None


def _load_json_arg(inline: Optional[str], file: Optional[str]) -> Optional[dict]:
    if file:
        with open(file) as f:
            return json.load(f)
    if inline:
        return json.loads(inline)
    return None


@click.group()
def cli() -> None:
    """Manage and report on the Trade Covenant Meta ad account."""


@cli.command()
def validate() -> None:
    """Check credentials/config and connectivity to the ad account."""
    try:
        client, account_id = _client()
        data = client.get(account_id, {"fields": "id,name,account_status,currency,timezone_name"})
    except ConfigError as exc:
        click.echo(f"Config error: {exc}", err=True)
        sys.exit(1)
    except GraphAPIError as exc:
        click.echo(f"Graph API error: {exc}", err=True)
        sys.exit(1)
    click.echo("Connected OK:")
    print_json(data)


@cli.group()
def account() -> None:
    """Ad account-level commands."""


@account.command("info")
def account_info() -> None:
    client, account_id = _client()
    data = client.get(
        account_id,
        {
            "fields": "id,name,account_status,currency,timezone_name,amount_spent,"
            "spend_cap,balance,business"
        },
    )
    print_json(data)


# ---- campaigns -------------------------------------------------------

@cli.group()
def campaigns() -> None:
    """Campaign commands."""


@campaigns.command("list")
@click.option("--status", "status_filter", help="Comma-separated effective statuses, e.g. ACTIVE,PAUSED")
@click.option("--limit", type=int, default=None)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
def campaigns_list(status_filter, limit, fmt) -> None:
    client, account_id = _client()
    data = campaigns_mod.list_campaigns(client, account_id, _parse_status_list(status_filter), limit)
    _emit(data, fmt, ["id", "name", "objective", "effective_status", "daily_budget"])


@campaigns.command("get")
@click.argument("campaign_id")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="json")
def campaigns_get(campaign_id, fmt) -> None:
    client, _ = _client()
    _emit(campaigns_mod.get_campaign(client, campaign_id), fmt)


@campaigns.command("create")
@click.option("--name", required=True)
@click.option("--objective", required=True, help="e.g. OUTCOME_TRAFFIC, OUTCOME_LEADS, OUTCOME_SALES, OUTCOME_AWARENESS, OUTCOME_ENGAGEMENT, OUTCOME_APP_PROMOTION")
@click.option("--daily-budget", type=int, default=None, help="Minor currency units, e.g. cents")
@click.option("--lifetime-budget", type=int, default=None)
@click.option("--bid-strategy", default=None)
@click.option("--special-ad-category", "special_ad_categories", multiple=True, help="e.g. HOUSING, EMPLOYMENT, CREDIT (repeatable); omit if none apply")
@click.option("--activate", is_flag=True, help="Create as ACTIVE instead of the default PAUSED")
def campaigns_create(name, objective, daily_budget, lifetime_budget, bid_strategy, special_ad_categories, activate) -> None:
    client, account_id = _client()
    result = campaigns_mod.create_campaign(
        client,
        account_id,
        name=name,
        objective=objective,
        status="ACTIVE" if activate else "PAUSED",
        special_ad_categories=list(special_ad_categories) or None,
        daily_budget=daily_budget,
        lifetime_budget=lifetime_budget,
        bid_strategy=bid_strategy,
    )
    print_json(result)
    if not activate:
        click.echo("Created PAUSED. Run `campaigns activate <id>` when ready to go live.")


@campaigns.command("update")
@click.argument("campaign_id")
@click.option("--name", default=None)
@click.option("--daily-budget", type=int, default=None)
@click.option("--lifetime-budget", type=int, default=None)
@click.option("--status", type=click.Choice(["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"]), default=None)
def campaigns_update(campaign_id, name, daily_budget, lifetime_budget, status) -> None:
    client, _ = _client()
    fields = {k: v for k, v in {
        "name": name, "daily_budget": daily_budget,
        "lifetime_budget": lifetime_budget, "status": status,
    }.items() if v is not None}
    if not fields:
        click.echo("Nothing to update -- pass at least one option.", err=True)
        sys.exit(1)
    print_json(campaigns_mod.update_campaign(client, campaign_id, **fields))


@campaigns.command("pause")
@click.argument("campaign_id")
def campaigns_pause(campaign_id) -> None:
    client, _ = _client()
    print_json(campaigns_mod.pause_campaign(client, campaign_id))


@campaigns.command("activate")
@click.argument("campaign_id")
def campaigns_activate(campaign_id) -> None:
    client, _ = _client()
    print_json(campaigns_mod.activate_campaign(client, campaign_id))


@campaigns.command("delete")
@click.argument("campaign_id")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def campaigns_delete(campaign_id, yes) -> None:
    if not yes:
        click.confirm(f"Delete campaign {campaign_id}?", abort=True)
    client, _ = _client()
    print_json(campaigns_mod.delete_campaign(client, campaign_id))


# ---- adsets -----------------------------------------------------------

@cli.group()
def adsets() -> None:
    """Ad set commands."""


@adsets.command("list")
@click.option("--campaign-id", default=None)
@click.option("--status", "status_filter", default=None)
@click.option("--limit", type=int, default=None)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
def adsets_list(campaign_id, status_filter, limit, fmt) -> None:
    client, account_id = _client()
    data = adsets_mod.list_adsets(client, account_id, campaign_id, _parse_status_list(status_filter), limit)
    _emit(data, fmt, ["id", "name", "campaign_id", "effective_status", "daily_budget", "optimization_goal"])


@adsets.command("get")
@click.argument("adset_id")
def adsets_get(adset_id) -> None:
    client, _ = _client()
    print_json(adsets_mod.get_adset(client, adset_id))


@adsets.command("create")
@click.option("--name", required=True)
@click.option("--campaign-id", required=True)
@click.option("--optimization-goal", required=True, help="e.g. LINK_CLICKS, LANDING_PAGE_VIEWS, OFFSITE_CONVERSIONS, IMPRESSIONS, REACH")
@click.option("--billing-event", required=True, help="e.g. IMPRESSIONS, LINK_CLICKS")
@click.option("--targeting", "targeting_inline", default=None, help="Inline JSON targeting spec")
@click.option("--targeting-file", default=None, type=click.Path(exists=True))
@click.option("--daily-budget", type=int, default=None)
@click.option("--lifetime-budget", type=int, default=None)
@click.option("--bid-amount", type=int, default=None)
@click.option("--bid-strategy", default=None)
@click.option("--start-time", default=None, help="ISO8601, e.g. 2026-08-20T00:00:00-0500")
@click.option("--end-time", default=None)
@click.option("--promoted-object", default=None, help="Inline JSON, e.g. for conversions/pixel")
@click.option("--activate", is_flag=True, help="Create as ACTIVE instead of the default PAUSED")
def adsets_create(name, campaign_id, optimization_goal, billing_event, targeting_inline, targeting_file,
                   daily_budget, lifetime_budget, bid_amount, bid_strategy, start_time, end_time,
                   promoted_object, activate) -> None:
    targeting = _load_json_arg(targeting_inline, targeting_file)
    if targeting is None:
        click.echo("Provide --targeting or --targeting-file with a JSON targeting spec.", err=True)
        sys.exit(1)
    client, account_id = _client()
    result = adsets_mod.create_adset(
        client, account_id, name=name, campaign_id=campaign_id,
        optimization_goal=optimization_goal, billing_event=billing_event,
        targeting=targeting, status="ACTIVE" if activate else "PAUSED",
        daily_budget=daily_budget, lifetime_budget=lifetime_budget,
        bid_amount=bid_amount, bid_strategy=bid_strategy,
        start_time=start_time, end_time=end_time,
        promoted_object=json.loads(promoted_object) if promoted_object else None,
    )
    print_json(result)
    if not activate:
        click.echo("Created PAUSED. Run `adsets activate <id>` when ready to go live.")


@adsets.command("update")
@click.argument("adset_id")
@click.option("--name", default=None)
@click.option("--daily-budget", type=int, default=None)
@click.option("--lifetime-budget", type=int, default=None)
@click.option("--status", type=click.Choice(["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"]), default=None)
def adsets_update(adset_id, name, daily_budget, lifetime_budget, status) -> None:
    client, _ = _client()
    fields = {k: v for k, v in {
        "name": name, "daily_budget": daily_budget,
        "lifetime_budget": lifetime_budget, "status": status,
    }.items() if v is not None}
    if not fields:
        click.echo("Nothing to update -- pass at least one option.", err=True)
        sys.exit(1)
    print_json(adsets_mod.update_adset(client, adset_id, **fields))


@adsets.command("pause")
@click.argument("adset_id")
def adsets_pause(adset_id) -> None:
    client, _ = _client()
    print_json(adsets_mod.pause_adset(client, adset_id))


@adsets.command("activate")
@click.argument("adset_id")
def adsets_activate(adset_id) -> None:
    client, _ = _client()
    print_json(adsets_mod.activate_adset(client, adset_id))


@adsets.command("delete")
@click.argument("adset_id")
@click.option("--yes", is_flag=True)
def adsets_delete(adset_id, yes) -> None:
    if not yes:
        click.confirm(f"Delete ad set {adset_id}?", abort=True)
    client, _ = _client()
    print_json(adsets_mod.delete_adset(client, adset_id))


# ---- creatives ----------------------------------------------------------

@cli.group()
def creatives() -> None:
    """Ad creative commands."""


@creatives.command("list")
@click.option("--limit", type=int, default=None)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
def creatives_list(limit, fmt) -> None:
    client, account_id = _client()
    data = creatives_mod.list_creatives(client, account_id, limit)
    _emit(data, fmt, ["id", "name", "status"])


@creatives.command("create-link")
@click.option("--name", required=True)
@click.option("--page-id", required=True)
@click.option("--link", required=True)
@click.option("--message", required=True)
@click.option("--headline", default=None)
@click.option("--description", default=None)
@click.option("--image-hash", default=None)
@click.option("--cta", "call_to_action_type", default=None, help="e.g. SHOP_NOW, LEARN_MORE, SIGN_UP")
def creatives_create_link(name, page_id, link, message, headline, description, image_hash, call_to_action_type) -> None:
    client, account_id = _client()
    result = creatives_mod.create_link_creative(
        client, account_id, name=name, page_id=page_id, link=link, message=message,
        headline=headline, description=description, image_hash=image_hash,
        call_to_action_type=call_to_action_type,
    )
    print_json(result)


@creatives.command("upload-image")
@click.argument("image_path", type=click.Path(exists=True))
def creatives_upload_image(image_path) -> None:
    client, account_id = _client()
    print_json(creatives_mod.upload_image(client, account_id, image_path))


# ---- ads ------------------------------------------------------------

@cli.group()
def ads() -> None:
    """Ad commands."""


@ads.command("list")
@click.option("--adset-id", default=None)
@click.option("--campaign-id", default=None)
@click.option("--limit", type=int, default=None)
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")
def ads_list(adset_id, campaign_id, limit, fmt) -> None:
    client, account_id = _client()
    data = ads_mod.list_ads(client, account_id, adset_id, campaign_id, limit)
    _emit(data, fmt, ["id", "name", "adset_id", "effective_status"])


@ads.command("create")
@click.option("--name", required=True)
@click.option("--adset-id", required=True)
@click.option("--creative-id", required=True)
@click.option("--activate", is_flag=True)
def ads_create(name, adset_id, creative_id, activate) -> None:
    client, account_id = _client()
    result = ads_mod.create_ad(
        client, account_id, name=name, adset_id=adset_id, creative_id=creative_id,
        status="ACTIVE" if activate else "PAUSED",
    )
    print_json(result)
    if not activate:
        click.echo("Created PAUSED. Run `ads activate <id>` when ready to go live.")


@ads.command("pause")
@click.argument("ad_id")
def ads_pause(ad_id) -> None:
    client, _ = _client()
    print_json(ads_mod.pause_ad(client, ad_id))


@ads.command("activate")
@click.argument("ad_id")
def ads_activate(ad_id) -> None:
    client, _ = _client()
    print_json(ads_mod.activate_ad(client, ad_id))


@ads.command("delete")
@click.argument("ad_id")
@click.option("--yes", is_flag=True)
def ads_delete(ad_id, yes) -> None:
    if not yes:
        click.confirm(f"Delete ad {ad_id}?", abort=True)
    client, _ = _client()
    print_json(ads_mod.delete_ad(client, ad_id))


# ---- insights ---------------------------------------------------------

@cli.group()
def insights() -> None:
    """Performance insights / reporting."""


def _insights_options(f):
    f = click.option("--date-preset", default=None, help="e.g. last_7d, last_30d, this_month, yesterday")(f)
    f = click.option("--since", default=None, help="YYYY-MM-DD (use with --until)")(f)
    f = click.option("--until", default=None, help="YYYY-MM-DD (use with --since)")(f)
    f = click.option("--breakdowns", default=None, help="Comma-separated, e.g. age,gender or publisher_platform")(f)
    f = click.option("--time-increment", default=None, help="Days per row, or 'monthly'/'all_days'")(f)
    f = click.option("--fields", default=None, help="Comma-separated field override")(f)
    f = click.option("--limit", type=int, default=None)(f)
    f = click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table")(f)
    return f


@insights.command("account")
@_insights_options
def insights_account(date_preset, since, until, breakdowns, time_increment, fields, limit, fmt) -> None:
    client, account_id = _client()
    data = insights_mod.get_insights(
        client, account_id, date_preset=date_preset, since=since, until=until,
        fields=fields.split(",") if fields else None,
        level="account", breakdowns=breakdowns.split(",") if breakdowns else None,
        time_increment=time_increment, limit=limit,
    )
    _emit(data, fmt)


@insights.command("campaign")
@click.argument("campaign_id")
@_insights_options
def insights_campaign(campaign_id, date_preset, since, until, breakdowns, time_increment, fields, limit, fmt) -> None:
    client, _ = _client()
    data = insights_mod.get_insights(
        client, campaign_id, date_preset=date_preset, since=since, until=until,
        fields=fields.split(",") if fields else None,
        breakdowns=breakdowns.split(",") if breakdowns else None,
        time_increment=time_increment, limit=limit,
    )
    _emit(data, fmt)


@insights.command("adset")
@click.argument("adset_id")
@_insights_options
def insights_adset(adset_id, date_preset, since, until, breakdowns, time_increment, fields, limit, fmt) -> None:
    client, _ = _client()
    data = insights_mod.get_insights(
        client, adset_id, date_preset=date_preset, since=since, until=until,
        fields=fields.split(",") if fields else None,
        breakdowns=breakdowns.split(",") if breakdowns else None,
        time_increment=time_increment, limit=limit,
    )
    _emit(data, fmt)


@insights.command("ad")
@click.argument("ad_id")
@_insights_options
def insights_ad(ad_id, date_preset, since, until, breakdowns, time_increment, fields, limit, fmt) -> None:
    client, _ = _client()
    data = insights_mod.get_insights(
        client, ad_id, date_preset=date_preset, since=since, until=until,
        fields=fields.split(",") if fields else None,
        breakdowns=breakdowns.split(",") if breakdowns else None,
        time_increment=time_increment, limit=limit,
    )
    _emit(data, fmt)


@insights.command("by-campaign")
@_insights_options
def insights_by_campaign(date_preset, since, until, breakdowns, time_increment, fields, limit, fmt) -> None:
    """Account-wide insights broken out per campaign (level=campaign)."""
    client, account_id = _client()
    data = insights_mod.get_insights(
        client, account_id, date_preset=date_preset, since=since, until=until,
        fields=fields.split(",") if fields else None,
        level="campaign", breakdowns=breakdowns.split(",") if breakdowns else None,
        time_increment=time_increment, limit=limit,
    )
    _emit(data, fmt)


def main() -> None:
    try:
        cli()
    except ConfigError as exc:
        click.echo(f"Config error: {exc}", err=True)
        sys.exit(1)
    except GraphAPIError as exc:
        click.echo(f"Graph API error: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

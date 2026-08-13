# Trade Covenant — Meta Ads Management

A CLI for managing campaigns/ad sets/ads and pulling performance insights
for the Trade Covenant Meta (Facebook/Instagram) ad account, via the
Marketing API.

Ad account: `act_1222452979529550`

## Safety defaults

- **New campaigns, ad sets, and ads are created `PAUSED`** unless you pass
  `--activate`. Nothing spends money until you explicitly flip it on.
- `delete` commands prompt for confirmation unless you pass `--yes`.
- The access token is never written to the repo. It's read from the
  `META_ACCESS_TOKEN` environment variable (local `.env`, or a GitHub
  Actions secret in CI).

## Setup

### 1. Credentials

This CLI needs a Meta access token with `ads_management`, `ads_read`, and
(if using Business Manager) `business_management` permissions for the
Trade Covenant account. A long-lived System User token is recommended so
it doesn't expire every 60 days.

**Required GitHub repo secret:** `META_ACCESS_TOKEN`
(Settings → Secrets and variables → Actions → New repository secret)

The ad account ID defaults to `1222452979529550` in code, so you don't
need to set `META_AD_ACCOUNT_ID` unless you want to point this at a
different account.

### 2. Local install (optional)

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in META_ACCESS_TOKEN
python -m meta_ads.cli validate
```

### 3. Run via GitHub Actions (no token ever leaves the repo's secrets)

Go to **Actions → Trade Covenant Ads CLI → Run workflow**, and enter the
CLI arguments in the `command` field, e.g.:

- `validate`
- `campaigns list --status ACTIVE,PAUSED`
- `insights account --date-preset last_7d`

Or trigger it from Claude / the `gh` CLI / API with `workflow_dispatch`.

## Command reference

```
python -m meta_ads.cli validate                     # check credentials + connectivity
python -m meta_ads.cli account info

python -m meta_ads.cli campaigns list [--status ACTIVE,PAUSED] [--format json]
python -m meta_ads.cli campaigns get <id>
python -m meta_ads.cli campaigns create --name "..." --objective OUTCOME_TRAFFIC \
    [--daily-budget 2000] [--special-ad-category HOUSING] [--activate]
python -m meta_ads.cli campaigns update <id> [--status ACTIVE] [--daily-budget 3000]
python -m meta_ads.cli campaigns pause <id>
python -m meta_ads.cli campaigns activate <id>
python -m meta_ads.cli campaigns delete <id> [--yes]

python -m meta_ads.cli adsets list [--campaign-id <id>]
python -m meta_ads.cli adsets create --name "..." --campaign-id <id> \
    --optimization-goal LINK_CLICKS --billing-event LINK_CLICKS \
    --targeting '{"geo_locations":{"countries":["US"]},"age_min":25,"age_max":54}' \
    [--daily-budget 2000] [--activate]
python -m meta_ads.cli adsets pause <id> / activate <id> / delete <id>

python -m meta_ads.cli creatives create-link --name "..." --page-id <id> \
    --link https://... --message "..." [--headline "..."] [--cta SHOP_NOW]
python -m meta_ads.cli creatives upload-image path/to/image.jpg

python -m meta_ads.cli ads create --name "..." --adset-id <id> --creative-id <id> [--activate]
python -m meta_ads.cli ads pause <id> / activate <id> / delete <id>

python -m meta_ads.cli insights account --date-preset last_30d
python -m meta_ads.cli insights by-campaign --date-preset last_7d
python -m meta_ads.cli insights campaign <id> --since 2026-08-01 --until 2026-08-13
python -m meta_ads.cli insights adset <id> --breakdowns age,gender
python -m meta_ads.cli insights ad <id> --time-increment 1
```

Budgets are in the account's currency's minor unit (e.g. cents for USD).
Every `create`/`list`/`get` command supports `--format json` for scripting.

## Project layout

```
meta_ads/
  client.py     Graph API HTTP wrapper (pagination, retries, error handling)
  config.py     env var loading / validation
  campaigns.py  campaign CRUD
  adsets.py     ad set CRUD
  ads.py        ad CRUD
  creatives.py  ad creative creation, image upload
  insights.py   performance reporting
  output.py     table/JSON formatting
  cli.py        command-line interface
```

## Extending

Things not yet wired up as CLI flags but supported by the underlying Graph
API (open a request and they can be added): carousel/video creatives via
`creatives.create_creative_from_spec`, Advantage+ shopping campaigns,
custom audiences, catalog/DPA ads, lookalike audiences, conversion
event/pixel-based optimization via `--promoted-object`.

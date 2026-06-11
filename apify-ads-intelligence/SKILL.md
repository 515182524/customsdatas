---
name: apify-ads-intelligence
description: Research, spy on, and analyze ads across Meta (Facebook & Instagram), Google (Ads Transparency Center + paid search results), TikTok (Ads Library + Creative Center), LinkedIn Ad Library, and X (Twitter — promoted tweets, best-effort) using Apify Actors. Use when user asks about competitor ads, ad library research, winning creatives, ad copy analysis, landing page audits from ads, cross-platform ad audits, brand transparency checks, or any task involving paid ad creatives, advertiser data, or ad targeting from public ad libraries.
author: Sameh Jarour
author_url: https://github.com/samehjarour
---

# Ads Intelligence Cluster

Answer natural language questions about ads, ad libraries, and competitor advertising activity by routing to the right Apify Actor and delivering a synthesized Markdown report.

**CLI rules:** Always pass `--user-agent apify-awesome-skills/apify-ads-intelligence`, `--json` (or the relevant `--format` flag on `datasets get-items`), and `2>/dev/null`. The `--user-agent` flag is critical for telemetry — never omit it.

## Note on platform coverage

- **Meta, Google, TikTok, LinkedIn**: real public ad libraries with rich data (creatives, targeting, dates, reach where disclosed).
- **X (Twitter)**: no public ad library exists. Coverage is a **best-effort workaround** that scrapes a brand's tweets and flags items with non-empty `card` field or `source` containing "Ads" as likely promoted. Always include the caveat in synthesis output.

## Note on overlap with `apify-ecommerce`

That skill has an `ads-intelligence` intent that routes to `apify/facebook-ads-scraper` for shallow Meta-ad lookups. This skill is the deep dive across all five platforms. If you only need Meta ads as a side detail of an ecommerce question, stay in `apify-ecommerce`. If ads are the main task, use this skill.

## Prerequisites

(No need to check it upfront)

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- `jq` (recommended for response parsing and filtering; `brew install jq` on macOS, `apt install jq` on Linux)
- Authentication via one of:
  - `apify login` (OAuth, opens browser)
  - `APIFY_TOKEN` env variable (e.g. `export APIFY_TOKEN=...` or `.env` file)
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

Verify auth: `apify info --user-agent apify-awesome-skills/apify-ads-intelligence` — should show username and userId.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Step 1: Detect intent and select Actor(s)
- [ ] Step 2: Fetch Actor schema
- [ ] Step 3: Ask user preferences (output format, result count, country)
- [ ] Step 4: Run the Actor (or Actors in parallel for cross-platform-audit) and fetch results
- [ ] Step 5: Synthesize findings and collect ad links
- [ ] Step 6: Save and deliver a Markdown report
```

### Step 1: Detect Intent and Select Actor

Classify the user's message into an intent, then pick the right Actor.

**Intent signals:**

| Signals in user message | Intent |
|-------------------------|--------|
| "what ads is X running", "competitor [brand] ads", "[brand] FB/Google/TikTok/LinkedIn/X/Twitter ads", "show ads from [page]", "promoted tweets from [brand]" | `competitor-ads` |
| "ads about [topic]", "find [keyword] ads", "ads for [vertical]", "fitness/fintech/saas ads" | `keyword-ads` |
| "trending ads", "winning ads", "top ads", "best performing", "long-running ads", "creative inspiration" | `top-creatives` |
| "where do these ads go", "landing pages from ads", "click destinations", "ad funnels" | `landing-page-audit` |
| "compare X's ads across platforms", "all ads from [brand]", "cross-platform ad audit" | `cross-platform-audit` |

If multiple intents detected, ask: *"Do you want [intent A] or [intent B]?"*

**Actor routing — always try Primary first, switch to Fallback only if it fails or returns 0 results:**

| Intent | Platform | Primary Actor | Fallback Actor |
|--------|----------|---------------|----------------|
| `competitor-ads` | Meta (FB/IG) | `apify/facebook-ads-scraper` | `brilliant_gum/facebook-ads-library-scraper` |
| `competitor-ads` | Google | `dz_omar/google-ads-scraper` | `solidcode/ads-transparency-scraper` |
| `competitor-ads` | TikTok | `brilliant_gum/tiktok-ads-library-scraper` (`source: library`) | `silva95gustavo/tiktok-ads-scraper` |
| `competitor-ads` | LinkedIn | `silva95gustavo/linkedin-ad-library-scraper` | `dz_omar/linkedin-ads-scraper` |
| `competitor-ads` | X (workaround) | `apidojo/twitter-scraper-lite` (`twitterHandles: [<brand>]`) + heuristic filter | `apidojo/tweet-scraper` |
| `keyword-ads` | Meta | `brilliant_gum/facebook-ads-library-scraper` | `apify/facebook-ads-scraper` |
| `keyword-ads` | Google | `apify/google-search-scraper` (`focusOnPaidAds: true`) | — |
| `keyword-ads` | TikTok | `brilliant_gum/tiktok-ads-library-scraper` | — |
| `keyword-ads` | LinkedIn | `silva95gustavo/linkedin-ad-library-scraper` | — |
| `keyword-ads` | X (workaround) | `apidojo/twitter-scraper-lite` (`searchTerms: [<keyword>]`) + heuristic filter | `apidojo/tweet-scraper` |
| `top-creatives` | Meta | `brilliant_gum/facebook-ads-library-scraper` (rank by `daysRunning`) | — |
| `top-creatives` | TikTok | `burbn/tiktok-top-ads-spy` (sort by CTR / impressions / likes) | `brilliant_gum/tiktok-ads-library-scraper` (`source: creative_center`) |
| `top-creatives` | Google | n/a — fall back to `competitor-ads` route, filter to active ads | — |
| `top-creatives` | LinkedIn | n/a — fall back to `competitor-ads` route, rank by `impressionsPerCountry` reach | — |
| `top-creatives` | X | n/a in v1 — no reliable promoted-content signal across timelines | — |
| `landing-page-audit` | Meta | `brilliant_gum/facebook-ads-library-scraper` (`resolveSnapshotUrls: true`) | — |
| `landing-page-audit` | Google | `apify/google-search-scraper` (`focusOnPaidAds: true`, `directUrl`) | `dz_omar/google-ads-scraper` (`destinationUrl`) |
| `landing-page-audit` | X | n/a in v1 — heuristics not reliable enough for landing-page extraction | — |
| `cross-platform-audit` | All five | Run Meta + Google + TikTok + LinkedIn primaries in parallel; X workaround runs separately with caveat. Merge by advertiser. | — |

**X (Twitter) heuristic filter** — after scraping, flag a tweet as *likely promoted* if any of the following hold:

- `card` field is non-empty (website cards / CTAs are commonly attached to promoted tweets)
- `source` field contains "Ads" (e.g. "Twitter Ads")

Surface results with the explicit caveat: *"X has no public ad library; results below are tweets from the brand's own timeline that match promoted-content heuristics. They will miss promoted-only ads that appear in other users' feeds."*

### Step 2: Fetch Actor Schema

Fetch the Actor summary, input schema, and README:

```bash
# Summary (title, description, pricing, stats)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ads-intelligence --json 2>/dev/null

# Input schema (required and optional parameters; schema lives in
# .taggedBuilds.latest.build.inputSchema as an escaped JSON string)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ads-intelligence --input --json 2>/dev/null

# README (capabilities, examples, gotchas)
apify actors info "ACTOR_ID" --user-agent apify-awesome-skills/apify-ads-intelligence --readme 2>/dev/null
```

Replace `ACTOR_ID` with the selected Actor (e.g., `apify/facebook-ads-scraper`).

### Step 3: Ask User Preferences

Before running, ask:

1. **Output format**:
   - **Markdown report** (default) — synthesized report saved to disk and delivered to the user
   - **CSV + Markdown report** — full CSV export plus the synthesized report
   - **JSON + Markdown report** — full JSON export plus the synthesized report
2. **Result count** — defaults by intent:

   | Intent | Default count |
   |--------|---------------|
   | `competitor-ads` | 30 |
   | `keyword-ads` | 30 |
   | `top-creatives` | 20 |
   | `landing-page-audit` | 50 |
   | `cross-platform-audit` | 15 per platform |

3. **Country** — default `US`. For TikTok library specifically, default `DE` (EU-only) and warn the user; for global TikTok use `source: creative_center`. X routes are global by handle/keyword, no country parameter.

**Cost safety**: Always set a sensible result limit in the Actor input (e.g., `maxResults`, `resultsLimit`, or the equivalent field per Actor schema). Warn the user before runs of 500+ ads — `apify/facebook-ads-scraper` charges per ad and X primaries charge per tweet.

### Step 4: Run the Actor and Fetch Results

Two steps: run the Actor (blocks until done), then fetch dataset items in the requested format.

**Run the Actor** — returns run metadata as JSON; extract `defaultDatasetId` for the next step:

```bash
apify actors call "ACTOR_ID" -i 'JSON_INPUT' \
  --user-agent apify-awesome-skills/apify-ads-intelligence --json 2>/dev/null
```

From the output use `.id` (run ID), `.status` (should be `SUCCEEDED`), and `.defaultDatasetId`.

**Fetch results** — always fetch enough JSON data to build the Markdown report. Optionally export CSV or JSON when requested:

```bash
# Report input: total count + fields + representative ads
apify datasets info DATASET_ID --json \
  --user-agent apify-awesome-skills/apify-ads-intelligence 2>/dev/null \
  | jq '{itemCount, fields, consoleUrl}'
apify datasets get-items DATASET_ID --limit 20 \
  --user-agent apify-awesome-skills/apify-ads-intelligence --format json 2>/dev/null

# CSV file
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-ads-intelligence --format csv 2>/dev/null > YYYY-MM-DD_filename.csv

# JSON file
apify datasets get-items DATASET_ID \
  --user-agent apify-awesome-skills/apify-ads-intelligence --format json 2>/dev/null > YYYY-MM-DD_filename.json
```

Other `--format` options: `jsonl`, `xlsx`, `xml`, `rss`, `html`. Use `--offset N` to paginate large datasets.

**Tip:** for anything more than a quick peek, save the dataset to a local file first (with `> file.json` / `> file.csv`) and run further analysis from disk. `apify datasets get-items` always streams over the network, so piping it straight into `jq` re-downloads the whole thing every iteration.

**Cross-platform audit (parallel runs):** For `cross-platform-audit`, kick off Meta + Google + TikTok + LinkedIn primaries in parallel by backgrounding each `apify actors call ...` invocation with `&` and calling `wait` before fetching results. Example:

```bash
apify actors call "apify/facebook-ads-scraper" -i '<META_INPUT>' \
  --user-agent apify-awesome-skills/apify-ads-intelligence --json 2>/dev/null > meta_run.json &
apify actors call "dz_omar/google-ads-scraper" -i '<GOOGLE_INPUT>' \
  --user-agent apify-awesome-skills/apify-ads-intelligence --json 2>/dev/null > google_run.json &
apify actors call "brilliant_gum/tiktok-ads-library-scraper" -i '<TIKTOK_INPUT>' \
  --user-agent apify-awesome-skills/apify-ads-intelligence --json 2>/dev/null > tiktok_run.json &
apify actors call "silva95gustavo/linkedin-ad-library-scraper" -i '<LINKEDIN_INPUT>' \
  --user-agent apify-awesome-skills/apify-ads-intelligence --json 2>/dev/null > linkedin_run.json &
wait
# Then extract each .defaultDatasetId and fetch items per platform; X workaround runs separately with caveat.
```

**Combining with `jq` for quick extraction:**

Treat `jq` as a complement to `apify datasets get-items`, not a replacement: server-side `--limit` / `--offset` / `--format` keeps cost and bandwidth down. Use `jq` on a sample item or on a file you already saved.

```bash
# Discover real field names from one sample item (Actor outputs vary —
# use this before composing further jq queries)
apify datasets get-items DATASET_ID --limit 1 --format json \
  --user-agent apify-awesome-skills/apify-ads-intelligence 2>/dev/null \
  | jq '.[0]'

# X heuristic filter on a saved tweets file: keep items with non-empty card
# or source containing "Ads"
jq '[.[] | select((.card != null and .card != "") or (.source != null and (.source | contains("Ads"))))]' \
  YYYY-MM-DD_x_tweets.json
```

### Step 5: Analyze Results and Collect Links

Synthesize, don't dump. Collect useful links while analyzing each representative ad:

- **Ad library link**: prefer the exact ad/creative transparency URL. If unavailable, provide the advertiser or filtered library URL.
- **Creative link**: include image, video, preview, or snapshot URL when the Actor exposes one.
- **Landing-page link**: include the click/destination URL when exposed. Do not confuse an ad library link with a landing page.
- **Apify evidence link**: include the dataset or run console URL in the methodology section, not as a replacement for the public ad link.
- Never invent links. If a platform does not expose a stable direct ad link, write `未提供稳定广告直链`.

Patterns by intent:

| Intent | What the synthesis surfaces |
|--------|------------------------------|
| `competitor-ads` | Total ads found, active vs inactive split, top creative formats, top 5 ad copy snippets, list of unique landing-page domains. For X specifically: total tweets scraped, count flagged as likely-promoted, top 5 flagged tweets with the heuristic-detection caveat. |
| `keyword-ads` | Top 5 advertisers running ads on this keyword, total ads, country split |
| `top-creatives` | Top 5 by `daysRunning` (Meta) or CTR (TikTok), with creative summary, link to Ad Library entry |
| `landing-page-audit` | List of unique landing URLs, grouped by domain, with ad counts pointing at each |
| `cross-platform-audit` | Per-platform ad count and tone summary, then a "where they're spending most" inference |

### Step 6: Save and Deliver a Markdown Report

Every completed research task must create a Markdown report, even when the user did not explicitly request a file.

**Default location and filename:**

```text
./ads-intelligence-reports/YYYY-MM-DD_<brand-or-keyword>_ads-report.md
```

- Create `ads-intelligence-reports/` under the current working directory if it does not exist.
- Sanitize the filename so it is filesystem-safe.
- Use the current date and a concise brand or keyword slug.
- If the user requests another location or filename, follow that request.
- In the final chat response, provide a clickable link to the generated `.md` file and a short 3-5 bullet summary.

**Required report structure:**

```markdown
# <品牌或关键词>广告投放调研

> 调研日期：YYYY-MM-DD
> 数据来源：Meta / Google / TikTok / LinkedIn / X / Apify Actors

## 核心结论

## 跨平台概览
| 平台 | 广告数量 | 活跃情况 | 主要形式 | 主要地区 |

## 代表性广告
### <平台>
| 广告/主题 | 状态与日期 | 文案或素材摘要 | 广告链接 | 素材链接 | 落地页 |

## 投放地区与受众

## 素材与文案策略

## 落地页与转化路径

## 判断与机会点

## 数据边界

## 调研方法与证据
```

**Link requirements for the `代表性广告` table:**

- Include up to 10 representative ads per platform, prioritizing active, recent, long-running, or high-performing ads.
- Use readable Markdown links such as `[查看广告](URL)`, `[查看素材](URL)`, and `[打开落地页](URL)`.
- For Google, prefer `adTransparencyUrl`.
- For LinkedIn, prefer a direct ad-library/detail URL when exposed; otherwise use the advertiser's filtered LinkedIn Ad Library search URL.
- For TikTok, prefer the ad detail/library URL when exposed, then `videoUrl` or `thumbnailUrl`.
- For Meta, use an exact Ad Library URL if exposed. Otherwise construct a public library search URL from the known page ID:
  `https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&search_type=page&view_all_page_id=<PAGE_ID>`
- For X, link to the source tweet and repeat the promoted-content heuristic caveat.

**Suggested follow-ups** — keyed off the intent that just ran:

| If user just ran… | Suggest next |
|-------------------|--------------|
| `competitor-ads` (Meta) | Stack with `apify-competitor-intelligence` to add their FB Page posts, IG profile, and Google Maps reviews |
| `landing-page-audit` (any) | Stack with `apify-ecommerce` (`tech-stack` intent) to detect the platform behind the landing pages, or with `apify-lead-generation` to enrich destination domains with contact info |
| `top-creatives` (TikTok / Meta) | Stack with `apify-influencer-discovery` if any creatives are influencer collabs |
| `keyword-ads` (Google / Meta) | Stack with `apify-trend-analysis` to see whether the keyword is rising or falling on Google Trends / Instagram / TikTok |
| `cross-platform-audit` | Stack with `apify-content-analytics` for the brand's organic content side; combined paid + organic picture |

## Quirks

- **TikTok keyword search is loose.** Searching "Nike" can return ads from unrelated advertisers (Interactive Brokers, Shopify in our test). Always post-filter by `advertiserName` matching the user's intended brand; warn the user if zero matches after filter.
- **TikTok Ads Library is EU/EEA/UK only.** The `library` source needs an EU country code (DE / FR / IT / ES / NL / PL / SE etc.). For US/global coverage, switch to `creative_center` source — different fields (CTR, impression ranges, no targeting data).
- **`dz_omar/google-ads-scraper` requires `resultsPerQuery >= 10`.** Smaller values fail validation. Always set 10+ even for small intents.
- **`apify/facebook-ads-scraper` takes URLs, not keywords.** For `competitor-ads`: build `https://www.facebook.com/<PageName>` from the brand name. For `keyword-ads`: build a Meta Ad Library URL with `q=<keyword>&country=<XX>`.
- **`apify/google-search-scraper` paid-ads mode** has a built-in retry (up to 3) when no paid results are found — sometimes a query genuinely has no paid results. Treat empty `paidResults` as a valid answer, not an error.
- **LinkedIn Ad Library URL construction:** company URL `https://www.linkedin.com/company/<slug>/` is allowed but slow and ignores filters. For `competitor-ads` use `https://www.linkedin.com/ad-library/search?accountOwner=<slug>&countries=<XX>`. For `keyword-ads` use `?keyword=<term>&countries=<XX>`.
- **X has no public ad library.** Coverage is heuristic only. The route uses `apidojo/twitter-scraper-lite` to scrape a brand's own tweets (or keyword search results), then flags items with non-empty `card` field or `source` containing "Ads" as *likely* promoted. This will miss promoted-only tweets that never appear in the brand's own timeline.
- **X session sensitivity.** If the primary X Actor returns only `noResults` sentinels, switch to the fallback before declaring zero results.
- **Pricing.** Most primaries are FREE in our pricing tier; `apify/facebook-ads-scraper` charges per ad ($0.001 - $0.0058); X primaries charge per tweet (~$0.0004 / 1k). Default counts (30 / 20 / 50) keep cost negligible. Warn before runs of 500+ ads.

## Error Handling

- Auth error → run `apify login`, or set `APIFY_TOKEN` env var
- `Actor not found` → check Actor ID against the routing table
- Run status `FAILED` → open the console URL (`.consoleUrl` from run metadata) for logs
- Timeout / very long run → pass `--timeout <seconds>` to `apify actors call`, or reduce result count
- 0 results → switch to the Fallback Actor; if still 0, try a different country code
- TikTok library: no EU country supplied → default to `DE` and warn the user
- `dz_omar/google-ads-scraper`: validation error on `resultsPerQuery` → bump to 10+
- X scraper: only `noResults` sentinels → switch to the fallback X Actor
- `proxy is required` error → add `"proxy": {"useApifyProxy": true}` to the input

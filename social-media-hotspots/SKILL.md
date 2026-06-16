---
name: social-media-hotspots
description: Unified Chinese and overseas social media hotspot research skill. Use when the user asks for 国内外社交媒体热点, 国内外社媒, social media trends, product keyword trend discovery, top content, KOL/influencer discovery, account analysis, competitor social content, platform rankings, hot posts, viral videos, content links, engagement metrics, or Markdown reports across Chinese platforms such as Douyin, WeChat Official Accounts, WeChat Channels, Xiaohongshu, Bilibili, Zhihu, Weibo/Kuaishou/Toutiao/Baidu hot topics, and overseas platforms such as TikTok, Instagram, YouTube, Twitter/X, Threads, Reddit, LinkedIn, and Bluesky.
---

# Social Media Hotspots

Use this as the single entrypoint for domestic and overseas social media research. It composes:

- `redfox-social-media` for China platforms and RedFox API-backed creator/content workflows.
- `foreign-social-media` for overseas platforms, TikHub, NoxInfluencer, KeyAPI, Apify, and public fallback workflows.

## Default Output

Always save a Markdown report for every research result, even if data is partial or empty.

Default locations:

- Current workspace: `output/social-media-hotspots/<slug>-YYYYMMDD-HHMMSS/report.md`
- If the workspace lacks `output/`: `social-media-hotspots/<slug>-YYYYMMDD-HHMMSS/report.md`

The report must include:

- Query scope: keyword, region, platforms, time window, sort method, providers.
- Top content table: rank, platform, title/summary, author, URL, date, metrics, why it matters.
- KOL/account table when relevant: handle, profile URL, followers/subscribers, recent performance, fit, confidence.
- Cross-platform insights: repeated hooks, claims, audience questions, complaints, product angles.
- Data caveats: failed providers, missing fields, cost/quota limits, whether data is API-backed or public fallback.
- Raw output links: local JSON/CSV/HTML files generated during the run.

In chat, show the top 10-20 most useful rows and link to the Markdown file. Do not paste more than 50 rows unless the user asks.

## Router

Choose the smallest route that answers the request:

| User intent | Primary route | Notes |
|---|---|---|
| China platform hot content | `redfox-social-media` | Douyin, WeChat, Xiaohongshu, Bilibili, Zhihu, trending hub |
| Overseas platform hot content | `foreign-social-media` | TikTok, Instagram, YouTube, X, Threads, Reddit, LinkedIn, Bluesky |
| 国内外 comparison | Run RedFox + foreign routes | Normalize both into one report |
| Product keyword across all platforms | RedFox `cn-last30days` + foreign TikHub/public fallback | Default time window: 30 days |
| KOL/influencer discovery | RedFox similar/top account tools + foreign Nox/KeyAPI/TikHub | Separate China and overseas creator tables |
| Competitor social content | RedFox platform search + foreign Apify/TikHub | Include links and content angles |
| Paid ads | `apify-ads-intelligence` plus RedFox only if organic context needed | Mark paid vs organic clearly |
| Compliance/word checks | `redfox-social-media` | Chinese platform review rules only |

Read `references/domestic.md` for RedFox routing, `references/overseas.md` for foreign routing, and `references/report-format.md` before producing a report.

## Workflow

1. Parse the request into objective, keyword/brand/product, platforms, geography, time window, content vs KOL vs account-detail, and output depth.
2. If the user says “所有社交媒体” or “国内外”, cover China and overseas. If the keyword is English and no region is specified, default to overseas first and note the China side if not queried.
3. Verify credentials without printing secrets:
   - `REDFOX_API_KEY` for RedFox.
   - `TIKHUB_API_KEY`, `APIFY_TOKEN`, `KEYAPI_TOKEN`, or NoxInfluencer login when needed.
4. Run bounded queries first. Default limits: 30 posts per platform, 20 creators per platform, top 10-20 rows in chat.
5. Save raw outputs under the report directory. Redact API keys from any captured errors or headers.
6. Normalize all results into the schema in `references/report-format.md`.
7. Generate `report.md` before the final response.
8. In the final response, include the Markdown report path, the highest-signal findings, and any provider failures or data gaps.

## Defaults

- China platforms: Douyin, WeChat Official Accounts, Xiaohongshu, Bilibili, Zhihu, Weibo/Kuaishou/Toutiao/Baidu hot topics when supported by RedFox.
- Overseas platforms: TikTok, Instagram, YouTube, X/Twitter, Reddit, Threads, LinkedIn, Bluesky.
- Time window: last 30 days for trend scans; latest available for platform hot lists; current snapshot for account/KOL analysis.
- Sort: engagement/top for proven content; recent for breaking trends; provider relevance if metrics are unavailable.
- Report filename: `report.md`.

## Rules

- Do not invent metrics. If only a public index is available, mark confidence as low.
- Prefer direct platform URLs over cache, mirror, or search-result URLs.
- Do not retrieve or export private creator contact data unless explicitly requested.
- Warn before large paid runs: more than 500 posts, 100 creators, or multiple premium API routes.
- Preserve exact dates for API/date limits.
- Keep source-specific obligations from the underlying skill when stricter than this merged skill.

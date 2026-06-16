# Overseas Routing

Use `foreign-social-media` for overseas social media. Read `/Users/lg/.codex/skills/foreign-social-media/SKILL.md` and its references when needed.

## Common Routes

| Need | Route |
|---|---|
| Product keyword across overseas platforms | TikHub via `tikhub-social-media`; public fallback when paid routes fail |
| YouTube top videos | TikHub YouTube or `yt-dlp` public search fallback |
| TikTok top content | TikHub TikTok; Apify/TikTok-specific fallback if configured |
| Instagram reels/content | TikHub Instagram; Apify Instagram routes if configured |
| X/Twitter search | TikHub X; `xurl` if authenticated; public search fallback |
| Reddit discussions | TikHub Reddit; public Reddit JSON/search fallback |
| Threads | TikHub Threads or `apify-threads-scraper` |
| Bluesky | `apify-bluesky-scraper` |
| KOL discovery | NoxInfluencer for YouTube/TikTok/Instagram; KeyAPI for TikTok deep analytics |
| Competitor organic content | Apify Competitor Intelligence plus TikHub/public fallback |
| Paid ad creatives | `apify-ads-intelligence` |

## Execution Rules

- Verify provider credentials without printing secrets.
- Use bounded queries first.
- Save raw outputs under the report directory.
- Redact tokens from captured API error bodies.
- If TikHub returns insufficient balance, immediately switch to public or Apify fallback and mark confidence lower.

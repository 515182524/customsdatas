---
name: industry-research-system
description: Build an Obsidian-compatible industry research system with Codex. Use when the user asks to quickly understand an unfamiliar industry, conduct industry research, build an industry database or knowledge map, analyze competitors or content ecosystems, identify opportunities, or create an ongoing industry intelligence workflow.
---

# Industry Research System

Turn scattered research into a structured, evidence-backed industry knowledge base.

Read [references/source-article.md](references/source-article.md) only when you need the original methodology or examples.

## Start

Determine these research boundaries from the request:

- Industry or niche
- Geography
- Time horizon
- Primary goal: market entry, product, content, investment, sourcing, or general learning
- Desired depth: quick scan or deep research
- Output location

If details are missing, use reasonable defaults and state them. For current industry facts, search the web and cite sources.

Default output location:

```text
00- 草稿/行业研究/{行业名}/
```

## Research Workflow

### 1. Create The Industry Database

Create only files that contain useful findings. Do not generate hundreds of empty placeholders.

```text
{行业名}/
├── README.md
├── Industry-Map.md
├── Opportunities.md
├── Sources.md
├── Brands/
├── Products/
├── Customers/
├── Pain-Points/
├── Keywords/
├── Competitors/
├── Content/
├── Business-Models/
├── Supply-Chain/
├── Regulations/
├── Trends/
└── Monitoring/
```

Use `README.md` as the research dashboard. Include scope, key conclusions, open questions, and links to important files.

### 2. Map The Industry

Build a three-level Markdown tree showing:

- Major segments
- Value chain and participants
- Products and use cases
- Customer groups
- Revenue flows
- Important relationships between nodes

Save it to `Industry-Map.md`.

### 3. Analyze Competitors

For each relevant competitor, capture:

- Positioning and target customer
- Product and pricing structure
- Navigation, collection, tag, landing-page, blog, and SEO structure when applicable
- Sales and distribution channels
- Content and social strategy
- Business model and likely growth loop
- Evidence, uncertainties, and lessons

Prefer a representative set of verified competitors over an arbitrary large list.

### 4. Study Customers And Content

Research customer pain points, goals, objections, frequently asked questions, and buying language.

For the content ecosystem, identify representative accounts and classify recurring content into:

- Exposure
- Growth
- Save
- Conversion
- Personal brand

Look for repeatable patterns, not isolated viral examples.

### 5. Identify Opportunities

Create `Opportunities.md` with:

- Underserved customer problems
- Fast-growing segments
- Content gaps
- Product or service opportunities
- Competitive risks
- Evidence and confidence level
- Recommended next validation step

Separate verified facts from inferences.

### 6. Design Monitoring

Create a lightweight monitoring plan under `Monitoring/`:

- Important sources and update frequency
- Competitor changes to watch
- Emerging products and keywords
- High-growth content
- Suggested weekly intelligence report structure

Create an automation only when the user explicitly asks for recurring monitoring.

## Evidence Rules

- Add source URLs and access dates for current claims.
- Prefer primary sources and clearly label estimates.
- Never invent market size, revenue, traffic, or rankings.
- Distinguish `Fact`, `Inference`, and `Unknown`.
- Note research gaps and conflicting evidence.
- Use absolute dates instead of vague relative dates.

## Completion

Before finishing:

1. Verify internal Markdown links and file paths.
2. Ensure the dashboard summarizes the most important findings.
3. Report what was created, key conclusions, and remaining gaps.

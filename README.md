# Public Health AI Watch

A responsive daily news briefing about AI governance in U.S. public health. The website runs without JavaScript build tools, paid APIs, or API keys. Python 3.12+ runs the news collector using only its standard library.

## Preview locally

From the repository directory:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

The repository includes a successfully collected briefing. Run `python3 scripts/collect_news.py` to refresh it with current stories. Network access to `news.google.com` is required. Google News links lead to the original publishers through Google's news redirect. Summaries are topic descriptions, not AI-generated article summaries. No full articles are copied. If sample data is used during design, the site labels it explicitly and the workflow refuses to save it.

## Checks

```sh
scripts/check.sh
```

This runs the unit tests and a JavaScript syntax check. GitHub Actions runs it on every push and pull request (**Actions → Tests**). In Claude Code sessions, a Stop hook in `.claude/settings.json` runs it whenever Claude finishes a turn and sends any failure back to Claude to fix.

## Put the site online (beginner steps)

Vercel hosts the website, and GitHub Actions refreshes the news.

1. In Vercel, import this GitHub repository with the **Other** framework preset and no build command. Vercel deploys every push to `main`.
2. On GitHub, open **Settings → Actions → General → Workflow permissions** and choose **Read and write permissions**, so the workflow can save each briefing.
3. Open **Actions → Collect daily briefing → Run workflow** to test it. A successful run saves a fresh `data/articles.json` to `main`, and Vercel redeploys the site.
4. The workflow runs daily at 12:17 UTC (7:17 a.m. Central daylight time / 6:17 a.m. Central standard time). GitHub may delay scheduled runs. Schedules require the workflow on the default branch; inactive public repositories may have scheduled workflows disabled after 60 days. Each daily commit counts as activity.

## How collection works

Four Google News RSS searches cover oversight, equity, privacy, and safety. The collector requires AI, health, and governance terms in each headline, selects results from the last 30 days, deduplicates headlines, and retains recent collected items across updates. U.S. search settings and queries favor U.S. coverage but can include international context. Strict headline filtering can miss relevant stories. This is a focused news discovery service, not an exhaustive search of every website. Topic assignment follows the search feed, so editorial review may be useful.

If all feeds fail or no recent results are found, collection exits with an error without overwriting existing data. The website keeps showing the previous briefing, whose visible collection date remains unchanged. The workflow refuses to save sample-only data. Git history keeps every saved briefing. No attempt is made to bypass publisher paywalls.

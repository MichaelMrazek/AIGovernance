# Public Health AI Watch

A responsive daily news briefing about AI governance in U.S. public health. The website runs without JavaScript build tools, paid APIs, or API keys. Python 3.12+ runs the news collector using only its standard library.

## Preview locally

From the repository directory:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

The repository includes a successfully collected briefing. Run `python3 scripts/collect_news.py` to refresh it with current stories. Network access to `news.google.com` is required. Google News links lead to the original publishers through Google's news redirect. Summaries are topic descriptions, not AI-generated article summaries. No full articles are copied. If sample data is used during design, the site labels it explicitly and the publishing workflow refuses to publish it.

## Checks

```sh
python3 -m unittest discover -s tests -v
node --check app.js
```

## Put the site online (beginner steps)

1. Save these files to your GitHub repository's `main` branch. A commit is simply a saved version of your files.
2. On GitHub, open the repository's **Settings → Pages**. Under **Build and deployment**, choose **GitHub Actions** as the source.
3. Open **Actions → Collect and publish daily briefing → Run workflow**. The first successful run collects news and publishes the website. GitHub will show the public website address in **Settings → Pages**.
4. The workflow runs daily at 12:17 UTC (7:17 a.m. Central daylight time / 6:17 a.m. Central standard time). GitHub may delay scheduled runs. Schedules require the workflow on the default branch; inactive public repositories may have scheduled workflows disabled after 60 days.

The cloud environment does not itself provide permanent hosting or a daily scheduler. GitHub Pages and GitHub Actions provide those once enabled. This repository has not yet been pushed or published by the setup task.

## How collection works

Four Google News RSS searches cover oversight, equity, privacy, and safety. The collector requires AI, health, and governance terms in each headline, selects results from the last 30 days, deduplicates headlines, and retains recent collected items across updates. U.S. search settings and queries favor U.S. coverage but can include international context. Strict headline filtering can miss relevant stories. This is a focused news discovery service, not an exhaustive search of every website. Topic assignment follows the search feed, so editorial review may be useful.

If all feeds fail or no recent results are found, collection exits with an error without overwriting existing data. The publishing workflow can use its cached previous briefing, whose visible collection date remains unchanged. It refuses to publish sample-only data. GitHub cache entries can expire, so the cache is not a permanent archive. No attempt is made to bypass publisher paywalls.

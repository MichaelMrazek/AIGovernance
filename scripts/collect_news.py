#!/usr/bin/env python3
"""Collect public Google News RSS results without credentials or paid APIs."""
import argparse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
QUERIES = {
    'Policy & oversight': '"artificial intelligence" ("public health" OR CDC OR HHS OR FDA) (policy OR governance OR regulation OR oversight) when:30d',
    'Health equity': '"artificial intelligence" ("public health" OR healthcare) (equity OR bias OR discrimination) (US OR U.S. OR American OR federal) when:30d',
    'Privacy & data': '"artificial intelligence" ("public health" OR HHS OR healthcare) (privacy OR HIPAA OR surveillance OR consent) when:30d',
    'Safety & standards': '"artificial intelligence" (FDA OR CDC OR "public health") (safety OR standards OR accountability OR validation) when:30d',
}

def relevant(title):
    """Require AI, health, and governance signals in each headline."""
    if re.search(r'\b(private equity|data cent(?:re|er)s?)\b', title, re.I):
        return False
    ai = r'\b(ai|artificial intelligence|algorithm\w*|machine learning)\b'
    health = r'\b(health\w*|medical|clinical|patient\w*|hospital\w*|fda|hhs|cdc|medicin\w*)\b'
    governance = r'\b(govern\w*|polic\w*|regulat\w*|oversight|equity|bias\w*|privacy|hipaa|consent|safety|standard\w*|accountab\w*|ethic\w*|trust|ban\w*|law\w*|legislat\w*|guid\w*|risk\w*|responsib\w*|validat\w*)\b'
    foreign = r'\b(oman|india|indian|china|chinese|europe|european|uk|britain|british|australia|australian)\b'
    domestic = r'\b(u\.?s\.?|united states|american|fda|hhs|cdc)\b'
    return (all(re.search(pattern, title, re.I) for pattern in (ai, health, governance))
            and (not re.search(foreign, title, re.I) or re.search(domestic, title, re.I)))

def parse_feed(payload, topic, now):
    results = []
    for item in ET.fromstring(payload).findall('./channel/item'):
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        source = (item.findtext('source') or 'Original reporting').strip()
        try:
            published = parsedate_to_datetime(item.findtext('pubDate') or '')
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError, OverflowError):
            continue
        if not title or urlsplit(link).scheme != 'https' or not urlsplit(link).hostname:
            continue
        if published < now - timedelta(days=30) or published > now + timedelta(days=1):
            continue
        if title.endswith(' - ' + source):
            title = title[:-(len(source) + 3)]
        if not relevant(title):
            continue
        results.append({'id': hashlib.sha256(link.encode()).hexdigest()[:16],
                        'title': title, 'url': link, 'source': source,
                        'publishedAt': published.isoformat(), 'topic': topic,
                        'description': f'Reporting from {source} on {topic.lower()} in health AI. Follow the source link for the full story and context.'})
    return results

def deduplicate(articles):
    seen, result = set(), []
    for a in sorted(articles, key=lambda a: a['publishedAt'], reverse=True):
        # A story can appear in multiple feeds with different Google tracking links.
        key = re.sub(r'\W+', '', a['title'].casefold())
        if key not in seen:
            seen.add(key)
            result.append(a)
    return result[:150]

def collect(output):
    now = datetime.now(timezone.utc)
    articles, failures = [], []
    for topic, query in QUERIES.items():
        url = 'https://news.google.com/rss/search?' + urlencode({'q': query, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'})
        try:
            request = Request(url, headers={'User-Agent': 'PublicHealthAIWatch/1.0 RSS reader'})
            with urlopen(request, timeout=30) as response:
                articles.extend(parse_feed(response.read(4_000_000), topic, now))
        except Exception as error:
            failures.append(topic)
            print(f'{topic}: {type(error).__name__}: {error}', file=sys.stderr)
    if len(failures) == len(QUERIES):
        raise RuntimeError('All feeds failed; the existing briefing was preserved.')
    if output.exists():
        old = json.loads(output.read_text())
        if not old.get('demo'):
            articles.extend(a for a in old.get('articles', []) if relevant(a['title']) and datetime.fromisoformat(a['publishedAt']) >= now-timedelta(days=30))
    articles = deduplicate(articles)
    if not articles:
        raise RuntimeError('No recent stories were found; the existing briefing was preserved.')
    data = {'updatedAt': now.isoformat(), 'demo': False, 'articles': articles,
            'warning': 'Some sources could not be refreshed; previously collected stories are retained.' if failures else None}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(output)
    print(f'Collected {len(articles)} stories; {len(failures)} feeds failed.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/articles.json')
    args = parser.parse_args()
    try:
        collect(args.output)
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)

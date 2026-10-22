from datetime import datetime
import importlib.util
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('collector', ROOT / 'scripts/collect_news.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

class SiteTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'index.html').read_text()
        self.js = (ROOT / 'app.js').read_text()

    def test_page_assets_exist(self):
        for asset in re.findall(r'(?:href|src)="([^"#:]+)"', self.html):
            if asset not in ('./',):
                self.assertTrue((ROOT / asset).is_file(), f'index.html references missing file {asset}')

    def test_script_elements_exist_in_page(self):
        ids = set(re.findall(r'id="([^"]+)"', self.html))
        for element in set(re.findall(r"el\('([^']+)'\)", self.js)):
            self.assertIn(element, ids, f'app.js looks up #{element}, which index.html lacks')

    def test_page_topics_match_collector(self):
        topics = re.search(r'topics\s*=\s*\[([^\]]*)\]', self.js).group(1)
        self.assertEqual(re.findall(r"'([^']+)'", topics)[1:], list(collector.QUERIES))

class BriefingDataTests(unittest.TestCase):
    def test_saved_briefing_is_publishable(self):
        data = json.loads((ROOT / 'data/articles.json').read_text())
        self.assertFalse(data.get('demo'), 'Sample data must not be committed')
        datetime.fromisoformat(data['updatedAt'])
        self.assertTrue(data['articles'])
        for article in data['articles']:
            self.assertTrue(article['title'].strip())
            self.assertEqual(urlparse(article['url']).scheme, 'https', article['url'])
            datetime.fromisoformat(article['publishedAt'])
            self.assertIn(article['topic'], collector.QUERIES)

if __name__ == '__main__':
    unittest.main()

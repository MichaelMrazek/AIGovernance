from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('collector', Path(__file__).resolve().parents[1] / 'scripts/collect_news.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

class CollectorTests(unittest.TestCase):
    def test_parsing_dates_sources_and_untrusted_links(self):
        feed = b'''<rss><channel>
        <item><title>New health AI oversight - Example News</title><source>Example News</source><link>https://example.com/story</link><pubDate>Wed, 14 Oct 2026 10:00:00 GMT</pubDate></item>
        <item><title>Unsafe</title><link>javascript:alert(1)</link><pubDate>Wed, 14 Oct 2026 10:00:00 GMT</pubDate></item>
        <item><title>Old</title><link>https://example.com/old</link><pubDate>Wed, 01 Jan 2020 10:00:00 GMT</pubDate></item>
        <item><title>No date</title><link>https://example.com/invalid</link></item>
        </channel></rss>'''
        articles = collector.parse_feed(feed, 'Policy & oversight', datetime(2026,10,14,tzinfo=timezone.utc))
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['title'], 'New health AI oversight')
        self.assertEqual(articles[0]['source'], 'Example News')

    def test_duplicate_headlines_across_feeds(self):
        a = {'title':'AI policy: new rules', 'publishedAt':'2026-10-14T00:00:00+00:00'}
        b = {'title':'AI policy — new rules', 'publishedAt':'2026-10-13T00:00:00+00:00'}
        self.assertEqual(collector.deduplicate([b,a]), [a])

    def test_relevance_rejects_unrelated_and_foreign_reporting(self):
        self.assertFalse(collector.relevant('Best equity stocks to buy'))
        self.assertFalse(collector.relevant('Oman health equity AI policies'))
        self.assertFalse(collector.relevant('FDA warning on food safety'))
        self.assertTrue(collector.relevant('California bans AI medical decisions without oversight'))

    def test_failed_collection_preserves_previous_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'articles.json'
            path.write_text('{"articles": []}')
            with patch.object(collector, 'urlopen', side_effect=OSError('offline')):
                with self.assertRaisesRegex(RuntimeError,'All feeds failed'):
                    collector.collect(path)
            self.assertEqual(path.read_text(), '{"articles": []}')

if __name__ == '__main__':
    unittest.main()

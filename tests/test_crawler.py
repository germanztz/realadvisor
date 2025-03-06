import unittest
import sys
sys.path.append('src/crawler')
from crawler import Crawler
from pathlib import Path

class TestCrawler(unittest.TestCase):

    def setUp(self):
        pass

    def test_crawler_item(self):

        crawler = Crawler(webs_specs_datafile_path = 'tests/webs_specs.example.csv', realty_datafile_path = None, cache_dir = None, cache_expires=None)
        anitem = crawler.crawl_item('fotocasa', None, dry_run=True)
        anitem = anitem[0]        
        self.assertEqual(anitem['link'], 'https://www.fotocasa.es/es/comprar/vivienda/barcelona-capital/no-amueblado/185497469/d')


if __name__ == '__main__':
    unittest.main()

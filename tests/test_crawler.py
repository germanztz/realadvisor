import unittest
import sys
sys.path.append('src/crawler')
from crawler import Crawler
from pathlib import Path

class TestCrawler(unittest.TestCase):

    def setUp(self):
        pass

    def test_crawler_item(self):

        crawler = Crawler(webs_specs_datafile_path = None, realty_datafile_path = None, cache_dir = None, cache_expires=None)
        anitem = crawler.crawl_item('fotocasa', None, dry_run=True)
        anitem = anitem[0]        
        self.assertEqual(anitem['link'], 'https://www.fotocasa.es/es/comprar/vivienda/barcelona-capital/no-amueblado/185497469/d')
        self.assertEqual(anitem['type_v'], 'Flat')
        self.assertEqual(anitem['address'], 'Nou Barris, Les Roquetes, 08042, Barcelona')
        self.assertEqual(anitem['town'], "Nou Barris")
        self.assertEqual(anitem['price'], '95000')
        self.assertEqual(anitem['rooms'], '1')
        self.assertEqual(anitem['surface'], '50')
        self.assertEqual(anitem['price_old'], '38000')
        self.assertEqual(len(anitem['info']), 13)
        self.assertEqual(len(anitem['description']), 144)
        self.assertEqual(anitem['tags'], None)
        self.assertEqual(anitem['agent'], 'https://www.fotocasa.es/es/inmobiliaria-gc-inmobiliaria/comprar/inmuebles/espana/todas-las-zonas/l?clientId=9202752587558')
        self.assertEqual(len(anitem['images']), 16)


if __name__ == '__main__':
    unittest.main()

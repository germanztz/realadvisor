import unittest
import sys
import re
sys.path.append('src/crawler')
from web_scraper import WebScraper
from pathlib import Path

class TestWebScraper(unittest.TestCase):

    def setUp(self):
        self.list_items_rx = {'list_items_rx':re.compile(r'<article class="item(.+?)</article>', re.DOTALL)}

        self.list_item_fields_rx = {
            'link': re.compile(r'<a href="(/inmueble/\d+?/)" role="heading" aria-level="2" class="item-link " title=".+? en .+?">'),
            'type_v': re.compile(r'<a href=".+?" role="heading" aria-level="2" class="item-link " title="(.+?) en .+?">'),
            'address': re.compile(r'<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">'),
            'town': re.compile(r'<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">'),
            'price': re.compile(r'<span class="item-price h2-simulated">(.+?)<span class="txt-big">€</span></span>'),
            'rooms': re.compile(r'<span class="item-detail">(\d+) hab.</span>'),
            'surface': re.compile(r'<span class="item-detail">(\d+) m²</span>'),
            'price_old': re.compile(r'<span class="pricedown_price">(.+?) €</span>'),
            'info_sub': re.compile(r'<div class="item-detail-char">(.+?)</div>'),
            'info_elem': re.compile(r'<span class="item-detail">(.*?)</span>', re.DOTALL),
            'description': re.compile(r'<div class="item-description description">(.+?)</div>'),
            'tags': re.compile(r'<span class="listing-tags ">(.+?)</span>', re.DOTALL),
            'agent': re.compile(r'<span class="hightop-agent-name">(.+?)</span>')
        }

        self.list_next_rx = {'list_next_rx':re.compile(r'<li class="next"><a rel="nofollow" class="icon-arrow-right-after" href="(.+?)">')}

        self.detail_item_fields_rx = {
            'link': re.compile(r'<link rel="canonical" href="https://www.idealista.com(.+?)"/>'),
            'type_v': re.compile(r'<span class="main-info__title-main">(.+?) en venta en .+?</span>'),
            'address': re.compile(r'<span class="main-info__title-main">.+? en venta en (.+?)</span>'),
            'town': re.compile(r'<span class="main-info__title-minor">(.+?)</span>'),
            'price': re.compile(r'<span class="info-data-price"><span class="txt-bold">(.+?)</span>'),
            'rooms': None,
            'surface': None,
            'price_old': re.compile(r'<span class="pricedown_price">(.+?) €</span>'),
            'info_sub': re.compile(r'<section id="details" class="details-box">(.*?)</section>'),
            'info_elem': re.compile(r'<li>(.*?)</li>', re.DOTALL),
            'description': re.compile(r'<div class="adCommentsLanguage.+?><p>(.+?)</p></div>', re.DOTALL),
            'tags': re.compile(r'<span class="tag ">(.+?)</span>', re.DOTALL),
            'agent': re.compile(r'<h2 class="aditional-link_title .+? href="(.+?)".+?</a>'),
        }

        self.url = 'https://www.TestWebScraper.local'
        self.datafile = Path(__file__+'_datafile.csv')
        
        self.post_fields_lambda = {
            'link': lambda m: f"https://www.TestWebScraper.local{m}" if isinstance(m, str) else m,
            # 'info_sub': lambda m: ','.join(m) if isinstance(m, list) else m,
            'description': lambda m: re.sub(r"<.*?>", " ", m) if isinstance(m, str) else m
        }

    def test_parse_list(self):
        webScraper = WebScraper(self.url, self.datafile, self.list_items_rx, self.list_item_fields_rx, self.list_next_rx, self.detail_item_fields_rx, self.post_fields_lambda)
        alist = webScraper.parse_list(open('tests/idealista_lista.html', 'r').read().replace("\n", "").replace("\r", ""), self.list_items_rx, self.list_item_fields_rx, self.post_fields_lambda)
        print(alist)
        self.assertEqual(len(alist), 30)

    def test_parse_item(self):
        webScraper = WebScraper(self.url, self.datafile, self.list_items_rx, self.list_item_fields_rx, self.list_next_rx, self.detail_item_fields_rx, self.post_fields_lambda)
        anitem = webScraper.parse_item(open('tests/idealista_detalle.html', 'r').read().replace("\n", "").replace("\r", ""), self.detail_item_fields_rx, self.post_fields_lambda)
        self.assertEqual(anitem['link'], 'https://www.TestWebScraper.local/inmueble/105043094/')
        self.assertEqual(anitem['type_v'], 'Piso')
        self.assertEqual(anitem['address'], 'paseo de Gràcia')
        self.assertEqual(anitem['town'], "La Dreta de l'Eixample, Barcelona")
        self.assertEqual(anitem['price'], '1.350.000')
        self.assertEqual(anitem['price_old'], '1.400.000')
        self.assertEqual(len(anitem['info']), 13)
        self.assertEqual(len(anitem['description']), 2438)
        self.assertEqual(anitem['tags'], 'Luminoso')
        self.assertEqual(anitem['agent'], 'https://www.bcn-advisors.com/propiedades/impresionante-y-tranquilo-piso-de-lujo-reformado-en-paseo-de-gracia')


if __name__ == "__main__":
    unittest.main()
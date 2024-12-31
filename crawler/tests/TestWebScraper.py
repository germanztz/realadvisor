import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from webScraper import WebScraper
import re

class TestWebScraper(unittest.TestCase):

    def setUp(self):
        self.list_items_rx = re.compile(r'<article class="item(.+?)</article>', re.DOTALL)

        self.list_item_fields_rx = {
            'link': re.compile(r'<a href="(/inmueble/\d+?/)" role="heading" aria-level="2" class="item-link " title=".+? en .+?">'),
            'type_v': re.compile(r'<a href=".+?" role="heading" aria-level="2" class="item-link " title="(.+?) en .+?">'),
            'address': re.compile(r'<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">'),
            'town': re.compile(r'<a href=".+?" role="heading" aria-level="2" class="item-link " title=".+? en (.+?)">'),
            'price': re.compile(r'<span class="item-price h2-simulated">(.+?)<span class="txt-big">€</span></span>'),
            'price_old': re.compile(r'<span class="pricedown_price">(.+?) €</span>'),
            'info_sub': re.compile(r'<div class="item-detail-char">(.+?)</div>'),
            'info_elem': re.compile(r'<span class="item-detail">(.*?)</span>', re.DOTALL),
            'description': re.compile(r'<div class="item-description description">(.+?)</div>'),
            'tags': re.compile(r'<span class="listing-tags ">(.+?)</span>', re.DOTALL),
            'agent': re.compile(r'<span class="hightop-agent-name">(.+?)</span>')
        }

        self.list_next_rx = re.compile(r'<li class="next"><a rel="nofollow" class="icon-arrow-right-after" href="(.+?)">')

        self.detail_item_fields_rx = {
            'link': re.compile(r'<link rel="canonical" href="https://www.idealista.com(.+?)"/>'),
            'type_v': re.compile(r'<span class="main-info__title-main">(.+?) en venta en .+?</span>'),
            'address': re.compile(r'<span class="main-info__title-main">.+? en venta en (.+?)</span>'),
            'town': re.compile(r'<span class="main-info__title-minor">(.+?)</span>'),
            'price': re.compile(r'<span class="info-data-price"><span class="txt-bold">(.+?)</span>'),
            'price_old': re.compile(r'<span class="pricedown_price">(.+?) €</span>'),
            'info_sub': re.compile(r'<section id="details" class="details-box">(.*?)</section>'),
            'info_elem': re.compile(r'<li>(.*?)</li>', re.DOTALL),
            'description': re.compile(r'<div class="adCommentsLanguage.+?><p>(.+?)</p></div>', re.DOTALL),
            'tags': re.compile(r'<span class="tag ">(.+?)</span>', re.DOTALL),
            'agent': re.compile(r'<h2 class="aditional-link_title .+? href="(.+?)".+?</a>'),
        }

        self.url = 'https://www.TestWebScraper.local'
        self.datafile = __file__+'_datafile.csv'

    def test_parse_list(self):
        webScraper = WebScraper(self.url, self.datafile, self.list_items_rx, self.list_item_fields_rx, self.list_next_rx, self.detail_item_fields_rx)
        alist = webScraper.parse_list(open('data-science-uoc/tfm/crawler/tests/idealista_lista_de_viviendas2.html', 'r').read(), self.list_items_rx, self.list_item_fields_rx)
        self.assertEqual(len(alist), 30)

    def test_parse_item(self):
        webScraper = WebScraper(self.url, self.datafile, self.list_items_rx, self.list_item_fields_rx, self.list_next_rx, self.detail_item_fields_rx)
        anitem = webScraper.parse_item(open('data-science-uoc/tfm/crawler/tests/idealista_detalle_vivienda.html', 'r').read(), self.detail_item_fields_rx)
        self.assertEqual(len(anitem), 11)


if __name__ == "__main__":
    unittest.main()
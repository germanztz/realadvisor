import unittest
import sys
import re
import datetime
from pathlib import Path
sys.path.append('src/crawler')
from scraper import Scraper

class TestScraper(unittest.TestCase):

    def setUp(self):
        
        self.ideal_list_items = {'list_items_rx':re.compile(r'<article class="item(.+?)</article>', re.DOTALL)}
        self.ideal_list_next = {'list_next_rx':re.compile(r'<li class="next"><a rel="nofollow" class="icon-arrow-right-after" href="(.+?)">')}
        self.ideal_list_fields = {
            'created': re.compile(r'(^.)'),
            'link': re.compile(r'<a href="(/inmueble/\d+?/)" role="heading" aria-level="2" class="item-link " title=".+? en .+?">'),}
        self.ideal_detail_fields = {
            'created': re.compile(r'(^.)'),
            'link': re.compile(r'<link rel="canonical" href="https://www.idealista.com(.+?)"/>'),}
        self.ideal_lambda = {
            'link': lambda m: f"https://www.testscraper.local{m}" if isinstance(m, str) else m,}

        self.foto_list_items = { 'list_items': re.compile(r'accuracy(.+?)userId',re.DOTALL)}
        self.foto_list_next =  { 'next_page': re.compile(r'"rel":"next","href":"(.*?)"') }
        self.foto_list_fields = {
            'created': re.compile(r'(^.)'),
            'link': re.compile(r'"detail":.*?:"(.*?)"'),}
        self.foto_detail_fields = {
            'created': re.compile(r'(^.)'),
            'link': re.compile(r'"realEstate":.*"detail":.*"es-ES":"(.+?)"'),}
        self.foto_list_lambda = {
            'created': lambda m: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'link': lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}" ,}
        self.foto_detail_lambda = {
            'created': lambda m: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'link': lambda m: f"https://www.fotocasa.es{m}" if isinstance(m, str) else f"https://www.fotocasa.es{m.group(1)}" ,}

    def test_parse_list_idealista(self):
        with open('tests/idealista_lista.html', 'r') as file:
            content = file.read()
            content = Scraper.CLEAN_RX.sub('', content)
            alist = Scraper().parse_list(content, self.ideal_list_items, self.ideal_list_fields, self.ideal_lambda, self.ideal_lambda)
            anitem = alist[0]

            self.assertEqual(len(alist), 30)
            self.assertEqual(anitem['link'], 'https://www.testscraper.local/inmueble/106590362/')
            # self.assertEqual(anitem['type_v'], 'Piso')
            # self.assertEqual(anitem['address'], 'calle de Vidal i Guasch, Les Roquetes, Barcelona')
            # self.assertEqual(anitem['town'], "calle de Vidal i Guasch, Les Roquetes, Barcelona")
            # self.assertEqual(anitem['price'], '95.000')
            # self.assertEqual(anitem['price_old'], None)
            # self.assertEqual(len(anitem['info']), 3)
            # self.assertEqual(len(anitem['description']), 320)
            # self.assertEqual(anitem['tags'], None)
            # self.assertEqual(anitem['agent'], None)
            # self.assertEqual(anitem['images'], 'https://img4.idealista.com/blur/WEB_LISTING-M/0/id.pro.es.image.master/67/39/78/1287885473.jpg')

    def test_parse_item_idealista(self):
        with open('tests/idealista_detalle.html', 'r') as file:
            content = file.read()
            content = Scraper.CLEAN_RX.sub('', content)
            anitem = Scraper().parse_item(content, self.ideal_detail_fields, self.ideal_lambda)
            self.assertEqual(anitem['link'], 'https://www.testscraper.local/inmueble/105043094/')
            # self.assertEqual(anitem['type_v'], 'Piso')
            # self.assertEqual(anitem['address'], 'paseo de Gràcia')
            # self.assertEqual(anitem['town'], "La Dreta de l'Eixample, Barcelona")
            # self.assertEqual(anitem['price'], '1.350.000')
            # self.assertEqual(anitem['price_old'], '1.400.000')
            # self.assertEqual(len(anitem['info']), 13)
            # self.assertEqual(len(anitem['description']), 2438)
            # self.assertEqual(anitem['tags'], 'Luminoso')
            # self.assertEqual(anitem['agent'], 'https://www.bcn-advisors.com/propiedades/impresionante-y-tranquilo-piso-de-lujo-reformado-en-paseo-de-gracia')
            # self.assertEqual(anitem['images'], 'https://img4.idealista.com/blur/WEB_DETAIL_TOP-L-L/0/id.pro.es.image.master/9a/b9/f3/1240865377.jpg')

    def test_parse_list_fotocasa(self):
        with open('tests/fotocasa_lista.html', 'r') as file:
            content = file.read()
            content = Scraper.CLEAN_RX.sub('', content)
            alist = Scraper().parse_list(content, self.foto_list_items, self.foto_list_fields, self.foto_list_lambda, self.foto_detail_lambda)
            anitem = alist[0]
            self.assertEqual(len(alist), 30)
            self.assertEqual(anitem['link'], 'https://www.fotocasa.es/es/comprar/vivienda/barcelona-capital/aire-acondicionado-no-amueblado/185311924/d')
            # self.assertEqual(anitem['type_v'], 'Flat')
            # self.assertEqual(anitem['address'], 'Nou Barris, Ciutat Meridiana, 08033, Barcelona')
            # self.assertEqual(anitem['town'], "Nou Barris")
            # self.assertEqual(anitem['price'], '48000')
            # self.assertEqual(anitem['rooms'], '2')
            # self.assertEqual(anitem['surface'], '50')
            # self.assertEqual(anitem['price_old'], None)
            # self.assertEqual(len(anitem['info']), 20)
            # self.assertEqual(len(anitem['description']), 847)
            # self.assertEqual(anitem['tags'], None)
            # self.assertEqual(anitem['agent'], 'https://www.fotocasa.es/es/comprar/inmuebles/espana/todas-las-zonas/l?clientId=9202770754462')
            # self.assertEqual(len(anitem['images']), 13)
            # self.assertEqual(anitem['images'][0], 'https://static.fotocasa.es/images/ads/489a1418-9c27-4ad7-92bd-8e19d8318912?rule=original')

    def test_parse_item_fotocasa(self):
        with open('tests/fotocasa_detalle.html', 'r') as file:
            content = file.read()
            content = Scraper.CLEAN_RX.sub('', content)
            anitem = Scraper().parse_item(content, self.foto_detail_fields, self.foto_detail_lambda)
            self.assertEqual(anitem['link'], 'https://www.fotocasa.es/es/comprar/vivienda/barcelona-capital/no-amueblado/185497469/d')
            # self.assertEqual(anitem['type_v'], 'Flat')
            # self.assertEqual(anitem['address'], 'Nou Barris, Les Roquetes, 08042, Barcelona')
            # self.assertEqual(anitem['town'], "Nou Barris")
            # self.assertEqual(anitem['price'], '95000')
            # self.assertEqual(anitem['rooms'], '1')
            # self.assertEqual(anitem['surface'], '50')
            # self.assertEqual(anitem['price_old'], '38000')
            # self.assertEqual(len(anitem['info']), 13)
            # self.assertEqual(len(anitem['description']), 144)
            # self.assertEqual(anitem['tags'], None)
            # self.assertEqual(anitem['agent'], 'https://www.fotocasa.es/es/inmobiliaria-gc-inmobiliaria/comprar/inmuebles/espana/todas-las-zonas/l?clientId=9202752587558')
            # self.assertEqual(len(anitem['images']), 16)

    def test_error_empty_list(self):
        content = '<html><body>ERROR LOADING</body></html>'
        alist = Scraper().parse_list(content, self.foto_list_items, self.foto_list_fields, self.foto_list_lambda, self.foto_detail_lambda)

if __name__ == "__main__":
    unittest.main()
import sys
from pathlib import Path
import requests
import time
import random
import re
import html
import datetime
import pandas as pd
import os
import warnings
import logging
import logging.config
import hashlib
from fake_useragent import UserAgent
# from selenium import webdriver
from seleniumwire2 import webdriver
sys.path.append('src')
from telegram_handler import TelegramHandler

class Scraper:

    CLEAN_RX = re.compile(r'\n|\r|\\(?!u)')

    # TODO: Implementar sin pandas ni numpy

    def __init__(self, url=None, datafile_path: Path=None, list_items: dict=None,
        list_items_fields: dict=None, list_next: dict=None, detail_fields:dict=None,
        list_fields_lambda:dict=None, detail_fields_lambda:dict=None, 
        cache_dir: Path = None, cache_expires: int = 3600, delay_seconds: int = 30):
        '''
        Class for scraping a website and obtaining a database

        Parameters
        ----------
        url : str
            initial url of the website to scrape
        datafile_path : Path
            path of the file where the database will be saved
        list_items_rx : dict
            regular expression to obtain the items of the list view
        list_items_fields : dict
            dictionary of regular expressions to obtain the fields of each item of the list view
        list_next_rx : dict
            regular expression to obtain the link of the next page of the list view
        detail_fields : dict
            dictionary of regular expressions to obtain the fields of each item of the detail view
        list_fields_lambda : dict
            dictionary of lambda functions to obtain the fields of each item of the detail view
        '''
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Init')

        self.init_headers(url)
        self.datafile_path = datafile_path if datafile_path else None
        self.list_items_rx = list_items
        self.list_items_fields = list_items_fields
        self.detail_fields = detail_fields
        self.list_next_rx = list_next
        self.list_fields_lambda = list_fields_lambda
        self.detail_fields_lambda = detail_fields_lambda

        self.last_scaped_df = None
        self.main_data_df = None
        if self.datafile_path and self.datafile_path.exists():
            self.main_data_df = pd.read_csv(self.datafile_path)

        self.cache_dir = cache_dir
        self.cache_expires = cache_expires
        self.delay_seconds = delay_seconds

    def init_headers(self, url):
        self.set_url(url)

        self.headers = {
            'Host': self.base_host,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
            # 'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Cookie': 'reese84=3:R73lXZFfOnfUROHIrHUhFQ==:ODP9sh+kBOs4QKf8llBT4iMuDMzDZ/62fUksvcMSCeyGESPXfmunUQmEQhAKRTeDXtpzRrVah2/pL5mEdlFJp1hrpVgxHtcdO6IiVLns0FGp+Ty4dgEAFTaBMhdhDr+2h1DJfUDPD+gYimCgT95ciHHtvoehvfmtsZEp6b67W2xTQNP9pO3RLW7ajkVstlJP+tMgfxK60CeheojgYQ+hbhzlSebwTa3CxSBtq8Rje1AwH4LdHQvmrvGwC1LU9q4vjUkheUInWu2lBtB+Whz3N+8WB49kwcyeacxAfdnaIkBRfEKUAywB/fh4HHVipk42f163NAdN7JMP8yZhHF1sQvCn7u9IZP6RiY6N9kmmKRQYbMOQJaO8mR8YjXEiLYjy0fyLFb1Duj8T0emHARRbIA1fqHVYnETXkH9gMrUD8oCBAuQxh/QdTOp6SbE6SuoPCJRLBNNMpCnW933FWSojPKEoWVaBMM4TPvhhAu3zo/g=:ro28gQOmbzrsTi699lGXrgESafv8oSiJbY/4hGnJ6M4=; cu=es-es; ASP.NET_SessionId=jxobaxwisddsptg3lf2s3pkg; usunico=03/02/2025:18-17116579; auth=jxobaxwisddsptg3lf2s3pkg; segment_ga_MH0GDRSFGC=GS1.1.1738871458.15.1.1738872884.60.0.0; segment_ga=GA1.1.343924352.1736710205; AMCV_05FF6243578784B37F000101%40AdobeOrg=-408604571%7CMCIDTS%7C20126%7CMCMID%7C81088011721785289588500497039989405303%7CMCAID%7CNONE%7CMCOPTOUT-1738942758s%7CNONE%7CvVersion%7C4.6.0; re_uuid=4c10c1b8-bcff-4f77-ad57-4618fc39dd7a; AMCVS_05FF6243578784B37F000101%40AdobeOrg=1',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Priority': 'u=0, i',
            'TE': 'trailers'
        }

        self.logger.debug('Headers: %s', self.headers)
        return self.headers

    def set_url(self, url):
        """
        Sets a new URL for the Scraper instance.

        Args:
            url (str): The new URL to be set for the scraper.
        """
        if url is not None:
            self.url = url.strip()
            self.base_url_rx = re.search(r'https?://([^/]+)', self.url)
            self.base_url = self.base_url_rx.group(0)
            self.base_host = self.base_url_rx.group(1)
        else:
            self.logger.warning('URL was not provided. Using example URL.')
            self.url = 'https://www.example.com'
            self.base_url_rx = re.search(r'https?://([^/]+)', self.url)
            self.base_url = self.base_url_rx.group(0)
            self.base_host = self.base_url_rx.group(1)

        self.logger.info(f'URL set to {self.url}')

    def parse_field(self, html, field_name, fields_rx, field_lambdas=None):
        """
        Parses the specified field from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            field_name (str): The name of the field to extract from the HTML.
            fields_rx (dict): A dictionary containing regular expressions for each field.
            field_lambdas (dict): A dictionary containing lambda functions for each field.

        Returns:
            The extracted field value(s), or None if not found. If the field name contains 'sub',
            it searches for elements within the previously extracted value using a different regex.

        Raises:
            Exception: If there is an error during parsing.
        """
        try:
            regex = fields_rx[field_name]
            if regex is None: return None
            ret = regex.findall(html)
            ret = ret[0] if len(ret) == 1 else ret
            ret = None if len(ret) == 0 else ret
            if 'sub' in field_name and not ret is None:
                ret = fields_rx[field_name.replace('sub', 'elem')].findall(ret)
            if field_lambdas is not None and field_name in field_lambdas and ret is not None:
                ret = field_lambdas[field_name](ret)


            self.logger.debug(f'parse_field {field_name}: {ret}')
            return ret
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(field_name, regex)
            return None

    def parse_item(self, html, fields_rx, field_lambdas=None) -> dict:
        """
        Parses a post from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            fields_rx (dict): A dictionary containing regular expressions for each field.
            field_lambdas (dict): A dictionary containing lambda functions for each field.
        Returns:
            dict: A dictionary containing the extracted fields and their values. The dictionary

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """
        if fields_rx is None or html is None :
            self.logger.warning('No field specs')
            return None
            
        dict_item = dict()

        for field, rx in fields_rx.items():
            if '_elem' not in field:
                dict_item[field.replace('_sub', '')] = self.parse_field(html, field, fields_rx, field_lambdas)

        self.logger.debug(f'parse_item: {dict_item}')
        return dict_item

    def parse_list(self, html, list_items_rx, fields_rx, list_fields_lambda=None, detail_fields_lambda=None):
        """
        Parses a list of items from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            list_items_rx (regex): expresion regular para obtener los items de la vista listado
            fields_rx (dict): A dictionary containing regular expressions for each field.
            list_fields_lambda (dict): A dictionary containing lambda functions for each field.
        Returns:
            list: A list containing dictionaries with the extracted fields and their values.

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """
        if html is None or list_items_rx is None or fields_rx is None:
            self.logger.warning('No field specs')
            return []

        elements_html = self.parse_item(html, list_items_rx, list_fields_lambda)
        elements_html = elements_html[next(iter(list_items_rx.keys()))]
        list_columns = [f.replace('_sub', '') for f in fields_rx.keys() if 'elem' not in f]

        self.logger.debug(f'Campos a extraer: {list_columns}')

        if elements_html is None:
            self.logger.warning(f'la busqueda de elementos de la lista devolvió None {list_items_rx}')
            return None

        item_list = list()
        for elem_html in elements_html:
            item_list += [self.parse_item(elem_html, fields_rx, detail_fields_lambda)]

        self.logger.info(f'Elementos extraidos de la lista: {len(item_list)} elementos')
        return item_list

    def _get_cache_filepath(self):
        hash_url = hashlib.md5(self.url.encode()).hexdigest()
        return Path(os.path.join(self.cache_dir, f'{self.base_host}_{hash_url}.html'))

    def _get_cached_response(self):

        if self.cache_dir is None: return None

        ts = int(datetime.datetime.now().timestamp())
        cache_file = self._get_cache_filepath()

        if  (not Path(cache_file).exists()) or (not (ts - os.path.getmtime(cache_file)) < self.cache_expires):
            return None

        with open(cache_file, 'rb') as f:
            response = requests.Response()
            response._content = f.read()
            response.status_code = 304
            self.logger.info(f'Obtendiendo desde el cache: {cache_file}')
            return response

    def _set_cached_response(self, response):
        if (self.cache_dir is None) or (response is None):
            return response

        cache_file = self._get_cache_filepath()
        if cache_file.exists(): return response
        with open(cache_file, 'wb') as f:
            f.write(response.content)
        self.logger.debug(f'Response Saved to {cache_file}')

        return response

    def selenium_interceptor(self, request):

        del request.headers['sec-ch-ua']
        del request.headers['sec-ch-ua-mobile']
        del request.headers['sec-ch-ua-platform']
        for key,value in self.headers.items():
            del request.headers[key]
            request.headers[key] = value

        self.logger.info('Slenium Headers: %s', request.headers)

    def _get_selenium_chrome(self):
        self.logger.info(f'Obterniendo con Chrome: {self.url}')
        options = webdriver.ChromeOptions()
        # options.add_argument("-headless")
        driver = webdriver.Chrome(options=options)
        try:
            driver.request_interceptor = self.selenium_interceptor
            driver.get(self.url)
            time.sleep(4) # Allow page to fully load
            html_content = driver.page_source.encode('utf-8')
            response = requests.Response()
            response.status_code = 200
            response._content = html_content
            return response
        except Exception as e:
            self.logger.error(e)
            self.logger.exception(e)

        finally:
            if driver is not None:
                driver.quit()

    def _get_selenium_firefox(self):

        self.logger.info(f'Obterniendo con Firefox: {self.url}')
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        geckodriver_path = "/snap/bin/geckodriver"
        driver_service = webdriver.FirefoxService(executable_path=geckodriver_path)
        driver = webdriver.Firefox(options=options, service=driver_service)
        driver.request_interceptor = self.selenium_interceptor
        driver.get(self.url)
        time.sleep(4) # Allow page to fully load
        response = requests.Response()
        response.status_code = 200
        response._content = driver.page_source.encode('utf-8')
        return response

    def _get_request_response(self):

        self.logger.info(f'Obterniendo con Request: {self.url}')
        session = requests.Session()
        session.headers.update(self.headers)
        response = session.get(self.url, headers=self.headers)

        self.logger.debug(f'Response status: {response.status_code}')
        return response

    def get_response(self, url = None, use_cache = True, driver = 'default'):

        if url is not None: self.init_headers(url)

        if use_cache:
            response = self._get_cached_response() 
            if response is not None: 
                return response

        seconds = random.uniform(self.delay_seconds / 2, self.delay_seconds)
        self.logger.info(f'Waiting {seconds:.0f} secs delay')
        time.sleep(seconds)

        if driver == 'chrome':
            response = self._get_selenium_chrome()
        elif driver == 'firefox': 
            response = self._get_selenium_firefox()
        else: 
            response = self._get_request_response()

        if response.status_code >= 400:
            self.logger.error(f"Error al enviar la solicitud: {response.status_code}: {response.reason}")
            return None

        return self._set_cached_response(response) if use_cache else response

    def get_content(self, response):
        content = response.content.decode('utf-8')
        content = Scraper.CLEAN_RX.sub('', content)

        self.logger.debug(f'Contenido de la página: {content}')
        return content

    def scrap_list(self):
        """
            Runs the web crawling and scraping process for the specified URL.

            This method starts the web crawling and scraping process for the specified URL.
            It uses the regular expressions defined in the constructor to parse the content
            of the web pages.

            The information is stored in a Pandas DataFrame and saved to a CSV file specified
            in the constructor.

            Returns:
                None """
        start = time.perf_counter()
        response = self.get_response()
        if response is not None:
            content = self.get_content(response)
            curr_page = self.parse_list(content, self.list_items_rx, self.list_items_fields, self.list_fields_lambda, self.detail_fields_lambda)
            hay_repetidos = self.store_page_csv(curr_page)
            self.logger.info(f'Tiempo transcurrido: {time.perf_counter() - start}')
            self.paginate(content, hay_repetidos)

        self.clean_cache_dir()

    def scrap_item(self):
        start = time.perf_counter()
        response = self.get_response()
        if response is not None:
            content = self.get_content(response)
            data = self.parse_item(content, self.detail_fields, self.list_fields_lambda)
            hay_repetidos = self.store_page_csv([data])
            self.logger.info(f'Tiempo transcurrido: {time.perf_counter() - start}')

        self.clean_cache_dir()

    def store_page_csv(self, curr_page):

        if self.datafile_path is None: return
        if curr_page is None or len(curr_page) == 0: return

        hay_repetidos = False
        curr_page_df = pd.DataFrame(curr_page)
        self.last_scaped_df= pd.concat([self.last_scaped_df, curr_page_df], ignore_index=True)
        if (self.main_data_df is not None):
            repetidos = curr_page_df['link'].isin(self.main_data_df['link'])
            hay_repetidos = repetidos.any()
            curr_page_df = curr_page_df[~repetidos]
        # print('main_data_df',self.main_data_df)
        if not curr_page_df.empty:
            self.main_data_df = pd.concat([self.main_data_df, curr_page_df], ignore_index=True)
            self.main_data_df.to_csv(self.datafile_path, index=False)
        self.logger.info(f"Elementos añadidos a la bbdd: {len(curr_page_df)}")
        return hay_repetidos

    def paginate(self, content, hay_repetidos):

        next_href = self.parse_item(content, self.list_next_rx, self.list_fields_lambda)
        next_href = next_href[next(iter(self.list_next_rx.keys()))] if next_href else None
        if next_href is None:
            self.logger.info('Finalizado, se ha procesado la última página')
        elif hay_repetidos:
            self.logger.info('Finalizado, se han procesado los nuevos elementos')
        else:
            self.set_url(next_href)
            self.scrap_list()

    def get_scraped_items(self):
        return self.last_scaped_df

    def clean_cache_dir(self):
        deleted_files = 0
        for file in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, file)
            if os.path.isfile(file_path) and file.endswith('.html'):
                if time.time() - os.path.getmtime(file_path) > self.cache_expires:
                    os.remove(file_path)
                    deleted_files += 1
        if deleted_files > 0:
            self.logger.info(f"Deleted {deleted_files} html files from the cache directory.")
            
    @staticmethod
    def scrap_ollama():

        import requests
        import json

        model = "llama3.1:8b"

        # _format = {
        #     "type": "object",
        #     "properties": {
        #         'url': {'type': 'string'},
        #         'tipo_inmueble':  {'type': 'string'},
        #         'ubicacion':  {'type': 'string'},
        #         'precio':  {'type': 'int'},
        #         'superficie_m2':  {'type': 'int'},
        #         'n_habitaciones':  {'type': 'int'},
        #         'description':  {'type': 'string'},
        #         'caracteristicas':  {'type': 'string'},
        #     }
        # }

        # prompt = f"Analiza el codigo html siguiente y extrae las caracteristicas del inmueble, \
        #     las caracteristicas son: url, tipo de inmueble, ubicacion, precio, superficie_m2,  numero de habitaciones, description. Respond using JSON. \n\n"

        # html = open('tests/idealista_detalle_vivienda.html', 'r').read()

        # html = """
        #     Piso en venta en paseo de Gràcia
        #     La Dreta de l'Eixample, Barcelona
        #     1.350.000 € 1.400.000 € 4%
        #     Calcular hipoteca
        #     115 m² 3 hab. Planta 3ª exterior con ascensor
        #     Luminoso
        #     Guardar favorito
        #     Descartar
        #     Compartir
        #     Comentario del anunciante
        #     Disponible en: Español English Otros idiomas

        #     Este piso de lujo se sitúa en el Paseo de Gracia, en un edificio obra del prestigioso arquitecto Josep Puig i Cadafalch, enfrente de la Casa Batlló y la Casa Ametller. Se trata de una ubicación envidiable en una de las mejores avenidas de toda Europa, rodeada de todas las comodidades y servicios que una ciudad como Barcelona te puede ofrecer.


        # """
        # data = {
        #     "prompt": prompt + html,
        #     "model": model,
        #     "format": 'json',
        #     "stream": False,
        #     "options": {"temperature": 2.5, "top_p": 0.99, "top_k": 100},
        # }

        # response = requests.post("http://localhost:11434/api/generate", json=data, stream=False)
        # # print(response.status_code, response.text)

        # # write response to file
        # with open('tests/idealista_detalle_vivienda.json', 'w') as f:
        #     f.write(response.text)

        # json_data = json.loads(response.text)

        # print(json.dumps(json.loads(json_data["response"]), indent=2))

if __name__ == '__main__':

    # logging.config.fileConfig('local/logging.conf', disable_existing_loggers=False)
    # if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    pass



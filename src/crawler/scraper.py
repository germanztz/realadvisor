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

class Scraper:

    # TODO: Implementar la rotación de User-Agent
    # TODO: Implementar el scrapping de un array de URLs
    # TODO: Implementar sin pandas ni numpy
    
    def __init__(self, url=None, datafile_path: Path=None, list_items: dict=None, list_items_fields: dict=None, list_next: dict=None, detail_fields:dict=None, post_fields_lambda:dict=None):
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
        post_fields_lambda : dict
            dictionary of lambda functions to obtain the fields of each item of the detail view
        '''

        warnings.filterwarnings('ignore')

        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f'Init {self.__class__.__name__}')

        self.init_headers(url)
        self.datafile_path = datafile_path if datafile_path else None
        self.list_items_rx = list_items        
        self.list_items_fields = list_items_fields
        self.detail_fields = detail_fields
        self.list_next_rx = list_next
        self.post_fields_lambda = post_fields_lambda

        # 5. Rotación de Agentes de Usuario (User-Agent)
        #     Cambia el User-Agent de manera aleatoria para cada solicitud.
        # from fake_useragent import UserAgent
        # ua = UserAgent()
        # headers = {"User-Agent": ua.random}

        # list_columns = [f.replace('_sub', '') for f in self.list_items_fields.keys() if 'elem' not in f]
        self.data = None
        if self.datafile_path and self.datafile_path.exists():
            self.data = pd.read_csv(self.datafile_path)


    def init_headers(self, url):
        self.set_url(url)
        self.headers = {
            'Host': self.base_host,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=0, i',
            'TE': 'trailers'
        }
        return self.headers

    def set_url(self, url):
        """
        Sets a new URL for the Scraper instance.

        Args:
            url (str): The new URL to be set for the scraper.
        """
        if url is None: return False
        self.url = url.strip()
        self.base_url_rx = re.search(r'https?://([^/]+)', self.url)
        self.base_url = self.base_url_rx.group(0)
        self.base_host = self.base_url_rx.group(1)
        self.logger.info(f'URL set to {url}')

    def get_response(self, url):
        session = requests.Session()
        session.headers.update(self.headers)
        response = session.get(self.url)  
        self.logger.debug(f'Response status: {response.status_code}')
        return response

    def get_content(self, response):
        content = response.content.decode('utf-8')
        content = content.replace("\n", "").replace("\r", "")
        self.logger.debug(f'Contenido de la página: {content}')
        return content

    def parse_field(self, html, field_name, fields_rx, post_fields_lambda=None):
        """
        Parses the specified field from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            field_name (str): The name of the field to extract from the HTML.
            fields_rx (dict): A dictionary containing regular expressions for each field.
            post_fields_lambda (dict): A dictionary containing lambda functions for each field.

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
            if post_fields_lambda is not None and field_name in post_fields_lambda and ret is not None:
                # # if ret is a list
                # if isinstance(ret, list):
                #     ret = [post_fields_lambda[field_name](r) for r in ret]
                # # if ret is a string
                # elif isinstance(ret, str):
                ret = post_fields_lambda[field_name](ret)
                

            self.logger.debug(f'parse_field {field_name}: {ret}')
            return ret
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(field_name, regex)
            return None

    def parse_item(self, html, fields_rx, post_fields_lambda=None) -> dict:
        """
        Parses a post from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            fields_rx (dict): A dictionary containing regular expressions for each field.
            post_fields_lambda (dict): A dictionary containing lambda functions for each field.
        Returns:
            dict: A dictionary containing the extracted fields and their values. The dictionary
            includes a 'created' timestamp indicating when the parsing occurred.

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """

        dict_item = dict({'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

        for field, rx in fields_rx.items():
            if '_elem' not in field:
                dict_item[field.replace('_sub', '')] = self.parse_field(html, field, fields_rx, post_fields_lambda)

        self.logger.debug(f'parse_item: {dict_item}')
        return dict_item

    def parse_list(self, html, list_items_rx, fields_rx, post_fields_lambda=None):
        """
        Parses a list of items from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            list_items_rx (regex): expresion regular para obtener los items de la vista listado
            fields_rx (dict): A dictionary containing regular expressions for each field.
            post_fields_lambda (dict): A dictionary containing lambda functions for each field.
        Returns:
            list: A list containing dictionaries with the extracted fields and their values.

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """
        elements_html = self.parse_item(html, list_items_rx, post_fields_lambda)
        elements_html = elements_html[next(iter(list_items_rx.keys()))]
        list_columns = [f.replace('_sub', '') for f in fields_rx.keys() if 'elem' not in f]

        self.logger.info(f'Campos a extraer: {list_columns}')

        if elements_html is None:
            self.logger.warn(f'la busqueda de elementos de la lista devolvió None {list_items_rx}')
            return None

        item_list = list()
        for elem_html in elements_html:
            item_list += [self.parse_item(elem_html, fields_rx, post_fields_lambda)]
        
        self.logger.info(f'Elementos extraidos de la lista: {len(item_list)} elementos')
        return item_list
        
    def scrap(self):
        """
        Runs the web crawling and scraping process for the specified URL.

        This method starts the web crawling and scraping process for the specified URL.
        It uses the regular expressions defined in the constructor to parse the content
        of the web pages.

        The information is stored in a Pandas DataFrame and saved to a CSV file specified
        in the constructor.

        Returns:
            None

        """
        start = time.perf_counter()

        self.logger.info(f'Procesando: {self.url}')

        response = self.get_response(self.url)

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:

            content = self.get_content(response)
            curr_page = self.scrap_page(content)
            hay_repetidos = self.store_page_csv(curr_page)
            self.logger.info(f'Tiempo transcurrido: {time.perf_counter() - start}')
            self.paginate(content, hay_repetidos)

        else:
            self.logger.error(f"Error al enviar la solicitud: {response.status_code}: {response.reason}")

    def scrap_page(self, content):
        # Parsear el contenido de la web
        curr_page = self.parse_list(content, self.list_items_rx, self.list_items_fields, self.post_fields_lambda)
        return curr_page

    def store_page_csv(self, curr_page):

        if self.datafile_path is None: return
        if curr_page is None or len(curr_page) == 0: return

        hay_repetidos = False
        curr_page_df = pd.DataFrame(curr_page)
        if (self.data is not None):
            repetidos = curr_page_df['link'].isin(self.data['link'])
            hay_repetidos = repetidos.any()
            curr_page_df = curr_page_df[~repetidos]
        self.data = pd.concat([self.data, curr_page_df], ignore_index=True)
        self.logger.info(f"Elementos añadidos a la bbdd: {len(curr_page_df)}")
        self.data.to_csv(self.datafile_path, index=False)
        return hay_repetidos

    def paginate(self, content, hay_repetidos):

        next_href = self.parse_item(content, self.list_next_rx, self.post_fields_lambda)
        next_href = next_href[next(iter(self.list_next_rx.keys()))]
        if next_href is None:
            self.logger.info('Finalizado, se ha procesado la última página')
        elif hay_repetidos:
            self.logger.info('Finalizado, se han procesado los nuevos elementos')
        else:
            time.sleep(random.uniform(1, 5))
            self.set_url(next_href)
            self.scrap()

    def scrap_realty(self, url, detail_fields = None, post_fields_lambda = None) -> dict:
        response = self.get_response(url)

        if response.status_code == 200:
            content = self.get_content(response)
            data = self.parse_item(content.replace('\n', '').replace('\r', ''), detail_fields, post_fields_lambda)
            return (data)
        else:
            self.logger.error(f"Error al enviar la solicitud: {response.status_code}: {response.reason}")
            return None

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

    if Path('realadvisor.log').exists(): os.remove('realadvisor.log')

    with open('tests/fotocasa_lista.html', 'r') as f:
        content = f.read().replace("\n", "").replace("\r", "")
        list_items = { 'list_items': re.compile(r'accuracy(.+?)userId',re.DOTALL)}
        next_page =  { 'next_page': re.compile(r'\\"rel\\":\\"next\\",\\"href\\":\\"(.*?)\\"') }

        list_fields = { 
            'address': re.compile(r'"district":"(.*?)","neighborhood":"(.*?)","zipCode":"(.*?)",.*?"province":"(.*?)"'), 
        }
        fields_lambda = { 
            'list_items': lambda m: [e.replace('\\', '') for e in m],
            'address': lambda m: ", ".join(m)
        }

        scraper = Scraper('https://tt.com', None, list_items, list_fields, next_page, None, fields_lambda)
        curr_page = scraper.scrap_page(content)
        hay_repetidos = scraper.store_page_csv(curr_page)
        scraper.paginate(content, hay_repetidos)
        print(curr_page)
    # [{"key":"air_conditioner","value":1,"maxValue":0,"minValue":0},{"key":"ceramic_stoneware","value":6,"maxValue":0,"minValue":0},{"key":"alarm","value":77,"maxValue":0,"minValue":0},{"key":"not_furnished","value":130,"maxValue":0,"minValue":0},{"key":"antiquity","value":7,"maxValue":0,"minValue":0},{"key":"bathrooms","value":2,"maxValue":0,"minValue":0},{"key":"conservationStatus","value":4,"maxValue":0,"minValue":0},{"key":"floor","value":3,"maxValue":0,"minValue":0},{"key":"rooms","value":2,"maxValue":0,"minValue":0},{"key":"surface","value":50,"maxValue":0,"minValue":0}]


    
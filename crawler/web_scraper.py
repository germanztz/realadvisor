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
import warnings


class WebScraper:

    # TODO: Implementar la rotación de User-Agent
    # TODO: Implementar el scrapping de un array de URLs
    # TODO: Implementar sin pandas ni numpy
    
    def __init__(self, url, datafile_path, list_items_rx, list_items_fields, list_next_rx, detail_fields, post_fields_lambda=None):
        '''
        Class for scraping a website and obtaining a database
        
        Parameters
        ----------
        url : str
            initial url of the website to scrape
        datafile_path : str
            path of the file where the database will be saved
        list_items_rx : regex
            regular expression to obtain the items of the list view
        list_items_fields : dict
            dictionary of regular expressions to obtain the fields of each item of the list view
        list_next_rx : regex
            regular expression to obtain the link of the next page of the list view
        detail_fields : dict
            dictionary of regular expressions to obtain the fields of each item of the detail view
        post_fields_lambda : dict
            dictionary of lambda functions to obtain the fields of each item of the detail view
        '''

        warnings.filterwarnings('ignore')

        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'WebScraper.log')
        logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger(__name__)
        # Crear un handler para mostrar en la consola
        console_handler = logging.StreamHandler()  # Por defecto va a stderr
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        self.logger.addHandler(console_handler)

        self.logger.info(f'Init WebScraper')


        self.set_url(url)
        self.datafile_path = datafile_path
        self.list_items_rx = list_items_rx        
        self.list_items_fields = list_items_fields
        self.detail_fields = detail_fields
        self.list_next_rx = list_next_rx
        self.post_fields_lambda = post_fields_lambda

        # 5. Rotación de Agentes de Usuario (User-Agent)
        #     Cambia el User-Agent de manera aleatoria para cada solicitud.
        # from fake_useragent import UserAgent
        # ua = UserAgent()
        # headers = {"User-Agent": ua.random}

        list_columns = [f.replace('_sub', '') for f in self.list_items_fields.keys() if 'elem' not in f]
        self.data = pd.DataFrame(columns=list_columns)
        if os.path.exists(self.datafile_path):
            self.data = pd.read_csv(self.datafile_path)

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

    def set_url(self, url):
        """
        Sets a new URL for the WebScraper instance.

        Args:
            url (str): The new URL to be set for the scraper.
        """
        self.url = url
        self.base_url_rx = re.search(r'https?://([^/]+)', self.url)
        self.base_url = self.base_url_rx.group(0)
        self.base_host = self.base_url_rx.group(1)
        self.logger.info(f'URL set to {url}')

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
            ret = fields_rx[field_name].findall(html)
            if field_name == 'description':
                self.logger.debug(f'description: {fields_rx[field_name]}')
            ret = ret[0] if len(ret) == 1 else ret    
            ret = None if len(ret) == 0 else ret    
            if 'sub' in field_name and not ret is None:
                ret = fields_rx[field_name.replace('sub', 'elem')].findall(ret)
            if post_fields_lambda is not None and field_name in post_fields_lambda:
                ret = post_fields_lambda[field_name](ret)

            self.logger.debug(f'parse_field {field_name}: {ret}')
            return ret
        except Exception as e:
            self.logger.error(e)
            return None

    def parse_item(self, html, fields_rx, post_fields_lambda=None):
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
        elements_html = self.parse_field(html, 'elements_html', {'elements_html': list_items_rx}, post_fields_lambda)
        list_columns = [f.replace('_sub', '') for f in fields_rx.keys() if 'elem' not in f]

        self.logger.info(f'Campos a extraer: {list_columns}')

        item_list = list()
        for elem_html in elements_html:
            item_list += [self.parse_item(elem_html, fields_rx, post_fields_lambda)]
        
        self.logger.info(f'Elementos extraidos de la lista: {len(item_list)} elementos')
        return item_list
        
    def parse_list_next(self, html, list_next_rx, post_fields_lambda=None):
        """
        Parses the next page link from the provided HTML content using regular expressions.

        Args:
            html (str): The HTML content to parse.
            list_next_rx (regex): expresion regular para obtener el enlace a la página siguiente
            post_fields_lambda (dict): A dictionary containing lambda functions for each field.
        Returns:
            str: The next page link, or None if the link is not found.

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """
        next_href = self.parse_field(html, 'next_page', {'next_page': list_next_rx}, post_fields_lambda)
        self.logger.debug(f'parse_list_next: {next_href}')
        return next_href

    def run_crawl_web(self, url):
        """
        Runs the web crawling and scraping process for the specified URL.

        This method starts the web crawling and scraping process for the specified URL.
        It uses the regular expressions defined in the constructor to parse the content
        of the web pages.

        The information is stored in a Pandas DataFrame and saved to a CSV file specified
        in the constructor.

        Args:
            url (str): The URL to start the crawling from.

        Returns:
            None

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """
        start = time.perf_counter()

        self.logger.info(f'Procesando: {url}')

        self.set_url(url)
        # request con cookies
        session = requests.Session()
        session.headers.update(self.headers)
        response = session.get(self.url)  

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:

            content = response.content.decode('utf-8')
            content = content.replace("\n", "").replace("\r", "")
            self.logger.debug(f'Contenido de la página: {content}')
            # Parsear el contenido de la web
            curr_page = self.parse_list(content, self.list_items_rx, self.list_items_fields, self.post_fields_lambda)

            curr_page_df = pd.DataFrame(curr_page)
            repetidos = curr_page_df['link'].isin(self.data['link'])
            hay_repetidos = repetidos.any()
            registros_nuevos = curr_page_df[~repetidos]
            self.data = pd.concat([self.data, registros_nuevos], ignore_index=True)
            self.logger.info(f"Elementos añadidos a la bbdd: {len(registros_nuevos)}")
            
            self.data.to_csv(self.datafile_path, index=False)

            next_href = self.parse_list_next(content, self.list_next_rx, self.post_fields_lambda)
            self.logger.info(f'Tiempo transcurrido: {time.perf_counter() - start}')
            if next_href is None:
                self.logger.info('Finalizado, se ha procesado la última página')
            elif hay_repetidos:
                self.logger.info('Finalizado, se han procesado los nuevos elementos')
            else:
                time.sleep(random.uniform(1, 5))
                self.run_crawl_web(self.base_url+next_href)

        else:
            self.logger.error(f"Error al enviar la solicitud: {response.status_code}: {response.reason}")

    def scrap(self, url_list = None):
        """
        Runs the web scraping process for a list of URLs.

        This method starts the web scraping process for each URL in the provided list.
        If the list is not provided, it uses the URL specified in the constructor.

        Args:
            url_list (list[str], optional): The list of URLs to scrape. Defaults to None (it uses the URL specified in the constructor).

        Returns:
            None

        Raises:
            Exception: If there is an error during parsing, it logs the error and returns None.
        """
        if url_list is None:
            url_list = [self.url]

        for url in url_list:
            self.run_crawl_web(url)

# if __name__ == '__main__':

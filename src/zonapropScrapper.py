import json
import logging
import pandas as pd
from progressBarPrinter import print_progress_bar
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs/zonapropScrapper.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


class ZonapropScrapper:

    def __init__(self, config, request_getter, path):
        self.from_page = config["from_page"]
        self.pages = config["pages"]
        self.publisher_types = config["publisher_types"]
        self.ids_filename = config["ids_filename"]
        self.result_filename = config["result_filename"]
        self.request_getter = request_getter
        self.path = path

        print("----------------------")
        print("ZONA PROP SCRAPPER CONFIGURATION:")
        print("page from: {}".format(self.from_page))
        print("pages: {}".format(self.pages))
        print("publishers types: {}".format(self.publisher_types))
        print("id filename prefix: {}".format(self.ids_filename))
        print("result filename prefix: {}".format(self.result_filename))
        print("----------------------")

    def scrap_id_aviso(url_casa):
        return

    def get(self, url):
        response = self.request_getter.get(url)
        return BeautifulSoup(response.content, 'html.parser') if response is not None else response

    def post(self, url, data):
        response = self.request_getter.post(url, data)
        return BeautifulSoup(response.content, 'html.parser') if response is not None else response

    def scrap(self):
        print("Start ZonaProp Scrapping")
        for publisher_type in self.publisher_types:
            print("Start {} id scrapping".format(publisher_type))
            houses_urls_df = pd.DataFrame()
            print_progress_bar(0, self.from_page + self.pages - 1, publisher_type + " houses")
            for i in range(self.from_page, self.from_page + self.pages - 1):
                page_part = "pagina-" + str(i) + "-"
                search_url_inmu = 'https://www.zonaprop.com.ar/inmuebles-{page_part}{publisher_type}.html'.format(
                    publisher_type=publisher_type, page_part=page_part).replace("\'", '"')
                response_soup = self.get(search_url_inmu)
                house_list = response_soup.find_all("script")[24].text
                house_list = house_list.split('listPostings = ')[1].split('const developmentData ')[0].strip()[:-1]
                page_list = json.loads(house_list)
                for page in page_list:
                    print(page['postingId'])
                    data = {'idAviso': page['postingId'], 'page': 'ficha'}
                    contacto_info = self.post('https://www.zonaprop.com.ar/aviso_verDatosAnunciante.ajax', data)
                    print(contacto_info)

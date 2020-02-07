import datetime
from bs4 import BeautifulSoup
import pandas as pd
import os
import logging
import re
from progressBarPrinter import print_progress_bar


class MeliScrapper:
    def __init__(self, config, request_getter, path):
        self.from_page = config["from_page"]
        self.pages = config["pages"]
        self.publisher_types = config["publisher_types"]
        self.ids_filename = config["ids_filename"]
        self.result_filename = config["result_filename"]
        self.request_getter = request_getter
        self.path = path
        self.ids_directory = self.path + "/ids_to_search/meli"

        print("----------------------")
        print("MELI SCRAPPER CONFIGURATION:")
        print("page from: {}".format(self.from_page))
        print("pages: {}".format(self.pages))
        print("publishers types: {}".format(self.publisher_types))
        print("id filename prefix: {}".format(self.ids_filename))
        print("result filename prefix: {}".format(self.result_filename))
        print("----------------------")

    def get(self, url):
        response = self.request_getter.get(url)
        return BeautifulSoup(response.content, 'html.parser') if response is not None else response

    def scrap_ids(self):
        print("Start Mercado libre scrapping")
        for publisher_type in self.publisher_types:
            print("Start {} id scrapping".format(publisher_type))
            houses_urls_df = pd.DataFrame()
            print_progress_bar(0, self.from_page + self.pages - 1, publisher_type + " ids")

            for i in range(self.from_page, self.from_page + self.pages - 1):

                if i == 1:
                    page_part_number = 1
                else:
                    page_part_number = 48 * (i - 1) + 1

                page_part = "_Desde_" + str(page_part_number)

                # Tenes que mejorar esta brasada
                search_url_inmu = 'https://inmuebles.mercadolibre.com.ar/venta/{publisher_type}/{page_part}'.format(
                    publisher_type=publisher_type, page_part=page_part).replace("\'", '"')

                response_soup = self.get(search_url_inmu)
                house_list = response_soup.find_all("a", {"class": "item__info-link"})
                for i in len(house_list):
                    print(house_list[i])

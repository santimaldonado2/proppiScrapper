import datetime
from bs4 import BeautifulSoup
import pandas as pd
import os
import logging
import re
from bs4 import Tag

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
                house_urls = list(set(house_item.get("href") for house_item in house_list))
                house_processed = [False for house in house_urls]
                houses_info = pd.DataFrame({
                    "url": house_urls,
                    "processed": house_processed
                })
                houses_urls_df = pd.concat([houses_urls_df, houses_info], axis=0, sort=False).reset_index().drop(
                    columns="index")
                houses_urls_df.to_csv(self.path + "/temp/temp_{}_{}.csv".format(publisher_type, self.ids_filename),
                                      index=False,
                                      encoding="UTF-8")
                print_progress_bar(i + 1, self.from_page + self.pages - 1, publisher_type + " ids")
                if not os.path.exists(self.ids_directory):
                    os.makedirs(self.ids_directory)

                houses_urls_df.to_csv(self.ids_directory + "/" + self.ids_filename + "_" + publisher_type + "_ids.csv",
                                      index=False,
                                      encoding="UTF-8")
                print("")
                print("End {} id scrapping".format(publisher_type))
            print("End Mercado Libre ID Scrapping")

    def listToString(self, s):
        string = ""
        ss = list(s)
        for e in ss:
            if isinstance(e, Tag):
                pass
            else:
                string += e
        return string

    def get_house_info(self, link):
        response_house = self.get(link)
        info = {}
        if response_house:
            short_description = response_house.find("section", {"class": "short-description--static"})
            info['shortDescription'] = short_description.find("h1").contents[0]
            info['currency'] = short_description.find("span").contents[1].contents[0]
            info['price'] = short_description.find("span").contents[3].contents[0]
            try:
                info['size'] = short_description.find_all("dl")[1].contents[2].contents[0]
            except:
                info['size'] = 'null data'

            try:
                info['rooms'] = short_description.find_all("dl")[2].contents[2].contents[0]
            except:
                info['rooms'] = 'null data'

            try:
                info['bathrooms'] = short_description.find_all("dl")[3].contents[2].contents[0]
            except:
                info['bathrooms'] = 'null data'

            section_view_more = response_house.find("section", {"class": "vip-section-seller-info"})
            try:
                info['name'] = section_view_more.contents[5].contents[1].contents[0]
            except:
                info['name'] = 'null data'

            try:
                info['phone1'] = section_view_more.find_all("span", {"class": "profile-info-phone-value"})[0].contents[
                    0]
                if list(section_view_more.find_all("span", {"class": "profile-info-phone-value"})).__len__() == 2:
                    info['phone2'] = \
                        section_view_more.find_all("span", {"class": "profile-info-phone-value"})[1].contents[
                            0]
            except:
                info['phone1'], info['phone2'] = 'null data'
            try:
                info['address'] = response_house.find("h2", {"class": "map-address"}).contents[0]
            except:
                info['address'] = 'null data'
            try:
                info['location'] = response_house.find("h3", {"class": "map-location"}).contents[0]
            except:
                info['location'] = ' null data'
            try:
                info['description'] = self.listToString(
                    response_house.find("div", {"class": "item-description__text"}).contents[1].contents)
            except:
                info['description'] = "null data"

            # Caracteristicas que varian segun la publicacion
            listali = []
            contador = 0

            # en tipo vendedor inmueble a veces no exiten estos datos
            try:
                caracteristicas = list(response_house.find("ul", {"class": "specs-list"}).contents)
                for caracteristica in caracteristicas:
                    if contador % 2 == 1:
                        elemento = response_house.find("ul", {"class": "specs-list"}).contents[contador]
                        listali.append(elemento)
                    contador += 1

                listnamecaract = []
                listvaluecaract = []
                for caracteristica in listali:
                    contenido = list(caracteristica.contents)
                    contador2 = 0
                    flag_nombre = True
                    for i in contenido:
                        if contador2 % 2 == 1:
                            elemento2 = caracteristica.contents[contador2].contents[0]
                            if flag_nombre == True:
                                listnamecaract.append(elemento2)
                                flag_nombre = False
                            else:
                                listvaluecaract.append(elemento2)
                                flag_nombre = True
                        contador2 += 1

                info_extra = {listnamecaract.lower().replace(' ', '_'): listvaluecaract for
                              listnamecaract, listvaluecaract in zip(listnamecaract, listvaluecaract)}
                info.update(info_extra)
            except:
                pass

            return info

    def houses_id_info(self):
        print("Start Mercado Libre houses info Scrapping")
        for publisher_type in self.publisher_types:
            print("Start {} houses info Scrapping".format(publisher_type))
            houses_df = pd.DataFrame()
            houses_urls_df = pd.read_csv(
                self.ids_directory + "/" + self.ids_filename + "_" + publisher_type + "_ids.csv")
            houses_urls_df.drop_duplicates(subset="url", keep="first", inplace=True)
            i = 0
            total_rows = houses_urls_df.shape[0]
            print_progress_bar(i, total_rows, publisher_type + " " + str(i))
            for row in houses_urls_df.itertuples():
                i += 1
                house_info = self.get_house_info(row.url)
                house_info_df = pd.DataFrame([house_info], columns=house_info.keys())
                houses_urls_df.loc[row.Index, 'processed'] = True
                houses_df = pd.concat([houses_df, house_info_df], axis=0, sort=False).reset_index().drop(
                    columns="index")
                if i % 5 == 0:
                    houses_df.to_csv(self.path + "/temp/temp_{}_{}.csv".format(self.result_filename, publisher_type),
                                     index=False, encoding="UTF-8")
                    houses_urls_df.to_csv(
                        self.path + "/temp/temp_{}_{}_ids.csv".format(self.result_filename, publisher_type),
                        index=False, encoding="UTF-8")
                print_progress_bar(i, total_rows, publisher_type + " " + str(i))

            directory = self.path + "/results/" + datetime.datetime.today().strftime('%Y-%m-%d')
            if not os.path.exists(directory):
                os.makedirs(directory)
            houses_df.to_csv(directory + "/{}_{}.csv".format(self.result_filename, publisher_type), index=False,
                             encoding="UTF-8")
            houses_urls_df.to_csv(self.ids_directory + "/" + self.ids_filename + "_" + publisher_type + "_ids.csv",
                                  index=False)
            print("")
            print("End {} houses info Scrapping".format(publisher_type))
        print("End Mercado Libre houses info Scrapping")

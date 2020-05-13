# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 09:48:07 2019

@author: smaldonado
"""
import datetime
import logging
import os
from abc import ABC

import pandas as pd
from bs4 import BeautifulSoup

from constants import FROM_PAGE, PAGES, PUBLISHER_TYPES, IDS_DIRECTORY, OPERATION_TYPES, \
    PAGE_SIZES, TEMP, INFO, IDS, RESULTS_DIRECTORY, ENCODING
from progressBarPrinter import print_progress_bar

NOT_HOUSE_INFO_ERROR_MESSAGE = "Error trying to get the houses list: number[{}] publisher_type[{}] url[{}]"

ERROR_MESSAGE = "Error trying to get this page: number[{}] publisher_type[{}] url[{}]"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs/lavozScrapper.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


class GeneralScrapper(ABC):

    def __init__(self, config, request_getter, path, name):
        self.from_page = config[FROM_PAGE]
        self.pages = config[PAGES]
        self.publisher_types = config[PUBLISHER_TYPES]
        self.operation_types = config[OPERATION_TYPES]
        self.request_getter = request_getter
        self.path = path
        self.name = name
        self.page_size = PAGE_SIZES[name]

        print("----------------------")
        print(self.name.upper(), "SCRAPPER CONFIGURATION:")
        print("page from: {}".format(self.from_page))
        print("pages: {}".format(self.pages))
        print("publishers types: {}".format(self.publisher_types))
        print("operation_types: {}".format(self.operation_types))
        print("----------------------")

    def get(self, url):
        response = self.request_getter.get(url)
        return BeautifulSoup(response.content, 'html.parser') if response is not None else response

    def post(self, url, data, headers):
        response = self.request_getter.post(url, data, headers)
        return response.json()

    def get_house_info(self, link) -> dict:
        pass

    def get_search_url(self, publisher_type: str, operation_type: str, page: int) -> str:
        pass

    def get_house_list(self, response_soup) -> list:
        pass

    def get_filename(self, publisher_type, operation_type, file_type) -> str:
        return '{name}_{publisher}_{operation}_{type}.csv'.format(
            name=self.name,
            publisher=publisher_type,
            operation=operation_type,
            type=file_type
        )

    def save_csv(self, df, operation_type, publisher_type, type, sub_directory):
        file_name = os.path.join(self.path,
                                 sub_directory,
                                 self.get_filename(publisher_type, operation_type, type))
        df.to_csv(file_name,
                  index=False,
                  encoding=ENCODING)

    def scrap_ids(self):
        self.show_message("Start Ids Scrapping", [self.name.upper()])
        for publisher_type in self.publisher_types:
            for operation_type in self.operation_types:
                stage = [self.name, publisher_type, operation_type]
                self.show_message("Start Ids Scrapping", stage)
                houses_urls_df = pd.DataFrame()
                end_page = self.from_page + self.pages
                print_progress_bar(self.from_page, end_page, start_value=self.from_page)
                for i in range(self.from_page, end_page):
                    try:
                        search_url_inmu = self.get_search_url(publisher_type, operation_type, i)
                        response_soup = self.get(search_url_inmu)
                        if not response_soup:
                            logger.info(ERROR_MESSAGE.format(i + 1,
                                                             publisher_type,
                                                             search_url_inmu))
                            continue
                        house_list = self.get_house_list(response_soup)
                        if not house_list:
                            logger.info(
                                NOT_HOUSE_INFO_ERROR_MESSAGE.format(i + 1,
                                                                    publisher_type,
                                                                    search_url_inmu))
                            continue

                        house_processed = [False for house in house_list]
                        houses_info = pd.DataFrame({
                            "url": house_list,
                            "processed": house_processed
                        })
                        houses_urls_df = pd.concat([houses_urls_df, houses_info], axis=0, sort=False).reset_index().drop(
                            columns="index")

                        self.save_csv(df=houses_urls_df,
                                      operation_type=operation_type,
                                      publisher_type=publisher_type,
                                      type=IDS,
                                      sub_directory=TEMP)

                        print_progress_bar(i + 1, end_page, start_value=self.from_page)
                    except:
                        logger.error("Error scrapping stage=[{stage}], page=[{}]".format(stage=stage,
                                                                                         page=i))
                        continue

                if not os.path.exists(os.path.join(self.path, IDS_DIRECTORY)):
                    os.makedirs(os.path.join(self.path, IDS_DIRECTORY))

                self.save_csv(df=houses_urls_df,
                              operation_type=operation_type,
                              publisher_type=publisher_type,
                              type=IDS,
                              sub_directory=IDS_DIRECTORY)

                logger.info("End scrap_ids {}".format(publisher_type))
                self.show_message()
                self.show_message("End Ids Scrapping", stage)
            logger.info("End scrap_ids")
        self.show_message("End Ids Scrapping", [self.name.upper()])

    def get_houses_info(self):
        logger.info("Start get_houses_info")
        self.show_message("Start Info Scrapping", [self.name.upper()])
        for publisher_type in self.publisher_types:
            for operation_type in self.operation_types:
                stage = [self.name, publisher_type, operation_type]
                self.show_message("Start Info Scrapping", stage)
                houses_df = pd.DataFrame()
                ids_file = os.path.join(self.path,
                                        IDS_DIRECTORY,
                                        self.get_filename(publisher_type, operation_type, IDS))
                houses_urls_df = pd.read_csv(ids_file)
                houses_urls_df.drop_duplicates(subset="url", keep="first", inplace=True)
                i = 0
                total_rows = len(houses_urls_df)
                print_progress_bar(i, total_rows)
                for row in houses_urls_df.itertuples():
                    i += 1
                    try:
                        house_info = self.get_house_info(row.url)
                        if not 'operation_type' in house_info:
                            house_info['operation_type'] = operation_type
                        if house_info == {}:
                            logger.info("This house could not be processed: {}".format(row.url))
                            continue
                        house_info_df = pd.DataFrame([house_info], columns=house_info.keys())
                        houses_urls_df.loc[row.Index, 'processed'] = True
                        houses_df = pd.concat([houses_df, house_info_df], axis=0, sort=False).reset_index().drop(
                            columns="index")
                        if i % 5 == 0:
                            self.save_csv(df=houses_df,
                                          operation_type=operation_type,
                                          publisher_type=publisher_type,
                                          type=INFO,
                                          sub_directory=TEMP)

                            self.save_csv(df=houses_urls_df,
                                          operation_type=operation_type,
                                          publisher_type=publisher_type,
                                          type=IDS,
                                          sub_directory=TEMP)
                    except:
                        logger.error("Error processing url=[{url}]".format(url=row.url))
                        continue

                    print_progress_bar(i, total_rows)

                result_sub_directory = os.path.join(
                    RESULTS_DIRECTORY,
                    datetime.datetime.today().strftime('%Y-%m-%d'))

                directory = os.path.join(
                    self.path,
                    result_sub_directory)

                if not os.path.exists(directory):
                    os.makedirs(directory)

                self.save_csv(df=houses_df,
                              operation_type=operation_type,
                              publisher_type=publisher_type,
                              type=INFO,
                              sub_directory=result_sub_directory)

                self.save_csv(df=houses_urls_df,
                              operation_type=operation_type,
                              publisher_type=publisher_type,
                              type=IDS,
                              sub_directory=IDS_DIRECTORY)
                logger.info("End get_houses_info {}".format(publisher_type))
                self.show_message()
                self.show_message("End Info Scrapping", stage)

        logger.info("End get_houses_info")
        self.show_message("End Info Scrapping", [self.name.upper()])

    def show_message(self, message="", stage=None):
        stage_message = ' '.join(stage) if stage else ''
        print(message, stage_message)

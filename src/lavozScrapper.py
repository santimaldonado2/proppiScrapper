# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 09:48:07 2019

@author: smaldonado
"""
import logging

from generalScrapper import GeneralScrapper
from utils import get_formated_telephone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs/lavozScrapper.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('|%(asctime)s\t|%(levelname)s\t|%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

BASE_URL = 'https://clasificados.lavoz.com.ar/buscar/inmuebles/'
URL_TEMPLATE = '{base}{operation}?filters={filters}&page={page}'

# ORIGINAL HTML FIELDS
TELEPHONE_FORMATED_COLUMN = 'telephone_formated'
TELEPHONE_COLUMN = 'telephone'
TEL = "tel"
ARTICLE_ID = "recs:articleid"
EMPTY_STRING = ""
OG_ = "og:"
C_XENSE_PARSE_ = "cXenseParse:"
CONTENT = "content"
PROPERTY = "property"
NAME = "name"
META = "meta"
A_TAG = "a"
HREF_ATTRIBUTE = 'href'
TEXT_DECORATION_NONE = "text-decoration-none"
CLASS = "class"


class LaVozScrapper(GeneralScrapper):

    def get_search_url(self, publisher_type: str, operation_type: str, page: int) -> str:
        filters = {
            'vendedor': [publisher_type]
        }

        return URL_TEMPLATE.format(
            base=BASE_URL,
            operation=operation_type,
            filters=str(filters).replace("'", '"'),
            page=page
        )

    def get_house_list(self, response_soup) -> list:
        house_list = response_soup.find_all(A_TAG, {CLASS: TEXT_DECORATION_NONE})
        return list(set(house_item.get(HREF_ATTRIBUTE) for house_item in house_list))

    def get_house_info(self, link):
        logger.info(f'Start get_house_info|\t\t{link}')
        response_house = self.get(link)
        info = {}
        if response_house:

            # Get general info
            for meta in response_house.find_all(META):
                name = meta.get(NAME)
                prop = meta.get(PROPERTY)
                content = meta.get(CONTENT)
                if name is not None:
                    name = name.replace(C_XENSE_PARSE_, EMPTY_STRING)
                    info[name] = content
                if prop is not None:
                    prop = prop.replace(OG_, EMPTY_STRING)
                    info[prop] = content

            tag_telephone = response_house.find(id=TEL)
            info[TELEPHONE_COLUMN] = tag_telephone.get_text() if tag_telephone else EMPTY_STRING
            info[TELEPHONE_FORMATED_COLUMN] = get_formated_telephone(info[TELEPHONE_COLUMN])

        logger.info(f"End get_house_info|\t\t{link}")
        return info

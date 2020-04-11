# -*- coding: utf-8 -*-
'''
Created on Thu Mar  7 09:48:07 2019

@author: smaldonado
'''

import json
import logging
import os
from random import randint

from constants import LAVOZ, MELI, ZONAPROP, SLEEP, CONTACT_INFO, REQUESTS, USE_PROXY, FALSE_STRING, TRUE_STRING, SCRAP
from lavozScrapper import LaVozScrapper
from meliScrapper import MeliScrapper
from requestgetter import RequestGetter
from zonapropScrapper import ZonapropScrapper

path = os.path.dirname(os.path.realpath('__file__'))
with open(path + '/config.json') as data_file:
    config = json.load(data_file)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs/scrapper.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info('-----Start Proppi Scrapper----')
print('-----Start Proppi Scrapper----')

config[ZONAPROP][SLEEP] = config[REQUESTS][USE_PROXY].lower() == FALSE_STRING
config[ZONAPROP][CONTACT_INFO] = config[ZONAPROP][CONTACT_INFO].lower() == TRUE_STRING

scrappers_flag = {key: config[SCRAP][key].lower() == TRUE_STRING for key in config[SCRAP]}
request_getter = RequestGetter(config[REQUESTS])

scrappers = {
    LAVOZ: lambda: LaVozScrapper(config[LAVOZ], request_getter, path, LAVOZ),
    MELI: lambda: MeliScrapper(config[MELI], request_getter, path, MELI),
    ZONAPROP: lambda: ZonapropScrapper(config[ZONAPROP], request_getter, path, ZONAPROP)
}

for key in scrappers_flag.keys():
    if scrappers_flag[key]:
        scrapper = scrappers[key]()
        scrapper.scrap_ids()
        scrapper.get_houses_info()

phrases = ['The best way to predict the future is to create it.',
           'Live as if you were to die tomorrow.Learn as if you were to live forever.',
           'Do the difficult things while they are easy and do the great things while they are small.'
           'A journey of a thousand miles begins with a single step.',
           'Today a reader, tomorrow a leader,',
           'If you can dream it, you can do it.',
           'Ever tried. Ever failed. No matter. Try again. Fail again. Fail better.',
           'Tell me and I forget. Teach me and I remember. Involve me and I learn']

logger.info('-----End Proppi Scrapper----')
print('-----End Proppi Scrapper Succsesfully----')
print('I hope you have a really nice day, and remember:')
print(phrases[randint(0, len(phrases) - 1)])

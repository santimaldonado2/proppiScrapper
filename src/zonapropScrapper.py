import json
import logging
import random
from ast import literal_eval
from time import sleep

from constants import SLEEP, CONTACT_INFO
from generalScrapper import GeneralScrapper

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs/zonapropScrapper.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

BASE_URL = 'https://www.zonaprop.com.ar/inmuebles'
CONTACT_URL = 'https://www.zonaprop.com.ar/aviso_verDatosAnunciante.ajax'

HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Host': 'www.zonaprop.com.ar',
    'origin': 'www.zonaprop.com.ar',
}

POST_DATA_TEMPLATE = 'idAviso={}&page=ficha'

# ORIGINAL JSON FIELDS
CLAVE = 'clave'
ERROR_MESSAGE = 'errorMessage'
ID_USUARIO = 'idUsuario'
ANUNCIANTE = 'anunciante'
STATUS = 'status'
CODIGO = 'codigo'
RESPONSE = 'response'
RESULTADO_CONTACTO = 'resultadoContacto'
CONTENIDO = 'contenido'
URL_STATIC_MAP = 'urlStaticMap'
LONGITUDE = 'longitude'
LATITUDE = 'latitude'
GEOLOCATION = 'geolocation'
POSTING_GEOLOCATION = 'postingGeolocation'
LOCATION = 'location'
CITY = 'city'
ADDRESS = 'address'
POSTING_LOCATION = 'postingLocation'
DAY_OF_MONTH = 'dayOfMonth'
MONTH_OF_YEAR = 'monthOfYear'
YEAR_OF_ERA = 'yearOfEra'
BEGIN_DATE = 'beginDate'
PUBLICATION = 'publication'
REAL_ESTATE_SUBTYPE = 'realEstateSubtype'
REAL_ESTATE_TYPE = 'realEstateType'
FEATURE_ID = 'featureId'
FLAGS_FEATURES = 'flagsFeatures'
GENERAL_FEATURES = 'generalFeatures'
MEASURE = 'measure'
VALUE = 'value'
LABEL = 'label'
MAIN_FEATURES = 'mainFeatures'
PRICES = 'prices'
NAME = 'name'
OPERATION_TYPE = 'operationType'
PRICE_OPERATION_TYPES = 'priceOperationTypes'
POSTING_TYPE = 'postingType'
URL = 'url'
ANTIQUITY = 'antiquity'
DESCRIPTION_NORMALIZED = 'descriptionNormalized'
TITLE = 'title'
POSTING_ID = 'postingId'
AMOUNT = 'amount'
CURRENCY = 'currency'
EXPENSES = 'expenses'

# FINAL CSV COLUMNS
CONTACT_ERROR_COLUMN = 'contact_error'
USER_ID_COLUMN = 'user_id'
GOOGLEMAPS_URL_COLUMN = 'googlemaps_url'
LONGITUDE_COLUMN = 'longitude'
LATITUDE_COLUMN = 'latitude'
PUBLICATION_DATE_COLUMN = 'publication_date'
HOUSE_SUBTYPE_COLUMN = 'house_subtype'
HOUSE_TYPE_COLUMN = 'house_type'
PUBLISHER_TYPE_COLUMN = 'publisher_type'
ADDRESS_COLUMN = 'address'
PRICE_CURRENCY_COLUMN = 'price_currency'
PRICE_COLUMN = 'price'
OPERATION_TYPE_COLUMN = 'operation_type'
EXPENSES_CURRENCY_COLUMN = 'expenses_currency'
EXPENSES_AMOUNT_COLUMN = 'expenses_amount'

# TEMPLATES
DATE_TEMPLATE = '{day}/{month}/{year}'
CONTACT_FIELD_TEMPLATE = 'contact_{}'
FEATURE_COLUMN_TEMPLATE = '{value} {measure}'
PAGE_PART_TEMPLATE = 'pagina-{}-'
URL_TEMPLATE = '{base}-{operation}-{page}{publisher}.html'

# OTHER CONSTANTS
END_HOUSES_INFO_TAG = 'const developmentData '
START_HOUSES_INFO_TAG = 'listPostings = '
SCRIPT = 'script'


class ZonapropScrapper(GeneralScrapper):

    def __init__(self, config, request_getter, path, name):
        super().__init__(config, request_getter, path, name)
        self.sleep = config.get(SLEEP, False)
        self.contact_info = config.get(CONTACT_INFO, False)

    def get_search_url(self, publisher_type: str, operation_type: str, page: int) -> str:
        page_part = PAGE_PART_TEMPLATE.format(page) if page > 1 else ''

        return URL_TEMPLATE.format(
            base=BASE_URL,
            operation=operation_type,
            page=page_part,
            publisher=publisher_type
        )

    def get_house_list(self, response_soup) -> list:
        self.sleep_random_time()
        house_list = '[]'
        for i, script in enumerate(response_soup.find_all(SCRIPT)):
            if START_HOUSES_INFO_TAG in script.text:
                house_list = script.text.split(START_HOUSES_INFO_TAG)[1].split('%s' % END_HOUSES_INFO_TAG)[0].strip()[
                             :-1]
                break

        return json.loads(house_list)

    def get_house_info(self, house_text):
        house_json = literal_eval(house_text)
        house_info = self.process_house_info(house_json)
        if self.contact_info:
            house_info.update(self.get_contact_info(house_json))
            self.sleep_random_time()
        return house_info

    def sleep_random_time(self):
        if self.sleep:
            sleep(random.randint(0, 45))

    def process_house_info(self, house_json):
        logger.info('Start process_house_info')
        keys_to_keep = [POSTING_ID, TITLE, DESCRIPTION_NORMALIZED, ANTIQUITY, URL, POSTING_TYPE]
        house_info = {key: house_json[key] for key in keys_to_keep if key in house_json}
        house_info.update(self.get_operation_and_price(house_json))
        house_info.update(self.process_expenses(house_json))
        house_info.update(self.process_main_features(house_json))
        house_info.update(self.process_general_features(house_json))
        #house_info.update(self.process_flag_features(house_json))
        house_info.update(self.process_real_state_type_and_subtype(house_json))
        house_info.update(self.process_pub_date(house_json))
        house_info.update(self.process_location(house_json))
        logger.info('End process_house_info')
        return house_info

    def get_operation_and_price(self, house_json):
        sub_info = house_json[PRICE_OPERATION_TYPES][0]
        operation_type = sub_info[OPERATION_TYPE][NAME]
        price = sub_info[PRICES][0][AMOUNT]
        currency = sub_info[PRICES][0][CURRENCY]
        return {
            OPERATION_TYPE_COLUMN: operation_type,
            PRICE_COLUMN: price,
            PRICE_CURRENCY_COLUMN: currency
        }

    def process_expenses(self, house_json):
        expenses_json = {}
        if EXPENSES in house_json and house_json[EXPENSES]:
            expenses_info = house_json[EXPENSES]
            expenses_json[EXPENSES_AMOUNT_COLUMN] = expenses_info[AMOUNT]
            expenses_json[EXPENSES_CURRENCY_COLUMN] = expenses_info[CURRENCY]
        return expenses_json

    def process_main_features(self, house_json):
        processed_main_features = {}
        main_features = house_json[MAIN_FEATURES]
        for key in main_features:
            feature_id = main_features[key][LABEL].lower().replace(' ', '_')
            value = main_features[key][VALUE]
            measure = main_features[key][MEASURE]
            measure = measure if measure else ''
            processed_main_features[feature_id] = FEATURE_COLUMN_TEMPLATE.format(value=value, measure=measure)
        return processed_main_features

    def process_general_features(self, house_json):
        processed_general_features = {}
        general_features = house_json[GENERAL_FEATURES]
        for key in general_features:
            subfeature = general_features[key]
            for subkey in subfeature:
                feature_id = subfeature[subkey][LABEL].lower().replace(' ', '_')
                processed_general_features[feature_id] = True
        return processed_general_features

    def process_flag_features(self, house_json):
        '''Deprecated.'''
        return {PUBLISHER_TYPE_COLUMN: house_json[FLAGS_FEATURES][0][FEATURE_ID]}

    def process_real_state_type_and_subtype(self, house_json):
        real_estate = {HOUSE_TYPE_COLUMN: house_json[REAL_ESTATE_TYPE][NAME]}
        if REAL_ESTATE_SUBTYPE in house_json and house_json[REAL_ESTATE_SUBTYPE]:
            real_estate[HOUSE_SUBTYPE_COLUMN] = house_json[REAL_ESTATE_SUBTYPE][NAME]
        return real_estate

    def process_pub_date(self, house_json):
        publication_date = house_json[PUBLICATION][BEGIN_DATE]
        return {PUBLICATION_DATE_COLUMN: DATE_TEMPLATE.format(
            year=publication_date[YEAR_OF_ERA],
            month=publication_date[MONTH_OF_YEAR],
            day=publication_date[DAY_OF_MONTH]
        )}

    def process_location(self, house_json):
        geolocation = {}
        if POSTING_LOCATION in house_json and house_json[POSTING_LOCATION]:
            location_info = house_json[POSTING_LOCATION]
            if ADDRESS in location_info and location_info[ADDRESS]:
                geolocation[ADDRESS_COLUMN] = location_info[ADDRESS][NAME]
            geolocation[CITY] = location_info[LOCATION][NAME]
            if POSTING_GEOLOCATION in location_info and location_info[POSTING_GEOLOCATION]:
                geolocation[LATITUDE_COLUMN] = location_info[POSTING_GEOLOCATION][GEOLOCATION][LATITUDE]
                geolocation[LONGITUDE_COLUMN] = location_info[POSTING_GEOLOCATION][GEOLOCATION][LONGITUDE]
                geolocation[GOOGLEMAPS_URL_COLUMN] = location_info[POSTING_GEOLOCATION][URL_STATIC_MAP]
        return geolocation

    def valid_contact_response(self, contact_info):
        return contact_info[CONTENIDO][RESULTADO_CONTACTO][RESPONSE][CODIGO] == 202

    def process_contact_info(self, contact_info):
        logger.info('Start process_contact_info')
        processed_contact_info = {}
        if STATUS in contact_info and contact_info[STATUS][STATUS] == 200 and self.valid_contact_response(
                contact_info):
            if CONTENIDO in contact_info and contact_info[CONTENIDO]:
                content = contact_info[CONTENIDO]
                if ANUNCIANTE in content and content[ANUNCIANTE]:
                    processed_contact_info = {CONTACT_FIELD_TEMPLATE.format(key): content[ANUNCIANTE][key] for key in
                                              content[ANUNCIANTE]}
                if RESULTADO_CONTACTO in content and content[RESULTADO_CONTACTO]:
                    contact_result = content[RESULTADO_CONTACTO]
                    if ID_USUARIO in contact_result and contact_result[ID_USUARIO]:
                        processed_contact_info[USER_ID_COLUMN] = contact_result[ID_USUARIO]

        else:
            processed_contact_info[CONTACT_ERROR_COLUMN] = contact_info[ERROR_MESSAGE] + \
                                                           contact_info[CONTENIDO][RESULTADO_CONTACTO][RESPONSE][CLAVE]
        logger.info('Start process_contact_info')
        return processed_contact_info

    def get_contact_info(self, house_info):
        data = POST_DATA_TEMPLATE.format(house_info[POSTING_ID])
        contact_response = self.post(url=CONTACT_URL,
                                     data=data,
                                     headers=HEADERS)
        return self.process_contact_info(contact_response)

import logging

from bs4 import Tag

from generalScrapper import GeneralScrapper
from utils import get_formated_telephone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('logs/meliScrapper.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('|%(asctime)s\t|%(levelname)s\t|%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

BASE_URL = 'https://inmuebles.mercadolibre.com.ar/'
URL_TEMPLATE = '{base}{operation}/{publisher}/{page}'

# OTHER CONSTANTS
UNDER_SCORE = '_'
BLANK_SPACE = ' '
EMPTY_STRING = ''

# FINAL CSV COLUMNS
LONGITUDE_COLUMN = 'longitude'
LATITUDE_COLUMN = 'latitude'
DESCRIPTION_COLUMN = 'description'
LOCATION_COLUMN = 'location'
ADDRESS_COLUMN = 'address'
PHONE_FORMATED_COLUMN_TEMPLATE = 'phone_{}_formated'
PHONE_COLUMN_TEMPLATE = 'phone_{}'
NAME_COLUMN = 'name'
LINK_COLUMN = 'link'
BATHROOMS_COLUMN = 'bathrooms'
ROOMS_COLUMN = 'rooms'
SIZE_COLUMN = 'size'
PRICE_COLUMN = 'price'
CURRENCY_COLUMN = 'currency'
TYPE_COLUMN = 'type'
SHORT_DESCRIPTION_COLUM = 'shortDescription'

# ORIGINAL HTML TAGS
A_TAG = 'a'
HREF = 'href'
SHORT_DESCRIPTION_STATIC = 'short-description--static'
VIP_SECTION_SELLER_INFO = 'vip-section-seller-info'
PROFILE_INFO_PHONE_VALUE = 'profile-info-phone-value'
MAP_ADDRESS = 'map-address'
MAP_LOCATION = 'map-location'
ITEM_DESCRIPTION__TEXT = 'item-description__text'
SPECS_LIST = 'specs-list'
STRONG = 'strong'
UL = 'ul'
LINE_BREAK = '<br>'
DIV = 'div'
H3 = 'h3'
H2 = 'h2'
H1 = 'h1'
DL = 'dl'
SPAN = 'span'
SECTION = 'section'
CLASS_TAG = 'class'
END_LAT_LONG_SEPARATOR = '&zoom'
SCRIPT = 'script'
LAT_LONG_SEPARATOR = '%2C'
GOOGLE_MAP_BASE_URL = 'https://maps.googleapis.com/maps/api/staticmap?center='
INFO_LINK = 'item__info-link'
PAGE_PART_TEMPLATE = '_Desde_{}'


class MeliScrapper(GeneralScrapper):
    def get_search_url(self, publisher_type: str, operation_type: str, page: int) -> str:
        page_part_number = self.page_size * (page - 1) + 1
        page_part = PAGE_PART_TEMPLATE.format(page_part_number)

        return URL_TEMPLATE.format(
            base=BASE_URL,
            operation=operation_type,
            publisher=publisher_type,
            page=page_part
        )

    def get_house_list(self, response_soup) -> list:
        house_list = response_soup.find_all(A_TAG, {CLASS_TAG: INFO_LINK})
        return list(set(house_item.get(HREF) for house_item in house_list))

    def get_data(self, base, content_lists):
        index = content_lists.pop(0)
        try:
            if content_lists:
                data = self.get_data(base[index].contents, content_lists)
            else:
                data = base[index]
        except Exception:
            return None

        return data

    def get_lat_long(self, response_house):
        lat_long = ' {} '.format(LAT_LONG_SEPARATOR)
        google_map_url = GOOGLE_MAP_BASE_URL
        for script in response_house.find_all(SCRIPT):
            if google_map_url in script.get_text():
                lat_long = \
                    script.get_text().split(google_map_url)[1].split(END_LAT_LONG_SEPARATOR)[0]

        return tuple(lat_long.split(LAT_LONG_SEPARATOR))

    def get_house_info(self, link):
        logger.info(f'Start get_house_info|\t\t{link}')
        response_house = self.get(link)
        info = {}
        if response_house:
            short_description = response_house.find(SECTION, {CLASS_TAG: SHORT_DESCRIPTION_STATIC})

            info[SHORT_DESCRIPTION_COLUM] = self.get_data(short_description.find(H1).contents, [0]).strip()
            info[TYPE_COLUMN] = link[8:].split('.')[0]
            info[CURRENCY_COLUMN] = self.get_data(short_description.find(SPAN).contents, [1, 0])
            info[PRICE_COLUMN] = self.get_data(short_description.find(SPAN).contents, [3, 0])
            info[SIZE_COLUMN] = self.get_data(short_description.find_all(DL), [1, 2, 0])
            info[ROOMS_COLUMN] = self.get_data(short_description.find_all(DL), [2, 2, 0])
            info[BATHROOMS_COLUMN] = self.get_data(short_description.find_all(DL), [3, 2, 0])
            info[LINK_COLUMN] = link

            section_view_more = response_house.find(SECTION, {CLASS_TAG: VIP_SECTION_SELLER_INFO})

            info[NAME_COLUMN] = self.get_data(section_view_more.contents, [5, 1, 0])

            for i, phone in enumerate(section_view_more.find_all(SPAN, {CLASS_TAG: PROFILE_INFO_PHONE_VALUE})):
                info[PHONE_COLUMN_TEMPLATE.format(i)] = phone.get_text()
                info[PHONE_FORMATED_COLUMN_TEMPLATE.format(i)] = get_formated_telephone(phone.get_text())

            info[ADDRESS_COLUMN] = self.get_data(response_house.find(H2, {CLASS_TAG: MAP_ADDRESS}).contents, [0])
            info[LOCATION_COLUMN] = self.get_data(response_house.find(H3, {CLASS_TAG: MAP_LOCATION}).contents, [0])

            try:
                info[DESCRIPTION_COLUMN] = response_house.find(DIV, {CLASS_TAG: ITEM_DESCRIPTION__TEXT}).find(
                    'p').get_text().replace(LINE_BREAK, EMPTY_STRING)
            except Exception:
                info[DESCRIPTION_COLUMN] = EMPTY_STRING

            info[LATITUDE_COLUMN], info[LONGITUDE_COLUMN] = self.get_lat_long(response_house)

            spec_items = response_house.find(UL, {CLASS_TAG: SPECS_LIST})
            if spec_items:
                for spec_item in spec_items.children:
                    if isinstance(spec_item, Tag):
                        info[spec_item.find(STRONG).get_text().replace(BLANK_SPACE, UNDER_SCORE)] = spec_item.find(
                            SPAN).get_text()

        logger.info(f'End get_house_info|\t\t{link}')
        return info

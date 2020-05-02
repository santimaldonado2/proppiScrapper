# CONFIGURATION FIELDS
FROM_PAGE = 'from_page'
PAGES = 'pages'
PUBLISHER_TYPES = 'publisher_types'
OPERATION_TYPES = 'operation_types'
SLEEP = 'sleep'
CONTACT_INFO = 'contact_info'
USE_PROXY = 'use_proxy'
REQUESTS = 'requests'
SCRAP = 'scrap'

# DIRECTORIES
IDS_DIRECTORY = 'ids_directory'
RESULTS_DIRECTORY = 'results'
TEMP = 'temp'

# FILES_SUFIXES
INFO = 'info'
IDS = 'ids'

# SCRAPPERS
LAVOZ = 'lavoz'
MELI = 'meli'
ZONAPROP = 'zonaprop'

PAGE_SIZES = {
    LAVOZ: 20,
    MELI: 48,
    ZONAPROP: 20
}

# OTHER
ENCODING = 'UTF-8'
TRUE_STRING = 'true'
FALSE_STRING = 'false'

#MERGE FILES
COLUMNS_TO_KEEP = {
    'zonaprop': ['publication_date', 'city', 'house_type', 'operation_type', 'price_currency', 'price', 'dormitorios', 'title', 'url'],
    'lavoz': ['recs:publishtime', 'gcl-barrio', 'gcl-tipo-aviso', 'gcl-operacion', 'price:currency', 'price:amount', 'gcl-dormitorios', 'title', 'url', 'telephone','telephone_formated'],
    'meli': ['publication_date', 'location', 'type', 'operation_type', 'currency', 'price', 'Dormitorios', 'shortDescription', 'link', 'phone_1', 'phone_1_formated']
}

COLUMNS_NAMES = ['Fecha Publicación', 'Barrio', 'Tipo de Propiedad', 'Tipo de Operación', 'Moneda', 'Precio', 'Dormitorios', 'Título', 'URL', 'Teléfono', 'Teléfono2']


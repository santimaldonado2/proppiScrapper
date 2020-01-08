##https://casa.mercadolibre.com.ar

import requests

pag_principal_meli = requests.get('https://casa.mercadolibre.com.ar/')
##print(pagina_principal_meli.text)

##busqueda de casas venta rosario
pagina_busqueda_meli = requests.get(
    'https://inmuebles.mercadolibre.com.ar/casas/venta/santa-fe/rosario/#origin=search&as_word=true')
##print(pagina_busqueda_meli.text)

##casa particular de MELI
busqueda_particular_meli = requests.get(
    'https://casa.mercadolibre.com.ar/MLA-832708373-hermosa-casa-1-habitacion-y-1-quinchocasa-monoambiente-_JM#position=3&type=item&tracking_id=163d7e26-199b-4609-8c7b-c8e27873bcd4')
print(busqueda_particular_meli.text)

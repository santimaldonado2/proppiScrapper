import requests

meli = 'https://inmuebles.mercadolibre.com.ar/cordoba/cordoba/#featured-locations=true'
meli_item = 'https://departamento.mercadolibre.com.ar/MLA-833561413-emprendimiento-claret-village-us-160000-cochera-incluida-_JM#position=1&type=item&tracking_id=9c820fe6-64cf-412f-a87b-d8f90e7c3429'
## para buscar los links a los items buscar :
##<a href="https://casa.mercadolibre.com
## para buscar el telefono en un item buscar:
## <span class="profile-info-phone-value">

lvz = 'https://clasificados.lavoz.com.ar/buscar/inmuebles'
lvz_item = 'https://clasificados.lavoz.com.ar/avisos/casas/3908477/casa-con-escritura-en-palmas-de-claret.html'
## para buscar los links a los items buscar :
## <a class="text-decoration-none" href="
## para buscar el telefono en un item buscar:
## <span class="fa fa-phone"></span>

m360 = 'https://miro360.com.ar/propiedades?words=&operation%5B%5D=&type%5B%5D='
m360_item = 'https://miro360.com.ar/propiedad/alquilamos-dto-2-dormitorios-semi-amoblado'
## para buscar los links a los items buscar :
##-> m360 hace la busqueda de los items en 2 llamados
## para buscar el telefono en un item buscar:
##<span class="d-block"><i class="la la-phone">
## buscar el mail con : <span class="d-block"><i class="la la-envelope"></i>

lux = 'https://es.luxuryestate.com/argentina'
lux_item = 'https://es.luxuryestate.com/p51312945-piso-apartamento-en-venta-buenos-aires'
## para buscar los links a los items buscar :
## -> no me deja buscar el item desde la pagina de busqueda
## para buscar el telefono en un item buscar:
##data-track-phone-value

cbav = 'https://www.cordobavende.com/productos/38-inmuebles/185-casas/lista-1-20.html'
cbav_item = 'https://www.cordobavende.com/ficha/18091732-casa-venta-excelente-ubicacin-b-cafferata-alta-graci.html'
## para buscar los links a los items buscar :
##<a href="https://www.cordobavende.com/ficha
## para buscar el telefono en un item buscar:
##<span>351

zonap = 'https://www.zonaprop.com.ar/inmuebles-cordoba.html'
zonap_item = 'https://www.zonaprop.com.ar/propiedades/amplia-oficina-zona-cambiaria-centro-5-privados-45518272.html'
## para buscar los links a los items buscar :
##"url" : "/propiedades/
## para buscar el telefono en un item buscar: SOLO BUSCA LOS PRIMEROS 5 digitos, se hace con 2 llamados
##'partialPhone': '

##reemplazar en response la pagina, o el item del get
response = requests.get(zonap_item)
print(response.text)

import requests

meli = 'https://inmuebles.mercadolibre.com.ar/cordoba/cordoba/#featured-locations=true'
meli_item = 'https://departamento.mercadolibre.com.ar/MLA-833561413-emprendimiento-claret-village-us-160000-cochera-incluida-_JM#position=1&type=item&tracking_id=9c820fe6-64cf-412f-a87b-d8f90e7c3429'
## para buscar los links a los items buscar :
##<a href="https://casa.mercadolibre.com
## para buscar el telefono en un item buscar:
## <span class="profile-info-phone-value">


##reemplazar en response la pagina, o el item
response = requests.get(meli)
print(response.text)

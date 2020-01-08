import requests

## zonaprop - argentino de inmuebles24

##deptos en la plata 2 ambientes


pagina_busqueda_zonaprop = requests.get('https://www.zonaprop.com.ar/departamentos-venta-la-plata-2-ambientes.html')
print('otorrinonaringologo')
print(pagina_busqueda_zonaprop.text)

## un depto particular
busqueda_particular_zonaprop = requests.get(
    'https://www.zonaprop.com.ar/propiedades/departamento-de-2-dorm.-en-venta-en-la-plata-45230267.html')

##print(pagina_busqueda_zonaprop.text)

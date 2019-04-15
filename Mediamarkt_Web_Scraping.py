#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Web scraping price information from www.mediamarkt.es
Based on:
https://github.com/Brinkhuis/Mediamarkt/blob/master/code/mediamarkt.py
"""

import ast
import requests
import urllib

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import time
import datetime

from bs4 import BeautifulSoup
from tqdm import tqdm
from requests.exceptions import HTTPError

#get_ipython().run_line_magic('matplotlib', 'inline')


# URL dónde está la lista de productos
URL = "https://www.mediamarkt.es/sitemap/sitemap-productlist.xml"


# Configuramos el user agent

headers = requests.utils.default_headers()
print(headers)


# Common user agent list
# Referencia: http://www.networkinghowtos.com/howto/common-user-agent-list/
# Google Chrome
# "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
# Mozilla Firefox
# "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
# Microsoft Edge
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 
# Safari/537.36 Edge/14.14393
# Google bot
# Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
# Bing bot
# Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)


# Actualizamos el user agent
headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0'})
print(headers)



# Definimoos la función para leer el xml y extraer los links que pasaremos
# Referencia:
# https://stackoverflow.com/questions/18966368/python-beautifulsoup-scrape-tables
# Le paso la URL como parámetro, así podrá valer para los diferentes sitios.
def get_products (URL):
    soup = BeautifulSoup(requests.get(URL).text, 'lxml')
    #links = soup.find_all('loc')
    links = []
    #links = soup.find_all("loc")
    for link in soup.find_all("loc"):
        links.append(str(link).replace("<loc>","").replace("</loc>",""))
    return links


# Cargamos los links a partir del sitemap
pagelinks = get_products(URL)



# Mostramos los primeros 10
print(pagelinks[1:10])


#Comprobamos la cantidad de pagelinks
print(len(pagelinks))


# Referencia del código:
# https://github.com/Brinkhuis/Mediamarkt/blob/master/code/mediamarkt.py
def npages(mysoup):
    pagination = list()
    npages = 1
    for page_number in mysoup.find_all('div', {'class': 'pagination-wrapper cf'}):
        pagination.append(page_number.find_all('a'))
        npages = int(str(pagination[0]).split(', ')[-2].strip('</a>').split('>')[-1])
        # Para debug, se imprime el número de páginas.
        print ("Número de páginas: %d" % npages)
    return npages 

# Referencia del código:
# https://github.com/Brinkhuis/Mediamarkt/blob/master/code/mediamarkt.py      


def get_data(URL, output_file = None):
    # Para debug, se imprime la URL que se está escaneando
    print("Rastreando: %s" % URL)
    item_list = list()    
    # Handle the requests exceptions
    # Referencia:
    # https://realpython.com/python-requests/
    try:
        response = requests.get(URL)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        for page in tqdm(range(1, npages(BeautifulSoup(response.text, 'html.parser')) +1)):
            try:
                pageresponse = requests.get(URL + '?page=' + str(page))
                # If the response was successful, no Exception will be raised
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')  # Python 3.6
            except Exception as err:
                print(f'Other error occurred: {err}')  # Python 3.6
            else:
                soup = BeautifulSoup(pageresponse.text, 'html.parser')
                all_scripts = soup.find_all('script')
                for script in all_scripts:
                    if script.text.startswith('var product'):
                        item_list.append(ast.literal_eval(script.text.split(' = ')[1].strip(';')))
    
    productinfo = pd.DataFrame() 
    if (len(item_list)>0):
        productinfo = pd.DataFrame(item_list)
        productinfo['price'] = pd.to_numeric(productinfo['price'], errors='coerce')
        
  
    #productinfo.to_csv(output_file, index=False)    
    #print(f'{productinfo.shape[0]} records saved to {output_file}')
    
    return productinfo


def viz_data(input_file, output_file, query = ':', x_px = 1500, y_px = 1000, d_pi = 150):
    productinfo = pd.read_csv(input_file)
    
    productinfo = productinfo[query]

    #x_pixels, y_pixels, dpi = 1500, 1000, 150
    x_pixels, y_pixels, dpi = x_px, y_px, d_pi
    x_inch, y_inch = x_pixels / dpi, y_pixels / dpi

    plt.figure(figsize=(x_inch, y_inch), dpi=dpi)
    sns.boxplot(x='price',
                y='brand',
                data=productinfo.groupby('brand').filter(lambda x: len(x) > 3),
                order=list(productinfo.groupby('brand').filter(lambda x: len(x) > 3)
                           .groupby('brand').price.median().sort_values(ascending=False).index),
                palette='PRGn',
                width=0.75).set_title('Price Distribution per Brand')
    sns.despine(offset=10, trim=True)
    plt.savefig(output_file)
    plt.show()
    plt.close()
    
    print(f'Visualization saved to {output_file}')


#def main():
dat = './data/productinfo.csv'
viz = './plots/price_distribution_brand.png'

# Limito a los 10 primeras líneas
products = pd.DataFrame()
total_products = pd.DataFrame()
k=0
#for link in pagelinks[1:10]:
for link in pagelinks:
    k += 1
    #print("Escaneando pagina %d de %d" % (k, len(pagelinks[1:10])))
    print("Escaneando página %d de %d" % (k, len(pagelinks)))
    products = get_data(link, dat)
    time.sleep(2)
    total_products = total_products.append(products)
        
print("Done. The prices have been scrapped.")


#if __name__ == "__main__":
#    main()



total_products.iloc[np.r_[0:3, -3:0]]


# En caso de error en el escaneo podemos recuperar el último link y continuar con el siguiente código
# k


#k=711
#for link in pagelinks[1:10]:
#for link in pagelinks[711:]:
#    k += 1
#    #print("Escaneando pagina %d de %d" % (k, len(pagelinks[1:10])))
#    print("Escaneando pagina %d de %d" % (k, len(pagelinks)))
#    products = get_data(link, dat)
#    time.sleep(2)
#    total_products = total_products.append(products)
        
#print("Done. The prices have been scrapped.")



# Mostramos los tipos de dato
total_products.dtypes



# Muestramos las primeras y últimas filas
#total_products.iloc[np.r_[0:3, -3:0]]


# Reindexamos el dataframe y volvemos a mostrar primeras y últimas filas
total_products = total_products.reset_index(drop=True)
total_products.iloc[np.r_[0:3, -3:0]]


# Hay productos que se han podido cargar más de una vez, los eliminamos
total_products = total_products.drop_duplicates()


# Reindexamos y volvemos a mostrar las primeras y últimas filas
total_products = total_products.reset_index(drop=True)
total_products.iloc[np.r_[0:3, -3:0]]


# Obtenemos la fecha del sistema
now = datetime.datetime.now()


# Solo nos interesa el día
now.strftime("%Y-%m-%d")


# Añadimos la fecha
total_products['date'] = now.strftime("%Y-%m-%d")


# Mostramos las tres primeras y últimas filas
total_products.iloc[np.r_[0:3, -3:0]]


# Renombramos las columnas
total_products = total_products.rename(columns = {'dimension9':'subcategory', 'dimension10':'producto',
                                                  'dimension11':'subproducto', 'dimension24':'iva_aplicado',
                                                  'dimension25':'stock_status', 'dimension26':'coste_envio'})


# Reordenamos el orden de las columnas
cols = total_products.columns.tolist()
print(len(cols))
print(cols)

if len(cols) == 14:
    cols = [cols[index] for index in [8,9,1,7,2,3,0,10,11,12,13,4,5,6]]
elif len(cols) == 13:
    cols = [cols[index] for index in [8,9,1,7,2,3,0,10,11,12,4,5,6]]
elif len(cols) == 12:
    cols = [cols[index] for index in [8,9,1,7,2,3,0,10,11,4,5,6]]
    
total_products = total_products[cols]


# Convertimos a número el coste de envío y el iva aplicado
total_products['iva_aplicado'] = pd.to_numeric(total_products['iva_aplicado'], errors='coerce')
total_products['coste_envio'] = pd.to_numeric(total_products['coste_envio'], errors='coerce')

# Mostramos los tipos de dato
print(total_products.dtypes)

# Mostramos el dataframe
total_products

print(dat.replace('info', 'info_'+now.strftime("%Y%m%d")))
# dat.replace('info', 'info_'+now.strftime("%Y%m%d")).replace('.csv', '.xlsx')

# Exportamos a csv, se añade la fecha en el nombre
total_products.to_csv(dat.replace('info', 'info_'+now.strftime("%Y%m%d")))

# Exportamos a excel
total_products.to_excel(dat.replace('info', 'info_'+now.strftime("%Y%m%d")).replace('.csv', '.xlsx'),
                        engine = 'xlsxwriter')

#query = total_products.producto == 'Instantáneas y retro'
#query = total_products.producto == 'Televisores'

#viz_data(dat.replace('info', 'info_'+now.strftime("%Y%m%d")), viz, query, 1500, 1000)

# Recuperamos el archivo guardado
#catalogue =  pd.read_csv('./data/productinfo_20190410.csv', dtype={'ean': str, 'id': str}, index_col=0)

#catalogue


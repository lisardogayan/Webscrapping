<html>
Tipología y Ciclo de Vida de los Datos<br/>
UOC<br/>
Práctica 1: Web Scraping

<p>
Proyecto en python realizado para la asignatura de Tipología y ciclo de vida de los datos en el cual se extraen los precios de todas las categorías de Media Markt, siendo este el portal de referencia para el mercado de consumo electrónico y que se puede tomar como base para la comparación de precios. El scraper puede ser ajustado para las webs de los diferentes países ya que utilizan la misma estructura web.
Se genera un dataset “productinfo.csv” con la información de todos y cada uno de los artículos listados en la web, </p>

•	Brand<br/>
•	category<br/>
•	dimension10<br/>
•	dimension11<br/>
•	dimension24<br/>
•	dimension25<br/>
•	dimension26<br/>
•	dimension9<br/>
•	ean<br/>
•	id<br/>
•	name<br/>
•	price<br/>

<p>Integrantes del equipo<br/>
Lisardo Gayán <br/>
Jose Luis Melo </p>

## Descripción de los ficheros
• Test_Webscrapping.ipynb: Código Python para la captura de datos.<br/>
• Mediamarkt_Web_Scraping.ipynb: Versión actualizada del código, se añade precio en formato numérico (float). 
  Se añade la fecha del scrap
  También en la visualización se le puede pasar una query.
  Faltaría renombrar los campos.
• Data/productinfo.csv: Archivo .csv con los datos capturados.<br/>
• Plots/price_distribution_brand.png: Imagen .png con gráfico de líneas de los resultado del análisis.<br/>
</html>

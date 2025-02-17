from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def buscar_noticias(url, xpath_articulo, xpath_titulo, xpath_enlace, xpath_fecha, nombre_archivo):
    driver.get(url)
    time.sleep(5)  # Esperar carga inicial

    # 🔥 Hacer scroll para cargar más resultados
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Esperar a que se carguen los artículos
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, xpath_articulo))
        )
    except:
        print(f"⚠️ No se encontraron artículos en {url} después de hacer scroll.")
        return

    # Obtener artículos con XPath
    noticias_filtradas = []
    resultados = driver.find_elements(By.XPATH, xpath_articulo)
    print(f"🔍 Se encontraron {len(resultados)} artículos en {url}.")

    for resultado in resultados:
        try:
            titulo = resultado.find_element(By.XPATH, xpath_titulo).text.strip()
            enlace = resultado.find_element(By.XPATH, xpath_enlace).get_attribute("href")
            
            try:
                fecha_texto = resultado.find_element(By.XPATH, xpath_fecha).get_attribute("datetime")
            except:
                fecha_texto = ""

            fecha_publicacion = datetime.strptime(fecha_texto[:10], "%Y-%m-%d") if fecha_texto else datetime.today()

            if FECHA_INICIO <= fecha_publicacion <= FECHA_FIN:
                noticias_filtradas.append({
                    "Fecha": fecha_publicacion.strftime("%Y-%m-%d"),
                    "Título": titulo,
                    "Enlace": enlace
                })
        except Exception as e:
            print(f"⚠️ Error procesando una noticia en {url}: {e}")

    if noticias_filtradas:
        df = pd.DataFrame(noticias_filtradas)
        df.to_csv(nombre_archivo, index=False, encoding="utf-8")
        print(f"✅ Noticias guardadas en '{nombre_archivo}'.")
    else:
        print("⚠️ No se encontraron noticias en el rango de fechas especificado.")

# 🔍 Rango de fechas
FECHA_INICIO = datetime(2025, 2, 1)
FECHA_FIN = datetime(2025, 2, 15)

# 🚀 Configurar Selenium con Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 🔎 Parámetros para cada sitio
sitios = [
    {   # El Espectador
        "url": "https://www.elespectador.com/buscador/Amazonas",
        "xpath_articulo": "//div[contains(@class, 'Card-Container')]",
        "xpath_titulo": ".//h2",
        "xpath_enlace": ".//a",
        "xpath_fecha": ".//time",
        "nombre_archivo": "C:/Users/william.mora/Desktop/codigo/noticias_brenda_olaya.csv"
    },
    {   # El Tiempo
        "url": "https://www.eltiempo.com/buscar/?q=Amazonas",
        "xpath_articulo": "//div[contains(@class, 'c-article__txt')]",
        "xpath_titulo": ".//h3",
        "xpath_enlace": ".//a",
        "xpath_fecha": ".//time",
        "nombre_archivo": "C:/Users/william.mora/Desktop/codigo/noticias_brenda_olaya2.csv"
    }
]

# Ejecutar búsqueda en cada sitio
for sitio in sitios:
    buscar_noticias(**sitio)

# Cerrar Selenium
driver.quit()
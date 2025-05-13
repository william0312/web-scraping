import os
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 📁 Configuración de rutas
base_path = 'C:/Users/william.mora/Desktop/codigo/'
archivo_excel = "Anexos_Descarga_ETB.xlsx"
download_dir = os.path.join(base_path, "descargas")
os.makedirs(download_dir, exist_ok=True)

# 📄 Leer URLs desde Excel
df = pd.read_excel(os.path.join(base_path, archivo_excel))
urls = df["URL"].tolist()

# 🚀 Configurar Selenium para login
options = webdriver.ChromeOptions()
service = Service()
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# 🔐 1. Iniciar sesión con Selenium
try:
    driver.get("https://etb.lavenirapps.co/")
    
    usuario = wait.until(EC.visibility_of_element_located((By.NAME, "LoginForm[username]")))
    password = wait.until(EC.visibility_of_element_located((By.NAME, "LoginForm[password]")))

    usuario.send_keys("william.mora")     # <-- Cambiar por usuario real
    password.send_keys("123456")          # <-- Cambiar por contraseña real
    password.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("✅ Login exitoso.")
    time.sleep(3)  # Espera un poco para asegurar cookies cargadas

    # 🍪 2. Extraer cookies
    selenium_cookies = driver.get_cookies()
    driver.quit()

except Exception as e:
    print("🚨 Error durante el login:", e)
    driver.quit()
    exit()

# 🍪 3. Convertir cookies de Selenium a requests
session = requests.Session()
for cookie in selenium_cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# 📊 Lista para registrar resultados
log_descargas = []

# 🧲 4. Descargar archivos usando requests + cookies
def descargar_pdf(url, carpeta_destino, nombre_archivo=None):
    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
        if "application/pdf" not in response.headers.get("Content-Type", ""):
            raise Exception("La URL no devolvió un PDF.")

        nombre_archivo = nombre_archivo or f"{url.split('=')[-1]}.pdf"
        path_destino = os.path.join(carpeta_destino, nombre_archivo)
        with open(path_destino, "wb") as f:
            f.write(response.content)

        print(f"✅ PDF descargado: {nombre_archivo}")
        log_descargas.append({
            "URL": url,
            "Archivo": nombre_archivo,
            "Estado": "Descargado",
            "Detalle": ""
        })
    except Exception as e:
        print(f"❌ Error al descargar {url}: {e}")
        log_descargas.append({
            "URL": url,
            "Archivo": "",
            "Estado": "Error",
            "Detalle": str(e)
        })

# 🔄 5. Descargar todos los PDFs
for index, url in enumerate(urls):
    print(f"📥 Descargando PDF {index + 1}/{len(urls)}: {url}")
    descargar_pdf(url, download_dir)

# 💾 6. Guardar log al final
df_log = pd.DataFrame(log_descargas)
log_path = os.path.join(base_path, "log_descarga_pdfs.xlsx")
df_log.to_excel(log_path, index=False)
print(f"\n📁 Log guardado en: {log_path}")
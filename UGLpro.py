from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import time
import datetime
import csv

CHROMEDRIVER_PATH = './chromedriver.exe'

# Palabras clave
palabras_clave = ['kit', 'neuro', 'neurocirugía', 'estimulador', 'batería',
                  'electrodos', 'neuroestimulador', 'bomba', 'intratecal',
                  'DRG', 'proclaim','abbott','infinity','IOS','direccional',
                  'epidural','ganglio','corriente','cerebral','electrodo','profundo']

# Lista de destinos (UGLs)
destinos = [
    "UGL II Corrientes",
    "UGL VII La Plata",
    "UGL IX Rosario",
    "UGL XIII Chaco",
    "UGL XIV Entre Ríos",
    "UGL XV Santa Fé",
    "UGL XVIII Misiones",
    "UGL XXIII Formosa",
    "UGL XXXIV Concordia",
    "Policlínico PAMI 1",
    "Policlínico PAMI 2"
]

# Fecha para "Desde" y "Hasta" (mañana)
hoy_dia = (datetime.datetime.now()+ datetime.timedelta(days=1)).day
mañana_dia = (datetime.datetime.now()+ datetime.timedelta(days=2)).day
print(f"{hoy_dia , mañana_dia}")
# Donde vamos a acumular los resultados
todos_los_resultados = []

# Loop por cada destino
for destino in destinos:
    print(f"\nBuscando en: {destino}")
    
    # Inicializar el navegador
##    driver = webdriver.Chrome()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")  # (opcional) Para que todo cargue bien
    chrome_options.add_argument("--disable-gpu")  # (opcional) Mejora estabilidad en algunos entornos
    driver = webdriver.Chrome(options=chrome_options)

    # Ir a la página
    driver.get("https://prestadores.pami.org.ar/result.php?c=7-5&par=2")
    wait = WebDriverWait(driver, 10)
##    driver.maximize_window()

    # Seleccionar destino (UGL)
    select_destino = Select(wait.until(EC.presence_of_element_located((By.ID, "destino_compra"))))
    select_destino.select_by_visible_text(destino)

    # --- Seleccionar fecha Desde ---
    campo_desde = driver.find_element(By.ID, 'fecha_post')
    campo_desde.click()

    # Esperar a que el calendario esté visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'ui-datepicker-calendar'))
    )


    # Selecciona el día
    dia_element = driver.find_element(By.XPATH, f"//a[text()='{hoy_dia}']")
    dia_element.click()

    # --- Seleccionar fecha Hasta ---
    campo_hasta = driver.find_element(By.ID, 'fecha_ant')
    campo_hasta.click()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'ui-datepicker-calendar'))
    )

    # Buscar el botón del día correcto nuevamente
    dia_element_hasta = driver.find_element(By.XPATH, f"//a[text()='{mañana_dia}']")
    dia_element_hasta.click()

    # Click en Buscar
    driver.find_element(By.ID, 'srchBtn').click()

    # Esperar que la tabla esté visible
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="resultados"]/table')))
        
        # Capturar tabla
        tabla = driver.find_element(By.XPATH, '//*[@id="resultados"]/table')
        filas = tabla.find_elements(By.TAG_NAME, 'tr')

        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, 'td')
            if len(columnas) >= 5:
                detalle = columnas[4].text.lower().strip()
                if any(palabra in detalle for palabra in palabras_clave):
                    numero = columnas[0].text.strip()
                    ugl = columnas[2].text.strip()
                    detalle = columnas[4].text.lower().strip()
                    todos_los_resultados.append((numero, ugl, destino, detalle))

    except Exception as e:
        print(f"No se encontraron resultados para {destino}")

    # Cerrar navegador
    driver.quit()

# Mostrar todos los resultados encontrados
for numero, ugl, destino, detalle in todos_los_resultados:
    print("="*60)
    print(f"Destino: {destino}\nNúmero: {numero}\nUGL: {ugl}\nDetalle: {detalle}")
    print("="*60)

# (Opcional) Guardar en CSV
with open('resultados_pami.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Destino', 'Número de Solicitud', 'UGL', 'Detalle'])
    for numero, ugl, destino, detalle in todos_los_resultados:
        writer.writerow([destino, numero, ugl, detalle])

print("\nBúsqueda completa y resultados guardados en 'resultados_pami.csv'!")

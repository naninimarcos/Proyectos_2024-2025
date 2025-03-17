import os
import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración del WebDriver
def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Para ejecución sin interfaz gráfica
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1470, 877)
    return driver

# Función para iniciar sesión
def iniciar_sesion(driver, usuario, clave):
    driver.get("https://cidi.cba.gov.ar/portal-publico/")
    driver.find_element(By.CSS_SELECTOR, ".btn-ingresar").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(clave, Keys.ENTER)
    time.sleep(2)

# Función para capturar datos de un trámite
def capturar_datos(driver, id_tramite, campos_ids):
    url = f"https://erseponline.cba.gov.ar/Paginas/Tramite.aspx?Accion=Consultar&Id_Tramite={id_tramite}"
    driver.get(url)
    datos_capturados = {"OL": id_tramite}
    
    for campo, id_html in campos_ids.items():
        try:
            elemento = driver.find_element(By.ID, id_html)
            datos_capturados[campo] = elemento.get_attribute("value") or "No especificado"
        except:
            datos_capturados[campo] = "No encontrado"
    
    return datos_capturados

# Función para escribir los datos en CSV
def guardar_datos_csv(datos, archivo_salida):
    with open(archivo_salida, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = datos[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(datos)
    print(f"Datos guardados en {archivo_salida}")

if __name__ == "__main__":
    USUARIO = os.getenv("CIDI_USUARIO", "TU_USUARIO")
    CLAVE = os.getenv("CIDI_CLAVE", "TU_CLAVE")
    ARCHIVO_ENTRADA = "transporte_Reclamos.xlsx"
    ARCHIVO_SALIDA = "datos_recolectados.csv"
    
    campos_ids = {"DNI": "ctl00_body_ucPersona_txtNro_Documento", "Nombre": "ctl00_body_ucPersona_txtNombre"}  # Agregar más campos
    
    driver = iniciar_driver()
    iniciar_sesion(driver, USUARIO, CLAVE)
    
    xls = pd.ExcelFile(ARCHIVO_ENTRADA, engine="openpyxl")
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[1]).dropna(subset=["ID TRAMITE"])
    lista_id_tramite = df["ID TRAMITE"].tolist()
    
    datos_recolectados = [capturar_datos(driver, id_tramite, campos_ids) for id_tramite in lista_id_tramite]
    guardar_datos_csv(datos_recolectados, ARCHIVO_SALIDA)
    driver.quit()

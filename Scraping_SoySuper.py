from datetime import datetime
from pathlib import Path
import time
import unicodedata
from urllib.parse import urlparse
import urllib.robotparser
from bs4 import BeautifulSoup
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ==============================================================================
# 1. CATÁLOGO DE SUBCATEGORÍAS
# ==============================================================================
SUBCATEGORIAS = [
    ("Aceite", "https://soysuper.com/c/conservas-sopas-aceites-y-condimentos/aceite"),
    ("Aceitunas", "https://soysuper.com/c/conservas-sopas-aceites-y-condimentos/aceitunas"),
    ("Agua", "https://soysuper.com/c/bebidas/agua"),
    ("Ambientadores", "https://soysuper.com/c/drogueria/ambientadores"),
    ("Arroz", "https://soysuper.com/c/pasta-arroz-y-legumbres/arroz"),
    ("Batido", "https://soysuper.com/c/lacteos-y-huevos/batido"),
    ("Bebida Energética", "https://soysuper.com/c/bebidas/bebida-energetica"),
    ("Bebida Isotónica", "https://soysuper.com/c/bebidas/bebida-isotonica"),
    ("Bolsas de Basura", "https://soysuper.com/c/drogueria/bolsas-de-basura"),
    ("Bombones", "https://soysuper.com/c/chocolates-y-dulces/bombones"),
    ("Cacao", "https://soysuper.com/c/cafes-cacaos-e-infusiones/cacao"),
    ("Café", "https://soysuper.com/c/cafes-cacaos-e-infusiones/cafe"),
    ("Cereales", "https://soysuper.com/c/cereales-y-galletas/cereales"),
    ("Chocolates", "https://soysuper.com/c/chocolates-y-dulces/chocolates"),
    ("Colonia", "https://soysuper.com/c/perfumeria-y-parafarmacia/colonia"),
    ("Conservas Dulces", "https://soysuper.com/c/conservas-sopas-aceites-y-condimentos/conservas-dulces"),
    ("Conservas de Pescado", "https://soysuper.com/c/conservas-sopas-aceites-y-condimentos/conservas-de-pescado"),
    ("Desodorante", "https://soysuper.com/c/perfumeria-y-parafarmacia/desodorante"),
    ("Galletas", "https://soysuper.com/c/cereales-y-galletas/galletas"),
    ("Horchata", "https://soysuper.com/c/bebidas/horchata"),
    ("Huevos", "https://soysuper.com/c/lacteos-y-huevos/huevos"),
    ("Infusiones", "https://soysuper.com/c/cafes-cacaos-e-infusiones/infusiones"),
    ("Insecticidas", "https://soysuper.com/c/drogueria/insecticidas"),
    ("Leche", "https://soysuper.com/c/lacteos-y-huevos/leche"),
    ("Mantequilla", "https://soysuper.com/c/lacteos-y-huevos/mantequilla"),
    ("Margarina", "https://soysuper.com/c/lacteos-y-huevos/margarina"),
    ("Nata", "https://soysuper.com/c/lacteos-y-huevos/nata"),
    ("Pasta", "https://soysuper.com/c/pasta-arroz-y-legumbres/pasta"),
    ("Patatas Fritas", "https://soysuper.com/c/aperitivos/patatas-fritas"),
    ("Paté", "https://soysuper.com/c/conservas-sopas-aceites-y-condimentos/pate"),
    ("Pañales", "https://soysuper.com/c/bebes-y-ninos/panales"),
    ("Platos Preparados", "https://soysuper.com/c/congelados/platos-preparados"),
    ("Productos Para Deportistas", "https://soysuper.com/c/dieteticos/productos-para-deportistas"),
    ("Queso", "https://soysuper.com/c/lacteos-y-huevos/queso"),
    ("Refresco", "https://soysuper.com/c/bebidas/refresco"),
    ("Snacks", "https://soysuper.com/c/aperitivos/snacks"),
    ("Toallitas", "https://soysuper.com/c/bebes-y-ninos/toallitas"),
    ("Vinagre", "https://soysuper.com/c/conservas-sopas-aceites-y-condimentos/vinagre"),
    ("Yogur", "https://soysuper.com/c/lacteos-y-huevos/yogur"),
    ("Zumo", "https://soysuper.com/c/bebidas/zumo"),
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


# ==============================================================================
# 2. FUNCIONES AUXILIARES DE TEXTO, SELECCIÓN Y VERIFICACIÓN ROBOTS/HTTP
# ==============================================================================

def log(mensaje):
    """Imprime mensajes forzando el vaciado inmediato del búfer en consola."""
    print(mensaje, flush=True)


def normalizar_texto(texto):
    """Elimina tildes, pasa a minúsculas y normaliza espacios para comparar entradas."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(sin_tildes.lower().strip().split())


def limpiar_slug(texto):
    """Genera un identificador seguro en minúsculas con guiones bajos para el nombre del CSV."""
    limpio = "".join(
        c.lower() if c.isalnum() else "_"
        for c in normalizar_texto(texto)
    ).strip("_")
    return limpio or "subcategoria"


def seleccionar_subcategoria():
    """Muestra las subcategorías y resuelve la elección del usuario por número o texto."""
    log("Subcategorías disponibles:")
    for idx, (nombre, _) in enumerate(SUBCATEGORIAS, start=1):
        log(f"  {idx:>2}. {nombre}")

    entrada = input("\nIntroduce la subcategoría a filtrar (nombre o número): ").strip()

    if entrada.isdigit():
        indice = int(entrada)
        if 1 <= indice <= len(SUBCATEGORIAS):
            return SUBCATEGORIAS[indice - 1]
        log("Número fuera de rango; se usará 'Yogur' por defecto.")
        return next(item for item in SUBCATEGORIAS if item[0] == "Yogur")

    consulta = normalizar_texto(entrada)
    if not consulta:
        return next(item for item in SUBCATEGORIAS if item[0] == "Yogur")

    coincidencias = [
        item for item in SUBCATEGORIAS
        if consulta in normalizar_texto(item[0])
    ]

    if len(coincidencias) == 1:
        return coincidencias[0]

    if len(coincidencias) > 1:
        log("\nSe encontraron varias coincidencias:")
        for i, (nombre, _) in enumerate(coincidencias, start=1):
            log(f"  {i}. {nombre}")
        sel = input("Elige cuál quieres extraer (Enter para 1): ").strip() or "1"
        if sel.isdigit() and 1 <= int(sel) <= len(coincidencias):
            return coincidencias[int(sel) - 1]
        return coincidencias[0]

    log(f"No se encontró '{entrada}'; se usará 'Yogur' por defecto.")
    return next(item for item in SUBCATEGORIAS if item[0] == "Yogur")


def verificar_robots_y_http(url_objetivo):
    """
    Ejecuta y muestra en consola la validación HTTP de la URL objetivo
    y la comprobación de permisos en robots.txt.
    """
    log("\n==========================================")
    log("VALIDACIÓN HTTP Y ROBOTS.TXT")
    log("==========================================")

    parsed = urlparse(url_objetivo)
    dominio_sin_www = parsed.netloc.replace("www.", "")
    url_robots = f"{parsed.scheme}://www.{dominio_sin_www}/robots.txt"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    # 1. Validación HTTP
    try:
        resp_http = requests.get(url_objetivo, headers=headers, timeout=10)
        estado_txt = "OK" if 200 <= resp_http.status_code < 400 else "REVISAR"
        log(f"[HTTP] URL: {url_objetivo} -> Código: {resp_http.status_code} ({estado_txt})")
    except Exception as e:
        log(f"[HTTP] Error al consultar {url_objetivo}: {e}")

    # 2. Validación robots.txt
    permitido = True
    try:
        resp_robots = requests.get(url_robots, headers=headers, timeout=10)
        log(f"[ROBOTS.TXT] URL: {url_robots} -> Código HTTP: {resp_robots.status_code}")

        if resp_robots.status_code == 200 and resp_robots.text.strip():
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(resp_robots.text.splitlines())
            permitido = rp.can_fetch("*", url_objetivo)
            estado_robot = "PERMITIDO" if permitido else "BLOQUEADO"
            log(f"[ROBOTS.TXT] Ruta '{parsed.path}' -> {estado_robot}")
        else:
            log("[ROBOTS.TXT] No devolvió contenido 200; se continúa con precaución.")
    except Exception as e:
        log(f"[ROBOTS.TXT] Error al leer {url_robots}: {e}")

    log("==========================================\n")
    return permitido


# ==============================================================================
# 3. FUNCIONES DE NAVEGACIÓN Y EXTRACCIÓN CON SELENIUM + BEAUTIFULSOUP
# ==============================================================================

def aceptar_consentimiento(driver, espera=5):
    """Intenta hacer clic en el botón de consentimiento/cookies si aparece en pantalla."""
    try:
        boton = WebDriverWait(driver, espera).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Consentir') or contains(., 'Aceptar')]")
            )
        )
        boton.click()
        time.sleep(0.8)
    except Exception:
        pass


def contar_productos_en_dom(driver):
    """Devuelve el número actual de enlaces de producto cargados en el DOM."""
    return driver.execute_script(
        "return document.querySelectorAll('li a.name, a.name').length;"
    )


def scroll_hasta_fin_productos(driver, pausa=1.0, rondas_sin_cambios=2):
    """
    Desplaza la página hasta el final de forma iterativa y se detiene cuando
    la cantidad de productos en el DOM deja de aumentar tras 'rondas_sin_cambios'.
    """
    total_anterior = contar_productos_en_dom(driver)
    sin_crecer = 0

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pausa)

        total_actual = contar_productos_en_dom(driver)
        if total_actual > total_anterior:
            total_anterior = total_actual
            sin_crecer = 0
        else:
            sin_crecer += 1
            if sin_crecer >= rondas_sin_cambios:
                break

    return total_actual


def extraer_productos_html(html, nombre_sub, fecha_obtencion):
    """Parsea el HTML renderizado y extrae los campos principales de cada producto."""
    soup = BeautifulSoup(html, "html.parser")
    filas = []

    for ficha in soup.select("li"):
        enlace = ficha.select_one("a.name")
        precio_tag = ficha.select_one("span.price")
        if not enlace or not precio_tag:
            continue

        nombre_producto = (enlace.get("title") or enlace.get_text(strip=True)).strip()
        precio_total = precio_tag.get_text(" ", strip=True)

        marca_tag = ficha.select_one("span.brand")
        unit_tag = ficha.select_one("span.unitprice")

        marca = marca_tag.get_text(strip=True) if marca_tag else "Sin marca"
        precio_unitario = unit_tag.get_text(" ", strip=True) if unit_tag else "No disponible"

        if nombre_producto:
            filas.append({
                "Subcategoria": nombre_sub,
                "Producto": nombre_producto,
                "Marca": marca,
                "Precio Total": precio_total,
                "Precio Unitario": precio_unitario,
                "Fecha Obtencion": fecha_obtencion,
            })

    return filas


# ==============================================================================
# 4. EJECUCIÓN PRINCIPAL DEL SCRAPING
# ==============================================================================

nombre_sub, url_sub = seleccionar_subcategoria()
slug_sub = limpiar_slug(nombre_sub)
fecha_obtencion = datetime.now().strftime("%Y-%m-%d")

permitido = verificar_robots_y_http(url_sub)
if not permitido:
    log("La ruta figura bloqueada en robots.txt. Extracción cancelada.")
    raise SystemExit(0)

try:
    driver = webdriver.Chrome()
except Exception as e:
    log(f"Error al iniciar Chrome con Selenium: {e}")
    raise SystemExit(1)

datos_scraping = []
claves_vistas = set()

try:
    log(f"Extrayendo subcategoría: {nombre_sub} -> {url_sub}")
    driver.get(url_sub)
    time.sleep(2.5)
    aceptar_consentimiento(driver, espera=4)

    cargados_dom = scroll_hasta_fin_productos(driver, pausa=1.0, rondas_sin_cambios=2)
    log(f"Productos en DOM tras scroll: {cargados_dom}")

    extraidos = extraer_productos_html(driver.page_source, nombre_sub, fecha_obtencion)

    for fila in extraidos:
        clave = (fila["Subcategoria"], fila["Producto"], fila["Precio Total"])
        if clave not in claves_vistas:
            claves_vistas.add(clave)
            datos_scraping.append(fila)

finally:
    driver.quit()


# ==============================================================================
# 5. ESTRUCTURACIÓN, EXPORTACIÓN A CSV Y RESUMEN EN CONSOLA
# ==============================================================================

for idx, registro in enumerate(datos_scraping, start=1):
    registro["Item"] = idx

columnas_ordenadas = [
    "Item",
    "Subcategoria",
    "Producto",
    "Marca",
    "Precio Total",
    "Precio Unitario",
    "Fecha Obtencion",
]

df_productos = pd.DataFrame(datos_scraping, columns=columnas_ordenadas)

carpeta_proyecto = Path(r"C:\Users\Erick Cordova\Desktop\scraping_eda_")
carpeta_proyecto.mkdir(parents=True, exist_ok=True)
ruta_csv = carpeta_proyecto / f"{slug_sub}_raw.csv"
df_productos.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

log(f"\nSubcategoría filtrada: {nombre_sub}")
log(f"Total productos extraídos: {len(df_productos)}")
log(f"CSV guardado en: {ruta_csv}")
log("\nMuestra de productos:")
log(df_productos.head(15).to_string(index=False))
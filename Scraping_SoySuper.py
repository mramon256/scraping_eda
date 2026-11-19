from datetime import datetime
from pathlib import Path
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CATEGORIAS = {
    "1": (
        "Lácteos y Huevos",
        "https://soysuper.com/c/lacteos-y-huevos",
        "lacteos_y_huevos",
    ),
    "2": (
        "Aperitivos",
        "https://soysuper.com/c/aperitivos",
        "aperitivos",
    ),
    "3": (
        "Bazar y Casa",
        "https://soysuper.com/c/bazar-y-casa",
        "bazar_y_casa",
    ),
    "4": (
        "Bebés y Niños",
        "https://soysuper.com/c/bebes-y-ninos",
        "bebes_y_ninos",
    ),
    "5": (
        "Bebidas",
        "https://soysuper.com/c/bebidas",
        "bebidas",
    ),
    "6": (
        "Cafés, Cacaos e Infusiones",
        "https://soysuper.com/c/cafes-cacaos-e-infusiones",
        "cafes_cacaos_infusiones",
    ),
    "7": (
        "Cereales y Galletas",
        "https://soysuper.com/c/cereales-y-galletas",
        "cereales_y_galletas",
    ),
    "8": (
        "Chocolates y Dulces",
        "https://soysuper.com/c/chocolates-y-dulces",
        "chocolates_y_dulces",
    ),
    "9": (
        "Congelados",
        "https://soysuper.com/c/congelados",
        "congelados",
    ),
    "10": (
        "Conservas, Sopas, Aceites y Condimentos",
        "https://soysuper.com/c/conservas-sopas-aceites-y-condimentos",
        "conservas_sopas_aceites_condimentos",
    ),
    "11": (
        "Dietéticos",
        "https://soysuper.com/c/dieteticos",
        "dieteticos",
    ),
    "12": (
        "Droguería",
        "https://soysuper.com/c/drogueria",
        "drogueria",
    ),
    "13": (
        "Frescos y Charcutería",
        "https://soysuper.com/c/frescos-y-charcuteria",
        "frescos_y_charcuteria",
    ),
    "14": (
        "Mascotas",
        "https://soysuper.com/c/mascotas",
        "mascotas",
    ),
    "15": (
        "Ocio y Cultura",
        "https://soysuper.com/c/ocio-y-cultura",
        "ocio_y_cultura",
    ),
    "16": (
        "Panadería, Pastelería y Repostería",
        "https://soysuper.com/c/panaderia-pasteleria-y-reposteria",
        "panaderia_pasteleria_reposteria",
    ),
    "17": (
        "Pasta, Arroz y Legumbres",
        "https://soysuper.com/c/pasta-arroz-y-legumbres",
        "pasta_arroz_legumbres",
    ),
    "18": (
        "Perfumería y Parafarmacia",
        "https://soysuper.com/c/perfumeria-y-parafarmacia",
        "perfumeria_y_parafarmacia",
    ),
    "19": (
        "Solidaridad",
        "https://soysuper.com/c/solidaridad",
        "solidaridad",
    ),
}


def aceptar_consentimiento(driver, espera=5):
  try:
    boton = WebDriverWait(driver, espera).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(., 'Consentir') or contains(., 'Aceptar')]",
        ))
    )
    boton.click()
    time.sleep(1)
    print("Consentimiento aceptado automáticamente.")
  except Exception:
    pass


print("Selecciona la categoría a extraer:")
for clave, (nombre_cat, _, _) in CATEGORIAS.items():
  print(f"  {clave}. {nombre_cat}")

opcion = (
    input("Elige una opción (Enter para 1 - Lácteos y Huevos): ").strip() or "1"
)
nombre_categoria, url_base, slug_cat = CATEGORIAS.get(opcion, CATEGORIAS["1"])

max_paginas_por_ruta = int(
    input("¿Cuántas páginas revisar por cada subcategoría? (Enter para 3): ").strip()
    or "3"
)

fecha_obtencion = datetime.now().strftime("%Y-%m-%d")
print(f"\nCategoría elegida: {nombre_categoria} | URL base: {url_base}")

try:
  driver = webdriver.Chrome()
except Exception as e:
  print("Error al iniciar Chrome con Selenium:", e)
  raise SystemExit(1)

datos_scraping = []

try:
  driver.get(url_base)
  time.sleep(4)
  aceptar_consentimiento(driver)

  subcategorias = [("General", url_base)]
  urls_vistas = {url_base}

  enlaces = driver.find_elements(By.CSS_SELECTOR, "a[href]")
  for enlace_cat in enlaces:
    href = (enlace_cat.get_attribute("href") or "").split("#")[0].rstrip("/")
    texto_cat = (
        enlace_cat.text.strip().splitlines()[0]
        if enlace_cat.text.strip()
        else ""
    )
    if href.startswith(url_base + "/") and href not in urls_vistas and texto_cat:
      urls_vistas.add(href)
      subcategorias.append((texto_cat, href))

  print(f"Rutas detectadas (general + subcategorías): {len(subcategorias)}")
  for nombre_sub, _ in subcategorias:
    print(f"  - {nombre_sub}")

  for nombre_sub, url_sub in subcategorias:
    for pagina in range(1, max_paginas_por_ruta + 1):
      url_pagina = f"{url_sub}?page={pagina}"
      print(f"\n[{nombre_sub}] Página {pagina}: {url_pagina}")
      driver.get(url_pagina)
      time.sleep(3)
      aceptar_consentimiento(driver, espera=2)

      driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      time.sleep(2)

      productos = driver.find_elements(By.TAG_NAME, "li")
      nuevos = 0

      for prod in productos:
        try:
          enlace = prod.find_element(By.CSS_SELECTOR, "a.name")
          nombre = enlace.get_attribute("title").strip()

          precio_total = (
              prod.find_element(By.CSS_SELECTOR, "span.price")
              .get_attribute("textContent")
              .strip()
          )

          try:
            marca = (
                prod.find_element(By.CSS_SELECTOR, "span.brand")
                .get_attribute("textContent")
                .strip()
            )
          except Exception:
            marca = "Sin marca"

          try:
            precio_unitario = (
                prod.find_element(By.CSS_SELECTOR, "span.unitprice")
                .get_attribute("textContent")
                .strip()
            )
          except Exception:
            precio_unitario = "No disponible"

          fila = {
              "Categoria": nombre_categoria,
              "Subcategoria": nombre_sub,
              "Marca": marca,
              "Producto": nombre,
              "Precio Total": precio_total,
              "Precio Unitario": precio_unitario,
              "Fecha Obtencion": fecha_obtencion,
          }

          if not any(
              d["Producto"] == fila["Producto"]
              and d["Precio Total"] == fila["Precio Total"]
              for d in datos_scraping
          ):
            datos_scraping.append(fila)
            nuevos += 1

        except Exception:
          continue

      print(f"  -> Productos nuevos añadidos: {nuevos}")
      if nuevos == 0:
        break

finally:
  driver.quit()

for idx, registro in enumerate(datos_scraping, start=1):
  registro["Item"] = idx

columnas_ordenadas = [
    "Item",
    "Categoria",
    "Subcategoria",
    "Marca",
    "Producto",
    "Precio Total",
    "Precio Unitario",
    "Fecha Obtencion",
]

df_lacteos = pd.DataFrame(datos_scraping, columns=columnas_ordenadas)

carpeta_proyecto = Path(r"C:\Users\Alumno\Desktop\scraping_eda")
carpeta_proyecto.mkdir(parents=True, exist_ok=True)
ruta_csv = carpeta_proyecto / f"{slug_cat}_todas_subcategorias_raw.csv"
df_lacteos.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

print(f"\nTotal productos extraidos: {len(df_lacteos)}")
print(f"CSV guardado en: {ruta_csv}")
print("\nTodos los productos extraídos:")
print(df_lacteos.to_string(index=False))
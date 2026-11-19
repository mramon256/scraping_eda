# Proyecto: Obtención de Datos y EDA — Supermercados (Soysuper)

## Integrantes
- Isaac Córdova
- Martín Ramón

## 1. Objetivo y ámbito
Análisis exploratorio de productos de supermercado extraídos de **Soysuper** (con foco en **Lácteos y Huevos** y extensible al resto de categorías) para comparar precios totales, precios unitarios y marcas comerciales, complementado con datos nutricionales (Nutri-Score) mediante la API de **Open Food Facts**.

## 2. Obtención de datos

### Fuente 1: Web Scraping — Soysuper
- **URL base:** `https://soysuper.com/c/lacteos-y-huevos` (y categorías principales del catálogo)
- **Fecha de extracción:** `2026-11-19`
- **Revisión legal (`robots.txt`):** Se verificó `https://www.soysuper.com/robots.txt`, confirmando que el acceso a las rutas `/c/...` está permitido para fines académicos sin peticiones masivas.
- **Procedimiento técnico:**
  - Automatización con **Selenium** (`webdriver.Chrome()`) para renderizar contenido dinámico en JavaScript y superar la verificación inicial (`#pow`).
  - Aceptación automática del aviso de consentimiento de cookies.
  - Recorrido automático por categorías, subcategorías y paginación (`?page=1..N`) con desplazamiento (*scroll*), evitando duplicados y exportando a CSV (`utf-8-sig`) en `C:\Users\Alumno\Desktop\scraping_eda`.
- **Campos extraídos:** `Item`, `Categoria`, `Subcategoria`, `Marca`, `Producto`, `Precio Total`, `Precio Unitario` y `Fecha Obtencion`.

### Fuente 2: API REST — Open Food Facts *(en integración)*
- **Endpoint:** `https://es.openfoodfacts.org/` (formato JSON vía `requests`).
- **Aporte:** Enriquecer el catálogo con la valoración nutricional (`Nutri-Score`).

## 3. Estructura del repositorio
```text
SCRAPING_EDA/
├── Productos_lacteos_scrapping.py                # Script principal de extracción
├── lacteos_y_huevos_todas_subcategorias_raw.csv  # Dataset original extraído
└── README.md                                     # Documentación del proyecto

## 4. Requisitos del Sistema y Instalación de Dependencias

### Requisitos del Sistema
- **Python 3.10 o superior**
- **Google Chrome** instalado y actualizado (necesario para el funcionamiento del ChromeDriver con Selenium)
- **Conexión a Internet** activa para la navegación y peticiones API

### Dependencias de Python
Las librerías externas que requiere el proyecto y su finalidad son:

- **`selenium` (`>=4.15.0`)**: Control del navegador Chrome, manejo del renderizado dinámico de JavaScript y gestión del aviso de cookies.
- **`beautifulsoup4` (`>=4.12.0`)**: Parseo del código HTML renderizado de las páginas para extraer etiquetas, títulos y precios rápidamente.
- **`pandas` (`>=2.0.0`)**: Construcción del `DataFrame`, eliminación de duplicados, ordenación de columnas y exportación a archivos CSV.
- **`requests` (`>=2.31.0`)**: Realización de peticiones HTTP `GET` a la API REST de Open Food Facts para consumir las respuestas JSON.
- **`matplotlib` (`>=3.8.0`)** y **`seaborn` (`>=0.13.0`)**: Elaboración de gráficos descriptivos y análisis visual durante el EDA.

*(Nota: Las librerías `datetime`, `pathlib` y `time` forman parte de la biblioteca estándar de Python y no requieren instalación adicional).*


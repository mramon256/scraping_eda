# Proyecto: Obtención de Datos y EDA — Supermercados (Soysuper)
---
## 1. Propósito y funcionamiento general del programa
El proyecto tiene como finalidad automatizar la recolección de datos de productos de supermercado desde **Soysuper** filtrando directamente por **subcategoría** (por ejemplo: *Aceite*, *Leche*, *Queso*, *Yogur*, *Galletas*, *Productos Para Deportistas*, entre otras) para construir un dataset estructurado y reproducible que sirva como base para un **Análisis Exploratorio de Datos (EDA)**.

A diferencia de recorrer todo el catálogo o entrar en vistas generales y niveles interiores redundantes, el programa arranca pidiendo al usuario **qué subcategoría desea filtrar** (por número o por nombre/coincidencia). A continuación:
1. Valida la disponibilidad HTTP de la URL objetivo y consulta `robots.txt` para comprobar si la ruta está permitida.
2. Abre Google Chrome mediante **Selenium**, acepta el banner de consentimiento si aparece y realiza un **desplazamiento (*scroll*) progresivo hasta el final** controlando el número de productos cargados en el DOM.
3. Parsea el HTML renderizado con **BeautifulSoup**, extrae los campos de cada ficha de producto, elimina duplicados, numera los registros (`Item`) y exporta el resultado a un archivo `.csv` (`utf-8-sig`) dentro de la `ruta local.

La integración de la **API de Open Food Facts** para enriquecer los productos con información nutricional (`Nutri-Score`) queda definida como la siguiente etapa del proyecto.

---

## 2. Requisitos previos y librerías necesarias

### Requisitos del entorno
- **Python 3.10 o superior**.
- **Google Chrome** instalado (necesario para la ejecución de `webdriver.Chrome()` en Selenium).
- **Conexión a Internet** activa para consultar Soysuper y `robots.txt`.

### Librerías externas (instalar con `pip`)
- **`selenium`**: Automatiza el navegador Google Chrome para ejecutar JavaScript, interactuar con el banner de consentimiento, hacer *scroll* progresivo y recuperar el HTML final una vez cargados los productos dinámicos.
- **`beautifulsoup4`**: Analiza el HTML renderizado por el navegador y localiza los selectores de cada producto (`li`, `a.name`, `span.price`, `span.brand`, `span.unitprice`).
- **`pandas`**: Construye el `DataFrame` con los datos extraídos, ordena las columnas, asigna el índice correlativo `Item`, exporta el archivo `.csv` con codificación `utf-8-sig` y formatea la vista resumen en consola.
- **`requests`**: Realiza las comprobaciones HTTP iniciales contra la URL de la subcategoría y descarga el archivo `robots.txt` antes de iniciar Selenium (y se empleará en la siguiente fase para consumir la API de Open Food Facts).
- **`matplotlib` y `seaborn`**: Librerías orientadas a la generación de gráficos y visualizaciones estadísticas durante el Análisis Exploratorio de Datos (EDA) sobre los CSV obtenidos.

### Módulos de la biblioteca estándar de Python (incluidos por defecto)
- **`datetime`**: Obtiene la fecha del sistema en formato `YYYY-MM-DD` para rellenar la columna `Fecha Obtencion`.
- **`pathlib`**: Maneja rutas de carpetas y archivos de forma limpia y multiplataforma, asegurando la creación y escritura en `C:\Users\Erick Cordova\Desktop\scraping_eda_`.
- **`time`**: Introduce pausas controladas tras navegar a una URL, pulsar consentimiento o avanzar en el *scroll* para dar margen a la carga del DOM.
- **`unicodedata`**: Normaliza cadenas de texto (eliminando tildes, pasando a minúsculas y compactando espacios) para interpretar lo que escribe el usuario al elegir subcategoría.
- **`urllib.parse` y `urllib.robotparser`**: Descomponen la URL objetivo y evalúan las reglas del archivo `robots.txt` frente a la ruta solicitada.

### Instalación de dependencias
Ejecuta en la terminal de VS Code:
```bash
pip install selenium beautifulsoup4 pandas requests matplotlib seaborn
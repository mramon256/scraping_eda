import requests
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns

url_api = "https://es.openfoodfacts.org/"

respuesta_api = requests.get(url_api, timeout=15)
print(respuesta_api.headers.get("Content-Type"))

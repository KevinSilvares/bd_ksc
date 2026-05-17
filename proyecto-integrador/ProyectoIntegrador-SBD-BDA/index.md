# Proyecto Integrador: Predictor de demanda para redes eléctricas

## Comprensión del negocio

En este bloque se explora a grandes rasgos los objetivos, fuentes, preparaciones pertinentes y evaluaciones que se realizarán a lo largo del proyecto.

| Bloque | Fase | Descripción |
| --- | --- | --- |
| Objetivo del negocio | Negocio | Predecir la demanda energética para optimizar el uso de fuentes renovables. |
| Valor del proyecto | Negocio | - **Económico:** Optimización de costes de infraestructura, venta de posibles excedentes de energía y menor dependencia de combustibles fósiles. <br><br> - **Medio ambiente:** Reducción en la contaminación del medio ambiente mediante el uso de fuentes renovables. |
| Fuentes de datos | Datos | - **API Entso-E (En lugar de REE, que no daban API key):** API con datos de las redes eléctricas de Europa públicos. https://www.entsoe.eu/ <br><br> - **Historial Climático:** Archivo excel con el histórico del clima publicado por la AEMET desde el 2013 hasta la actualidad. https://datosclima.es/Aemet2013/DescargaDatos.html <br><br> - **Calendario Laboral y Festivos:** Librería `holidays` para detectar cuando una fecha es festiva o no en la región. Fichero csv con el calendario de festividades por regiones en su defecto. <br><br> - **Precio diario del Mercado:** A través de la API de Red Eléctrica para predecir con mayor exactitud los precios en función de la demanda y la disponibilidad de energía renovable. |
| Variable objetivo | Datos | **Numérica:** Predicción de consumo para un día determinado en MW. |
| Calidad y riesgos | Datos | - **Calidad:** Pueden existir valores no válidos en los datos obtenidos por la API o el historial climático. <br><br> **Riesgos:** La demanda energética puede depende del calendario (festivos, fines de semana, vacaciones, estaciones...). |
| Preparación y features | Preparación | - Limpieza de datos (filtrado de outliers y nulos, transformaciones, etc.). <br><br> - Creación de variables temporales: `es_festivo`. <br><br> - Inclusión de datos históricos de España desde el 2013 como predictores. <br><br> - Arquitectura de datos con AWS S3 para capas bronce, plata y oro, AWS Lambda y procesamiento local con Pandas. |
| Modelado | Modelado | Uso de algoritmos de regresión basados en series temporales. |
| Evaluación (KPIs) | Evaluación | - **Técnico:** - Obtener un MAPE (Mean Absolute Percentage Error) < 5% y reducir al máximo posible el RMSE (Root Mean Square Error). <br><br> - **Negocio:** Traducir la predicción obtenida en una optimización real; reducción de costes por venta de energía y mayor aprovechación de la cuota de la generación renovable. |
| Despliegue y uso | Despliege | Panel de control o dashboard interactivo para representar los valores de forma rápida y visual. |

## Comprensión de los datos

En este bloque se realizará una exploración rápida sobre los datos disponibles, identificaciones de posibles relaciones y/o modificaciones y transformaciones que puedan ser adecuadas más adelante. 

*Instalación, importaciones de librerías necesarias y definiciones base.*


```python
# Instalaciones
!pip install boto3
!pip install lxml
!pip install beautifulsoup4
!pip install rarfile
!pip install xlrd
!pip install entsoe-py
!pip install holidays
!pip install awswrangler
!pip install pyarrow
!pip install "numpy<2.0" --upgrade
```

    Requirement already satisfied: boto3 in /opt/conda/lib/python3.11/site-packages (1.42.97)
    Requirement already satisfied: botocore<1.43.0,>=1.42.97 in /opt/conda/lib/python3.11/site-packages (from boto3) (1.42.97)
    Requirement already satisfied: jmespath<2.0.0,>=0.7.1 in /opt/conda/lib/python3.11/site-packages (from boto3) (1.1.0)
    Requirement already satisfied: s3transfer<0.17.0,>=0.16.0 in /opt/conda/lib/python3.11/site-packages (from boto3) (0.16.1)
    Requirement already satisfied: python-dateutil<3.0.0,>=2.1 in /opt/conda/lib/python3.11/site-packages (from botocore<1.43.0,>=1.42.97->boto3) (2.9.0.post0)
    Requirement already satisfied: urllib3!=2.2.0,<3,>=1.25.4 in /opt/conda/lib/python3.11/site-packages (from botocore<1.43.0,>=1.42.97->boto3) (2.0.7)
    Requirement already satisfied: six>=1.5 in /opt/conda/lib/python3.11/site-packages (from python-dateutil<3.0.0,>=2.1->botocore<1.43.0,>=1.42.97->boto3) (1.16.0)
    Requirement already satisfied: lxml in /opt/conda/lib/python3.11/site-packages (6.1.0)
    Requirement already satisfied: beautifulsoup4 in /opt/conda/lib/python3.11/site-packages (4.12.2)
    Requirement already satisfied: soupsieve>1.2 in /opt/conda/lib/python3.11/site-packages (from beautifulsoup4) (2.5)
    Requirement already satisfied: rarfile in /opt/conda/lib/python3.11/site-packages (4.2)
    Requirement already satisfied: xlrd in /opt/conda/lib/python3.11/site-packages (2.0.1)
    Requirement already satisfied: entsoe-py in /opt/conda/lib/python3.11/site-packages (0.8.0)
    Requirement already satisfied: requests in /opt/conda/lib/python3.11/site-packages (from entsoe-py) (2.31.0)
    Requirement already satisfied: pytz in /opt/conda/lib/python3.11/site-packages (from entsoe-py) (2023.3.post1)
    Requirement already satisfied: beautifulsoup4>=4.11.1 in /opt/conda/lib/python3.11/site-packages (from entsoe-py) (4.12.2)
    Requirement already satisfied: pandas>=2.2.0 in /opt/conda/lib/python3.11/site-packages (from entsoe-py) (3.0.3)
    Requirement already satisfied: soupsieve>1.2 in /opt/conda/lib/python3.11/site-packages (from beautifulsoup4>=4.11.1->entsoe-py) (2.5)
    Requirement already satisfied: numpy>=1.26.0 in /opt/conda/lib/python3.11/site-packages (from pandas>=2.2.0->entsoe-py) (2.4.4)
    Requirement already satisfied: python-dateutil>=2.8.2 in /opt/conda/lib/python3.11/site-packages (from pandas>=2.2.0->entsoe-py) (2.9.0.post0)
    Requirement already satisfied: charset-normalizer<4,>=2 in /opt/conda/lib/python3.11/site-packages (from requests->entsoe-py) (3.3.0)
    Requirement already satisfied: idna<4,>=2.5 in /opt/conda/lib/python3.11/site-packages (from requests->entsoe-py) (3.4)
    Requirement already satisfied: urllib3<3,>=1.21.1 in /opt/conda/lib/python3.11/site-packages (from requests->entsoe-py) (2.0.7)
    Requirement already satisfied: certifi>=2017.4.17 in /opt/conda/lib/python3.11/site-packages (from requests->entsoe-py) (2026.4.22)
    Requirement already satisfied: six>=1.5 in /opt/conda/lib/python3.11/site-packages (from python-dateutil>=2.8.2->pandas>=2.2.0->entsoe-py) (1.16.0)
    Requirement already satisfied: holidays in /opt/conda/lib/python3.11/site-packages (0.96)
    Requirement already satisfied: python-dateutil<3,>=2.9.0.post0 in /opt/conda/lib/python3.11/site-packages (from holidays) (2.9.0.post0)
    Requirement already satisfied: six>=1.5 in /opt/conda/lib/python3.11/site-packages (from python-dateutil<3,>=2.9.0.post0->holidays) (1.16.0)
    Requirement already satisfied: awswrangler in /opt/conda/lib/python3.11/site-packages (3.16.1)
    Requirement already satisfied: boto3<2,>=1.20.32 in /opt/conda/lib/python3.11/site-packages (from awswrangler) (1.42.97)
    Requirement already satisfied: botocore<2,>=1.23.32 in /opt/conda/lib/python3.11/site-packages (from awswrangler) (1.42.97)
    Requirement already satisfied: numpy<3.0,>=1.26 in /opt/conda/lib/python3.11/site-packages (from awswrangler) (2.4.4)
    Requirement already satisfied: packaging<27.0,>=21.1 in /opt/conda/lib/python3.11/site-packages (from awswrangler) (23.2)
    Requirement already satisfied: pandas<4.0.0,>=1.2.0 in /opt/conda/lib/python3.11/site-packages (from awswrangler) (3.0.3)
    Requirement already satisfied: pyarrow<25.0.0,>=8.0.0 in /opt/conda/lib/python3.11/site-packages (from awswrangler) (24.0.0)
    Requirement already satisfied: typing-extensions<5,>=4.4.0 in /opt/conda/lib/python3.11/site-packages (from awswrangler) (4.8.0)
    Requirement already satisfied: jmespath<2.0.0,>=0.7.1 in /opt/conda/lib/python3.11/site-packages (from boto3<2,>=1.20.32->awswrangler) (1.1.0)
    Requirement already satisfied: s3transfer<0.17.0,>=0.16.0 in /opt/conda/lib/python3.11/site-packages (from boto3<2,>=1.20.32->awswrangler) (0.16.1)
    Requirement already satisfied: python-dateutil<3.0.0,>=2.1 in /opt/conda/lib/python3.11/site-packages (from botocore<2,>=1.23.32->awswrangler) (2.9.0.post0)
    Requirement already satisfied: urllib3!=2.2.0,<3,>=1.25.4 in /opt/conda/lib/python3.11/site-packages (from botocore<2,>=1.23.32->awswrangler) (2.0.7)
    Requirement already satisfied: six>=1.5 in /opt/conda/lib/python3.11/site-packages (from python-dateutil<3.0.0,>=2.1->botocore<2,>=1.23.32->awswrangler) (1.16.0)
    Requirement already satisfied: pyarrow in /opt/conda/lib/python3.11/site-packages (24.0.0)
    Collecting numpy<2.0
      Using cached numpy-1.26.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (61 kB)
    Using cached numpy-1.26.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (18.3 MB)
    Installing collected packages: numpy
      Attempting uninstall: numpy
        Found existing installation: numpy 2.4.4
        Uninstalling numpy-2.4.4:
          Successfully uninstalled numpy-2.4.4
    [31mERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
    numba 0.57.1 requires numpy<1.25,>=1.21, but you have numpy 1.26.4 which is incompatible.[0m[31m
    [0mSuccessfully installed numpy-1.26.4



```python
# Importaciones y definiciones base
import datetime
import boto3
import pandas as pd
import numpy as np
import requests
from urllib.parse import urljoin
import rarfile
import subprocess
import os
import shutil
import io
import holidays
import json
import math
import awswrangler as wr
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, RequestException

API_REE_URL = "https://apidatos.ree.es"
DATOS_CLIMA = "https://datosclima.es/Aemet2013/DescargaDatos.html"

BUCKET_BRONCE = "ksc-proyecto-integrador-bronce"
BUCKET_PLATA = "ksc-proyecto-integrador-plata"
BUCKET_ORO = "ksc-proyecto-integrador-oro"

DIR_TEMP = "./tempfiles"

rarfile.UNRAR_TOOl = "/opt/conda/bin/unrar"

def connect_s3():
    try:
        s3 = boto3.client("s3")
        print("Conexión establecida.")
    except Exception as e:
        print("Error de conexión.")
        print(e)

    return s3

def upload_raw_data_to_s3(s3, bucket, filename, data):
    print("Subiendo datos a S3 desde memoria")
    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    existe_bucket = bucket in buckets

    if not existe_bucket:
        s3.create_bucket(Bucket = bucket)

    # Para mantener el df en memoria sin escribirlo al disco
    csv_buffer = io.StringIO()
    data.to_csv(csv_buffer, index = False)

    # s3_key = filename.replace(".xls", ".csv")
    s3_key = filename.replace("-", "/")
    s3_key = os.path.splitext(s3_key)[0]
    s3_key = f"{s3_key}.csv"
    
    s3.put_object(
            Bucket = bucket,
            Key = s3_key,
            Body = csv_buffer.getvalue().encode("utf-8")
        )
    print(f"Datos subidos con éxito a s3://{bucket}/{s3_key}")

def upload_from_disk_to_s3(s3, bucket, path, data):
    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    existe_bucket = bucket in buckets

    if not existe_bucket:
        s3.create_bucket(Bucket = bucket)

    s3.upload_file(data, bucket, path)
    print(f"Datos subidos con éxito a s3://{bucket}/{path}")

def upload_parquet_to_s3(s3, bucket, path, df):
    target_path = f"s3://{bucket}/{path}.parquet"
    print(f"Subiendo archivo parquet a {bucket}")
    
    try:
        if not df.empty:
            wr.s3.to_parquet(
                df = df,
                path = target_path,
                index = False
            )
        print(f"Archivo .parquet subido correctamente a {target_path}")
    except Exception as e:
        print(f"ERRROR: {e}")
        raise e

def download_from_s3(s3, bucket, object_path):
    download_path = os.path.join("s3_downloads", object_path)

    try:
        print(f"Descargando desde s3: s3//{bucket}/{object_path}")
        s3.download_file(bucket, object_path, download_path)
        print(f"Archivo descargado y almacenado en: {download_path}")
    except Exception as e:
        print(f"ERROR: {e}")
```

Los datos con los que se van a trabajar provienen de: 
- [API de entso-e (Red de transparencia)](https://transparency.entsoe.eu/)
- [Datos Clima publicados por la AEMET desde el 2013](https://datosclima.es/Aemet2013/DescargaDatos.html)
- Calendario laboral y festivos ([librería holiday](https://pypi.org/project/holidays/))

### API ENTSO-E

La red de transpariencia ENTSO-E provee de datos eléctricos de toda Europa de consumo, demanda, generación... Esta sección se centra en la obtención de datos de generación con sus diferentes fuentes.


```python
from entsoe import EntsoePandasClient

ENTSOE_KEY = ""
SPAIN_CODE = "ES"

with open("entsoe-key.txt") as f:
    ENTSOE_KEY = f.read().strip()

if not ENTSOE_KEY:
    raise ValueError("No se ha encontrado la key de la API de ENTSOE. Crea un fichero .txt con la clave.")

def connect_entsoe():
    entsoe = EntsoePandasClient(ENTSOE_KEY)
    return entsoe

def get_entsoe_data(entsoe_client, year):
    print(f"Descargando los datos brutos de generación de energía de ENTSO-E del año {year}")

    start = pd.Timestamp(f"{year}-01-01", tz="Europe/Madrid")
    end = pd.Timestamp(f"{year}-12-31T23:59", tz="Europe/Madrid")

    try:
        df_raw_entsoe = entsoe_client.query_generation(SPAIN_CODE, start = start, end = end)

        # A veces devuelve un MultiIndex de pandas (el de las plantas). Con esto se aplana.
        if isinstance(df_raw_entsoe.columns, pd.MultiIndex):
            df_raw_entsoe = df_raw_entsoe.xs("Actual Aggregated", axis = 1, level = 1)

        # Se pone la fecha y hora como el índice. Limpia el índice y la pasa a una columna
        df_raw_entsoe = df_raw_entsoe.reset_index().rename(columns = {"index": "Datetime"})
        return df_raw_entsoe
    except Exception as e:
        print(f"ERROR: {e}")
```


```python
s3 = connect_s3()

# 2027 porque no lo incluye
for i in range(2020, 2027):
    raw_entsoe = get_entsoe_data(connect_entsoe(), i)
    upload_raw_data_to_s3(s3, BUCKET_BRONCE, f"entsoe/year={i}/raw_{i}", raw_entsoe)
```

    Conexión establecida.
    Descargando los datos brutos de generación de energía de ENTSO-E del año 2020
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/entsoe/year=2020/raw_2020.csv
    Descargando los datos brutos de generación de energía de ENTSO-E del año 2021
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/entsoe/year=2021/raw_2021.csv
    Descargando los datos brutos de generación de energía de ENTSO-E del año 2022
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/entsoe/year=2022/raw_2022.csv
    Descargando los datos brutos de generación de energía de ENTSO-E del año 2023
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/entsoe/year=2023/raw_2023.csv
    Descargando los datos brutos de generación de energía de ENTSO-E del año 2024
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/entsoe/year=2024/raw_2024.csv
    Descargando los datos brutos de generación de energía de ENTSO-E del año 2025
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/entsoe/year=2025/raw_2025.csv
    Descargando los datos brutos de generación de energía de ENTSO-E del año 2026
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/entsoe/year=2026/raw_2026.csv


El código anterior recopila datos de la API de entso-e y los sube a a la capa bronce en S3.

Los datos obtenidos por la API de entso-e vienen en inglés y son horarios. Existe una función lambda en AWS que se lanza cuando se sube un archivo con prefijo `entsoe/` para poder pasar los nombres de las columnas a español, unificar los datos para que sean diarios en lugar de horarios y pasarlo a parquet. Luego los guarda en la capa bronce en el formato `energia_consolidada/year=año/energia_año.parquet`.

Función Lambda:

```python
import json
import urllib.parse
import boto3
import pandas as pd
import awswrangler as wr
import io

TRANSLATION_ENTSOE = {
    "datetime": "fecha_hora",
    "Biomass": "biomasa_mwh",
    "Fossil Brown coal/Lignite": "carbon_marron_lignito_mwh",
    "Fossil Coal-derived gas": "gas_derivado_carbon_mwh",
    "Fossil Gas": "gas_natural_mwh",
    "Fossil Hard coal": "hulla_antracita_mwh",
    "Fossil Oil": "petroleo_mwh",
    "Fossil Oil shale": "esquisto_bituminoso_mwh",
    "Fossil Peat": "turba_mwh",
    "Geothermal": "geotermica_mwh",
    "Hydro Run-of-river and poundage": "hidraulica_fluyente_mwh",
    "Hydro Water Reservoir": "hidraulica_embalse_mwh",
    "Marine": "maritima_mwh",
    "Nuclear": "nuclear_mwh",
    "Other": "otras_tecnologias_mwh",
    "Other renewable": "otras_renovables_mwh",
    "Solar": "solar_fotovoltaica_mwh",
    "Waste": "residuos_mwh",
    "Wind Offshore": "eolica_marina_mwh",
    "Wind Onshore": "eolica_terrestre_mwh"
}

BUCKET_PLATA = "ksc-proyecto-integrador-plata"

def lambda_handler(event, context):
    bucket_bronce = event["Records"][0]["s3"]["bucket"]["name"]
    key_bronce = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding = "utf-8")

    # entsoe/year=2020/raw_data_2020.csv
    year = key_bronce.split("=")[1].split("/")[0]

    try:
        df_raw = wr.s3.read_csv(path = f"s3://{bucket_bronce}/{key_bronce}")

        df_raw["Datetime"] = pd.to_datetime(df_raw["Datetime"], utc = True)
        df_raw = df_raw.set_index("Datetime")

        cols = [c for c in TRANSLATION_ENTSOE.keys() if c in df_raw.columns]
        df_final = df_raw[cols].rename(columns = TRANSLATION_ENTSOE)

        # Convierte los registros horarios a diarios
        df_daily = df_final.resample("D").sum().reset_index()
        df_daily["fecha"] = df_daily["Datetime"].dt.date
        df_daily.drop(columns = ["Datetime"], inplace = True)

        path = f"s3://{BUCKET_PLATA}/energia_consolidada/year={year}/energia_{year}.parquet"

        wr.s3.to_parquet(
            df = df_daily, 
            path = path, 
            index = False
        )

    except Exception as e:
        print(f"ERROR: {e}")


```

### Datos del clima publicados por la AEMET

Fuente: https://datosclima.es/Aemet2013/DescargaDatos.html

En esta página se encuentran datos publicados por la AEMET desde mayo del 2013 y recogidos de forma libre. Los diferentes enlaces de descarga se encuentran en formato de tabla, divididas por año y mes.

Como descargar uno a uno estos archivos serían un proceso lento y tedioso, se procede a realizar un trabajo de *web scraping* (raspado de web) para las descarga y almacenamiento en AWS S3 de los datos.


```python
def unpack_rar(url, filename, dir = DIR_TEMP):
    filename = filename.split("/")[-1] # Si añade la barra rompe la ruta

    # Comprueba que el directorio existe para borrarlo recursivamente y crearlo otra vez
    if os.path.exists(dir):
        shutil.rmtree(dir)    
    os.makedirs(dir)

    rar_path = os.path.join(dir, filename)

    try:
        print(f"Descargando: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://datosclima.es/Aemet2013/DescargaDatos.html'
        }
        
        response = requests.get(url, stream = True, timeout = (3, 10), headers = headers)
        response.raise_for_status()

        with open(rar_path, "wb") as file:
            for chunk in response.iter_content(chunk_size = 8192):
                file.write(chunk)

        file_kb = os.path.getsize(rar_path)
        if file_kb < 1000:
            print("ERROR: El servidor no ha enviado un .rar")
            with open(rar_path, "r", encoding = "utf-8", errors = "ignore") as f:
                print(f.read())
            return

        print("Descomprimiendo...")
        final_path = os.path.join(dir, "")
        command = ["unrar", "x", "-y", rar_path, final_path]

        process = subprocess.run(command, capture_output = True, text = True)
        print(f"Número de elementos descomprimidos: {len(os.listdir(dir)) - 1}") # -1 porque guarda el .rar también
        return True
    except Timeout:
        print("ERROR: El servidor tardó demasiado en responder.")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    # quiza deberia meter un finally para eliminar la carpeta de tempfiles al acabar

def convert_files_to_df():
    dfs = []
    
    print("Convirtiendo de excel a DataFrame de pandas")
    tempfiles_path = "tempfiles"
    
    if os.path.exists(tempfiles_path):
        for file in os.listdir(tempfiles_path):
            if file.endswith(".xls"):
                path = os.path.join(tempfiles_path, file)
                try:
                    df = pd.read_excel(path, engine = "xlrd", skiprows = 4)
                    
                    df["archivo_origen"] = file # por si lo necesito más adelante
                    dfs.append((file, df))
                except Exception:
                    # Algún fichero daba error de corrupción o formato
                    continue
    return dfs

# def convert_to_parquet(dfs):
#     print("Convirtiendo de DataFrame de pandas a parquet")
#     path = "parquet"
#     for df in dfs:
#         full_path = os.path.join(path, df.name)
#         df.to_parquet(full_path)

def get_aemet2013_data():
    s3 = connect_s3()
    
    try:
        response = requests.get(DATOS_CLIMA, timeout = (3, 10))
        response.raise_for_status()
        response.encoding = "utf-8"
        
        soup = BeautifulSoup(response.text, "html.parser")
    
        # Captura todos los enlaces en la página
        links = soup.find_all("a")
    
        for link in links:
            path = link.get("href")
    
            if "../capturadatos/" in path:
                full_url = urljoin("https://datosclima.es", path)
                if unpack_rar(full_url, path):
                    dfs = convert_files_to_df()

                    for filename, df in dfs:
                        upload_raw_data_to_s3(s3, BUCKET_BRONCE, filename, df)
    except Timeout:
        print("ERROR: El servidor tardó demasiado en responder.")
    except RequestException as e:
        print(f"ERROR: {e}")
```


```python
get_aemet2013_data()
```

*Limpio la salida de la anterior celda porque ocupa demasiado.*

Para utilizar la librería `rarfile` hace falta tener WinRar o `unrar` instalados en la máquina para poder descomprimir. Como este notebook se asienta en un contenedor de docker con la imagen `jupyter/datascience-notebook` ha sido necesario instalarlo desde `conda` en lugar de hacer el usual `apt-get` que se haría en cualquier caso por falta de permisos. Comando: 

`conda install -c conda-forge unrar -y`

#### Estructura de datos

Los datos se estructuran en unas tablas en la propia web:

![image.png](22a3eeed-f67a-4620-bf94-b8fc6c882920.png)

Cada tabla es un año con sus meses. Cada mes es un enlace a un `.rar` que contiene datos de cada día del mes. Así pues, se entiende que al descargar un fichero se descomprime en 30-31 xls.

Se almacenan en AWS S3 por año/mes/(resto de días del mes)

![image.png](9accc7d8-e754-4a4a-afda-a5f06d947dac.png)

## Librería Holidays

Esta librería permite obtener los días festivos de diferentes zonas del mundo, incluidas las Comunidades Autónomas de España.

Este proceso se llevará a cabo con una función lambda, que se disparará al subir los datos de la AEMET. Su función será añadir en el csv si el día era festivo o no y guardará el objeto en la capa plata.

Además, como las funciones lambda de AWS se cobran por invocación y tiempo de ejecución, se filtrarán los datos para que sólo se aplique a los datos desde 2020 hasta 2026.

![image.png](c90d2d03-2340-4635-bc22-3dc258545c4f.png)
Se crea una notificación por año (Aemet2020, Aemet2021...)
![image.png](f294ce87-2e10-4b23-bcbf-6568dd78edd3.png)

Función Lambda:

```python
import json
import urllib.parse
import boto3
import pandas as pd
import holidays
from datetime import datetime
import io

s3_client = boto3.client('s3') # lo creo fuera del handler para poder reutilizar la conexión

PROVINCIAS_CCAA = {
    # Andalucía (AN)
    'ALMERÍA': 'AN', 'CÁDIZ': 'AN', 'CÓRDOBA': 'AN', 'GRANADA': 'AN', 
    'HUELVA': 'AN', 'JAÉN': 'AN', 'MÁLAGA': 'AN', 'SEVILLA': 'AN',
    # Aragón (AR)
    'HUESCA': 'AR', 'TERUEL': 'AR', 'ZARAGOZA': 'AR',
    # Principado de Asturias (AS)
    'ASTURIAS': 'AS',
    # Canarias (CN)
    'LAS PALMAS': 'CN', 'SANTA CRUZ DE TENERIFE': 'CN',
    # Cantabria (CB)
    'CANTABRIA': 'CB',
    # Castilla y León (CL)
    'ÁVILA': 'CL', 'BURGOS': 'CL', 'LEÓN': 'CL', 'PALENCIA': 'CL', 
    'SALAMANCA': 'CL', 'SEGOVIA': 'CL', 'SORIA': 'CL', 'VALLADOLID': 'CL', 'ZAMORA': 'CL',
    # Castilla-La Mancha (CM)
    'ALBACETE': 'CM', 'CIUDAD REAL': 'CM', 'CUENCA': 'CM', 'GUADALAJARA': 'CM', 'TOLEDO': 'CM',
    # Cataluña (CT)
    'BARCELONA': 'CT', 'GIRONA': 'CT', 'GERONA': 'CT', 'LLEIDA': 'CT', 'LÉRIDA': 'CT', 'TARRAGONA': 'CT',
    # Extremadura (EX)
    'BADAJOZ': 'EX', 'CÁCERES': 'EX',
    # Galicia (GA)
    'A CORUÑA': 'GA', 'LA CORUÑA': 'GA', 'LUGO': 'GA', 'OURENSE': 'GA', 'ORENSE': 'GA', 'PONTEVEDRA': 'GA',
    # Illes Balears (IB)
    'BALEARES': 'IB', 'ILLES BALEARS': 'IB', 'ISLAS BALEARES': 'IB',
    # La Rioja (RI)
    'LA RIOJA': 'RI',
    # Comunidad de Madrid (MD)
    'MADRID': 'MD',
    # Región de Murcia (MC)
    'MURCIA': 'MC',
    # Comunidad Foral de Navarra (NC)
    'NAVARRA': 'NC',
    # País Vasco (PV)
    'ÁLAVA': 'PV', 'ARABA': 'PV', 'GUIPÚZCOA': 'PV', 'GIPUZKOA': 'PV', 'VIZCAYA': 'PV', 'BIZKAIA': 'PV',
    # Comunidad Valenciana (VC)
    'ALICANTE': 'VC', 'ALACANT': 'VC', 'CASTELLÓN': 'VC', 'CASTELLÓ': 'VC', 'VALENCIA': 'VC', 'VALÈNCIA': 'VC',
    # Ciudades Autónomas
    'CEUTA': 'CE',
    'MELILLA': 'ML'
}

BUCKET_DESTINO = "ksc-proyecto-integrador-meteo-y-vacaciones"

def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")

    print(f"Procesando: {key} de {bucket}")

    try:
        response = s3_client.get_object(Bucket = bucket, Key = key)
        path_splitted = key.split("/")

        year = int(path_splitted[0].replace("Aemet", ""))
        month = int(path_splitted[1])
        day = int(path_splitted[2].replace(".csv", ""))

        if year < 2020:
            print("ERROR: El fichero era anterior a 2020.")
            return
        
        df = pd.read_csv(io.BytesIO(response["Body"].read()))

        # Si no pongo la fecha en formato de pandas da errores
        current_date = pd.to_datetime(f"{year}-{month}-{day}")
        df["fecha"] = current_date

        # Separa la provincia en 2 partes (Alacant/Alicante) para quedarse con la última
        df["Provincia_Limpia"] = df["Provincia"].str.split('/').str[-1]
        df["ccaa_codigo"] = df["Provincia_Limpia"].str.strip().str.upper().map(PROVINCIAS_CCAA)
        
        df["es_festivo"] = 0

        # Es posible que deje algunas sin mapear sin darme cuenta, así que me dejo de problemas con esto
        ccaa_dataset = df["ccaa_codigo"].dropna().unique()

        for ccaa in ccaa_dataset:
            # Obtiene festivos para la comunidad autónoma específica
            country_holidays = holidays.ES(subdiv = ccaa, years = year)

            if current_date in country_holidays:
                df.loc[df['ccaa_codigo'] == ccaa, 'es_festivo'] = 1
        
        s3_client.put_object(
            Bucket = BUCKET_DESTINO,
            Key = f"{key}",
            Body = df.to_csv(index = False),
            ContentType = "text/csv"
        )
        print(f"Fichero procesado y almacenado en: {BUCKET_DESTINO}/{key}")
    except Exception as e:
        print(e)
        raise e

```

Esta función requirió de la creación de capas (Pandas y Holidays) y de asignación de memoria extra.

## Compactación de datos

Como se ha indicado, los datos almacenados en la capa bronce están divididos en ficheros `.csv` por día. Su estructura es como la siguiente:

- Aemet2020/
    - 01/
        - 01.csv
        - 02.csv
        - 03.csv
        - resto de días
    - 02/
        - 01.csv
        - 02.csv
        - 03.csv
        - resto de días
    - resto de meses
- Resto de años

Esta estructura es un problema para su posterior procesamiento, por lo que se van a compactar los datos por años. Para ello se lanzará una función manual.

*La idea inicial era lanzar una regla promada Cron desde EventBridge para que se ejecutase automáticamente cada mes o cada año, dependiendo de las necesidades. Pero para evitar esperas se creará una función Lambda que se invocará manualmente desde este código. El código de la función Lambda puede ser configurado perfectamente para una regla definida en EventBridge.*

Código de la función Lambda:

```python
import json
import pandas as pd
import awswrangler as wr

BUCKET_METEO_VACACIONES = "ksc-proyecto-integrador-meteo-y-vacaciones"
BUCKET_PLATA = "ksc-proyecto-integrador-plata"

def lambda_handler(event, context):
    year = event.get("year", "")

    if not year:
        raise ValueError("No se ha especificado el año.")

    print(f"Iniciando compactación para el año: {year}")

    try:
        target_path = f"s3://{BUCKET_METEO_VACACIONES}/Aemet{year}/"
        df_anual = wr.s3.read_csv(path = target_path)

        # Formato Hive/Spark
        target_path = f"s3://{BUCKET_PLATA}/aemet_consolidada/year={year}/aemet_historico_{year}.parquet"

        if not df_anual.empty:
            wr.s3.to_parquet(
            df = df_anual,
            path = target_path,
            index = False
        )
        
    except Exception as e:
        print(ROR: {e}")
        raise e




```


```python
client = boto3.client("lambda", region_name = "us-east-1")

try:
    for year in range(2020, 2027):
        year_message = {
            "year": year
        }

        client.invoke(
            FunctionName = "compact-data",
            InvocationType = "RequestResponse",
            Payload = json.dumps(year_message).encode("utf-8")
        )
except Exception as e:
    print(f"ERROR: {e}")
```

## Unificación y compactación completa de datos

Una vez que tenemos los datos de días con la meteorología y los datos de generación necesitamos compactarlos en un mismo dataset para poder operar de manera eficiente con ello. Aunque las transformaciones en los datos de generación las he considerado como de capa plata, esta unificación de todos los datos también la consideraré como tal, pues aún no se han realizado procesos de limpieza de datos como tal, simplemente se ha realizado un enriquecimiento.

Como los datos que he enriquecido son los de los años 2020 en adelante, estos serán los que utilice en este punto.


```python
BUCKET_PLATA = "ksc-proyecto-integrador-plata"

dfs_energy = []
dfs_meteo_holidays = []

for year in range(2020, 2027):
    energy_object_path = f"s3://{BUCKET_PLATA}/energia_consolidada/year={year}"
    dfs_energy.append(wr.s3.read_parquet(path = energy_object_path))

    meteo_holidays_object_path = f"s3://{BUCKET_PLATA}/aemet_consolidada/year={year}"
    dfs_meteo_holidays.append(wr.s3.read_parquet(path = meteo_holidays_object_path))

df_energy_full = pd.concat(dfs_energy)
df_aemet_full = pd.concat(dfs_meteo_holidays)

df_energy_full["fecha"] = pd.to_datetime(df_energy_full["fecha"], utc = True).dt.tz_localize(None).dt.normalize()
df_aemet_full["fecha"] = pd.to_datetime(df_aemet_full["fecha"], utc = True).dt.tz_localize(None).dt.normalize()
```


```python
df_full = pd.merge(df_aemet_full, df_energy_full, on = "fecha", how = "inner")
df_full.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Estación</th>
      <th>Provincia</th>
      <th>Temperatura_máxima__ºC_</th>
      <th>Temperatura_mínima__ºC_</th>
      <th>Temperatura_media__ºC_</th>
      <th>Racha__km/h_</th>
      <th>Velocidad_máxima__km/h_</th>
      <th>Precipitación_00-24h__mm_</th>
      <th>Precipitación_00-06h__mm_</th>
      <th>Precipitación_06-12h__mm_</th>
      <th>...</th>
      <th>hidraulica_fluyente_mwh</th>
      <th>hidraulica_embalse_mwh</th>
      <th>maritima_mwh</th>
      <th>nuclear_mwh</th>
      <th>otras_tecnologias_mwh</th>
      <th>otras_renovables_mwh</th>
      <th>solar_fotovoltaica_mwh</th>
      <th>residuos_mwh</th>
      <th>eolica_marina_mwh</th>
      <th>eolica_terrestre_mwh</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Estaca de Bares</td>
      <td>A Coruña</td>
      <td>20.3 (13:50)</td>
      <td>14.9 (01:20)</td>
      <td>17.6</td>
      <td>46 (03:10)</td>
      <td>40 (03:10)</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>0.0</td>
      <td>95104.0</td>
      <td>1239.0</td>
      <td>2465.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>0.0</td>
      <td>46137.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Ferrol</td>
      <td>A Coruña</td>
      <td>24.4 (14:40)</td>
      <td>15.6 (04:10)</td>
      <td>20.0</td>
      <td>32 (17:00)</td>
      <td>23 (16:20)</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>0.0</td>
      <td>95104.0</td>
      <td>1239.0</td>
      <td>2465.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>0.0</td>
      <td>46137.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>As Pontes</td>
      <td>A Coruña</td>
      <td>29.1 (15:30)</td>
      <td>13.8 (07:20)</td>
      <td>21.5</td>
      <td>&lt;NA&gt;</td>
      <td>&lt;NA&gt;</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>0.0</td>
      <td>95104.0</td>
      <td>1239.0</td>
      <td>2465.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>0.0</td>
      <td>46137.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>A Coruña</td>
      <td>A Coruña</td>
      <td>22.8 (12:50)</td>
      <td>15.8 (04:10)</td>
      <td>19.3</td>
      <td>39 (02:00)</td>
      <td>22 (02:00)</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>0.0</td>
      <td>95104.0</td>
      <td>1239.0</td>
      <td>2465.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>0.0</td>
      <td>46137.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A Coruña Aeropuerto</td>
      <td>A Coruña</td>
      <td>22.1 (12:30)</td>
      <td>15.2 (06:40)</td>
      <td>18.7</td>
      <td>37 (02:20)</td>
      <td>25 (16:50)</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>0.0</td>
      <td>95104.0</td>
      <td>1239.0</td>
      <td>2465.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>0.0</td>
      <td>46137.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 36 columns</p>
</div>




```python
# Una vez unidos por la clave podemos volver a tener la fecha como tipo Date
df_full["fecha"] = pd.to_datetime(df_full["fecha"]).dt.date
df_full_copy = df_full.copy()
```

### Limpieza de datos

Como podemos ver tanto el `head()`de arriba como en el `describe()` de abajo, existen varias columnas que deben de ser tratadas para poder disponer de datos de calidad real.


```python
df_full.describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Temperatura_media__ºC_</th>
      <th>Precipitación_00-24h__mm_</th>
      <th>Precipitación_00-06h__mm_</th>
      <th>Precipitación_06-12h__mm_</th>
      <th>Precipitación_12-18h__mm_</th>
      <th>Precipitación_18-24h__mm_</th>
      <th>fecha</th>
      <th>es_festivo</th>
      <th>biomasa_mwh</th>
      <th>carbon_marron_lignito_mwh</th>
      <th>...</th>
      <th>hidraulica_fluyente_mwh</th>
      <th>hidraulica_embalse_mwh</th>
      <th>maritima_mwh</th>
      <th>nuclear_mwh</th>
      <th>otras_tecnologias_mwh</th>
      <th>otras_renovables_mwh</th>
      <th>solar_fotovoltaica_mwh</th>
      <th>residuos_mwh</th>
      <th>eolica_marina_mwh</th>
      <th>eolica_terrestre_mwh</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>497686.000000</td>
      <td>486948.000000</td>
      <td>492093.000000</td>
      <td>490623.000000</td>
      <td>491575.000000</td>
      <td>492751.000000</td>
      <td>524881</td>
      <td>524881.0</td>
      <td>524881.000000</td>
      <td>524881.0</td>
      <td>...</td>
      <td>524881.000000</td>
      <td>524881.000000</td>
      <td>524881.0</td>
      <td>524881.00000</td>
      <td>524881.000000</td>
      <td>524881.000000</td>
      <td>524881.000000</td>
      <td>524881.000000</td>
      <td>524881.0</td>
      <td>5.248810e+05</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>9.767342</td>
      <td>3.368206</td>
      <td>0.776317</td>
      <td>0.892675</td>
      <td>0.903023</td>
      <td>0.798447</td>
      <td>2026-02-13 22:23:59.846365</td>
      <td>0.026566</td>
      <td>36082.161023</td>
      <td>0.0</td>
      <td>...</td>
      <td>120027.486017</td>
      <td>357751.073017</td>
      <td>0.0</td>
      <td>579690.60123</td>
      <td>470.337010</td>
      <td>6118.421722</td>
      <td>414250.807303</td>
      <td>14355.257965</td>
      <td>0.0</td>
      <td>8.184246e+05</td>
    </tr>
    <tr>
      <th>min</th>
      <td>-14.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>2025-12-31 00:00:00</td>
      <td>0.0</td>
      <td>1612.000000</td>
      <td>0.0</td>
      <td>...</td>
      <td>4272.000000</td>
      <td>9400.000000</td>
      <td>0.0</td>
      <td>28464.00000</td>
      <td>0.000000</td>
      <td>272.000000</td>
      <td>144.000000</td>
      <td>848.000000</td>
      <td>0.0</td>
      <td>8.520000e+03</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>6.900000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>2026-01-22 00:00:00</td>
      <td>0.0</td>
      <td>31704.000000</td>
      <td>0.0</td>
      <td>...</td>
      <td>105724.000000</td>
      <td>268708.000000</td>
      <td>0.0</td>
      <td>538156.00000</td>
      <td>356.000000</td>
      <td>5796.000000</td>
      <td>254412.000000</td>
      <td>11904.000000</td>
      <td>0.0</td>
      <td>4.502160e+05</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>10.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>2026-02-14 00:00:00</td>
      <td>0.0</td>
      <td>38344.000000</td>
      <td>0.0</td>
      <td>...</td>
      <td>126784.000000</td>
      <td>362352.000000</td>
      <td>0.0</td>
      <td>587716.00000</td>
      <td>500.000000</td>
      <td>6136.000000</td>
      <td>402752.000000</td>
      <td>14768.000000</td>
      <td>0.0</td>
      <td>8.582400e+05</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>12.900000</td>
      <td>2.600000</td>
      <td>0.000000</td>
      <td>0.100000</td>
      <td>0.200000</td>
      <td>0.200000</td>
      <td>2026-03-09 00:00:00</td>
      <td>0.0</td>
      <td>41004.000000</td>
      <td>0.0</td>
      <td>...</td>
      <td>138688.000000</td>
      <td>473140.000000</td>
      <td>0.0</td>
      <td>682016.00000</td>
      <td>664.000000</td>
      <td>6616.000000</td>
      <td>570328.000000</td>
      <td>16700.000000</td>
      <td>0.0</td>
      <td>1.117800e+06</td>
    </tr>
    <tr>
      <th>max</th>
      <td>26.500000</td>
      <td>581.500000</td>
      <td>151.700000</td>
      <td>133.300000</td>
      <td>151.100000</td>
      <td>145.400000</td>
      <td>2026-03-31 00:00:00</td>
      <td>1.0</td>
      <td>46760.000000</td>
      <td>0.0</td>
      <td>...</td>
      <td>156428.000000</td>
      <td>577304.000000</td>
      <td>0.0</td>
      <td>683416.00000</td>
      <td>972.000000</td>
      <td>7176.000000</td>
      <td>847064.000000</td>
      <td>20348.000000</td>
      <td>0.0</td>
      <td>1.716292e+06</td>
    </tr>
    <tr>
      <th>std</th>
      <td>4.602619</td>
      <td>8.915143</td>
      <td>2.949548</td>
      <td>3.249500</td>
      <td>2.943985</td>
      <td>2.775037</td>
      <td>NaN</td>
      <td>0.160811</td>
      <td>7773.234896</td>
      <td>0.0</td>
      <td>...</td>
      <td>25132.580695</td>
      <td>127566.146233</td>
      <td>0.0</td>
      <td>102974.47590</td>
      <td>274.012818</td>
      <td>791.285618</td>
      <td>199913.644440</td>
      <td>3208.506305</td>
      <td>0.0</td>
      <td>4.088148e+05</td>
    </tr>
  </tbody>
</table>
<p>8 rows × 27 columns</p>
</div>



En los datos de arriba podemos ver varios problemas:
- Existen valores extremos en las precipitaciones (media de `3.368` y valor máximo de `581.5`, por ejemplo) y la información que representa cada columna es redundante (hay una columna para las precipitaciones acumuladas durante 24 horas, pero tenemos 4 divisiones cada 4 horas).
- Existen columnas de generación de energía que no contienen datos. Aunque esto no es un error porque España no utiliza estas fuentes para generar energía, pueden generar problemas en el modelo, además de ocupar un tamaño en memoria significativo sin aportar nada a cambio.
- Existen errores de formato en algunas columnas:
    - Temperatura Máxima y Temperatura Mínima con el formato: 10.5 (15:00) -> refiriéndose a la medida y a la hora
    - Rachas de viento por hora y rachas máximas con el formato: 50 (1:00) -> Similar al anterior punto.

La siguiente matriz de correlación muestra también esta falta de valores en aquellas columnas en las que España no tiene ningún tipo de generación. Estas columnas serán eliminadas por considerarse redundantes e inútiles.


```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(15, 10))
sns.heatmap(df_full.corr(numeric_only = True))
plt.show()
```


    
![png](output_23_0.png)
    


#### Eliminación de valores redundantes o poco útiles

En esta sección se eliminarán todas aquellas columnas que no aportan información extra, presentan multicolinealidad o están vacías.


```python
print(f"Registros, dimensiones pre-limpieza: {df_full_copy.shape}")
```

    Registros, dimensiones pre-limpieza: (1690840, 36)



```python
def clean_value_hour_format(value):
    if isinstance(value, str):
        value, _ = splitted_value = value.split(" ")
    return float(value)
```


```python
# Conversiones de datos

# Los datos de viento nulos pasan a ser 0
df_full_copy["Racha__km/h_"] = df_full_copy["Racha__km/h_"].fillna(0)
df_full_copy["Velocidad_máxima__km/h_"] = df_full_copy["Velocidad_máxima__km/h_"].fillna(0)

# Conversión del formato de 10.5 (10:30)
df_full_copy["Racha__km/h_"] = df_full_copy["Racha__km/h_"].apply(clean_value_hour_format)
df_full_copy["Velocidad_máxima__km/h_"] = df_full_copy["Velocidad_máxima__km/h_"].apply(clean_value_hour_format)

# Media viento
df_full_copy["Viento_media_km/h"] = df_full_copy[["Racha__km/h_", "Velocidad_máxima__km/h_"]].mean(axis = 1)
```


```python
# Columnas sin datos
columnas_eliminar = ["carbon_marron_lignito_mwh", "gas_derivado_carbon_mwh", "esquisto_bituminoso_mwh", "geotermica_mwh", "turba_mwh", "maritima_mwh", "eolica_marina_mwh"]

# Columnas precipitaciones por horas
columnas_eliminar.extend(["Precipitación_00-06h__mm_", "Precipitación_06-12h__mm_", "Precipitación_12-18h__mm_",	"Precipitación_18-24h__mm_"])

# Columnas de temperatura media y temperatura minima
columnas_eliminar.extend(["Temperatura_máxima__ºC_", "Temperatura_mínima__ºC_"])

# Columnas de viento
columnas_eliminar.extend(["Racha__km/h_", "Velocidad_máxima__km/h_"])

df_full_copy.drop(columns = columnas_eliminar, inplace = True)
```


```python
print(f"Registros, dimensiones post-limpieza: {df_full_copy.shape}")
```

    Registros, dimensiones post-limpieza: (1690840, 22)



```python
plt.figure(figsize=(15, 10))
sns.heatmap(df_full_copy.corr(numeric_only = True))
plt.show()
```


    
![png](output_30_0.png)
    


Como vemos, la matriz de correlación se ve muchísimo más limpia ahora, sin columnas faltantes y ya se pueden empezar a ver comportamientos en ella (la generación solar fotovoltaica sube un poco cuando hay más temperatura -más horas de sol generalmente- o las hidraúlicas bajan cuando hay la temperatura media se eleva también -como antes, más sol, menos lluvias-...)

Sin embargo nos quedan unos cuantos valores extremos limpiar o adaptar para que un modelo pueda funcionar con estos datos.


```python
# Al hacer la limpieza los valores se muestran en notación científica, así que los ponemos en formato de dos decimales sólo para este describe
df_full_copy.describe().apply(lambda s: s.apply(lambda x: f'{x:.2f}'))
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Temperatura_media__ºC_</th>
      <th>Precipitación_00-24h__mm_</th>
      <th>es_festivo</th>
      <th>biomasa_mwh</th>
      <th>gas_natural_mwh</th>
      <th>hulla_antracita_mwh</th>
      <th>petroleo_mwh</th>
      <th>hidraulica_fluyente_mwh</th>
      <th>hidraulica_embalse_mwh</th>
      <th>nuclear_mwh</th>
      <th>otras_tecnologias_mwh</th>
      <th>otras_renovables_mwh</th>
      <th>solar_fotovoltaica_mwh</th>
      <th>residuos_mwh</th>
      <th>eolica_terrestre_mwh</th>
      <th>Viento_media_km/h</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>1618374.00</td>
      <td>1603006.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
      <td>1690840.00</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>15.81</td>
      <td>1.82</td>
      <td>0.03</td>
      <td>29016.48</td>
      <td>455291.88</td>
      <td>28737.48</td>
      <td>4288.52</td>
      <td>65179.69</td>
      <td>168476.91</td>
      <td>433547.01</td>
      <td>1374.02</td>
      <td>5638.11</td>
      <td>340027.48</td>
      <td>15656.45</td>
      <td>476605.19</td>
      <td>22.61</td>
    </tr>
    <tr>
      <th>std</th>
      <td>7.23</td>
      <td>6.36</td>
      <td>0.18</td>
      <td>13900.80</td>
      <td>305318.18</td>
      <td>27894.57</td>
      <td>2763.96</td>
      <td>40460.34</td>
      <td>127520.83</td>
      <td>221250.56</td>
      <td>1291.16</td>
      <td>2476.07</td>
      <td>267727.39</td>
      <td>7437.72</td>
      <td>364890.34</td>
      <td>15.09</td>
    </tr>
    <tr>
      <th>min</th>
      <td>-16.10</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>492.00</td>
      <td>3478.00</td>
      <td>0.00</td>
      <td>32.00</td>
      <td>1070.00</td>
      <td>1333.00</td>
      <td>680.00</td>
      <td>0.00</td>
      <td>96.00</td>
      <td>10.00</td>
      <td>218.00</td>
      <td>6342.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>10.40</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>12334.00</td>
      <td>212245.00</td>
      <td>10590.00</td>
      <td>2576.00</td>
      <td>27026.00</td>
      <td>65763.00</td>
      <td>167392.00</td>
      <td>664.00</td>
      <td>2530.00</td>
      <td>87101.00</td>
      <td>7193.00</td>
      <td>183180.00</td>
      <td>14.50</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>15.70</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>35028.00</td>
      <td>392676.00</td>
      <td>23808.00</td>
      <td>3707.00</td>
      <td>56992.00</td>
      <td>126392.00</td>
      <td>489232.00</td>
      <td>1040.00</td>
      <td>6580.00</td>
      <td>295336.00</td>
      <td>17332.00</td>
      <td>379144.00</td>
      <td>22.50</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>21.30</td>
      <td>0.20</td>
      <td>0.00</td>
      <td>40736.00</td>
      <td>621192.00</td>
      <td>33396.00</td>
      <td>5083.00</td>
      <td>100596.00</td>
      <td>243680.00</td>
      <td>658772.00</td>
      <td>1411.00</td>
      <td>7604.00</td>
      <td>549912.00</td>
      <td>21820.00</td>
      <td>687488.00</td>
      <td>31.00</td>
    </tr>
    <tr>
      <th>max</th>
      <td>40.20</td>
      <td>758.00</td>
      <td>1.00</td>
      <td>54132.00</td>
      <td>1630056.00</td>
      <td>171352.00</td>
      <td>19288.00</td>
      <td>159380.00</td>
      <td>577304.00</td>
      <td>685048.00</td>
      <td>5704.00</td>
      <td>10944.00</td>
      <td>1047012.00</td>
      <td>30380.00</td>
      <td>1746940.00</td>
      <td>199.50</td>
    </tr>
  </tbody>
</table>
</div>



En las características estadísticas podemos detectar varios valores extraños:

- **Precipitaciones**: El valor medio es de `1.82` mm, pero el valor máximo es de `758` mm. Es muy posible que esto se pueda deber o bien a un error tipográfico o a un evento extraño y muy poco frecuente (como la de la DANA de Valencia de 2024). En cualquier caso, al ser un dato tan extraordinario, podría confundir a un modelo al no ser la norma general.
- **Viento medio**: El valor medio es de `22.6` km/h, pero el valor máximo es de `199.50` km/h. De nuevo, probablemente se pueda deber a un caso aislado y por lo tanto puede evitar una buena generalización del modelo.
- **Solar fotovoltaica**: El mínimo de la generación solar fotovoltaica es de `10` MWh. Esto es muy poco para un país como España. Podemos suponer que se debe a un fallo en la lectura o la carga de datos en la API de entso-e.
- **Hulla/antracita y otras tecnologías**: Presentan mínimos de `0.0` MWh. En el caso de la hulla/antracita, la desviación estándar de `27894.57` (casi lo mismo que la media), lo que indica un cambio demasiado drástico en los datos. Es posible que esto sea cierto; el sistema de electricidad español ha ido dejando los combustibles fósiles por más energía renovable y esto podría explicarlo, pero no dejan de ser valores extremos que podrían confundir a un modelo.

A estas conclusiones hay que hacerles el apunte del apagón de 2025. Aunque haya sido un día, hay generaciones energéticas que no pueden parar de golpe y deben autoprotegerse (como la nuclear) que pueden tardar días en volver a funcionar con normalidad, los datos podrían no haber transmitido bien ese día, etc. Para este trabajo sería hilar muy fino, pero en una exloración más seria sería conveniente tenerlo en cuenta.

#### Visualización de outliers con boxplot


```python
def create_boxplots(outliers_cols):
    fig, axes = plt.subplots(nrows = 1, ncols = len(outliers_cols), figsize = (18, 6))
    
    for i, col in enumerate(outliers_cols):
        df_full_copy.boxplot(column = col, ax = axes[i])
    
        axes[i].set_title(col)
        axes[i].set_xticklabels([""])

outliers_cols = ["Precipitación_00-24h__mm_", "Viento_media_km/h", "solar_fotovoltaica_mwh", "hulla_antracita_mwh", "otras_tecnologias_mwh"]
create_boxplots(outliers_cols)
```


    
![png](output_34_0.png)
    


- **Precipitaciones**: Observamos como la caja no existe como tal. España es relativamente seco, pero con lluvia. Hay que tener en cuenta que hay zonas en las que unos cuantos días de lluvia pueden presentar variaciones en la media y esto no quiere decir necesariamente que los datos sean incorrectos, pero pueden desestabilizar un modelo. Por ello vamos a cortarlos en torno a los `250 mm`, que es donde los datos empiezan a dispersarse claramente.
- **Viento medio**: La distribución es muy similar a la de la hulla/antracita, pero por razones distintas. El viento no es estable y no siempre sopla de la misma manera, pero sí es progresivo. Es por ello que los outliers están muy próximos entre sí. La media se sitúa en torno a los `25 km/h` en todo el país, lo que habla de la suavizaz del clima, pero existen datos altos más allá de los `100 km/h`. De todos modos, debemos tener en cuenta que los aerogeneradores tienen una velocidad de giro máxima por seguridad, lo que se traduce en que la creencia de que `+ viento = + energía` no siempre es cierta. Este freno de seguridad depende del aerogenerador, pero el valor medio es de `25 m/s ≈ 90 km/h`. ([Fuente](https://researchhubs.com/post/engineering/wind-energy/power-output-variation-with-wind-speed.html))
- **Solar fotovoltaica**: El boxplot no presenta outliers (lo que son buenas noticias). De hecho, que no los presente puede hablarnos sobre el ciclo de estaciones de la propia Tierra y el clima suave de España: el bigote inferior baja hasta esos `10.0` MWh que se habían observado antes y el superior sube por encima de los `100000` MWh sin presentar ningún outlier. Esto quiere decir que el patrón se repite y que es normal. Por el momento esta columna no será tratada, pero será vigilada a la hora de entrenar un modelo y su comportamiento.
- **Hulla/antracita**: La caja está muy abajo y los valores extremos están por arriba, pero muy cercanos entre sí. Con una rápida búsqueda en Google podemos confirmar que, en efecto, entre 2018 y 2023 España comenzó a apagar centrales térmicas de carbón. Es por ello que estos valores están muy pegados entre sí, pero ya no cuadran con la media (la caja). Para acabar con este punto, en 2025 se apagó la última central de carbón española, por lo que podemos eliminar esta columna por no aportar información predictora relevante. ([Fuente](https://es.wikipedia.org/wiki/Cierre_de_las_centrales_t%C3%A9rmicas_de_carb%C3%B3n_en_Espa%C3%B1a))
- **Otras tecnologías**: No se puede decir demasiado de esta columna, ya que ni siquiera la API de entso-e da alguna explicación. Seguramente incluya muchas formas de energía menores que no tienen tanta relevancia como para tener su propia columna. Vemos que los outliers son muy fuertes, pero no podemos sacar más conclusiones. Ante la duda, será eliminada (junto con `otras_renovables_mwh` por consistencia). 

Tenemos suficientes datos (> 1 millón y medio), por lo que podemos aplicar un corte en lugar de una imputación y así mantenemos datos fieles a la realidad.


```python
# Tratamiento de outliers descritos
print(f"Registros pre-tratamiento de outliers: {df_full_copy.shape[0]}")

# Precipitaciones solo menores a 250 mm
df_full_copy = df_full_copy[df_full_copy["Precipitación_00-24h__mm_"] < 250]

# Viento medio solo menor a 90 km/h
df_full_copy = df_full_copy[df_full_copy["Viento_media_km/h"] < 90]

df_full_copy.drop(columns = ["hulla_antracita_mwh", "otras_tecnologias_mwh", "otras_renovables_mwh"], inplace = True)

print(f"Registros post-tratamiento de outliers: {df_full_copy.shape[0]}")

outliers_cols = ["Precipitación_00-24h__mm_", "Viento_media_km/h", "solar_fotovoltaica_mwh"]
create_boxplots(outliers_cols)
```

    Registros pre-tratamiento de outliers: 1690840
    Registros post-tratamiento de outliers: 1601759



    
![png](output_36_1.png)
    


Han sido eliminados cerca de `90000` registros, pero eso apenas representa un `5%` de los datos.

En cuanto a los nuevos boxplots, aunque presenten los outliers, creo que estos representan la realidad del clima y pueden ser importantes para predecir la generación en un futuro:

- Las precipitaciones presentan muchos outliers, pero mientras que hay sitios muy secos (Cabo de Gata o Almería apenas reciben `150 mm` de precipitaciones al año), existen otros mucho más húmedos (Asturias con más de `900 mm` de media). Esto puede ir contra del pensamiento de cortar estos datos por encima de los `250 mm`, pero no se debe olvidar de que estamos hablando de medias nacionales y son dos climas completamente distintos. Para más precisión sería mejor desarrollar modelos específicos por clima.
- La media del viento se ve contenida y con esos puntos extremos solapándose. Al igual que en el anterior punto, existen zonas con muchísimo viento (cualquier lugar de montaña o costa) y otras con mucho menos (ciudades de interior como Madrid).

### Feature Engineering (Ingeniería de variables)

Para enriquecer un poco el dataset se pueden crear variables que serán más útiles de cara al entrenamiento de un algoritmo. Un algoritmo no puede trabajar con fechas como tal. Por ello en este putno se crearán:

- `mes`: Una columna con el número del mes. Como se refleja en el boxplot de la solar fotovoltaica, en un año el clima general es cambiante y sigue un patrón (las estaciones). Por tanto, el mes permitirá al algoritmo comprender, por ejemplo, que en invierno se genera una demanda extra por las calefacciones, pero en verano se genera más solar fotovoltaica por las horas de sol.
- `dia_semana`: Permitirá a un algoritmo identificar patrones de consumo recurrentes, (la actividad industrial y laboral en general es de lunes a viernes).
- `es_fin_de_semana`: Siguiendo con el punto anterior, la actividad laboral disminuirá los fines de semana. Esta característica le dará al algoritmo mayor capacidad de segmentación por momento de la semana (entre semana o fin de semana). Esta columna será de tipo `int` para mantener la consistencia con `es_festivo`, pero a efectos prácticos será `1` ó `0` si es `True` o `False`.


```python
# Debería estar ya convertida
df_full_copy["fecha"] = pd.to_datetime(df_full_copy["fecha"])
df_full_copy = df_full_copy.sort_values("fecha").reset_index(drop = True)

df_full_copy["mes"] = df_full_copy["fecha"].dt.month # 0 = Enero, 11 = Diciembre
df_full_copy["dia_semana"] = df_full_copy["fecha"].dt.dayofweek # 0 = Lunes, 6 = Domingo
df_full_copy["es_fin_de_semana"] = df_full_copy["dia_semana"].isin([5, 6]).astype(int)

df_full_copy.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Estación</th>
      <th>Provincia</th>
      <th>Temperatura_media__ºC_</th>
      <th>Precipitación_00-24h__mm_</th>
      <th>archivo_origen</th>
      <th>fecha</th>
      <th>Provincia_Limpia</th>
      <th>ccaa_codigo</th>
      <th>es_festivo</th>
      <th>biomasa_mwh</th>
      <th>...</th>
      <th>hidraulica_fluyente_mwh</th>
      <th>hidraulica_embalse_mwh</th>
      <th>nuclear_mwh</th>
      <th>solar_fotovoltaica_mwh</th>
      <th>residuos_mwh</th>
      <th>eolica_terrestre_mwh</th>
      <th>Viento_media_km/h</th>
      <th>mes</th>
      <th>dia_semana</th>
      <th>es_fin_de_semana</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Estaca de Bares</td>
      <td>A Coruña</td>
      <td>17.6</td>
      <td>0.0</td>
      <td>Aemet2020-06-01.xls</td>
      <td>2020-06-01</td>
      <td>A Coruña</td>
      <td>GA</td>
      <td>0</td>
      <td>6848.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>95104.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>46137.0</td>
      <td>43.0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Manilva</td>
      <td>Málaga</td>
      <td>21.0</td>
      <td>0.0</td>
      <td>Aemet2020-06-01.xls</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6848.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>95104.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>46137.0</td>
      <td>18.5</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Benahavís</td>
      <td>Málaga</td>
      <td>19.9</td>
      <td>0.0</td>
      <td>Aemet2020-06-01.xls</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6848.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>95104.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>46137.0</td>
      <td>15.5</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Marbella, Puerto</td>
      <td>Málaga</td>
      <td>20.2</td>
      <td>0.0</td>
      <td>Aemet2020-06-01.xls</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6848.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>95104.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>46137.0</td>
      <td>17.0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Marbella</td>
      <td>Málaga</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>Aemet2020-06-01.xls</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6848.0</td>
      <td>...</td>
      <td>32022.0</td>
      <td>74460.0</td>
      <td>95104.0</td>
      <td>67691.0</td>
      <td>5141.0</td>
      <td>46137.0</td>
      <td>12.5</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 22 columns</p>
</div>



## Capa Oro

En la capa oro se guardarán dos datasets:

1. **Dataset con los valores sin normalizar**: Este dataset permite visualizar gráficas con los valores reales y sin tener que desnormalizarlos o realizar modificaciones sin necesidad de volver a las capas plata o bronce. Este dataset es justo el que se ha terminado de construir en el punto anterior.
2. **Dataset con los valores normalizados**: Este dataset ya tendrá ajustadas las distribuciones y los valores en unos rangos óptimos para entrenar a un algoritmo sin necesidad de realizar más modificaciones. Este dataset necesitará unas cuantas modificaciones antes de poder ser exportado.


```python
# Subida del dataset sin normalizar
s3 = connect_s3()
df_clean = df_full_copy.copy()
upload_parquet_to_s3(
    s3,
    bucket = BUCKET_ORO,
    path = "generacion-energetica-limpio",
    df = df_clean
)
```

    Conexión establecida.
    Subiendo archivo parquet a ksc-proyecto-integrador-oro
    Archivo .parquet subido correctamente a s3://ksc-proyecto-integrador-oro/generacion-energetica-limpio.parquet


### Normalización

En este punto se realizarán transformaciones para normalizar los datos del dataset. 

Debemos entender que el objetivo del proyecto es poder predecir la generación de fuentes renovables para poder optimizar la generación eléctrica por medio de dichas fuentes. Para ello debemos clarificar como funcionan las fuente energéticas en el sistema energético español:

- Fuentes constantes: Son la base del sistema.
    1. Nuclear: Es la base del sistema y suele producir lo mismo siempre. Encendida 24/7 y la más estable de todas.
    2. Biomasa: Quema restos forestales o agrícolas de desecho. También suele estar encendida 24/7.
    3. Residuos: Quema residuos urbanos (basuras). Encendida 24/7.
- Renovables: Estas fuentes no son siempre estables y dependen de las condiciones. **Variables objetivo del proyecto**.
    1. Solar fotovoltaica: Depende del sol y las nubes.
    2. Eólica: Depende del viento
    3. Hidraúlica fluyente: Son presas en ríos. Dependen de la fuerza de la corriente (lluvia = + corriente).
- Reserva: Pueden usarse en función de la demanda y son controlables:
    1. Hidraúlica de embalses (Realmente es renovable, pero no presenta la naturaleza cambiante característica de estas): Dependen de que el operario abra la puerta (y de que haya agua en el embalse, pero contamos con ello).
- Fósiles: Son más caras, menos eficientes y más contaminantes. Son las que queremos evitar a toda costa.
    1. Gas natural: La más limpia y eficiente de las fósiles. Se compra cuando es necesario suplir la demanda.
    2. Petróleo: Muy cara y muy contamimente. Apenas utilizada en la península, pero sí es usada en las islas Canarias, Baleares y Ceuta y Melilla.

Por lo tanto, podemos imaginar una fórmula cómo:

`Fósiles = Demanda Total - Constantes - Renovables - Reserva`

Las variables objetivo (las variables a predecir) nunca se escalan.

En los siguiente histogramas se dibujarán las distribuciones de cada columna para ver dónde las distribuciones pueden ser más problemáticas.


```python
def create_distributions(df, cols, num_cols = 4):
    num_rows = math.ceil(len(cols) / num_cols)
    
    fig, axes = plt.subplots(nrows = num_rows, ncols = num_cols, figsize = (18, 4 * num_rows))
    axes = axes.flatten()
    
    for i, col in enumerate(cols):
        sns.histplot(data = df, x = col, kde = True, ax = axes[i], color = "steelblue", bins = 30)
    
        axes[i].set_title(col)
        # axes[i].set_xlabel([""])
        # axes[i].set_ylabel([""])
    plt.tight_layout()
    plt.show()
```


```python
# Columnas con riesgos de distribuciones extrañas
cols = ["Temperatura_media__ºC_", "Precipitación_00-24h__mm_", "biomasa_mwh", "gas_natural_mwh", "petroleo_mwh", 
        "hidraulica_fluyente_mwh", "hidraulica_embalse_mwh", "nuclear_mwh", "solar_fotovoltaica_mwh", "residuos_mwh", 
        "eolica_terrestre_mwh", "Viento_media_km/h"]

create_distributions(df_clean, cols, 4)
```


    
![png](output_44_0.png)
    


Las gráficas muestran distintas necesidades de normalización:

- **Distribución normal**: `Temperatura_media__ºC_` presenta una campana de Gauss casi perfecta, por lo que tiene una distribución normal, gracias al ciclo repetitivo de las estaciones. Por ello utilizará la estandarización `StandardScaler` para normalizarse.
- **Sesgo a la derecha**: `Precipitación_00-24h__mm_`, `Viento_media_km/h`, `gas_natural_mwh`, `petróleo_mwh`, `hidraulica_embalse_mwh`. Son la mayoría. Presentan un agrupamiento de los datos en los valores bajos y largas colas hacia los valores más altos. Utilizarán una transformación logarítmica.
- **Multimodales**: `nuclear_mwh`, `biomasa_mwh`, `residuos_mwh`. Presentan varias cordilleras de datos. Utilizarán una normalización Min-Max, que conservará los picos y las cordilleras donde están, pero mantendrá los valores entre `0.0` y `1.0`

Como se ha dicho anteriormente, las variables objetivo (las renovables `solar_fotovoltaica_mwh`, `eolica_terrestre_mwh` y `hidraulica_fluyente_mwh`) no se escalarán por ser las variables objetivo. De hacerlo, el algoritmo predecirá en los valores normalizados en lugar de los MWh reales.


```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, FunctionTransformer
from sklearn.compose import ColumnTransformer # para hacer toda la transformación a la vez

cols_normal = ["Temperatura_media__ºC_"]
cols_skew = ["Precipitación_00-24h__mm_", "Viento_media_km/h", "gas_natural_mwh", "petroleo_mwh", "hidraulica_embalse_mwh"]
cols_multimodal = ["nuclear_mwh", "biomasa_mwh", "residuos_mwh"]

preprocess = ColumnTransformer(
    transformers = [
        ("estandarizacion", StandardScaler(), cols_normal),
        ("log", FunctionTransformer(np.log1p, validate = True, feature_names_out = "one-to-one"), cols_skew),
        ("min_max", MinMaxScaler(), cols_multimodal)
    ],
    remainder = "passthrough"
)
```


```python
target_cols = ["solar_fotovoltaica_mwh", "eolica_terrestre_mwh", "hidraulica_fluyente_mwh"]
df_clean_norm = df_clean.copy()

# Separa para no mezclar datos en el escalado
df_target = df_clean_norm[target_cols]
df_transform = df_clean_norm.drop(columns = target_cols)

norm_data = preprocess.fit_transform(df_transform)

# Al normalizar con ColumTransformer se convierte a un array de np y pierde el nombre de las columnas 
cols_output = preprocess.get_feature_names_out()
cols_output_clean = [col.split("__")[-1] for col in cols_output]

df_norm_data = pd.DataFrame(norm_data, columns = cols_output_clean)
df_norm_clean = pd.concat([df_norm_data, df_target], axis = 1).reset_index()
```


```python
 # Al limpiar las salidas del ColumnTransform se carga el nombre de la Temperatura media y Precipitaciones
df_norm_clean.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>index</th>
      <th>ºC_</th>
      <th>mm_</th>
      <th>Viento_media_km/h</th>
      <th>gas_natural_mwh</th>
      <th>petroleo_mwh</th>
      <th>hidraulica_embalse_mwh</th>
      <th>nuclear_mwh</th>
      <th>biomasa_mwh</th>
      <th>residuos_mwh</th>
      <th>...</th>
      <th>fecha</th>
      <th>Provincia_Limpia</th>
      <th>ccaa_codigo</th>
      <th>es_festivo</th>
      <th>mes</th>
      <th>dia_semana</th>
      <th>es_fin_de_semana</th>
      <th>solar_fotovoltaica_mwh</th>
      <th>eolica_terrestre_mwh</th>
      <th>hidraulica_fluyente_mwh</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0.236426</td>
      <td>0.0</td>
      <td>3.78419</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>A Coruña</td>
      <td>GA</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>0.711003</td>
      <td>0.0</td>
      <td>2.970414</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>0.557464</td>
      <td>0.0</td>
      <td>2.80336</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>0.599338</td>
      <td>0.0</td>
      <td>2.890372</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>2.60269</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 23 columns</p>
</div>




```python
# Renombra las columnas que han perdido su nombre
df_norm_clean.rename(columns = {"ºC_": "temperatura_media_ºC", "mm_": "precipitaciones_medias_diarias_mm"}, inplace = True)
df_norm_clean.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>index</th>
      <th>temperatura_media_ºC</th>
      <th>precipitaciones_medias_diarias_mm</th>
      <th>Viento_media_km/h</th>
      <th>gas_natural_mwh</th>
      <th>petroleo_mwh</th>
      <th>hidraulica_embalse_mwh</th>
      <th>nuclear_mwh</th>
      <th>biomasa_mwh</th>
      <th>residuos_mwh</th>
      <th>...</th>
      <th>fecha</th>
      <th>Provincia_Limpia</th>
      <th>ccaa_codigo</th>
      <th>es_festivo</th>
      <th>mes</th>
      <th>dia_semana</th>
      <th>es_fin_de_semana</th>
      <th>solar_fotovoltaica_mwh</th>
      <th>eolica_terrestre_mwh</th>
      <th>hidraulica_fluyente_mwh</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0.236426</td>
      <td>0.0</td>
      <td>3.78419</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>A Coruña</td>
      <td>GA</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>0.711003</td>
      <td>0.0</td>
      <td>2.970414</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>0.557464</td>
      <td>0.0</td>
      <td>2.80336</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>0.599338</td>
      <td>0.0</td>
      <td>2.890372</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>2.60269</td>
      <td>12.160317</td>
      <td>8.796339</td>
      <td>11.218031</td>
      <td>0.137973</td>
      <td>0.118494</td>
      <td>0.163219</td>
      <td>...</td>
      <td>2020-06-01</td>
      <td>Málaga</td>
      <td>AN</td>
      <td>0</td>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>67691.0</td>
      <td>46137.0</td>
      <td>32022.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 23 columns</p>
</div>



Estos datos ya están preparados y listos para ser guardados en la capa oro.


```python
# Subida del dataset sin normalizar
s3 = connect_s3()
upload_parquet_to_s3(
    s3,
    bucket = BUCKET_ORO,
    path = "generacion-energetica-normalizado",
    df = df_norm_clean
)
```

    Conexión establecida.
    Subiendo archivo parquet a ksc-proyecto-integrador-oro
    Archivo .parquet subido correctamente a s3://ksc-proyecto-integrador-oro/generacion-energetica-normalizado.parquet


![image.png](25a3c43b-709f-4103-93b1-c7a2547ad46b.png)

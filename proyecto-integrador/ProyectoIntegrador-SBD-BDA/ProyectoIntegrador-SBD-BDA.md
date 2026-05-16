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
import requests
from urllib.parse import urljoin
import rarfile
import subprocess
import os
import shutil
import io
import holidays
import json
import awswrangler as wr
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, RequestException

API_REE_URL = "https://apidatos.ree.es"
DATOS_CLIMA = "https://datosclima.es/Aemet2013/DescargaDatos.html"

BUCKET_BRONCE = "ksc-proyecto-integrador-bronce"
BUCKET_PLATA = "ksc-proyecto-integrador-plata"

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

def download_from_s3(s3, bucket, object_path):
    download_path = os.path.join("s3_downloads", object_path)

    try:
        print(f"Descargando desde s3: s3//{bucket}/{object_path}")
        s3.download_file(bucket, object_path, download_path)
        print(f"Archivo descargado y almacenado en: {download_path}")
    except Exception as e:
        print(f"ERROR: {e}")
```

    /opt/conda/lib/python3.11/site-packages/pandas/core/computation/expressions.py:23: UserWarning: Pandas requires version '2.10.2' or newer of 'numexpr' (version '2.8.7' currently installed).
      from pandas.core.computation.check import NUMEXPR_INSTALLED
    /opt/conda/lib/python3.11/site-packages/pandas/core/arrays/masked.py:56: UserWarning: Pandas requires version '1.4.2' or newer of 'bottleneck' (version '1.3.7' currently installed).
      from pandas.core import (


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

    Conexión establecida.
    Descargando: https://datosclima.es/capturadatos/Aemet2013-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 25
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2013-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2013-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2013-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2013-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2013-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2013-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 29
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2013-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2013/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 29
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 29
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2014-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2014/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2015-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2015/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 29
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/02/29.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2016-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2016/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 27
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2017-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2017/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2018-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2018/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2019/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2019-10.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2019-11.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2019-12.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2020-01.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2020-02.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2020-03.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2020-04.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2020-05.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2020-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2020-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2020-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2020-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2020-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2020-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2020-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2020/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2021-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2021/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2022-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2022/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-03.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2023-04.rar
    ERROR: El servidor tardó demasiado en responder.
    Descargando: https://datosclima.es/capturadatos/Aemet2023-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2023-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2023/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 29
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/02/29.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2024-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2024/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/03/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-04.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/04/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-05.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/05/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-06.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/06/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-07.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/07/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-08.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/08/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-09.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/09/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-10.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/10/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-11.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 30
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/11/30.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2025-12.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2025/12/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2026-01.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/01/31.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2026-02.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 28
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/02/28.csv
    Descargando: https://datosclima.es/capturadatos/Aemet2026-03.rar
    Descomprimiendo...
    Número de elementos descomprimidos: 31
    Convirtiendo de excel a DataFrame de pandas
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/01.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/02.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/03.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/04.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/05.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/06.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/07.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/08.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/09.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/10.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/11.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/12.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/13.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/14.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/15.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/16.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/17.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/18.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/19.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/20.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/21.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/22.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/23.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/24.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/25.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/26.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/27.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/28.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/29.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/30.csv
    Subiendo datos a S3 desde memoria
    Datos subidos con éxito a s3://ksc-proyecto-integrador-bronce/Aemet2026/03/31.csv


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
import matplotlib.pyplot as plt
import seaborn as sns

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

df_full_copy.drop(columns = ["hulla_antracita_mwh", "otras_tecnologias_mwh", "otras_renovables_mwh"])

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

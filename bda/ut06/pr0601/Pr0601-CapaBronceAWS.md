# PR0601 - Capa bronce en Amazon AWS

### Lectura API Key desde fichero


```python
# Pongo la API Key en un fichero para no subirla directamente al github
API_KEY = ""
with open("aemet.txt") as f:
    API_KEY = f.read().strip()

BASE_URL = "https://opendata.aemet.es/opendata"
BUCKET = "capa-bronce-amazon-ksc"
```

### Importaciones


```python
!pip install boto3
```

    Requirement already satisfied: boto3 in /opt/conda/lib/python3.11/site-packages (1.42.71)
    Requirement already satisfied: botocore<1.43.0,>=1.42.71 in /opt/conda/lib/python3.11/site-packages (from boto3) (1.42.71)
    Requirement already satisfied: jmespath<2.0.0,>=0.7.1 in /opt/conda/lib/python3.11/site-packages (from boto3) (1.1.0)
    Requirement already satisfied: s3transfer<0.17.0,>=0.16.0 in /opt/conda/lib/python3.11/site-packages (from boto3) (0.16.0)
    Requirement already satisfied: python-dateutil<3.0.0,>=2.1 in /opt/conda/lib/python3.11/site-packages (from botocore<1.43.0,>=1.42.71->boto3) (2.8.2)
    Requirement already satisfied: urllib3!=2.2.0,<3,>=1.25.4 in /opt/conda/lib/python3.11/site-packages (from botocore<1.43.0,>=1.42.71->boto3) (2.0.7)
    Requirement already satisfied: six>=1.5 in /opt/conda/lib/python3.11/site-packages (from python-dateutil<3.0.0,>=2.1->botocore<1.43.0,>=1.42.71->boto3) (1.16.0)



```python
import boto3
import pandas as pd
import requests
import json
import datetime
from requests.exceptions import Timeout, RequestException
```

## 1.- Obtención de datos

### Catálogo de playas (CSV)


```python
!head -n 1 playas_espanolas.csv
```

    ﻿X,Y,OBJECTID,Comunidad_,Provincia,Isla,Código_IN,Término_M,Web_munici,Identifica,Nombre,Nombre_alt,Nombre_a_1,Descripci,Longitud,Anchura,Variación,Grado_ocup,Grado_urba,Paseo_mar,Tipo_paseo,Tipo_de_ar,Condicione,Zona_fonde,Nudismo,Vegetació,Vegetaci_1,Actuacione,Actuacio_1,Bandera_az,Auxilio_y_,Auxilio_y1,Señalizac,Señaliza_,Forma_de_a,Señaliza1,Acceso_dis,Carretera_,Autobús,Autobús_t,Aparcamien,Aparcami_1,Aparcami_2,Aseos,Lavapies,Duchas,Teléfonos,Papelera,Servicio_l,Alquiler_s,Alquiler_h,Alquiler_n,Oficina_tu,Establecim,Establec_1,Zona_infan,Zona_depor,Club_naút,Submarinis,Zona_Surf,Observacio,Coordenada,Coordena_1,Huso,Coordena_2,Coordena_3,Puerto_dep,Web_puerto,Distancia_,Hospital,Dirección,Teléfono_,Distancia1,Composici,Fachada_Li,Espacio_pr,Espacio__1,Coordena_4,Coordena_5,URL_MAGRAM



```python
def get_df_playas():
    print("Leyendo csv.")
    df_playas = pd.read_csv(
        "playas_espanolas.csv",
        usecols = ["Nombre", "Provincia", "Término_M", "Duchas", "Aseos", "Acceso_dis", "Bandera_az", "X", "Y", "Grado_ocup", "Grado_urba"]
    )

    print("csv convertido a DataFrame.")
    return df_playas
```

### API AEMET OpenData (API REST)


```python
def get_datos_aemet(df_playas):
    provincias = set(df_playas["Provincia"].unique())
    endpoint = "/api/prediccion/provincia/hoy/"
    query_string = {"api_key": API_KEY}
    
    with open("codigos_provincias.json") as f:
        codigos_provincias = json.load(f)

    print("Obteniendo datos de AEMET.")
    datos_aemet = ""
    for provincia in provincias:
        codigo = codigos_provincias[provincia]
    
        url = BASE_URL + endpoint + codigo
        try:
            response = requests.get(url, params = query_string, timeout = (3, 10))
            response.raise_for_status()
            response_json = response.json()
        
            datos = response_json.get("datos", None)
        
            if datos:
                response_provincia = requests.get(datos, timeout = (3, 10)).text

                datos_aemet = datos_aemet + "\n" + response_provincia
        except Timeout:
            print("ERROR: El servidor tardó demasiado en responder.")
        except RequestException as e:
            print(f"ERROR: {e}")

    print("Datos de AEMET obtenidos.")
    return datos_aemet
```

### Subida a AWS S3


```python
def conectar_s3():
    try:
        s3 = boto3.client("s3")
        print("Conexión establecida.")
    except Exception as e:
        print("Error de conexión.")
        print(e)

    return s3
```


```python
def subir_datos(s3, bucket, ruta, datos):
    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    existe_bucket = bucket in buckets

    if not existe_bucket:
        s3.create_bucket(Bucket = bucket)

    s3.upload_file(datos, bucket, ruta)
    print(f"Dataframe subido con éxito a s3://{bucket}/{ruta}")
```


```python
# He tenido que crear un método aparte porque me está dando problemas subirlo con el otro al ser texto y no un csv
def subir_texto(s3, bucket, ruta, texto):
    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    existe_bucket = bucket in buckets

    if not existe_bucket:
        s3.create_bucket(Bucket = bucket)
    
    s3.put_object(
            Bucket = bucket,
            Key = ruta,
            Body = texto.encode('utf-8')
        )
    print(f"Texto subido con éxito a s3://{bucket}/{ruta}")
```

### Ingestor


```python
s3 = conectar_s3()
df_playas = get_df_playas()
datos_aemet = get_datos_aemet(df_playas)

fecha_hoy = datetime.datetime.now()

df_playas.to_csv("df_playas.csv")

subir_datos(s3, BUCKET, "bronce/catalogos/guia_playas/v1/playas.csv", "df_playas.csv")
subir_texto(s3, BUCKET, f"bronce/meteorologia/prediccion_playas/{fecha_hoy.year}/{fecha_hoy.month}/{fecha_hoy.day}.txt", datos_aemet)
```

    Conexión establecida.
    Leyendo csv.
    csv convertido a DataFrame.
    Obteniendo datos de AEMET.
    Datos de AEMET obtenidos.
    Dataframe subido con éxito a s3://capa-bronce-amazon-ksc/bronce/catalogos/guia_playas/v1/playas.csv
    Texto subido con éxito a s3://capa-bronce-amazon-ksc/bronce/meteorologia/prediccion_playas/2026/4/8.txt


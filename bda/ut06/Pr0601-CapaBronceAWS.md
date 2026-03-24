# PR0601 - Capa bronce en Amazon AWS

### Lectura API Key desde fichero


```python
# Pongo la API Key en un fichero para no subirla directamente al github
API_KEY = ""
with open("aemet.txt") as f:
    API_KEY = f.read()

BASE_URL = "https://opendata.aemet.es/opendata"
```

### Importaciones


```python
import boto3
import pandas as pd
```

## 1.- Obtención de datos

### Catálogo de playas (CSV)


```python
!head -n 1 playas_espanolas.csv
```

    ﻿X,Y,OBJECTID,Comunidad_,Provincia,Isla,Código_IN,Término_M,Web_munici,Identifica,Nombre,Nombre_alt,Nombre_a_1,Descripci,Longitud,Anchura,Variación,Grado_ocup,Grado_urba,Paseo_mar,Tipo_paseo,Tipo_de_ar,Condicione,Zona_fonde,Nudismo,Vegetació,Vegetaci_1,Actuacione,Actuacio_1,Bandera_az,Auxilio_y_,Auxilio_y1,Señalizac,Señaliza_,Forma_de_a,Señaliza1,Acceso_dis,Carretera_,Autobús,Autobús_t,Aparcamien,Aparcami_1,Aparcami_2,Aseos,Lavapies,Duchas,Teléfonos,Papelera,Servicio_l,Alquiler_s,Alquiler_h,Alquiler_n,Oficina_tu,Establecim,Establec_1,Zona_infan,Zona_depor,Club_naút,Submarinis,Zona_Surf,Observacio,Coordenada,Coordena_1,Huso,Coordena_2,Coordena_3,Puerto_dep,Web_puerto,Distancia_,Hospital,Dirección,Teléfono_,Distancia1,Composici,Fachada_Li,Espacio_pr,Espacio__1,Coordena_4,Coordena_5,URL_MAGRAM



```python
df = pd.read_csv(
    "playas_espanolas.csv",
    usecols = ["Nombre", "Provincia", "Término_M", "Duchas", "Aseos", "Acceso_dis", "Bandera_az", "X", "Y", "Grado_ocup", "Grado_urba"]
)

df.head()
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
      <th>X</th>
      <th>Y</th>
      <th>Provincia</th>
      <th>Término_M</th>
      <th>Nombre</th>
      <th>Grado_ocup</th>
      <th>Grado_urba</th>
      <th>Bandera_az</th>
      <th>Acceso_dis</th>
      <th>Aseos</th>
      <th>Duchas</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-543984.9557</td>
      <td>4.370555e+06</td>
      <td>Málaga</td>
      <td>Marbella</td>
      <td>La Venus</td>
      <td>Alto</td>
      <td>Urbana</td>
      <td>No</td>
      <td>Sí</td>
      <td>Sí</td>
      <td>Sí</td>
    </tr>
    <tr>
      <th>1</th>
      <td>-529891.9081</td>
      <td>4.367771e+06</td>
      <td>Málaga</td>
      <td>Marbella</td>
      <td>Las Cañas</td>
      <td>Medio</td>
      <td>Urbana</td>
      <td>No</td>
      <td>No</td>
      <td>Sí</td>
      <td>Sí</td>
    </tr>
    <tr>
      <th>2</th>
      <td>-524448.3850</td>
      <td>4.367937e+06</td>
      <td>Málaga</td>
      <td>Mijas</td>
      <td>Calahonda</td>
      <td>Medio / Alto</td>
      <td>Urbana</td>
      <td>Sí</td>
      <td>Sí</td>
      <td>Sí</td>
      <td>Sí</td>
    </tr>
    <tr>
      <th>3</th>
      <td>-517145.8264</td>
      <td>4.370638e+06</td>
      <td>Málaga</td>
      <td>Mijas</td>
      <td>El Charcón</td>
      <td>Bajo</td>
      <td>Semiurbana</td>
      <td>No</td>
      <td>No</td>
      <td>No</td>
      <td>Sí</td>
    </tr>
    <tr>
      <th>4</th>
      <td>-4975.9812</td>
      <td>4.664878e+06</td>
      <td>Alicante/Alacant</td>
      <td>Altea</td>
      <td>L'Espigó</td>
      <td>Alto</td>
      <td>Urbana</td>
      <td>Sí</td>
      <td>Sí</td>
      <td>Sí</td>
      <td>No</td>
    </tr>
  </tbody>
</table>
</div>



### API AEMET OpenData (API REST)


```python
endpoint = "/api/prediccion/especifica/playa/"
url = base_url + endpoint

try:
    response = requests.get(url, timeout = (3, 10))
    response.raise_for_status()
    response_json = response.json()


except Timeout:
    print("ERROR: El servidor tardó demasiado en responder.")
except RequestException as e:
    print(f"ERROR: {e}")

```

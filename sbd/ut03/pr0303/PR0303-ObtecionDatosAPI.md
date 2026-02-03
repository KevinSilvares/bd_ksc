# PR0303 - Obtención de datos de una API REST

### Importaciones y definiciones base


```python
import requests
from requests.exceptions import Timeout, RequestException
import pandas as pd

base_url = "https://swapi.dev/api/"
```

## 1.- Conexión básica y primer DataFrame


```python
endpoint = "vehicles"
url = base_url + endpoint

try:
    response = requests.get(url, timeout = (3, 10))
    response.raise_for_status()
    response_json = response.json()

    df_vehicles = pd.json_normalize(
            response_json,
            record_path = ["results"]
            )
except Timeout:
    print("ERROR: El servidor tardó demasiado en responder.")
except RequestException as e:
    print(f"ERROR: {e}")


df_vehicles.head(5)
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
      <th>name</th>
      <th>model</th>
      <th>manufacturer</th>
      <th>cost_in_credits</th>
      <th>length</th>
      <th>max_atmosphering_speed</th>
      <th>crew</th>
      <th>passengers</th>
      <th>cargo_capacity</th>
      <th>consumables</th>
      <th>vehicle_class</th>
      <th>pilots</th>
      <th>films</th>
      <th>created</th>
      <th>edited</th>
      <th>url</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Sand Crawler</td>
      <td>Digger Crawler</td>
      <td>Corellia Mining Corporation</td>
      <td>150000</td>
      <td>36.8</td>
      <td>30</td>
      <td>46</td>
      <td>30</td>
      <td>50000</td>
      <td>2 months</td>
      <td>wheeled</td>
      <td>[]</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-10T15:36:25.724000Z</td>
      <td>2014-12-20T21:30:21.661000Z</td>
      <td>https://swapi.dev/api/vehicles/4/</td>
    </tr>
    <tr>
      <th>1</th>
      <td>T-16 skyhopper</td>
      <td>T-16 skyhopper</td>
      <td>Incom Corporation</td>
      <td>14500</td>
      <td>10.4</td>
      <td>1200</td>
      <td>1</td>
      <td>1</td>
      <td>50</td>
      <td>0</td>
      <td>repulsorcraft</td>
      <td>[]</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>2014-12-10T16:01:52.434000Z</td>
      <td>2014-12-20T21:30:21.665000Z</td>
      <td>https://swapi.dev/api/vehicles/6/</td>
    </tr>
    <tr>
      <th>2</th>
      <td>X-34 landspeeder</td>
      <td>X-34 landspeeder</td>
      <td>SoroSuub Corporation</td>
      <td>10550</td>
      <td>3.4</td>
      <td>250</td>
      <td>1</td>
      <td>1</td>
      <td>5</td>
      <td>unknown</td>
      <td>repulsorcraft</td>
      <td>[]</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>2014-12-10T16:13:52.586000Z</td>
      <td>2014-12-20T21:30:21.668000Z</td>
      <td>https://swapi.dev/api/vehicles/7/</td>
    </tr>
    <tr>
      <th>3</th>
      <td>TIE/LN starfighter</td>
      <td>Twin Ion Engine/Ln Starfighter</td>
      <td>Sienar Fleet Systems</td>
      <td>unknown</td>
      <td>6.4</td>
      <td>1200</td>
      <td>1</td>
      <td>0</td>
      <td>65</td>
      <td>2 days</td>
      <td>starfighter</td>
      <td>[]</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-10T16:33:52.860000Z</td>
      <td>2014-12-20T21:30:21.670000Z</td>
      <td>https://swapi.dev/api/vehicles/8/</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Snowspeeder</td>
      <td>t-47 airspeeder</td>
      <td>Incom corporation</td>
      <td>unknown</td>
      <td>4.5</td>
      <td>650</td>
      <td>2</td>
      <td>0</td>
      <td>10</td>
      <td>none</td>
      <td>airspeeder</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/2/]</td>
      <td>2014-12-15T12:22:12Z</td>
      <td>2014-12-20T21:30:21.672000Z</td>
      <td>https://swapi.dev/api/vehicles/14/</td>
    </tr>
  </tbody>
</table>
</div>



## 2.- Gestión de paginación


```python
def request_people(url, timeout):
    try:
        response = requests.get(url, timeout = timeout)
        response.raise_for_status()
        return response.json()
    except Timeout:
        print("ERROR: El servidor tardó demasiado en responder.")
    except RequestException as e:
        print(f"ERROR: {e}")
```


```python
endpoint = "people"
url = base_url + endpoint

results = []
data = request_people(url, (3, 10))

while data["next"] != None:
    # results.append(data["results"])
    results.extend(data["results"])

    url = data["next"]
    data = request_people(url, (3, 10))

df_people = pd.json_normalize(results)

df_people.head()
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
      <th>name</th>
      <th>height</th>
      <th>mass</th>
      <th>hair_color</th>
      <th>skin_color</th>
      <th>eye_color</th>
      <th>birth_year</th>
      <th>gender</th>
      <th>homeworld</th>
      <th>films</th>
      <th>species</th>
      <th>vehicles</th>
      <th>starships</th>
      <th>created</th>
      <th>edited</th>
      <th>url</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Luke Skywalker</td>
      <td>172</td>
      <td>77</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>19BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>[]</td>
      <td>[https://swapi.dev/api/vehicles/14/, https://s...</td>
      <td>[https://swapi.dev/api/starships/12/, https://...</td>
      <td>2014-12-09T13:50:51.644000Z</td>
      <td>2014-12-20T21:17:56.891000Z</td>
      <td>https://swapi.dev/api/people/1/</td>
    </tr>
    <tr>
      <th>1</th>
      <td>C-3PO</td>
      <td>167</td>
      <td>75</td>
      <td>n/a</td>
      <td>gold</td>
      <td>yellow</td>
      <td>112BBY</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>[https://swapi.dev/api/species/2/]</td>
      <td>[]</td>
      <td>[]</td>
      <td>2014-12-10T15:10:51.357000Z</td>
      <td>2014-12-20T21:17:50.309000Z</td>
      <td>https://swapi.dev/api/people/2/</td>
    </tr>
    <tr>
      <th>2</th>
      <td>R2-D2</td>
      <td>96</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, blue</td>
      <td>red</td>
      <td>33BBY</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>[https://swapi.dev/api/species/2/]</td>
      <td>[]</td>
      <td>[]</td>
      <td>2014-12-10T15:11:50.376000Z</td>
      <td>2014-12-20T21:17:50.311000Z</td>
      <td>https://swapi.dev/api/people/3/</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Darth Vader</td>
      <td>202</td>
      <td>136</td>
      <td>none</td>
      <td>white</td>
      <td>yellow</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>[]</td>
      <td>[]</td>
      <td>[https://swapi.dev/api/starships/13/]</td>
      <td>2014-12-10T15:18:20.704000Z</td>
      <td>2014-12-20T21:17:50.313000Z</td>
      <td>https://swapi.dev/api/people/4/</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Leia Organa</td>
      <td>150</td>
      <td>49</td>
      <td>brown</td>
      <td>light</td>
      <td>brown</td>
      <td>19BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/2/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>[]</td>
      <td>[https://swapi.dev/api/vehicles/30/]</td>
      <td>[]</td>
      <td>2014-12-10T15:20:09.791000Z</td>
      <td>2014-12-20T21:17:50.315000Z</td>
      <td>https://swapi.dev/api/people/5/</td>
    </tr>
  </tbody>
</table>
</div>



## 3.- Cruce de datos


```python
def request_by_homeworld(homeworld):
    try:
        response = requests.get(homeworld, timeout = (3, 10))
        response.raise_for_status()
        return response.json()
    except Timeout:
        print("ERROR: El servidor tardó demasiado en responder.")
    except RequestException as e:
        print(f"ERROR: {e}")
```


```python
df_20_people = df_people.head(20).copy()
planets = df_20_people["homeworld"].apply(request_by_homeworld)
df_planets = pd.json_normalize(planets)

df_people = pd.concat([df_people, df_planets])
```


```python
df_people
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
      <th>name</th>
      <th>height</th>
      <th>mass</th>
      <th>hair_color</th>
      <th>skin_color</th>
      <th>eye_color</th>
      <th>birth_year</th>
      <th>gender</th>
      <th>homeworld</th>
      <th>films</th>
      <th>...</th>
      <th>url</th>
      <th>rotation_period</th>
      <th>orbital_period</th>
      <th>diameter</th>
      <th>climate</th>
      <th>gravity</th>
      <th>terrain</th>
      <th>surface_water</th>
      <th>population</th>
      <th>residents</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Luke Skywalker</td>
      <td>172</td>
      <td>77</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>19BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/1/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>C-3PO</td>
      <td>167</td>
      <td>75</td>
      <td>n/a</td>
      <td>gold</td>
      <td>yellow</td>
      <td>112BBY</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/2/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>R2-D2</td>
      <td>96</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, blue</td>
      <td>red</td>
      <td>33BBY</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/3/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Darth Vader</td>
      <td>202</td>
      <td>136</td>
      <td>none</td>
      <td>white</td>
      <td>yellow</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/4/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Leia Organa</td>
      <td>150</td>
      <td>49</td>
      <td>brown</td>
      <td>light</td>
      <td>brown</td>
      <td>19BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/2/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/5/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Nal Hutta</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>[]</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/24/</td>
      <td>87</td>
      <td>413</td>
      <td>12150</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>urban, oceans, swamps, bogs</td>
      <td>unknown</td>
      <td>7000000000</td>
      <td>[https://swapi.dev/api/people/16/]</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Corellia</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>[]</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/22/</td>
      <td>25</td>
      <td>329</td>
      <td>11000</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>plains, urban, hills, forests</td>
      <td>70</td>
      <td>3000000000</td>
      <td>[https://swapi.dev/api/people/14/, https://swa...</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Bestine IV</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>[]</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/26/</td>
      <td>26</td>
      <td>680</td>
      <td>6400</td>
      <td>temperate</td>
      <td>unknown</td>
      <td>rocky islands, oceans</td>
      <td>98</td>
      <td>62000000</td>
      <td>[https://swapi.dev/api/people/19/]</td>
    </tr>
    <tr>
      <th>18</th>
      <td>unknown</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>[]</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/28/</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>[https://swapi.dev/api/people/20/, https://swa...</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Naboo</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>[https://swapi.dev/api/films/3/, https://swapi...</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>26</td>
      <td>312</td>
      <td>12120</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
    </tr>
  </tbody>
</table>
<p>100 rows × 25 columns</p>
</div>



## 4.- Expansión de filas


```python
df_people = df_people.explode("films")
df_people
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
      <th>name</th>
      <th>height</th>
      <th>mass</th>
      <th>hair_color</th>
      <th>skin_color</th>
      <th>eye_color</th>
      <th>birth_year</th>
      <th>gender</th>
      <th>homeworld</th>
      <th>films</th>
      <th>...</th>
      <th>url</th>
      <th>rotation_period</th>
      <th>orbital_period</th>
      <th>diameter</th>
      <th>climate</th>
      <th>gravity</th>
      <th>terrain</th>
      <th>surface_water</th>
      <th>population</th>
      <th>residents</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Luke Skywalker</td>
      <td>172</td>
      <td>77</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>19BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/1/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Luke Skywalker</td>
      <td>172</td>
      <td>77</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>19BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>https://swapi.dev/api/films/2/</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/1/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Luke Skywalker</td>
      <td>172</td>
      <td>77</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>19BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/1/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>0</th>
      <td>Luke Skywalker</td>
      <td>172</td>
      <td>77</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>19BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/1/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>C-3PO</td>
      <td>167</td>
      <td>75</td>
      <td>n/a</td>
      <td>gold</td>
      <td>yellow</td>
      <td>112BBY</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>...</td>
      <td>https://swapi.dev/api/people/2/</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>18</th>
      <td>unknown</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/28/</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>[https://swapi.dev/api/people/20/, https://swa...</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Naboo</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>26</td>
      <td>312</td>
      <td>12120</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Naboo</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>26</td>
      <td>312</td>
      <td>12120</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Naboo</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>26</td>
      <td>312</td>
      <td>12120</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Naboo</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>...</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>26</td>
      <td>312</td>
      <td>12120</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
    </tr>
  </tbody>
</table>
<p>218 rows × 25 columns</p>
</div>



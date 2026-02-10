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




```python
print("Nombre columnas: ", df_vehicles.columns.to_list())
```

    Nombre columnas:  ['name', 'model', 'manufacturer', 'cost_in_credits', 'length', 'max_atmosphering_speed', 'crew', 'passengers', 'cargo_capacity', 'consumables', 'vehicle_class', 'pilots', 'films', 'created', 'edited', 'url']


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
planets_urls = df_20_people["homeworld"].unique()

planets = {}
for planet in planets_urls:
    planets[planet] = request_by_homeworld(planet)

df_planets = pd.DataFrame.from_dict(planets, orient = "index").reset_index()

df_planets["homeworld"] = df_planets["index"]

df_20_people = df_20_people.merge(df_planets, on = "homeworld", how = "left")
```


```python
df_20_people
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
      <th>name_x</th>
      <th>height</th>
      <th>mass</th>
      <th>hair_color</th>
      <th>skin_color</th>
      <th>eye_color</th>
      <th>birth_year</th>
      <th>gender</th>
      <th>homeworld</th>
      <th>films_x</th>
      <th>...</th>
      <th>climate_y</th>
      <th>gravity_y</th>
      <th>terrain_y</th>
      <th>surface_water_y</th>
      <th>population_y</th>
      <th>residents_y</th>
      <th>films</th>
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
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>[https://swapi.dev/api/films/3/, https://swapi...</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grasslands, mountains</td>
      <td>40</td>
      <td>2000000000</td>
      <td>[https://swapi.dev/api/people/5/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-10T11:35:48.479000Z</td>
      <td>2014-12-20T20:58:18.420000Z</td>
      <td>https://swapi.dev/api/planets/2/</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Owen Lars</td>
      <td>178</td>
      <td>120</td>
      <td>brown, grey</td>
      <td>light</td>
      <td>blue</td>
      <td>52BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Beru Whitesun lars</td>
      <td>165</td>
      <td>75</td>
      <td>brown</td>
      <td>light</td>
      <td>blue</td>
      <td>47BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>7</th>
      <td>R5-D4</td>
      <td>97</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, red</td>
      <td>red</td>
      <td>unknown</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Biggs Darklighter</td>
      <td>183</td>
      <td>84</td>
      <td>black</td>
      <td>light</td>
      <td>brown</td>
      <td>24BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Obi-Wan Kenobi</td>
      <td>182</td>
      <td>77</td>
      <td>auburn, white</td>
      <td>fair</td>
      <td>blue-gray</td>
      <td>57BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/20/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grass</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>[https://swapi.dev/api/people/10/]</td>
      <td>[]</td>
      <td>2014-12-10T16:16:26.566000Z</td>
      <td>2014-12-20T20:58:18.452000Z</td>
      <td>https://swapi.dev/api/planets/20/</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Anakin Skywalker</td>
      <td>188</td>
      <td>84</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/4/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Wilhuff Tarkin</td>
      <td>180</td>
      <td>unknown</td>
      <td>auburn, grey</td>
      <td>fair</td>
      <td>blue</td>
      <td>64BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/21/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>polluted</td>
      <td>1 standard</td>
      <td>cityscape</td>
      <td>unknown</td>
      <td>22000000000</td>
      <td>[https://swapi.dev/api/people/12/]</td>
      <td>[]</td>
      <td>2014-12-10T16:26:54.384000Z</td>
      <td>2014-12-20T20:58:18.454000Z</td>
      <td>https://swapi.dev/api/planets/21/</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Chewbacca</td>
      <td>228</td>
      <td>112</td>
      <td>brown</td>
      <td>unknown</td>
      <td>blue</td>
      <td>200BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/14/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>tropical</td>
      <td>1 standard</td>
      <td>jungle, forests, lakes, rivers</td>
      <td>60</td>
      <td>45000000</td>
      <td>[https://swapi.dev/api/people/13/, https://swa...</td>
      <td>[https://swapi.dev/api/films/6/]</td>
      <td>2014-12-10T13:32:00.124000Z</td>
      <td>2014-12-20T20:58:18.442000Z</td>
      <td>https://swapi.dev/api/planets/14/</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Han Solo</td>
      <td>180</td>
      <td>80</td>
      <td>brown</td>
      <td>fair</td>
      <td>brown</td>
      <td>29BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/22/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>plains, urban, hills, forests</td>
      <td>70</td>
      <td>3000000000</td>
      <td>[https://swapi.dev/api/people/14/, https://swa...</td>
      <td>[]</td>
      <td>2014-12-10T16:49:12.453000Z</td>
      <td>2014-12-20T20:58:18.456000Z</td>
      <td>https://swapi.dev/api/planets/22/</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Greedo</td>
      <td>173</td>
      <td>74</td>
      <td>n/a</td>
      <td>green</td>
      <td>black</td>
      <td>44BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/23/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>hot</td>
      <td>1 standard</td>
      <td>jungles, oceans, urban, swamps</td>
      <td>60</td>
      <td>1300000000</td>
      <td>[https://swapi.dev/api/people/15/]</td>
      <td>[]</td>
      <td>2014-12-10T17:03:28.110000Z</td>
      <td>2014-12-20T20:58:18.458000Z</td>
      <td>https://swapi.dev/api/planets/23/</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Jabba Desilijic Tiure</td>
      <td>175</td>
      <td>1,358</td>
      <td>n/a</td>
      <td>green-tan, brown</td>
      <td>orange</td>
      <td>600BBY</td>
      <td>hermaphrodite</td>
      <td>https://swapi.dev/api/planets/24/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>urban, oceans, swamps, bogs</td>
      <td>unknown</td>
      <td>7000000000</td>
      <td>[https://swapi.dev/api/people/16/]</td>
      <td>[]</td>
      <td>2014-12-10T17:11:29.452000Z</td>
      <td>2014-12-20T20:58:18.460000Z</td>
      <td>https://swapi.dev/api/planets/24/</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Wedge Antilles</td>
      <td>170</td>
      <td>77</td>
      <td>brown</td>
      <td>fair</td>
      <td>hazel</td>
      <td>21BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/22/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>plains, urban, hills, forests</td>
      <td>70</td>
      <td>3000000000</td>
      <td>[https://swapi.dev/api/people/14/, https://swa...</td>
      <td>[]</td>
      <td>2014-12-10T16:49:12.453000Z</td>
      <td>2014-12-20T20:58:18.456000Z</td>
      <td>https://swapi.dev/api/planets/22/</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Jek Tono Porkins</td>
      <td>180</td>
      <td>110</td>
      <td>brown</td>
      <td>fair</td>
      <td>blue</td>
      <td>unknown</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/26/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>temperate</td>
      <td>unknown</td>
      <td>rocky islands, oceans</td>
      <td>98</td>
      <td>62000000</td>
      <td>[https://swapi.dev/api/people/19/]</td>
      <td>[]</td>
      <td>2014-12-12T11:16:55.078000Z</td>
      <td>2014-12-20T20:58:18.463000Z</td>
      <td>https://swapi.dev/api/planets/26/</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Yoda</td>
      <td>66</td>
      <td>17</td>
      <td>white</td>
      <td>green</td>
      <td>brown</td>
      <td>896BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/28/</td>
      <td>[https://swapi.dev/api/films/2/, https://swapi...</td>
      <td>...</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>[https://swapi.dev/api/people/20/, https://swa...</td>
      <td>[]</td>
      <td>2014-12-15T12:25:59.569000Z</td>
      <td>2014-12-20T20:58:18.466000Z</td>
      <td>https://swapi.dev/api/planets/28/</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Palpatine</td>
      <td>170</td>
      <td>75</td>
      <td>grey</td>
      <td>pale</td>
      <td>yellow</td>
      <td>82BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>[https://swapi.dev/api/films/2/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>[https://swapi.dev/api/films/3/, https://swapi...</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
    </tr>
  </tbody>
</table>
<p>20 rows × 46 columns</p>
</div>



## 4.- Expansión de filas


```python
df_people = df_20_people.explode("films")
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
      <th>name_x</th>
      <th>height</th>
      <th>mass</th>
      <th>hair_color</th>
      <th>skin_color</th>
      <th>eye_color</th>
      <th>birth_year</th>
      <th>gender</th>
      <th>homeworld</th>
      <th>films_x</th>
      <th>...</th>
      <th>climate_y</th>
      <th>gravity_y</th>
      <th>terrain_y</th>
      <th>surface_water_y</th>
      <th>population_y</th>
      <th>residents_y</th>
      <th>films</th>
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
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grasslands, mountains</td>
      <td>40</td>
      <td>2000000000</td>
      <td>[https://swapi.dev/api/people/5/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-10T11:35:48.479000Z</td>
      <td>2014-12-20T20:58:18.420000Z</td>
      <td>https://swapi.dev/api/planets/2/</td>
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
      <td>temperate</td>
      <td>1 standard</td>
      <td>grasslands, mountains</td>
      <td>40</td>
      <td>2000000000</td>
      <td>[https://swapi.dev/api/people/5/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-10T11:35:48.479000Z</td>
      <td>2014-12-20T20:58:18.420000Z</td>
      <td>https://swapi.dev/api/planets/2/</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Owen Lars</td>
      <td>178</td>
      <td>120</td>
      <td>brown, grey</td>
      <td>light</td>
      <td>blue</td>
      <td>52BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Owen Lars</td>
      <td>178</td>
      <td>120</td>
      <td>brown, grey</td>
      <td>light</td>
      <td>blue</td>
      <td>52BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Owen Lars</td>
      <td>178</td>
      <td>120</td>
      <td>brown, grey</td>
      <td>light</td>
      <td>blue</td>
      <td>52BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Owen Lars</td>
      <td>178</td>
      <td>120</td>
      <td>brown, grey</td>
      <td>light</td>
      <td>blue</td>
      <td>52BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Owen Lars</td>
      <td>178</td>
      <td>120</td>
      <td>brown, grey</td>
      <td>light</td>
      <td>blue</td>
      <td>52BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Beru Whitesun lars</td>
      <td>165</td>
      <td>75</td>
      <td>brown</td>
      <td>light</td>
      <td>blue</td>
      <td>47BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Beru Whitesun lars</td>
      <td>165</td>
      <td>75</td>
      <td>brown</td>
      <td>light</td>
      <td>blue</td>
      <td>47BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Beru Whitesun lars</td>
      <td>165</td>
      <td>75</td>
      <td>brown</td>
      <td>light</td>
      <td>blue</td>
      <td>47BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Beru Whitesun lars</td>
      <td>165</td>
      <td>75</td>
      <td>brown</td>
      <td>light</td>
      <td>blue</td>
      <td>47BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Beru Whitesun lars</td>
      <td>165</td>
      <td>75</td>
      <td>brown</td>
      <td>light</td>
      <td>blue</td>
      <td>47BBY</td>
      <td>female</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>7</th>
      <td>R5-D4</td>
      <td>97</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, red</td>
      <td>red</td>
      <td>unknown</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>7</th>
      <td>R5-D4</td>
      <td>97</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, red</td>
      <td>red</td>
      <td>unknown</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>7</th>
      <td>R5-D4</td>
      <td>97</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, red</td>
      <td>red</td>
      <td>unknown</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>7</th>
      <td>R5-D4</td>
      <td>97</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, red</td>
      <td>red</td>
      <td>unknown</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>7</th>
      <td>R5-D4</td>
      <td>97</td>
      <td>32</td>
      <td>n/a</td>
      <td>white, red</td>
      <td>red</td>
      <td>unknown</td>
      <td>n/a</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Biggs Darklighter</td>
      <td>183</td>
      <td>84</td>
      <td>black</td>
      <td>light</td>
      <td>brown</td>
      <td>24BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Biggs Darklighter</td>
      <td>183</td>
      <td>84</td>
      <td>black</td>
      <td>light</td>
      <td>brown</td>
      <td>24BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Biggs Darklighter</td>
      <td>183</td>
      <td>84</td>
      <td>black</td>
      <td>light</td>
      <td>brown</td>
      <td>24BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Biggs Darklighter</td>
      <td>183</td>
      <td>84</td>
      <td>black</td>
      <td>light</td>
      <td>brown</td>
      <td>24BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Biggs Darklighter</td>
      <td>183</td>
      <td>84</td>
      <td>black</td>
      <td>light</td>
      <td>brown</td>
      <td>24BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Obi-Wan Kenobi</td>
      <td>182</td>
      <td>77</td>
      <td>auburn, white</td>
      <td>fair</td>
      <td>blue-gray</td>
      <td>57BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/20/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grass</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>[https://swapi.dev/api/people/10/]</td>
      <td>NaN</td>
      <td>2014-12-10T16:16:26.566000Z</td>
      <td>2014-12-20T20:58:18.452000Z</td>
      <td>https://swapi.dev/api/planets/20/</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Anakin Skywalker</td>
      <td>188</td>
      <td>84</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/4/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/1/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Anakin Skywalker</td>
      <td>188</td>
      <td>84</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/4/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Anakin Skywalker</td>
      <td>188</td>
      <td>84</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/4/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Anakin Skywalker</td>
      <td>188</td>
      <td>84</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/4/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Anakin Skywalker</td>
      <td>188</td>
      <td>84</td>
      <td>blond</td>
      <td>fair</td>
      <td>blue</td>
      <td>41.9BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/1/</td>
      <td>[https://swapi.dev/api/films/4/, https://swapi...</td>
      <td>...</td>
      <td>arid</td>
      <td>1 standard</td>
      <td>desert</td>
      <td>1</td>
      <td>200000</td>
      <td>[https://swapi.dev/api/people/1/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-09T13:50:49.641000Z</td>
      <td>2014-12-20T20:58:18.411000Z</td>
      <td>https://swapi.dev/api/planets/1/</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Wilhuff Tarkin</td>
      <td>180</td>
      <td>unknown</td>
      <td>auburn, grey</td>
      <td>fair</td>
      <td>blue</td>
      <td>64BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/21/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>polluted</td>
      <td>1 standard</td>
      <td>cityscape</td>
      <td>unknown</td>
      <td>22000000000</td>
      <td>[https://swapi.dev/api/people/12/]</td>
      <td>NaN</td>
      <td>2014-12-10T16:26:54.384000Z</td>
      <td>2014-12-20T20:58:18.454000Z</td>
      <td>https://swapi.dev/api/planets/21/</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Chewbacca</td>
      <td>228</td>
      <td>112</td>
      <td>brown</td>
      <td>unknown</td>
      <td>blue</td>
      <td>200BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/14/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>tropical</td>
      <td>1 standard</td>
      <td>jungle, forests, lakes, rivers</td>
      <td>60</td>
      <td>45000000</td>
      <td>[https://swapi.dev/api/people/13/, https://swa...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-10T13:32:00.124000Z</td>
      <td>2014-12-20T20:58:18.442000Z</td>
      <td>https://swapi.dev/api/planets/14/</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Han Solo</td>
      <td>180</td>
      <td>80</td>
      <td>brown</td>
      <td>fair</td>
      <td>brown</td>
      <td>29BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/22/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>plains, urban, hills, forests</td>
      <td>70</td>
      <td>3000000000</td>
      <td>[https://swapi.dev/api/people/14/, https://swa...</td>
      <td>NaN</td>
      <td>2014-12-10T16:49:12.453000Z</td>
      <td>2014-12-20T20:58:18.456000Z</td>
      <td>https://swapi.dev/api/planets/22/</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Greedo</td>
      <td>173</td>
      <td>74</td>
      <td>n/a</td>
      <td>green</td>
      <td>black</td>
      <td>44BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/23/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>hot</td>
      <td>1 standard</td>
      <td>jungles, oceans, urban, swamps</td>
      <td>60</td>
      <td>1300000000</td>
      <td>[https://swapi.dev/api/people/15/]</td>
      <td>NaN</td>
      <td>2014-12-10T17:03:28.110000Z</td>
      <td>2014-12-20T20:58:18.458000Z</td>
      <td>https://swapi.dev/api/planets/23/</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Jabba Desilijic Tiure</td>
      <td>175</td>
      <td>1,358</td>
      <td>n/a</td>
      <td>green-tan, brown</td>
      <td>orange</td>
      <td>600BBY</td>
      <td>hermaphrodite</td>
      <td>https://swapi.dev/api/planets/24/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>urban, oceans, swamps, bogs</td>
      <td>unknown</td>
      <td>7000000000</td>
      <td>[https://swapi.dev/api/people/16/]</td>
      <td>NaN</td>
      <td>2014-12-10T17:11:29.452000Z</td>
      <td>2014-12-20T20:58:18.460000Z</td>
      <td>https://swapi.dev/api/planets/24/</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Wedge Antilles</td>
      <td>170</td>
      <td>77</td>
      <td>brown</td>
      <td>fair</td>
      <td>hazel</td>
      <td>21BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/22/</td>
      <td>[https://swapi.dev/api/films/1/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>plains, urban, hills, forests</td>
      <td>70</td>
      <td>3000000000</td>
      <td>[https://swapi.dev/api/people/14/, https://swa...</td>
      <td>NaN</td>
      <td>2014-12-10T16:49:12.453000Z</td>
      <td>2014-12-20T20:58:18.456000Z</td>
      <td>https://swapi.dev/api/planets/22/</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Jek Tono Porkins</td>
      <td>180</td>
      <td>110</td>
      <td>brown</td>
      <td>fair</td>
      <td>blue</td>
      <td>unknown</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/26/</td>
      <td>[https://swapi.dev/api/films/1/]</td>
      <td>...</td>
      <td>temperate</td>
      <td>unknown</td>
      <td>rocky islands, oceans</td>
      <td>98</td>
      <td>62000000</td>
      <td>[https://swapi.dev/api/people/19/]</td>
      <td>NaN</td>
      <td>2014-12-12T11:16:55.078000Z</td>
      <td>2014-12-20T20:58:18.463000Z</td>
      <td>https://swapi.dev/api/planets/26/</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Yoda</td>
      <td>66</td>
      <td>17</td>
      <td>white</td>
      <td>green</td>
      <td>brown</td>
      <td>896BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/28/</td>
      <td>[https://swapi.dev/api/films/2/, https://swapi...</td>
      <td>...</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>unknown</td>
      <td>[https://swapi.dev/api/people/20/, https://swa...</td>
      <td>NaN</td>
      <td>2014-12-15T12:25:59.569000Z</td>
      <td>2014-12-20T20:58:18.466000Z</td>
      <td>https://swapi.dev/api/planets/28/</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Palpatine</td>
      <td>170</td>
      <td>75</td>
      <td>grey</td>
      <td>pale</td>
      <td>yellow</td>
      <td>82BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>[https://swapi.dev/api/films/2/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/3/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Palpatine</td>
      <td>170</td>
      <td>75</td>
      <td>grey</td>
      <td>pale</td>
      <td>yellow</td>
      <td>82BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>[https://swapi.dev/api/films/2/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/4/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Palpatine</td>
      <td>170</td>
      <td>75</td>
      <td>grey</td>
      <td>pale</td>
      <td>yellow</td>
      <td>82BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>[https://swapi.dev/api/films/2/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/5/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Palpatine</td>
      <td>170</td>
      <td>75</td>
      <td>grey</td>
      <td>pale</td>
      <td>yellow</td>
      <td>82BBY</td>
      <td>male</td>
      <td>https://swapi.dev/api/planets/8/</td>
      <td>[https://swapi.dev/api/films/2/, https://swapi...</td>
      <td>...</td>
      <td>temperate</td>
      <td>1 standard</td>
      <td>grassy hills, swamps, forests, mountains</td>
      <td>12</td>
      <td>4500000000</td>
      <td>[https://swapi.dev/api/people/3/, https://swap...</td>
      <td>https://swapi.dev/api/films/6/</td>
      <td>2014-12-10T11:52:31.066000Z</td>
      <td>2014-12-20T20:58:18.430000Z</td>
      <td>https://swapi.dev/api/planets/8/</td>
    </tr>
  </tbody>
</table>
<p>59 rows × 46 columns</p>
</div>



# PR0204: Estructuras de datos avanzadas: datos geoespaciales

Todos los scripts están en la misma carpeta.

### Tarea 1: Carga de datos

Script `load_locations.py`

```python
# Conexión a la BD
import redis, locations

r = redis.Redis(
    host = "redis",
    port = 6379,
    db = 0,
    decode_responses = True
)

print(r.ping())

# Carga de datos
data = locations.POIS

for poi in data:
    r.geoadd("poi:locations", (poi["lon"], poi["lat"], poi["id"]))
    r.hset("poi:info", poi["id"], poi["name"])

print("Datos cargados")
```

### Tarea 2: Búsqueda por radio

Script `find_by_radius.py`

```python
# Localización del usuario predefinida (Pueta del Sol)
user_location = {
    "lat": 40.41677,
    "lon": -3.70379,
}

import redis

r = redis.Redis(
    host = "redis",
    port = 6379,
    db = 0,
    decode_responses = True
)

nearest_pois = r.geosearch(
    "poi:locations", 
    longitude = user_location["lon"], 
    latitude = user_location["lat"],
    radius = 2000,
    unit="km"
)

for poi in nearest_pois:
    print(f"-> {r.hget('poi:info', poi)} ({poi})")
```

### Tarea 3: Búsqueda del más cercano

Script `find_nearest.py`

```python
# Localización del usuario predefinida (Pueta del Sol)
user_location = {
    "lat": 40.41677,
    "lon": -3.70379,
}

# Conexión a la BD
import redis, locations

r = redis.Redis(
    host = "redis",
    port = 6379,
    db = 0,
    decode_responses = True
)

print(r.ping())

nearest_poi = r.geosearch(
    "poi:locations", 
    longitude = user_location["lon"], 
    latitude = user_location["lat"],
    radius = 2000,
    unit = "km",
    count = 1,
    withdist = True
)

print(f"El POI más cercano es {r.hget('poi:info', nearest_poi[0][0])}, que está a {nearest_poi[0][1]} km.")
```

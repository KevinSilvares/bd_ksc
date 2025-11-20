## Trabajo con Python


```python
!pip install redis
```

    Requirement already satisfied: redis in /opt/conda/lib/python3.11/site-packages (6.4.0)



```python
import redis

r = redis.Redis(
    host = "redis",
    port = 6379,
    db = 0,
    decode_responses = True
    )

print(r.ping())
```

    True


#### 1. Inserta la clave `app:version` con el valor "1.0"


```python
r.set("app:version", 1.0)
```




    True



#### 2. Recupera y muestra el valor de `app:version`.


```python
r.get("app:version")
```




    '1.0'



#### 3. Modifica el valor de `app:version` a "1.1".


```python
r.set("app:version", 1.1)
r.get("app:version")
```




    '1.1'



#### 4. Crea la clave `contador:descargas` con valor 0.


```python
r.set("contador:descargas", 0)
r.get("contador:descargas")
```




    '0'



#### 5. Incrementa en 5 el valor de `contador:descargas`.


```python
r.incr("contador:descargas", 5)
r.get("contador:descargas")
```




    '5'



#### 6. Decrementa en 2 el valor de `contador:descargas`.


```python
r.decr("contador:descargas", 2)
r.get("contador:descargas")
```




    '3'



#### 7. Inserta la clave `app:estado` con el valor "activo".


```python
r.set("app:estado", "activo")
r.get("app:estado")
```




    'activo'



#### 8. Cambia el valor de `app:estado`con el valor "mantenimiento".


```python
r.set("app:estado", "mantenimiento")
r.get("app:estado")
```




    'mantenimiento'



#### 9. Inserta la clave `mensaje:bienvenida` con el texto "Hola alumno".


```python
r.set("mensaje:bienvenida", "Hola alumno")
r.get("mensaje:bienvenida")
```




    'Hola alumno'



#### 10. Establece un tiempo de expiración de 30 segundos para la clave `app:estado`.


```python
r.expire("app:estado", 30)
```




    True



#### 11. Verifica si la clave `app:estado` todavía existe después de unos segundos.


```python
# Justo después de poner el tiempo.
r.exists("app:estado")
```




    1




```python
# Una vez pasado el tiempo.
r.exists("app:estado")
```




    0



#### 12. Elimina la clave `app:version` y muestra un mensaje confirmando su eliminiación.


```python
if r.delete("app:version") == 1:
    print("La clave app:version ha sido eliminada.")
else:
    print("Ha ocurrido un error.")
```

    La clave app:version ha sido eliminada.


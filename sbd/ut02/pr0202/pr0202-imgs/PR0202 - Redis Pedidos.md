### 1.- Crea un script en Python que use la librería `redis`.


```python
import redis

pedidos_clave = "pedidos"

r = redis.Redis(
    host = "redis",
    port = 6379,
    db = 0,
    decode_responses = True
)

print(r.ping())
```

    True


### 2.- Define una función `agregar_pedido(cliente, producto)`


```python
import json
```


```python
def agregar_pedido(cliente, producto, urgente = False):    
    num_id = f"pedido_{r.llen('pedidos') + 1}" if r.exists("pedidos") else "pedido_1"
    
    pedido_json = {
        "id": num_id,
        "cliente": cliente,
        "producto": producto,
        "cantidad": 1,
        "urgente": urgente,
    }

    pedido = json.dumps(pedido_json)

    if urgente:
        r.lpush(pedidos_clave, pedido)
    else:
        r.rpush(pedidos_clave, pedido)
```

### 3.- Define una función `procesar_pedido()` que extraiga un pedido de la lista de `pedidos`.


```python
def procesar_pedido():
    pedido = json.loads(r.lpop("pedidos"))
    print(f"Procesando pedido: {pedido}")
```

### 4.- Inserta 5 pedidos iniciales llamando a la función `agregar_pedido()`.


```python
agregar_pedido("Carlos Pérez", "Portátil")
agregar_pedido("Juan López", "Auriculares")
agregar_pedido("María Martínez", "Altavoces")
agregar_pedido("Lucía González", "Móvil")
agregar_pedido("Luis García", "Ratón")
```

![{3EFB5107-0253-4CE9-9E5B-25391015EB88}.png](617389da-03fe-41c3-aef5-96d66a63bc4c.png)

### 5.- Muesta los pedidos actuales con 'LRANGE`.


```python
print(r.lrange(pedidos_clave, 0, -1))
```

    ['{"id": "pedido_1", "cliente": "Carlos P\\u00e9rez", "producto": "Port\\u00e1til", "cantidad": 1, "urgente": false}', '{"id": "pedido_2", "cliente": "Juan L\\u00f3pez", "producto": "Auriculares", "cantidad": 1, "urgente": false}', '{"id": "pedido_3", "cliente": "Mar\\u00eda Mart\\u00ednez", "producto": "Altavoces", "cantidad": 1, "urgente": false}', '{"id": "pedido_4", "cliente": "Luc\\u00eda Gonz\\u00e1lez", "producto": "M\\u00f3vil", "cantidad": 1, "urgente": false}', '{"id": "pedido_5", "cliente": "Luis Garc\\u00eda", "producto": "Rat\\u00f3n", "cantidad": 1, "urgente": false}']


### 6.- Inserta 2 pedidos adicionales.


```python
agregar_pedido("Víctor García", "Teclado")
agregar_pedido("Marcos Viñuela", "Torre de Ordenador")
```

![{3498D171-CF96-45AF-B9DE-8D101E736078}.png](046f105c-0a46-4b7f-8e14-bbca045096b8.png)

### 7.- Procesa todos los pedidos.


```python
for i in range(r.llen(pedidos_clave)):
    procesar_pedido()
```

    Procesando pedido: {'id': 'pedido_1', 'cliente': 'Carlos Pérez', 'producto': 'Portátil', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_2', 'cliente': 'Juan López', 'producto': 'Auriculares', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_3', 'cliente': 'María Martínez', 'producto': 'Altavoces', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_4', 'cliente': 'Lucía González', 'producto': 'Móvil', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_5', 'cliente': 'Luis García', 'producto': 'Ratón', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_6', 'cliente': 'Víctor García', 'producto': 'Teclado', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_7', 'cliente': 'Marcos Viñuela', 'producto': 'Torre de Ordenador', 'cantidad': 1, 'urgente': False}


Después de procesar
![{8F358938-9423-494A-A706-424A5DFA7363}.png](ffb44680-809b-4e33-a5c9-489a66733ed3.png)

### 8.- Inserta un pedido urgente


```python
agregar_pedido("María Pérez", "Alfombrilla", True)
```

![{3F615C7C-6170-4344-A5B6-8C021F3045C2}.png](fd6a7ca7-bfa1-4ad1-8e5a-db5eadd7b7b1.png)


```python
procesar_pedido()
```

    Procesando pedido: {'id': 'pedido_1', 'cliente': 'María Pérez', 'producto': 'Alfombrilla', 'cantidad': 1, 'urgente': True}


![{06A1DE46-185D-4004-8DD5-082619FD3912}.png](c8e43d53-e9da-4432-8140-6005762176c3.png)

Ejecutando el paso 4 antes.

![{2F886E6C-D1CD-43E8-A45B-7CB1F7A5F2F8}.png](e6f9fe4d-5154-4188-a9b8-bfd74aa5b84c.png)

Agregamos el urgente.

![{4D107CD3-808D-44BF-9D19-9FDFEDE97CE0}.png](938decdc-5921-40ba-b9de-464d80740dcd.png)

Procesamiento


```python
for i in range(r.llen(pedidos_clave)):
    procesar_pedido()
```

    Procesando pedido: {'id': 'pedido_6', 'cliente': 'María Pérez', 'producto': 'Alfombrilla', 'cantidad': 1, 'urgente': True}
    Procesando pedido: {'id': 'pedido_1', 'cliente': 'Carlos Pérez', 'producto': 'Portátil', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_2', 'cliente': 'Juan López', 'producto': 'Auriculares', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_3', 'cliente': 'María Martínez', 'producto': 'Altavoces', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_4', 'cliente': 'Lucía González', 'producto': 'Móvil', 'cantidad': 1, 'urgente': False}
    Procesando pedido: {'id': 'pedido_5', 'cliente': 'Luis García', 'producto': 'Ratón', 'cantidad': 1, 'urgente': False}


![{3EEF6316-72AD-4F94-BA91-5E76AC88A60D}.png](e41a2efa-dc94-47ce-8a83-6a9348271100.png)

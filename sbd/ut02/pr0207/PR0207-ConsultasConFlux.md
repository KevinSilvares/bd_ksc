# PR0207: Consultas con Flux


```python
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client import Point
from urllib3.exceptions import NewConnectionError

INFLUX_URL = "http://influxdb2:8086"
INFLUX_TOKEN = "MyInitialAdminToken0=="
INFLUX_BUCKET = "crypto_raw"
INFLUX_ORG = "docs"
```


```python
def connect_influxdb():
    print("--- Iniciando conexión a InfluxDB ---")
    
    client = None
    try:
        # 1. Inicializar el cliente
        client = influxdb_client.InfluxDBClient(
            url = INFLUX_URL,
            token = INFLUX_TOKEN,
            org = INFLUX_ORG
        )
    
        # 2. Verificar la conexión con el servidor
        print(f"Verificando estado de salud de InfluxDB en {INFLUX_URL}...")
        health = client.health()
        
        if health.status == "pass":
            print("[INFO] ¡Conexión exitosa!")
            print(f"[INFO]  Versión del servidor: {health.version}")

            query_api = client.query_api()
            return client, query_api
        else:
            print(f"[ERROR] Conexión fallida. Estado: {health.status}")
            print(f"[INFO] Mensaje: {health.message}")
    
    except (InfluxDBError, NewConnectionError) as e:
        print("[ERROR] Error al conectar con InfluxDB:")
        print(f"   Detalle: {e}")
        
    finally:
        # 3. Es buena práctica cerrar siempre el cliente
        if client:
            client.close()
            print("--- Conexión cerrada ---")
```

## PARTE I: Consultas de filtrado y estructura

### Tarea 1.1: Precio de cierre de Bitcoin


```python
def bitcoin(c, q_api):
    query = f"""
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: 2020-12-01T00:00:00Z, stop: 2021-01-01T00:00:00Z)
            |> filter(fn: (r) => r.symbol == "BTC")
            |> filter(fn: (r) => r._field == "close")
        """

    result = q_api.query(org = INFLUX_ORG, query = query)
    for table in result:
        for record in table:
            print(record)
```


```python
client, query_api = connect_influxdb()
bitcoin(client, query_api)
```

### Tarea 1.2: Volumen Total del Ethereum (ETHUSDT)


```python
def total_volume_eth(c, q_api):
    # El enunciado pone de enero a junio. La consulta filtra de enero a junio sin incluirlo.
    query = f"""
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: 2021-01-01T00:00:00Z, stop: 2021-06-01T00:00:00Z)
            |> filter(fn: (r) => r.symbol == "ETH")
            |> filter(fn: (r) => r._field == "volume")
    """

    result = q_api.query(org = INFLUX_ORG, query = query)
    volume = []
    for table in result:
        for record in table:
            volume.append(record["_value"])

    print(f"Volumen total: {sum(volume)}")
```


```python
client, query_api = connect_influxdb()
total_volume_eth(client, query_api)
```

    --- Iniciando conexión a InfluxDB ---
    Verificando estado de salud de InfluxDB en http://influxdb2:8086...
    [INFO] ¡Conexión exitosa!
    [INFO]  Versión del servidor: v2.7.12
    --- Conexión cerrada ---
    Volumen total: 5425858492404.717


## PARTE II: Agregación temporal

### Tarea 2.1: Precio promedio mensual


```python
def historic_bitcoin_close(c, q_api):
    query = f"""
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -10y)
            |> filter(fn: (r) => r.symbol == "BTC")
            |> filter(fn: (r) => r._field == "close")
            |> aggregateWindow(every: 1mo, fn: mean)
    """

    result = q_api.query(org = INFLUX_ORG, query = query)
    for table in result:
        for record in table:
            print(record)
```


```python
client, query_api = connect_influxdb()
historic_bitcoin_close(client, query_api)
```

    --- Iniciando conexión a InfluxDB ---
    Verificando estado de salud de InfluxDB en http://influxdb2:8086...
    [INFO] ¡Conexión exitosa!
    [INFO]  Versión del servidor: v2.7.12
    --- Conexión cerrada ---
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 441.27693367004395, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 410.84448537518904, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 404.4082736311288, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 416.5257735713836, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 434.3393981933594, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 461.9544146137853, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 642.8690612792968, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 661.3561027280746, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 579.585197202621, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 605.8486328125, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 643.5509348223286, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2016, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 726.3491007486979, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 828.0603558940272, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 914.9161593529486, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 1062.533671787807, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 1129.365228468372, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 1206.641007486979, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 1895.383529170867, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 2636.204345703125, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 2519.4183861517135, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 3880.9899981098793, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 4064.8363118489583, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 5360.071604082661, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2017, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 7813.132975260417, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 15294.270980342742, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 13085.558089717742, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9472.001150948661, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9040.557097404233, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 8033.596630859375, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 8450.997731854839, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 6793.507666015625, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 7146.349989919355, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 6700.130000000002, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 6610.675000000001, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 6485.118709677419, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2018, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 5404.250163745335, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 3717.4883192654843, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 3701.5549733116122, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 3711.907275630714, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 3976.0690934074196, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 5178.469425008667, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 7309.694113368711, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9415.900143546, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 10669.33622277516, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 10643.24839313613, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9814.067782100668, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 8411.929149071937, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 8373.572452042665, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 7284.0130458951635, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 8389.270450449678, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9630.722210922067, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 6871.016110927743, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 7224.477345241333, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9263.151880502257, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9489.227163164333, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 9589.899754957421, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 11652.394214906453, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 10660.276814935667, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 11886.978148203545, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2020, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 16645.757397035995, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 21983.13691412839, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 34761.6498821042, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 46306.798799221775, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 54998.00857016419, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 57206.72022674067, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 46443.28605283192, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 35845.15485565401, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 34234.44838624, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2021, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2022, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2023, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2024, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 2, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 3, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 4, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 5, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 6, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 7, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 9, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 10, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 11, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 12, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, '_start': datetime.datetime(2015, 12, 16, 22, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2025, 12, 16, 10, 18, 24, 533995, tzinfo=datetime.timezone.utc), '_value': None, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Bitcoin', 'symbol': 'BTC'}


### Tarea 2.2: Rango de volatilidad


```python
def stellar_min_max(c, q_api):
    query = f"""
        data = from(bucket: "{INFLUX_BUCKET}")
            |> range(start: 2019-01-01T00:00:00Z, stop: 2019-12-31T23:59:59Z)
            |> filter(fn: (r) => r.symbol == "XLM")
            |> filter(fn: (r) => r._field == "close")

            data
                |> aggregateWindow(every: 1w, fn: max)
                |> yield(name: "max")
            
            data
                |> aggregateWindow(every: 1w, fn: min)
                |> yield(name: "min")
    """

    result = q_api.query(org = INFLUX_ORG, query = query)
    for table in result:
        for record in table:
            print(record)
```


```python
client, query_api = connect_influxdb()
stellar_min_max(client, query_api)
```

    --- Iniciando conexión a InfluxDB ---
    Verificando estado de salud de InfluxDB en http://influxdb2:8086...
    [INFO] ¡Conexión exitosa!
    [INFO]  Versión del servidor: v2.7.12
    --- Conexión cerrada ---
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.119331410154, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.123774386729, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.109878610051, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.108460938657, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102210392352, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0835802499476, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.081224003372, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0917350058181, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0942568445555, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0872353323243, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.108198619481, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.115914392752, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.108692806617, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.121900837603, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.131995967869, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.117505252017, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.117362975895, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 2, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.101351137089, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 9, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102295013854, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 16, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.137001655066, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 23, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.141485197931, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 30, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.138959876059, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 6, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.137622959913, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 13, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.127541536282, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 20, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.131035168284, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 27, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.129050324633, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.114503902451, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.105053888576, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0979634554654, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0951105058824, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0879653185781, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 8, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0830260889325, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 15, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.077841261029, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 22, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0717945667003, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 29, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0716762386253, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.063233045025, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0608816630268, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0831183072597, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0813871907299, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0614401007616, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0633552899625, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.064924881188, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0645472454791, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0661851181536, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.082164007855, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0798086163683, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.074740405351, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0616827581745, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0596409680538, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0561321294528, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0529900639054, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0472958798315, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_value': 0.0462155943798, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.11593003965, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.113824645405, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.103608750666, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102576372742, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0839227197999, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0743873347098, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0746880850898, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.076635145311, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0842337176392, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0835385127758, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0855406472047, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.107271925309, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102469191942, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.107359387845, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.11878829353, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.113628616719, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.103259281028, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 2, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0964745129392, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 9, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0936971600069, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 16, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0902320403193, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 23, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.124257250797, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 30, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.125166646196, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 6, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.121283780398, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 13, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.119915400277, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 20, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.124301592251, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 27, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.12150678527, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.103390157874, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0950565703023, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0783180471619, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.084467858308, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.083512564551, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 8, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0782121757967, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 15, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0691830893629, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 22, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0676973150428, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 29, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0661375592649, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0621784173174, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0583726083727, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0569399656847, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0545038067121, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0581272753922, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0588752275909, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0596294085884, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0599839569322, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0606116062591, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0652148662313, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.071887807681, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0655019886487, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0568813691786, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0554190238714, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0526917948915, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0440530520227, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0434406551581, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_value': 0.0451006564413, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}


## PARTE III: Manipulación y Joins

### Tarea 3.1: Cálculo de variación porcentual diario (Map)


```python
def diff_usdt(c, q_api):
    query = f"""
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: 2016-01-01T00:00:00Z, stop: 2018-12-31T23:59:59Z)
        |> filter(fn: (r) => r.symbol == "USDT")
        |> filter(fn: (r) => r._field == "close")

        |> duplicate(column: "_value", as: "current_price")
        |> difference()
        
        |> map(fn: (r) => ({{r with 
            _value: (r._value / (r.current_price - r.value)) * 100.0
        }}))
    """

    result = q_api.query(org = INFLUX_ORG, query = query)
    for table in result:
        for record in table:
            print(record)
```


```python
client, query_api = connect_influxdb()
stellar_min_max(client, query_api)
```

    --- Iniciando conexión a InfluxDB ---
    Verificando estado de salud de InfluxDB en http://influxdb2:8086...
    [INFO] ¡Conexión exitosa!
    [INFO]  Versión del servidor: v2.7.12
    --- Conexión cerrada ---
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.11593003965, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.113824645405, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.103608750666, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102576372742, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0839227197999, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0743873347098, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0746880850898, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.076635145311, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0842337176392, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0835385127758, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0855406472047, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.107271925309, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102469191942, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.107359387845, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.11878829353, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.113628616719, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.103259281028, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 2, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0964745129392, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 9, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0936971600069, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 16, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0902320403193, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 23, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.124257250797, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 30, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.125166646196, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 6, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.121283780398, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 13, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.119915400277, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 20, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.124301592251, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 27, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.12150678527, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.103390157874, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0950565703023, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0783180471619, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.084467858308, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.083512564551, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 8, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0782121757967, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 15, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0691830893629, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 22, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0676973150428, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 29, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0661375592649, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0621784173174, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0583726083727, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0569399656847, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0545038067121, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0581272753922, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0588752275909, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0596294085884, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0599839569322, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0606116062591, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0652148662313, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.071887807681, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0655019886487, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0568813691786, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0554190238714, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0526917948915, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0440530520227, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0434406551581, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 0, {'result': 'min', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_value': 0.0451006564413, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.119331410154, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.123774386729, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.109878610051, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.108460938657, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 1, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102210392352, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0835802499476, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.081224003372, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0917350058181, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 2, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0942568445555, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0872353323243, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.108198619481, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.115914392752, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 3, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.108692806617, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.121900837603, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.131995967869, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.117505252017, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 4, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.117362975895, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 2, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.101351137089, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 9, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.102295013854, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 16, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.137001655066, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 23, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.141485197931, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 5, 30, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.138959876059, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 6, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.137622959913, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 13, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.127541536282, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 20, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.131035168284, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 6, 27, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.129050324633, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 4, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.114503902451, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 11, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.105053888576, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 18, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0979634554654, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 7, 25, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0951105058824, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 1, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0879653185781, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 8, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0830260889325, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 15, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.077841261029, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 22, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0717945667003, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 8, 29, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0716762386253, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.063233045025, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0608816630268, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0831183072597, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 9, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0813871907299, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 3, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0614401007616, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 10, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0633552899625, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 17, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.064924881188, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 24, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0645472454791, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 10, 31, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0661851181536, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 7, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.082164007855, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 14, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0798086163683, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 21, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.074740405351, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 11, 28, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0616827581745, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 5, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0596409680538, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 12, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0561321294528, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 19, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0529900639054, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 26, 0, 0, tzinfo=datetime.timezone.utc), '_value': 0.0472958798315, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}
    FluxRecord() table: 1, {'result': 'max', 'table': 0, '_start': datetime.datetime(2019, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), '_stop': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_time': datetime.datetime(2019, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc), '_value': 0.0462155943798, '_field': 'close', '_measurement': 'daily_quote', 'name': 'Stellar', 'symbol': 'XLM'}


### Tarea 3.2: Comparación de precios de cierre (Join)


```python
def btc_eth_combined(c, q_api):
    query = f"""
        btc = from(bucket: "{INFLUX_BUCKET}")
        |> range(start: 2020-01-01T00:00:00Z, stop: 2020-12-31T23:59:59Z)
        |> filter(fn: (r) => r.symbol == "BTC")
        |> filter(fn: (r) => r._field == "close")

        eth = from(bucket: "{INFLUX_BUCKET}")
        |> range(start: 2020-01-01T00:00:00Z, stop: 2020-12-31T23:59:59Z)
        |> filter(fn: (r) => r.symbol == "ETH")
        |> filter(fn: (r) => r._field == "close")

        join(tables: {{btc_data: btc, eth_data: eth}}, on: ["_time"])
            |> map(fn: (r) => ({{
                ratio: r._value_btc_data / r._value_eth_data
            }}))
    """
    # Las columnas se renombran al hacer el join
    
    result = q_api.query(org = INFLUX_ORG, query = query)
    for table in result:
        for record in table:
            print(record)
```


```python
c, q_api = connect_influxdb()
btc_eth_combined(c, q_api)
```

    --- Iniciando conexión a InfluxDB ---
    Verificando estado de salud de InfluxDB en http://influxdb2:8086...
    [INFO] ¡Conexión exitosa!
    [INFO]  Versión del servidor: v2.7.12
    --- Conexión cerrada ---
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 55.04635975084901}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 54.826622724946034}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 54.74241960078684}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 54.865559059396446}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 54.38430160917732}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 53.83919200734419}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 56.87240382056238}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 57.199274294479224}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 56.692452639384605}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 56.72644932841569}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 56.23521762945415}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 56.16146722408875}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 56.4680510924508}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 53.19360881110391}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 52.98065318034378}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 53.06729189935334}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 52.28387326158819}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 50.99520806008978}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 52.142620649024536}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.80479029097138}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.5382495901254}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.581563816992265}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.596332459511295}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.79621596931114}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.882710471087485}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.14813266143075}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 52.12527211997642}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 53.06216084612973}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 53.222573658948335}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.486106799855}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.90120043331226}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 51.13885510514019}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 49.54133843374127}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.94803146367804}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.51219943508927}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.07150159451453}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.82200432993593}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.98202660201977}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 44.209156351392934}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 44.25906487820941}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 44.096691342471146}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.28252848617256}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.906617100751845}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.09924583350441}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.282479939699876}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.356844628170535}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.22483973997492}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.37940097500106}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.97159555842996}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.085155244799004}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.24945223294236}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.46995052300462}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.83573527994248}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.25338651133517}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.38603863102596}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.695891897145245}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.08415376931937}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.74029686734207}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.24499987165157}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.11560974406965}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.10321318448474}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.46848550827005}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.14736831997639}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.995745624833894}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.59887691738972}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.46036072240639}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.459902088992465}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.40138811691255}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.228619167601494}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.3975087810875}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.598808804097715}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 44.244905741539256}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.7690045429129}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 42.174470234402655}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.06468745408474}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.33646998045531}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.861883991157754}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.61420144358381}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.32555888079858}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.69964111713715}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.56773594004339}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.27700726322817}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.55939583586004}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.53512284928312}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 49.05480616124777}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.54267816749151}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.304447013411924}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.65524777136764}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.15613321808601}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.37940094146445}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.19577023506215}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 48.71012698831635}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.83260837465724}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.387749444852446}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.2907066355906}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.30956453500892}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 42.99372170555325}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.46656611507364}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 42.48160796637747}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 42.75049152201612}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.33935515976416}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.352644087088166}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.260437473926714}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.79995806561231}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.41741339579971}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.331231829302375}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.33894289720744}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.34376168150795}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.82889795068277}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.586082872935464}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.94238088201961}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.831047030264465}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.97713062282018}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.154450744424324}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.9018339258385}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.71787020086474}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.921362927351005}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.5264893116756}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.34704221646001}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.563717628816185}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.70745873600251}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.38177475225838}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.74424784825307}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 42.18145994374276}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 42.81348360950389}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.54054457929895}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.42268774901983}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.877133167374495}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.21152806517064}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.33975014734609}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.42869080606648}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.26789813708987}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.50764056897545}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.53765200426907}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.961392459211716}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 47.68464607095532}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.72687195881886}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 46.682758849959924}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.34004107571151}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.57970149547075}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.326649792541026}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 45.435252168079224}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 44.32404892308358}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 44.128099758257456}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.43703491469731}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.38079876512339}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.75904892231059}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.95703917903041}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 43.33029660345318}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 42.77384875826417}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.027194487528575}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.96127377467478}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.16440195308232}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.17301176024715}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.54764721767049}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.096475231475424}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.069036486427436}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.90256101823357}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.80487627700768}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.67152575201674}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.99690517385707}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.8880425840101}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.23165258080163}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.92048352916103}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.66063887551918}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.094825673372625}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.10271442441696}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.688422677133204}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.68285354581442}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.55059593498059}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.89147067551519}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.703831701726536}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.62901003028423}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.78308076049767}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.44283521041944}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.50253675123972}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.7726221149447}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.89635490328679}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.56960728870966}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.57553620301196}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.276341871934505}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.37732146316808}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.92985574736459}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.77210250130795}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 40.31865795503741}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.866957724271266}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.85662646197479}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.82019800409667}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.70022820205849}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.22245306595681}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.17842913494685}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.503676315060616}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.5885604117048}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.31179491465059}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.5786184403048}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.47948012682995}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.556754383743986}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.08660053481254}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.314649352738186}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.894563882183284}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.51697048688105}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.806302933151585}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.26223452519334}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.32991192242055}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.879701410322824}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.15603996661401}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.826667689261303}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.98892839964681}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.18473343417712}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.46257102852728}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.88619149341402}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.20878157547391}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.768959825627846}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.528560070881614}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.82049495093063}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.113355662296776}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.74223526516692}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.251240519006036}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.825083262425988}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.569380089662037}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.833559468059757}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.852029459828596}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.003749145399652}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.99738061834584}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.627157859573966}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 27.48539535096936}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 26.906558642786717}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 27.38101690909681}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 27.41625441957758}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.52970963512354}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.30328466693334}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.928243974638193}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.52362278306583}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.79106666953896}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.511845579053713}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.804062244440036}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.849106847917316}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.599229710071455}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.726702471152855}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.59339084482479}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.15695476857921}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.77281204190868}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 27.338056100906012}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 26.847539141033916}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 25.092611798450136}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 25.93859781965723}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 26.56479751929881}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 27.075476518185777}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.333367602062946}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.092952761794994}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.402730550627492}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.010228872090302}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.17133461922526}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.15290777092603}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 27.75830566876725}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 26.969592277765503}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.2401609950814}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.310942509909324}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.5937236092131}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.0014656479094}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.14511304618205}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.474493896282556}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 28.7757953374707}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.47901354579077}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.61054973428604}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.59031519601225}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.908021920795985}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.7997545035899}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.36123203485708}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.24214838770099}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.145799793369786}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.154492519149205}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.144317154160014}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.962091694582}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.065894884778086}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.54531024788006}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.44345320068334}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.261536678354936}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.493383077685422}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.11476779196222}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.213277847011735}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.119551987337957}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.264621978950338}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.451073861510228}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.34632340310645}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.80250476550749}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 29.974229603394562}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.118544510324487}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.455949121996788}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.915416725495795}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.79278472681975}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.362093636698756}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.905334651023878}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.28161329647929}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.69764723740341}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.33576023446287}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.55829716369672}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.780386670497325}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.079282473658786}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.19531770988242}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.79781760143842}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.14707075975717}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.7474447225843}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.386141144200906}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.64754067675337}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.65832240035471}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.365395496418884}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.991286450327614}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.14606086454366}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.62636417730987}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.23184569738127}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.04477145972242}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.129431619449015}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.51956517629433}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.003992983705885}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.91507221796654}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.30619923052275}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.38031991236414}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 34.919361964109605}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.65023614838041}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.34408827963405}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.73370541675121}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.13158946334317}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.77765280625633}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.53067701607403}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.92663635149677}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.91713445126989}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 30.18160901079035}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.640231439866305}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.82383053207436}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.058181903278424}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.060116740957504}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.91793763947592}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.571392682057407}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.920100394181254}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.01468407349635}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.08994066173358}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 31.53092659483054}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.84381795340753}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.1058940974159}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.139611140031896}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.42687500936774}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.02132000845137}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.35325402544165}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.63479313950263}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.08719553886098}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.07199742656653}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.463246482190094}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.8434779383777}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 32.946282266091316}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 33.49765192938446}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.47404317530312}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 35.33527660612828}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.20492497603539}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 36.781500675791996}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.39326521704113}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.462189779535144}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.81628177338486}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.809141283597505}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 39.37479070829904}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 41.57840157158582}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.48617686382304}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.08229135326082}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 37.4048995459348}
    FluxRecord() table: 0, {'result': '_result', 'table': 0, 'ratio': 38.37177412544385}


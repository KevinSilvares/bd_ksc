# PR0504B - Limpieza de datos sobre dataset de lugares famosos

### Conexiones e importaciones


```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType
from pyspark.sql.functions import col, lit
import pyspark.sql.functions as f
```


```python
def connect_spark():
    try:
        spark = (SparkSession.builder
             .appName("Prueba")
             .master("spark://spark-master:7077")
             .getOrCreate()
            )
    
        print("SparkSession inciada correctamente.")
        return spark
    except Exception as e:
        print("Error en la conexión.")
        print(e)
```

## Dataset 3: Datos de turismo de Castilla y León


```python
def load_cyl_turistic_places(spark):
    schema = StructType([
        StructField("establecimiento", StringType(), False),
        StructField("n_registro", StringType(), False),
        StructField("codigo", StringType(), True),
        StructField("tipo", StringType(), False),
        StructField("categoria", StringType(), True),
        StructField("especialidades", StringType(), True),
        StructField("clase", StringType(), True),
        StructField("nombre", StringType(), False),
        StructField("direccion", StringType(), False),
        StructField("c_postal", IntegerType(), False),
        StructField("provincia", StringType(), False),
        StructField("municipio", StringType(), False),
        StructField("localidad", StringType(), False),
        StructField("nucleo", StringType(), True),
        StructField("telefono_1", IntegerType(), True),
        StructField("telefono_2", IntegerType(), True),
        StructField("telefono_3", IntegerType(), True),
        StructField("email", StringType(), True),
        StructField("web", StringType(), True),
        StructField("q_calidad", StringType(), True),
        StructField("posada_real", StringType(), True),
        StructField("plazas", IntegerType(), True),
        StructField("gps_longitud", DoubleType(), True),
        StructField("gps_latitud", DoubleType(), True),
        StructField("accesible_a_personas_con_discapacidad", StringType(), True),
        StructField("column_27", StringType(), True), # Dudo que tenga nada
        StructField("posicion", StringType(), True),
    ])

    df = (spark.read
            .format("csv")
            .schema(schema)
            .option("header", "true")
            .option("delimiter", ";")
            .load("registro-de-turismo-de-castilla-y-leon.csv")
         )
    return df
```


```python
spark = connect_spark()
df = load_cyl_turistic_places(spark)
```

    SparkSession inciada correctamente.


### 1.- Identificación y categorización


```python
df_cyl = (df
            .withColumn("establecimiento", f.trim(f.initcap(col("establecimiento"))))
            .withColumn("n_registro", f.coalesce(f.trim(col("n_registro"))))
            .withColumn("tipo", f.trim(f.split(col("tipo"), "-")[0]))
            .withColumn("categoria", f.regexp_replace(col("categoria"), "Llaves", f.concat(
                f.substring(
                    f.split(col("categoria"), "-")[1],
                        0, 1))))
            # .withColumn("categoria", f.regexp_replace(col("categoria"), "Categoría única", "Única"))
            # .withColumn("categoria", f.split(col("categoria"), " ")[0])
         )
df_cyl.select("establecimiento", "n_registro", "tipo", "categoria").show(15)
```

    +--------------------+----------+--------------------+----------------+
    |     establecimiento|n_registro|                tipo|       categoria|
    +--------------------+----------+--------------------+----------------+
    |      Turismo Activo| 47/000047|Profesional de Tu...|            NULL|
    |Alojam. Turismo R...| 05/000788|Casa Rural de Alq...|            NULL|
    |Alojam. Turismo R...| 05/000696|Casa Rural de Alq...|            NULL|
    |Alojam. Turismo R...| 05/001050|Casa Rural de Alq...|            NULL|
    |               Bares| 05/002525|                 Bar|            NULL|
    |               Bares| 05/000864|                 Bar|            NULL|
    |               Bares| 05/003351|                 Bar|            NULL|
    |               Bares| 05/001762|                 Bar|            NULL|
    |          Cafeterías| 05/000033|           Cafetería|     2ª - 1 Taza|
    |          Cafeterías| 05/000032|           Cafetería|     2ª - 1 Taza|
    |        Restaurantes| 05/000490|   Restaurante / Bar|3ª - 2 Tenedores|
    |  Vivienda Turística| 05/000836|               Chalé|            NULL|
    |  Vivienda Turística| 05/000120|    Inmueble análogo|            NULL|
    |Activ.tur.complem...| 05/000019|                   p|            NULL|
    |Activ.tur.complem...| 05/000011|                   n|            NULL|
    +--------------------+----------+--------------------+----------------+
    only showing top 15 rows
    


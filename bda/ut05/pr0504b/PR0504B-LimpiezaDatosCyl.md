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

    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    26/02/03 12:32:41 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession inciada correctamente.


### 1.- Identificación y categorización


```python
df_cyl = (df
            .withColumn("establecimiento", f.trim(f.initcap(col("establecimiento"))))
            .withColumn("n_registro", f.coalesce(f.trim(col("n_registro"))))
            .withColumn("tipo", f.trim(f.regexp_replace(col("tipo"), r"^[a-zA-Z] -", "")))
            .withColumn("categoria", 
                f.when(col("categoria") == "Categoría única", "Unica")
                .otherwise(f.regexp_extract(col("categoria"), r"(\d+)", 1)) 
            )
         )
df_cyl.select("establecimiento", "n_registro", "tipo", "categoria").show(15)
```

                                                                                    

    +--------------------+----------+--------------------+---------+
    |     establecimiento|n_registro|                tipo|categoria|
    +--------------------+----------+--------------------+---------+
    |      Turismo Activo| 47/000047|Profesional de Tu...|     NULL|
    |Alojam. Turismo R...| 05/000788|Casa Rural de Alq...|        3|
    |Alojam. Turismo R...| 05/000696|Casa Rural de Alq...|        4|
    |Alojam. Turismo R...| 05/001050|Casa Rural de Alq...|        4|
    |               Bares| 05/002525|                 Bar|    Unica|
    |               Bares| 05/000864|                 Bar|    Unica|
    |               Bares| 05/003351|                 Bar|    Unica|
    |               Bares| 05/001762|                 Bar|    Unica|
    |          Cafeterías| 05/000033|           Cafetería|        2|
    |          Cafeterías| 05/000032|           Cafetería|        2|
    |        Restaurantes| 05/000490|   Restaurante / Bar|        3|
    |  Vivienda Turística| 05/000836|               Chalé|     NULL|
    |  Vivienda Turística| 05/000120|    Inmueble análogo|     NULL|
    |Activ.tur.complem...| 05/000019|Actividades de ed...|     NULL|
    |Activ.tur.complem...| 05/000011|Oficinas y puntos...|     NULL|
    +--------------------+----------+--------------------+---------+
    only showing top 15 rows
    


### 2.- Datos del negocio


```python
df_cyl = (df
            .withColumn("nombre", f.trim(f.initcap(col("nombre"))))
            .withColumn("direccion", f.initcap(
                f.regexp_replace(
                    f.regexp_replace(col("direccion"), "C/", "Calle"),
                    "Avda.", "Avenida")
                ))
            .withColumn("c_postal", f.lpad(col("c_postal").cast("string"), 5, "0"))
            .withColumn("provincia", f.trim(f.initcap(col("provincia"))))
            .withColumn("municipio", f.trim(f.initcap(col("municipio"))))
            .withColumn("localidad", f.trim(f.initcap(col("localidad"))))
            .withColumn("nucleo", f.coalesce(col("nucleo"), col("localidad")))
         )

df_cyl.select("nombre", "direccion", "c_postal", "provincia", "municipio", "localidad", "nucleo").show(15)
```

    26/02/03 12:32:55 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors


    +--------------------+--------------------+--------+---------+-----------+---------------+---------------+
    |              nombre|           direccion|c_postal|provincia|  municipio|      localidad|         nucleo|
    +--------------------+--------------------+--------+---------+-----------+---------------+---------------+
    |Bernardo Moro Men...|Calle Rio Somiedo...|   33840| Asturias|    Somiedo|Pola De Somiedo|POLA DE SOMIEDO|
    |        La Sastrería|Calle Veintiocho ...|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |         Las Hazanas|       Plaza Mayor 4|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    | La Casita Del Pajar|   Plaza Mayor 4   B|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |            Maracana|Calle 28 De Junio...|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |               Plaza|      Plaza Mayor, 7|   05296|    Ávila|    Adanero|        Adanero|        Adanero|
    |          La Oficina|    Calle Estanque 8|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |              Jardin|Paseo De La Flori...|   05296|    Ávila|    Adanero|        Adanero|        Adanero|
    |               Cesar|Carretera Madrid-...|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |             Adanero|Carretera Madrid ...|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |                  Ma|   Carretera A-6 111|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |Chalet Encantador...|Avenida Nuestra S...|   05296|    Ávila|    Adanero|        Adanero|        ADANERO|
    |  Finca Aguatachales| Camino Estacion S/n|   05292|    Ávila|    Adanero|        Adanero|        ADANERO|
    |Jardin Botánico V...|Carretera Cl-501 ...|   05430|    Ávila|Adrada (la)|    Adrada (la)|    ADRADA (LA)|
    |P.información T. ...|Calle Subida Al C...|   05430|    Ávila|Adrada (la)|    Adrada (la)|    ADRADA (LA)|
    +--------------------+--------------------+--------+---------+-----------+---------------+---------------+
    only showing top 15 rows
    


### 3.- Contacto


```python
df_cyl = (df_cyl
             .withColumn("telefono", f.array(
                 f.trim(col("telefono_1")),
                 f.trim(col("telefono_2")),
                 f.trim(col("telefono_3"))
             ))
          # TODO
         )
df_cyl = df_cyl.drop("telefono_1", "telefono_2", "telefono_3")

df_cyl.select("telefono").show(15)
```

    +--------------------+
    |            telefono|
    +--------------------+
    |[616367277, NULL,...|
    |[920307158, 60694...|
    |[655099974, NULL,...|
    |[655099974, NULL,...|
    |[666389333, NULL,...|
    |  [NULL, NULL, NULL]|
    |[636212800, NULL,...|
    |  [NULL, NULL, NULL]|
    |[920307137, NULL,...|
    |[920307125, NULL,...|
    |[920307050, 63916...|
    |[920307172, 67987...|
    |[649324058, NULL,...|
    |[918671333, 91867...|
    |[690873136, 91867...|
    +--------------------+
    only showing top 15 rows
    


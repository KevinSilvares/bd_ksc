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
    26/02/04 08:40:16 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


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
            .withColumn("email", 
                f.when(col("email").contains("@"), f.lower(col("email")))
                .otherwise(f.lit(None))
                )
            .withColumn("web", 
                f.when(col("web").startswith("http"), col("web"))
                .otherwise(f.concat(f.lit("https://"), col("web")))
             )
         )
df_cyl = df_cyl.drop("telefono_1", "telefono_2", "telefono_3")

df_cyl.select("telefono", "email", "web").show(15)
```

    +--------------------+--------------------+--------------------+
    |            telefono|               email|                 web|
    +--------------------+--------------------+--------------------+
    |[616367277, NULL,...|bernardomoro@hotm...|                NULL|
    |[920307158, 60694...|                NULL|https://www.lasas...|
    |[655099974, NULL,...|lashazanas@hotmai...|                NULL|
    |[655099974, NULL,...|lashazanas@hotmai...|                NULL|
    |[666389333, NULL,...|emo123anatoliev@g...|                NULL|
    |  [NULL, NULL, NULL]|                NULL|                NULL|
    |[636212800, NULL,...|                NULL|                NULL|
    |  [NULL, NULL, NULL]|                NULL|                NULL|
    |[920307137, NULL,...|                NULL|                NULL|
    |[920307125, NULL,...|                NULL|                NULL|
    |[920307050, 63916...|info@restaurantem...|                NULL|
    |[920307172, 67987...|correcaminos_ssp@...|                NULL|
    |[649324058, NULL,...|fausto.saez.illob...|                NULL|
    |[918671333, 91867...|axel.mahlau@gmail...|https://WWW.JARDI...|
    |[690873136, 91867...|oficinaturismolaa...|                NULL|
    +--------------------+--------------------+--------------------+
    only showing top 15 rows
    


### 4.- Datos cuantitativos y lógicos


```python
df_cyl = (df_cyl
             .withColumn("plazas", 
                f.when(col("plazas").isNotNull(), col("plazas").cast("int"))
                .otherwise(lit(0))
            )
              .withColumn("accesible_a_personas_con_discapacidad",
                f.when(col("accesible_a_personas_con_discapacidad") == "Si", True)
                .otherwise(False)
            )
              .withColumn("q_calidad",
                f.when(col("q_calidad").isNull(), lit("No aplica"))
                .otherwise(col("q_calidad"))
            )
              .withColumn("posada_real",
                    f.when(col("posada_real").isNull(), lit("No aplica"))
                    .otherwise(col("posada_real"))
            )
              .withColumn("especialidades",
                    f.when(col("especialidades").isNull(), lit("No aplica"))
                    .otherwise(col("especialidades"))
            )
         )

df_cyl.select("plazas", "accesible_a_personas_con_discapacidad", "q_calidad", "posada_real", "especialidades").show(15)
```

    +------+-------------------------------------+---------+-----------+--------------+
    |plazas|accesible_a_personas_con_discapacidad|q_calidad|posada_real|especialidades|
    +------+-------------------------------------+---------+-----------+--------------+
    |     0|                                false|No aplica|  No aplica|     No aplica|
    |     6|                                false|No aplica|  No aplica|     No aplica|
    |     8|                                false|No aplica|  No aplica|     No aplica|
    |     2|                                false|No aplica|  No aplica|     No aplica|
    |    42|                                 true|No aplica|  No aplica|     No aplica|
    |     0|                                false|No aplica|  No aplica|     No aplica|
    |    50|                                false|No aplica|  No aplica|     No aplica|
    |     0|                                false|No aplica|  No aplica|     No aplica|
    |    20|                                false|No aplica|  No aplica|     No aplica|
    |    20|                                 true|No aplica|  No aplica|     No aplica|
    |   310|                                false|No aplica|  No aplica|     No aplica|
    |     5|                                 true|No aplica|  No aplica|     No aplica|
    |    16|                                false|No aplica|  No aplica|     No aplica|
    |     0|                                false|No aplica|  No aplica|     No aplica|
    |     0|                                false|No aplica|  No aplica|     No aplica|
    +------+-------------------------------------+---------+-----------+--------------+
    only showing top 15 rows
    


### 5.- Geolocalización


```python
df_cyl = (df_cyl
             .withColumn("posicion_split",
                        f.split(col("posicion"), ",")
                        )
              .withColumn("gps_latitud",
                          f.regexp_replace(
                              f.element_at(col("posicion_split"), 1),
                              ",", ".").cast("double")
                         )
              .withColumn("gps_longitud",
                          f.regexp_replace(
                              f.element_at(col("posicion_split"), 2),
                              ",", ".").cast("double")
                         )
         )

df_cyl = df_cyl.drop("posicion_split", "posicion", "column_27")

df_cyl.select("gps_latitud", "gps_longitud").show(15)
```

    +-----------+------------+
    |gps_latitud|gps_longitud|
    +-----------+------------+
    |       NULL|        NULL|
    |       NULL|        NULL|
    | 40.9438881|  -4.6033331|
    | 40.9438889|  -4.6033333|
    |       NULL|        NULL|
    |       NULL|        NULL|
    |       NULL|        NULL|
    |       NULL|        NULL|
    |       NULL|        NULL|
    |       NULL|        NULL|
    |       NULL|        NULL|
    |       NULL|        NULL|
    |  40.966576|   -4.626714|
    |  40.310505|   -4.660014|
    | 40.2988889|       -4.64|
    +-----------+------------+
    only showing top 15 rows
    


    26/02/04 08:40:33 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors


### Resultado


```python
df_cyl.show(10)
```

    +--------------------+----------+------+--------------------+---------------+--------------+-----+--------------------+--------------------+--------+---------+---------+---------------+---------------+--------------------+--------------------+---------+-----------+------+------------+-----------+-------------------------------------+--------------------+
    |     establecimiento|n_registro|codigo|                tipo|      categoria|especialidades|clase|              nombre|           direccion|c_postal|provincia|municipio|      localidad|         nucleo|               email|                 web|q_calidad|posada_real|plazas|gps_longitud|gps_latitud|accesible_a_personas_con_discapacidad|            telefono|
    +--------------------+----------+------+--------------------+---------------+--------------+-----+--------------------+--------------------+--------+---------+---------+---------------+---------------+--------------------+--------------------+---------+-----------+------+------------+-----------+-------------------------------------+--------------------+
    |      Turismo Activo| 47/000047|  NULL|Profesional de Tu...|           NULL|     No aplica| NULL|Bernardo Moro Men...|Calle Rio Somiedo...|   33840| Asturias|  Somiedo|Pola De Somiedo|POLA DE SOMIEDO|bernardomoro@hotm...|                NULL|No aplica|  No aplica|     0|        NULL|       NULL|                                false|[616367277, NULL,...|
    |Alojam. Turismo R...| 05/000788|  NULL|Casa Rural de Alq...|    3 Estrellas|     No aplica| NULL|        La Sastrería|Calle Veintiocho ...|   05296|    Ávila|  Adanero|        Adanero|        ADANERO|                NULL|https://www.lasas...|No aplica|  No aplica|     6|        NULL|       NULL|                                false|[920307158, 60694...|
    |Alojam. Turismo R...| 05/000696|  NULL|Casa Rural de Alq...|    4 Estrellas|     No aplica| NULL|         Las Hazanas|       Plaza Mayor 4|   05296|    Ávila|  Adanero|        Adanero|        ADANERO|lashazanas@hotmai...|                NULL|No aplica|  No aplica|     8|  -4.6033331| 40.9438881|                                false|[655099974, NULL,...|
    |Alojam. Turismo R...| 05/001050|  NULL|Casa Rural de Alq...|    4 Estrellas|     No aplica| NULL| La Casita Del Pajar|   Plaza Mayor 4   B|   05296|    Ávila|  Adanero|        Adanero|        ADANERO|lashazanas@hotmai...|                NULL|No aplica|  No aplica|     2|  -4.6033333| 40.9438889|                                false|[655099974, NULL,...|
    |               Bares| 05/002525|  NULL|                 Bar|Categoría única|     No aplica| NULL|            Maracana|Calle 28 De Junio...|   05296|    Ávila|  Adanero|        Adanero|        ADANERO|emo123anatoliev@g...|                NULL|No aplica|  No aplica|    42|        NULL|       NULL|                                 true|[666389333, NULL,...|
    |               Bares| 05/000864|  NULL|                 Bar|Categoría única|     No aplica| NULL|               Plaza|      Plaza Mayor, 7|   05296|    Ávila|  Adanero|        Adanero|        Adanero|                NULL|                NULL|No aplica|  No aplica|     0|        NULL|       NULL|                                false|  [NULL, NULL, NULL]|
    |               Bares| 05/003351|  NULL|                 Bar|Categoría única|     No aplica| NULL|          La Oficina|    Calle Estanque 8|   05296|    Ávila|  Adanero|        Adanero|        ADANERO|                NULL|                NULL|No aplica|  No aplica|    50|        NULL|       NULL|                                false|[636212800, NULL,...|
    |               Bares| 05/001762|  NULL|                 Bar|Categoría única|     No aplica| NULL|              Jardin|Paseo De La Flori...|   05296|    Ávila|  Adanero|        Adanero|        Adanero|                NULL|                NULL|No aplica|  No aplica|     0|        NULL|       NULL|                                false|  [NULL, NULL, NULL]|
    |          Cafeterías| 05/000033|  NULL|           Cafetería|    2ª - 1 Taza|     No aplica| NULL|               Cesar|Carretera Madrid-...|   05296|    Ávila|  Adanero|        Adanero|        ADANERO|                NULL|                NULL|No aplica|  No aplica|    20|        NULL|       NULL|                                false|[920307137, NULL,...|
    |          Cafeterías| 05/000032|  NULL|           Cafetería|    2ª - 1 Taza|     No aplica| NULL|             Adanero|Carretera Madrid ...|   05296|    Ávila|  Adanero|        Adanero|        ADANERO|                NULL|                NULL|No aplica|  No aplica|    20|        NULL|       NULL|                                 true|[920307125, NULL,...|
    +--------------------+----------+------+--------------------+---------------+--------------+-----+--------------------+--------------------+--------+---------+---------+---------------+---------------+--------------------+--------------------+---------+-----------+------+------------+-----------+-------------------------------------+--------------------+
    only showing top 10 rows
    


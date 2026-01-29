# PR0501 - Ingesta de datos de ficheros CSV

## Conexión e importaciones


```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType
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

## Dataset 1: Datos para la predicción del rendimiento en cultivos


```python
!head crop_yield_dataset.csv -n2
```

    Crop,Region,Soil_Type,Soil_pH,Rainfall_mm,Temperature_C,Humidity_pct,Fertilizer_Used_kg,Irrigation,Pesticides_Used_kg,Planting_Density,Previous_Crop,Yield_ton_per_ha
    Maize,Region_C,Sandy,7.01,1485.4,19.7,40.3,105.1,Drip,10.2,23.2,Rice,101.48



```python
def load_crops_df(spark):
    schema = StructType([
        StructField("crop", StringType(), False),
        StructField("region", StringType(), False),
        StructField("soil_type", StringType(), False),
        StructField("soil_ph", DoubleType(), False),
        StructField("rainfall_mm", DoubleType(), False),
        StructField("temperature_C", DoubleType(), False),
        StructField("humidity_pct", DoubleType(), False),
        StructField("fertilizer_used_kg", DoubleType(), False),
        StructField("irrigation", StringType(), False),
        StructField("pesticides_used_kg", DoubleType(), False),
        StructField("planting_density", DoubleType(), False),
        StructField("previous_crop", StringType(), True),
        StructField("yield_ton_per_ha", DoubleType(), False),
    ])
    
    df = (spark.read
          .format("csv")
          .schema(schema)
          .option("header", "true")
          .load("./crop_yield_dataset.csv")
         )

    df.show(5)
```


```python
spark = connect_spark()
load_crops_df(spark)
```

    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    26/01/29 09:26:46 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession inciada correctamente.


                                                                                    

    +------+--------+---------+-------+-----------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+
    |  crop|  region|soil_type|soil_ph|rainfall_mm|temperature_C|humidity_pct|fertilizer_used_kg|irrigation|pesticides_used_kg|planting_density|previous_crop|yield_ton_per_ha|
    +------+--------+---------+-------+-----------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+
    | Maize|Region_C|    Sandy|   7.01|     1485.4|         19.7|        40.3|             105.1|      Drip|              10.2|            23.2|         Rice|          101.48|
    |Barley|Region_D|     Loam|   5.79|      399.4|         29.1|        55.4|             221.8| Sprinkler|              35.5|             7.4|       Barley|          127.39|
    |  Rice|Region_C|     Clay|   7.24|      980.9|         30.5|        74.4|              61.2| Sprinkler|              40.0|             5.1|        Wheat|           68.99|
    | Maize|Region_D|     Loam|   6.79|     1054.3|         26.4|        62.0|             257.8|      Drip|              42.7|            23.7|         None|          169.06|
    | Maize|Region_D|    Sandy|   5.96|      744.6|         20.4|        70.9|             195.8|      Drip|              25.5|            15.6|        Maize|          118.71|
    +------+--------+---------+-------+-----------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+
    only showing top 5 rows
    


## Dataset 2: Lugares famosos del mundo


```python
!head world_famous_places_2024.csv -n2
```

    Place_Name,Country,City,Annual_Visitors_Millions,Type,UNESCO_World_Heritage,Year_Built,Entry_Fee_USD,Best_Visit_Month,Region,Tourism_Revenue_Million_USD,Average_Visit_Duration_Hours,Famous_For
    Eiffel Tower,France,Paris,7,Monument/Tower,No,1889,35,May-June/Sept-Oct,Western Europe,95,2.5,"Iconic iron lattice tower, symbol of Paris"



```python
def load_world_places_df(spark):
    schema = StructType([
        StructField("place_name", StringType(), False),
        StructField("country", StringType(), False),
        StructField("city", StringType(), False),
        StructField("annual_visitors_million", DoubleType(), False),
        StructField("type", StringType(), False),
        StructField("unesco_world_heritage", StringType(), False),
        StructField("year_built", IntegerType(), False),
        StructField("entry_fee_usd", DoubleType(), False),
        StructField("best_visit_month", StringType(), False),
        StructField("region", StringType(), False),
        StructField("average_visit_duration_hours", DoubleType(), False),
        StructField("tourism_revenue_million_usd", DoubleType(), False),
        StructField("famous_for", StringType(), False)
    ])

    df = (spark.read
            .format("csv")
            .schema(schema)
            .option("header", "true")
            .load("world_famous_places_2024.csv")
         )

    df.show(5)
```


```python
spark = connect_spark()
load_world_places_df(spark)
```

    SparkSession inciada correctamente.
    +-------------------+-------------+----------------+-----------------------+------------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+
    |         place_name|      country|            city|annual_visitors_million|              type|unesco_world_heritage|year_built|entry_fee_usd| best_visit_month|        region|average_visit_duration_hours|tourism_revenue_million_usd|          famous_for|
    +-------------------+-------------+----------------+-----------------------+------------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+
    |       Eiffel Tower|       France|           Paris|                    7.0|    Monument/Tower|                   No|      1889|         35.0|May-June/Sept-Oct|Western Europe|                        95.0|                        2.5|Iconic iron latti...|
    |       Times Square|United States|   New York City|                   50.0|    Urban Landmark|                   No|      1904|          0.0|Apr-June/Sept-Nov| North America|                        70.0|                        1.5|Bright lights, Br...|
    |      Louvre Museum|       France|           Paris|                    8.7|            Museum|                  Yes|      1793|         22.0|        Oct-March|Western Europe|                       120.0|                        4.0|World's most visi...|
    |Great Wall of China|        China|Beijing/Multiple|                   10.0| Historic Monument|                  Yes|      NULL|         10.0| Apr-May/Sept-Oct|     East Asia|                       180.0|                        4.0|Ancient defensive...|
    |          Taj Mahal|        India|            Agra|                    7.5|Monument/Mausoleum|                  Yes|      1653|         15.0|        Oct-March|    South Asia|                        65.0|                        2.0|White marble maus...|
    +-------------------+-------------+----------------+-----------------------+------------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+
    only showing top 5 rows
    


## Dataset 3: Registro turístico de Castilla y León


```python
!head registro-de-turismo-de-castilla-y-leon.csv -n2
```

    establecimiento;n_registro;codigo;tipo;categoria;especialidades;clase;nombre;direccion;c_postal;provincia;municipio;localidad;nucleo;telefono_1;telefono_2;telefono_3;email;web;q_calidad;posada_real;plazas;gps_longitud;gps_latitud;accesible_a_personas_con_discapacidad;column_27;posicion
    Turismo Activo;47/000047;;Profesional de Turismo Activo;;;;BERNARDO MORO MENENDEZ;Calle Rio Somiedo 1  2º C;33840;Asturias;Somiedo;POLA DE SOMIEDO;POLA DE SOMIEDO;616367277;;;bernardomoro@hotmail.com;;;;;;;;;



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

    df.show(5)
```


```python
spark = connect_spark()
load_cyl_turistic_places(spark)
```

    SparkSession inciada correctamente.


    26/01/29 09:26:59 WARN SparkStringUtils: Truncated the string representation of a plan since it was too large. This behavior can be adjusted by setting 'spark.sql.debug.maxToStringFields'.


    +--------------------+----------+------+--------------------+---------------+--------------+-----+--------------------+--------------------+--------+---------+---------+---------------+---------------+----------+----------+----------+--------------------+--------------------+---------+-----------+------+------------+-----------+-------------------------------------+---------+--------------------+
    |     establecimiento|n_registro|codigo|                tipo|      categoria|especialidades|clase|              nombre|           direccion|c_postal|provincia|municipio|      localidad|         nucleo|telefono_1|telefono_2|telefono_3|               email|                 web|q_calidad|posada_real|plazas|gps_longitud|gps_latitud|accesible_a_personas_con_discapacidad|column_27|            posicion|
    +--------------------+----------+------+--------------------+---------------+--------------+-----+--------------------+--------------------+--------+---------+---------+---------------+---------------+----------+----------+----------+--------------------+--------------------+---------+-----------+------+------------+-----------+-------------------------------------+---------+--------------------+
    |      Turismo Activo| 47/000047|  NULL|Profesional de Tu...|           NULL|          NULL| NULL|BERNARDO MORO MEN...|Calle Rio Somiedo...|   33840| Asturias|  Somiedo|POLA DE SOMIEDO|POLA DE SOMIEDO| 616367277|      NULL|      NULL|bernardomoro@hotm...|                NULL|     NULL|       NULL|  NULL|        NULL|       NULL|                                 NULL|     NULL|                NULL|
    |Alojam. Turismo R...| 05/000788|  NULL|Casa Rural de Alq...|    3 Estrellas|          NULL| NULL|        LA SASTRERÍA|Calle VEINTIOCHO ...|    5296|    Ávila|  Adanero|        ADANERO|        ADANERO| 920307158| 606945069| 609289521|                NULL|www.lasastreriade...|     NULL|       NULL|     6|        NULL|       NULL|                                 NULL|     NULL|                NULL|
    |Alojam. Turismo R...| 05/000696|  NULL|Casa Rural de Alq...|    4 Estrellas|          NULL| NULL|         LAS HAZANAS|       Plaza MAYOR 4|    5296|    Ávila|  Adanero|        ADANERO|        ADANERO| 655099974|      NULL|      NULL|lashazanas@hotmai...|                NULL|     NULL|       NULL|     8|  -4.6033331| 40.9438881|                                 NULL|     NULL|40.9438881, -4.60...|
    |Alojam. Turismo R...| 05/001050|  NULL|Casa Rural de Alq...|    4 Estrellas|          NULL| NULL| LA CASITA DEL PAJAR|   Plaza MAYOR 4   B|    5296|    Ávila|  Adanero|        ADANERO|        ADANERO| 655099974|      NULL|      NULL|lashazanas@hotmai...|                NULL|     NULL|       NULL|     2|  -4.6033333| 40.9438889|                                 NULL|     NULL|40.9438889, -4.60...|
    |               Bares| 05/002525|  NULL|                 Bar|Categoría única|          NULL| NULL|            MARACANA|Calle 28 DE JUNIO...|    5296|    Ávila|  Adanero|        ADANERO|        ADANERO| 666389333|      NULL|      NULL|emo123anatoliev@g...|                NULL|     NULL|       NULL|    42|        NULL|       NULL|                                   Si|     NULL|                NULL|
    +--------------------+----------+------+--------------------+---------------+--------------+-----+--------------------+--------------------+--------+---------+---------+---------------+---------------+----------+----------+----------+--------------------+--------------------+---------+-----------+------+------------+-----------+-------------------------------------+---------+--------------------+
    only showing top 5 rows
    



```python
spark.stop()
```

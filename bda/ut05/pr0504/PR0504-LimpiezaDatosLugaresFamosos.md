# PR0504 - Limpieza de datos sobre dataset de lugares famosos

## Conexión e importaciones


```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType
from pyspark.sql.functions import col, lit, split, substring, upper, concat, concat_ws, rpad, log10, round, greatest, to_date, date_add, month, ceil, least, datediff, regexp_replace
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

## Dataset 2: Lugares famosos del mundo


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
    return df
```

### Ejercicio 1: Generación de códigos SKUs


```python
# ESP-LEO-MONUMENT

spark = connect_spark()
df = load_world_places_df(spark)

df_feat = (df
              .withColumn("SKU_LUGAR",
                          concat_ws("_", 
                                    upper(substring(col("country"), 0, 3)),
                                    upper(rpad(substring(col("city"), 0, 3), 3, "X")),
                                    upper(split(col("type"), "/")[0])
                          )
                         )
          )

df_feat.show(3)
```

    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    26/01/29 09:49:09 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession inciada correctamente.


                                                                                    

    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+
    |   place_name|      country|         city|annual_visitors_million|          type|unesco_world_heritage|year_built|entry_fee_usd| best_visit_month|        region|average_visit_duration_hours|tourism_revenue_million_usd|          famous_for|           SKU_LUGAR|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+
    | Eiffel Tower|       France|        Paris|                    7.0|Monument/Tower|                   No|      1889|         35.0|May-June/Sept-Oct|Western Europe|                        95.0|                        2.5|Iconic iron latti...|    FRA_PAR_MONUMENT|
    | Times Square|United States|New York City|                   50.0|Urban Landmark|                   No|      1904|          0.0|Apr-June/Sept-Nov| North America|                        70.0|                        1.5|Bright lights, Br...|UNI_NEW_URBAN LAN...|
    |Louvre Museum|       France|        Paris|                    8.7|        Museum|                  Yes|      1793|         22.0|        Oct-March|Western Europe|                       120.0|                        4.0|World's most visi...|      FRA_PAR_MUSEUM|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+
    only showing top 3 rows
    


### Ejercicio 2: Ajuste de precios y tiempos


```python
df_feat = (df_feat
            .withColumn("duracion_techo", ceil(col("average_visit_duration_hours")))
            .withColumn("log_ingresos", log10(col("tourism_revenue_million_usd")))
            .withColumn("mejor_oferta", least(col("entry_fee_usd"), lit(20)))
          )
df_feat.show(3)
```

    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+
    |   place_name|      country|         city|annual_visitors_million|          type|unesco_world_heritage|year_built|entry_fee_usd| best_visit_month|        region|average_visit_duration_hours|tourism_revenue_million_usd|          famous_for|           SKU_LUGAR|duracion_techo|       log_ingresos|mejor_oferta|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+
    | Eiffel Tower|       France|        Paris|                    7.0|Monument/Tower|                   No|      1889|         35.0|May-June/Sept-Oct|Western Europe|                        95.0|                        2.5|Iconic iron latti...|    FRA_PAR_MONUMENT|            95| 0.3979400086720376|        20.0|
    | Times Square|United States|New York City|                   50.0|Urban Landmark|                   No|      1904|          0.0|Apr-June/Sept-Nov| North America|                        70.0|                        1.5|Bright lights, Br...|UNI_NEW_URBAN LAN...|            70|0.17609125905568124|         0.0|
    |Louvre Museum|       France|        Paris|                    8.7|        Museum|                  Yes|      1793|         22.0|        Oct-March|Western Europe|                       120.0|                        4.0|World's most visi...|      FRA_PAR_MUSEUM|           120| 0.6020599913279624|        20.0|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+
    only showing top 3 rows
    


### Ejercicio 3: Limpieza de texto


```python
df_feat = (df_feat
            .withColumn("desc_cort", substring(col("famous_for"), 0, 15))
            .withColumn("ciudad_limpia", regexp_replace(col("city"), "New York City", "NYC"))
          )
df_feat.show(3)
```

    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+---------------+-------------+
    |   place_name|      country|         city|annual_visitors_million|          type|unesco_world_heritage|year_built|entry_fee_usd| best_visit_month|        region|average_visit_duration_hours|tourism_revenue_million_usd|          famous_for|           SKU_LUGAR|duracion_techo|       log_ingresos|mejor_oferta|      desc_cort|ciudad_limpia|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+---------------+-------------+
    | Eiffel Tower|       France|        Paris|                    7.0|Monument/Tower|                   No|      1889|         35.0|May-June/Sept-Oct|Western Europe|                        95.0|                        2.5|Iconic iron latti...|    FRA_PAR_MONUMENT|            95| 0.3979400086720376|        20.0|Iconic iron lat|        Paris|
    | Times Square|United States|New York City|                   50.0|Urban Landmark|                   No|      1904|          0.0|Apr-June/Sept-Nov| North America|                        70.0|                        1.5|Bright lights, Br...|UNI_NEW_URBAN LAN...|            70|0.17609125905568124|         0.0|Bright lights, |          NYC|
    |Louvre Museum|       France|        Paris|                    8.7|        Museum|                  Yes|      1793|         22.0|        Oct-March|Western Europe|                       120.0|                        4.0|World's most visi...|      FRA_PAR_MUSEUM|           120| 0.6020599913279624|        20.0|World's most vi|        Paris|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+---------------+-------------+
    only showing top 3 rows
    


### Ejercicio 4: Gestión de fechas de campaña


```python
df_feat = (df_feat
            .withColumn("inicio_campana", to_date(lit("2024-06-01")))
            .withColumn("fin_campana", date_add(col("inicio_campana"), 90))
            .withColumn("dias_hasta_fin", 
                            datediff(col("fin_campana"),
                                 to_date(concat(col("year_built"), lit("-01-01"))),   
                )
            )
          )
df_feat.show(3)
```

    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+---------------+-------------+--------------+-----------+--------------+
    |   place_name|      country|         city|annual_visitors_million|          type|unesco_world_heritage|year_built|entry_fee_usd| best_visit_month|        region|average_visit_duration_hours|tourism_revenue_million_usd|          famous_for|           SKU_LUGAR|duracion_techo|       log_ingresos|mejor_oferta|      desc_cort|ciudad_limpia|inicio_campana|fin_campana|dias_hasta_fin|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+---------------+-------------+--------------+-----------+--------------+
    | Eiffel Tower|       France|        Paris|                    7.0|Monument/Tower|                   No|      1889|         35.0|May-June/Sept-Oct|Western Europe|                        95.0|                        2.5|Iconic iron latti...|    FRA_PAR_MONUMENT|            95| 0.3979400086720376|        20.0|Iconic iron lat|        Paris|    2024-06-01| 2024-08-30|         49549|
    | Times Square|United States|New York City|                   50.0|Urban Landmark|                   No|      1904|          0.0|Apr-June/Sept-Nov| North America|                        70.0|                        1.5|Bright lights, Br...|UNI_NEW_URBAN LAN...|            70|0.17609125905568124|         0.0|Bright lights, |          NYC|    2024-06-01| 2024-08-30|         44072|
    |Louvre Museum|       France|        Paris|                    8.7|        Museum|                  Yes|      1793|         22.0|        Oct-March|Western Europe|                       120.0|                        4.0|World's most visi...|      FRA_PAR_MUSEUM|           120| 0.6020599913279624|        20.0|World's most vi|        Paris|    2024-06-01| 2024-08-30|         84612|
    +-------------+-------------+-------------+-----------------------+--------------+---------------------+----------+-------------+-----------------+--------------+----------------------------+---------------------------+--------------------+--------------------+--------------+-------------------+------------+---------------+-------------+--------------+-----------+--------------+
    only showing top 3 rows
    



```python
spark.stop()
```

    26/01/29 09:49:29 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors


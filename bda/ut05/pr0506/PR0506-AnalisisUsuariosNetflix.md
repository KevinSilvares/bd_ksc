# PR0506 - Análisis de comportamiento de usuarios en Netflix


```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType, DecimalType, TimestampType
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


```python
!head -n 1 vodclickstream_uk_movies_03.csv
```

    ,datetime,duration,title,genres,release_date,movie_id,user_id



```python
def load_dataset(spark):
    schema = StructType([
        StructField("row_id", IntegerType(), False),
        StructField("click_datetime", TimestampType(), False),
        StructField("duration", DoubleType(), False),
        StructField("title", StringType(), False),
        StructField("genres", StringType(), False),
        StructField("release_date", TimestampType(), False),
        StructField("movie_id", StringType(), False),
        StructField("user_id", StringType(), False),
    ])

    df = (spark.read
            .format("csv")
            .schema(schema)
            .option("header", "true")
            .option("delimiter", ",")
            .load("vodclickstream_uk_movies_03.csv")
         )
    return df
```


```python
spark = connect_spark()
df = load_dataset(spark)
df.show(3)
```

    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    26/03/04 11:05:50 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession inciada correctamente.


                                                                                    

    +------+-------------------+--------+--------------------+--------------------+-------------------+----------+----------+
    |row_id|     click_datetime|duration|               title|              genres|       release_date|  movie_id|   user_id|
    +------+-------------------+--------+--------------------+--------------------+-------------------+----------+----------+
    | 58773|2017-01-01 01:15:09|     0.0|Angus, Thongs and...|Comedy, Drama, Ro...|2008-07-25 00:00:00|26bd5987e8|1dea19f6fe|
    | 58774|2017-01-01 13:56:02|     0.0|The Curse of Slee...|Fantasy, Horror, ...|2016-06-02 00:00:00|f26ed2675e|544dcbc510|
    | 58775|2017-01-01 15:17:47| 10530.0|   London Has Fallen|    Action, Thriller|2016-03-04 00:00:00|f77e500e7a|7cbcc791bf|
    +------+-------------------+--------+--------------------+--------------------+-------------------+----------+----------+
    only showing top 3 rows
    


## 1.- Auditoría de telemetría Web (validación de datos)


```python
click_window = (Window
                .partitionBy("user_id").orderBy("click_datetime")
)

df = (df
      .withColumn("calculated_time_to_next", 
                  (f.lead("click_datetime", 1).over(click_window).cast("long") - col("click_datetime").cast("long"))
                 )
)

df.select("user_id", "duration", "calculated_time_to_next").show(15)
```

    [Stage 3:>                                                          (0 + 1) / 1]

    +----------+--------+-----------------------+
    |   user_id|duration|calculated_time_to_next|
    +----------+--------+-----------------------+
    |0006ea6b5c|     0.0|                  91971|
    |0006ea6b5c|     0.0|                 506607|
    |0006ea6b5c|     0.0|                  17625|
    |0006ea6b5c|     0.0|                  83635|
    |0006ea6b5c|     0.0|                 518737|
    |0006ea6b5c|  1182.0|                   1182|
    |0006ea6b5c|     0.0|                  81826|
    |0006ea6b5c|  4200.0|                   4200|
    |0006ea6b5c|     0.0|                  87798|
    |0006ea6b5c|  1800.0|                 424015|
    |0006ea6b5c|     0.0|                  94226|
    |0006ea6b5c|  4800.0|                 618404|
    |0006ea6b5c|     0.0|                 153005|
    |0006ea6b5c|  4831.0|                 786194|
    |0006ea6b5c|     0.0|                   NULL|
    +----------+--------+-----------------------+
    only showing top 15 rows
    


                                                                                    

## 2.- Detección de "zapping"


```python
df = (df
      .withColumn("es_zapping", 
                 f.when(col("calculated_time_to_next").cast("long") > 300, 0)
                  .otherwise(1)
                 )
)

df.select("user_id", "calculated_time_to_next", "es_zapping").show(5)
```

    26/03/04 11:06:11 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors
    [Stage 4:==============>                                            (2 + 6) / 8]

    +----------+-----------------------+----------+
    |   user_id|calculated_time_to_next|es_zapping|
    +----------+-----------------------+----------+
    |0006ea6b5c|                  91971|         0|
    |0006ea6b5c|                 506607|         0|
    |0006ea6b5c|                  17625|         0|
    |0006ea6b5c|                  83635|         0|
    |0006ea6b5c|                 518737|         0|
    +----------+-----------------------+----------+
    only showing top 5 rows
    


                                                                                    

## 3.- El ranking de "maratones"


```python
ventana = (Window
           .partitionBy("user_id").orderBy("click_datetime")
          )

df_maratones = (df
                .withColumn(
                    "pelicula", f.row_number().over(ventana)
                )
)

df_maratones.select("user_id", "title", "movie_id", "pelicula").show(5)
```

    [Stage 13:=====================>                                    (3 + 5) / 8]

    +----------+--------------------+----------+--------+
    |   user_id|               title|  movie_id|pelicula|
    +----------+--------------------+----------+--------+
    |0006ea6b5c|                XOXO|7369676dec|       1|
    |0006ea6b5c|            Hot Fuzz|6467fee6b6|       2|
    |0006ea6b5c|         War Machine|0f3b137f4e|       3|
    |0006ea6b5c|          Apocalypto|40dd7bf1f9|       4|
    |0006ea6b5c|Joshua: Teenager ...|4a138aeefc|       5|
    +----------+--------------------+----------+--------+
    only showing top 5 rows
    


                                                                                    

## 4.- Análisis de re-visualización


```python
ventana = (Window.partitionBy("user_id"))

# las comparaciones del when tienen que ir entre paréntesis para que el & funcione 

df = (df
    .withColumn("veces_vista_por_usuario", 
                f.when((f.year("click_datetime") >= 2017) & (f.year("click_datetime") <= 2019),
                    f.count("movie_id").over(ventana)
                      )
                .otherwise(0)
               )
)

df.filter(df.veces_vista_por_usuario > 3).select("user_id", "title", "movie_id", "veces_vista_por_usuario").show(10)
```

    [Stage 36:=======>                                                  (1 + 7) / 8]

    +----------+--------------------+----------+-----------------------+
    |   user_id|               title|  movie_id|veces_vista_por_usuario|
    +----------+--------------------+----------+-----------------------+
    |0006ea6b5c|                XOXO|7369676dec|                     15|
    |0006ea6b5c|            Hot Fuzz|6467fee6b6|                     15|
    |0006ea6b5c|          Apocalypto|40dd7bf1f9|                     15|
    |0006ea6b5c|         War Machine|0f3b137f4e|                     15|
    |0006ea6b5c|Joshua: Teenager ...|4a138aeefc|                     15|
    |0006ea6b5c|Stranger than Fic...|73183024a6|                     15|
    |0006ea6b5c|         Lucid Dream|27b44a3183|                     15|
    |0006ea6b5c|        Dragon Blade|ed515d444e|                     15|
    |0006ea6b5c|Handsome: A Netfl...|9f2550ca52|                     15|
    |0006ea6b5c|        Dragon Blade|ed515d444e|                     15|
    +----------+--------------------+----------+-----------------------+
    only showing top 10 rows
    


                                                                                    

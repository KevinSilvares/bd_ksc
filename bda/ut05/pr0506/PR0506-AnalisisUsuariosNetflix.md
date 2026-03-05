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
    26/03/05 09:58:42 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    26/03/05 09:58:44 WARN Utils: Service 'SparkUI' could not bind on port 4040. Attempting port 4041.


    SparkSession inciada correctamente.


    26/03/05 09:58:55 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors
                                                                                    

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
# f.unix_timestamp(click_datetime)
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

    [Stage 4:=======>                                                   (1 + 7) / 8]

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
df = df.withColumn("date", f.to_date("click_datetime"))

ventana = (Window
           .partitionBy("user_id", "date").orderBy("click_datetime")
          )

df = df.withColumn("pelicula_num", f.row_number().over(ventana))

(df
 .groupBy("user_id", "date")
 .agg(f.max("pelicula_num").alias("total_peliculas"))
).orderBy("total_peliculas", ascending = False).show()
```

    [Stage 9:>                                                          (0 + 8) / 8]

    +----------+----------+---------------+
    |   user_id|      date|total_peliculas|
    +----------+----------+---------------+
    |23c52f9b50|2019-01-21|             64|
    |59416738c3|2017-02-21|             54|
    |3675d9ba4a|2018-11-26|             44|
    |b15926c011|2018-03-24|             42|
    |b090d94e51|2017-05-01|             40|
    |423d95651d|2019-05-04|             38|
    |fa48fa50ae|2018-12-22|             38|
    |16d994f6dd|2017-11-11|             37|
    |b15926c011|2018-05-13|             36|
    |b15926c011|2018-04-15|             36|
    |779343a3ea|2018-06-17|             34|
    |f0d52ca74c|2018-03-30|             34|
    |b15926c011|2018-05-06|             33|
    |779343a3ea|2018-05-26|             32|
    |6924354498|2017-11-05|             31|
    |da01959c0b|2019-03-21|             31|
    |5495affecb|2017-09-09|             29|
    |f98c8ca112|2017-09-06|             29|
    |da01959c0b|2019-03-12|             29|
    |ae77c5157f|2017-02-21|             29|
    +----------+----------+---------------+
    only showing top 20 rows
    


                                                                                    

## 4.- Análisis de re-visualización


```python
ventana = (Window.partitionBy("user_id", "title"))

# las comparaciones del when tienen que ir entre paréntesis para que el & funcione 

df = (df
     .withColumn("veces_vista_por_usuario", 
                 f.count("title").over(ventana)
                )
     )

df_reviews = (df
    .filter(col("veces_vista_por_usuario") >= 3)
    .orderBy("veces_vista_por_usuario", ascending = False)
    .select("user_id", "title", "movie_id", "veces_vista_por_usuario")
    .distinct()
)

df_reviews.show(10)

# df = (df
#     .withColumn("veces_vista_por_usuario", 
#                 f.when((f.year("click_datetime") >= 2017) & (f.year("click_datetime") <= 2019),
#                     f.count("movie_id").over(ventana)
#                       )
#                 .otherwise(0)
#                )
# )

# df.filter(df.veces_vista_por_usuario > 3).select("user_id", "title", "movie_id", "veces_vista_por_usuario").show(10)
```

    [Stage 13:=============================>                            (4 + 4) / 8]

    +----------+--------------------+----------+-----------------------+
    |   user_id|               title|  movie_id|veces_vista_por_usuario|
    +----------+--------------------+----------+-----------------------+
    |000052a0a0|              Looper|4718f9963c|                      9|
    |0012a95d5f|           Footloose|91e826cb17|                      3|
    |0016c962c8|          Iron Man 3|afab92c7a7|                      4|
    |0023e9b95e|Black Mirror: Ban...|e847f14da5|                      3|
    |00305e5c73|                Lion|ea4d08cf70|                      4|
    |004ad258d2|              Carrie|0b4c284ea9|                      4|
    |004ad258d2|              Carrie|6f8ac8a090|                      4|
    |004e33f215|             Detroit|c2bee3b484|                      3|
    |004e33f215|   Hitler - A Career|fd68f2e667|                      4|
    |004e33f215|The Legend of Coc...|3395cdc07c|                      3|
    +----------+--------------------+----------+-----------------------+
    only showing top 10 rows
    


                                                                                    


```python
spark.stop()
```

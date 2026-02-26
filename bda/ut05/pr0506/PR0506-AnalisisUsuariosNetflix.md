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

    [Stage 23:==============>                                           (2 + 6) / 8]

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

    [Stage 32:=====================>                                    (3 + 5) / 8]

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
    


                                                                                    


```python

```

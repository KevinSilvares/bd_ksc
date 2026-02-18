# PR0505 - Análisis de estadísticas en dataset


```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType, DecimalType
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
!head -n 1 house_prices.csv
```

    Index,Title,Description,Amount(in rupees),Price (in rupees),location,Carpet Area,Status,Floor,Transaction,Furnishing,facing,overlooking,Society,Bathroom,Balcony,Car Parking,Ownership,Super Area,Dimensions,Plot Area



```python
def load_dataset(spark):
    schema = StructType([
        StructField("index", IntegerType(), False),
        StructField("title", StringType(), False),
        StructField("description", StringType(), False),
        StructField("amount(in rupees)", StringType(), True),
        StructField("price(in rupees)", StringType(), True),
        StructField("location", StringType(), False),
        StructField("carpet_area", StringType(), True),
        StructField("status", StringType(), False),
        StructField("floor", StringType(), False),
        StructField("transaction", StringType(), False),
        StructField("furnishing", IntegerType(), False),
        StructField("facing", StringType(), True),
        StructField("overlooking", StringType(), True),
        StructField("society", StringType(), True),
        StructField("bathroom", IntegerType(), False),
        StructField("balcony", IntegerType(), True),
        StructField("car_parking", StringType(), True),
        StructField("ownership", StringType(), True),
        StructField("super_area", StringType(), True),
    ])

    df = (spark.read
            .format("csv")
            .schema(schema)
            .option("header", "true")
            .option("delimiter", ",")
            .load("house_prices.csv")
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
    26/02/18 11:34:45 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession inciada correctamente.


                                                                                    

    +-----+--------------------+--------------------+-----------------+----------------+--------+-----------+-------------+------------+-----------+----------+------+-----------+--------------------+--------+-------+-----------+---------+----------+
    |index|               title|         description|amount(in rupees)|price(in rupees)|location|carpet_area|       status|       floor|transaction|furnishing|facing|overlooking|             society|bathroom|balcony|car_parking|ownership|super_area|
    +-----+--------------------+--------------------+-----------------+----------------+--------+-----------+-------------+------------+-----------+----------+------+-----------+--------------------+--------+-------+-----------+---------+----------+
    |    0|1 BHK Ready to Oc...|Bhiwandi, Thane h...|          42 Lac |            6000|   thane|   500 sqft|Ready to Move|10 out of 11|     Resale|      NULL|  NULL|       NULL|Srushti Siddhi Ma...|       1|      2|       NULL|     NULL|      NULL|
    |    1|2 BHK Ready to Oc...|One can find this...|          98 Lac |           13799|   thane|   473 sqft|Ready to Move| 3 out of 22|     Resale|      NULL|  East|Garden/Park|         Dosti Vihar|       2|   NULL|     1 Open| Freehold|      NULL|
    |    2|2 BHK Ready to Oc...|Up for immediate ...|         1.40 Cr |           17500|   thane|   779 sqft|Ready to Move|10 out of 29|     Resale|      NULL|  East|Garden/Park|Sunrise by Kalpataru|       2|   NULL|  1 Covered| Freehold|      NULL|
    +-----+--------------------+--------------------+-----------------+----------------+--------+-----------+-------------+------------+-----------+----------+------+-----------+--------------------+--------+-------+-----------+---------+----------+
    only showing top 3 rows
    


## 1.- Objetivos de ingeniería de datos (ETL)

### 1.1.- Estandarización monetaria (de INR a USD)


```python
df_stats = (df
    .withColumn("currency", f.split(col("amount(in rupees)"), " ")[1])
    .withColumn("amount(in rupees)", 
                f.split(col("amount(in rupees)"), " ")[0]
                .cast(DecimalType(10, 2)))
    .withColumn("amount(in rupees)", 
        f.when(col("currency") == "Lac", col("amount(in rupees)") * 100000)
        .otherwise(col("amount(in rupees)") * 10000000)
               )
    .withColumn("price(in rupees)", col("price(in rupees)").cast(DecimalType(10, 2)))
    .withColumn("amount_usd", col("amount(in rupees)") * 0.012)
          )
df_stats.drop("currency")

df_stats.select("amount(in rupees)", "price(in rupees)", "amount_usd").show(3)
```

    +-----------------+----------------+----------+
    |amount(in rupees)|price(in rupees)|amount_usd|
    +-----------------+----------------+----------+
    |       4200000.00|         6000.00|   50400.0|
    |       9800000.00|        13799.00|  117600.0|
    |      14000000.00|        17500.00|  168000.0|
    +-----------------+----------------+----------+
    only showing top 3 rows
    


### 1.2.- Estandarización de superficie (de sqft a m2)


```python
df_stats = (df_stats
            .withColumn("carpet_area",
                       f.split(col("carpet_area"), " ")[0]
                       .cast(IntegerType())
                       )
            .withColumn("area_m2", col("carpet_area") * 0.0929)
           )

df_stats.select("carpet_area", "area_m2").show(3)
```

    +-----------+------------------+
    |carpet_area|           area_m2|
    +-----------+------------------+
    |        500|46.449999999999996|
    |        473|           43.9417|
    |        779|           72.3691|
    +-----------+------------------+
    only showing top 3 rows
    


## 2.- Objetivos de análisis estadístico

### 2.1.- Medidas de dispersión (varianza y desviación estándar)


```python
df_stats.show(3)
```

    +-----+--------------------+--------------------+-----------------+----------------+--------+-----------+-------------+------------+-----------+----------+------+-----------+--------------------+--------+-------+-----------+---------+----------+--------+----------+------------------+
    |index|               title|         description|amount(in rupees)|price(in rupees)|location|carpet_area|       status|       floor|transaction|furnishing|facing|overlooking|             society|bathroom|balcony|car_parking|ownership|super_area|currency|amount_usd|           area_m2|
    +-----+--------------------+--------------------+-----------------+----------------+--------+-----------+-------------+------------+-----------+----------+------+-----------+--------------------+--------+-------+-----------+---------+----------+--------+----------+------------------+
    |    0|1 BHK Ready to Oc...|Bhiwandi, Thane h...|       4200000.00|         6000.00|   thane|        500|Ready to Move|10 out of 11|     Resale|      NULL|  NULL|       NULL|Srushti Siddhi Ma...|       1|      2|       NULL|     NULL|      NULL|     Lac|   50400.0|46.449999999999996|
    |    1|2 BHK Ready to Oc...|One can find this...|       9800000.00|        13799.00|   thane|        473|Ready to Move| 3 out of 22|     Resale|      NULL|  East|Garden/Park|         Dosti Vihar|       2|   NULL|     1 Open| Freehold|      NULL|     Lac|  117600.0|           43.9417|
    |    2|2 BHK Ready to Oc...|Up for immediate ...|      14000000.00|        17500.00|   thane|        779|Ready to Move|10 out of 29|     Resale|      NULL|  East|Garden/Park|Sunrise by Kalpataru|       2|   NULL|  1 Covered| Freehold|      NULL|      Cr|  168000.0|           72.3691|
    +-----+--------------------+--------------------+-----------------+----------------+--------+-----------+-------------+------------+-----------+----------+------+-----------+--------------------+--------+-------+-----------+---------+----------+--------+----------+------------------+
    only showing top 3 rows
    



```python
df_metrics = (df_stats
            .agg(
                f.stddev("amount_usd").alias("stddev amount_usd"),
                f.variance("amount_usd").alias("varianza amount_usd")
            )
)

df_metrics.show()
```

    [Stage 4:======================>                                    (3 + 5) / 8]

    +-----------------+--------------------+
    |stddev amount_usd| varianza amount_usd|
    +-----------------+--------------------+
    |472949.7097866941|2.236814279873181...|
    +-----------------+--------------------+
    


                                                                                    

**Pregunta:** Si la desviación estándar es muy alta en comparación con el precio medio (por ejemplo, si la media es $100k y la desviación es $80k), ¿podemos decir que el “precio promedio” es un buen representante del mercado? ¿O los precios son demasiado dispares para confiar en el promedio?

No. Son demasiado dispares para confiar en el promedio. Una desviación estandar alta indica que los datos están muy dispersos.

### 2.2 Medidas de forma (skewness y kurtosis)


```python
df_metrics = (df_stats
              .agg(
                  f.skewness("amount_usd").alias("skewness amount_usd"),
                  f.kurtosis("amount_usd").alias("skewness amount_usd")
             )
)

df_metrics.show()
```

    26/02/18 11:35:03 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors
    [Stage 7:============================================>              (6 + 2) / 8]

    +-------------------+-------------------+
    |skewness amount_usd|skewness amount_usd|
    +-------------------+-------------------+
    |  270.7690536208719|  91491.17725573125|
    +-------------------+-------------------+
    


                                                                                    

**Pregunta:** Suponiendo que has obtenido un valor positivo, ¿qué significa esto para el negocio? ¿Hay más oferta de casas “baratas” con algunas pocas mansiones ultra-caras, o hay muchas casas caras y pocas baratas?

Hay muchas más ofertas de casas baratas. Que el `skewness` (sesgo) sea positivo indica que la montaña de datos (donde se agrupan la mayoría de los datos) es a la izquierda de la gráfica. Es decir, en los valores más bajos. Esto luego deja colas largas de datos con valores más altos (pocos registros en valores más altos).

**Pregunta:** Supón que obtienes una kurtosis superior a 3. ¿Deberíamos preocuparnos por la presencia de datos erróneos o propiedades de lujo extremo que podrían distorsionar nuestros análisis futuros?

Significa que tenemos que tratar los datos. Una kurtosis superior a 3 quiere decir que hay valores muy altos muy anormalmente extremos y esto puede ser muy problemático en el futuro.

## 3.- Interpretación para IA

### 3.1.- Pre-procesamiento para redes neuronales


```python
df_metrics = (df_stats
              .agg(
                  f.stddev("amount_usd").alias("stddev amount_usd"),
                  f.stddev("area_m2").alias("stddev area m2")
              )   
)

df_metrics.show()
```

    [Stage 10:=======>                                                  (1 + 7) / 8]

    +-----------------+------------------+
    |stddev amount_usd|    stddev area m2|
    +-----------------+------------------+
    |472949.7097866941|283.10876647919014|
    +-----------------+------------------+
    


                                                                                    


```python
df_mean_std = (df_stats
                .agg(
                    f.mean("amount_usd").alias("amount_usd_mean"),
                    f.stddev("amount_usd").alias("amount_usd_std"),
                    f.mean("area_m2").alias("area_m2_mean"),
                    f.stddev("area_m2").alias("area_m2_std")
                )
)

df_stats = df_stats.join(df_mean_std)

df_stats = (df_stats
            .withColumn("norm_amount_usd", 
                           (col("amount_usd") - col("amount_usd_mean")) / col("amount_usd_std")
                       )
            .withColumn("norm_area_m2",
                           (col("area_m2") - col("area_m2_mean")) / col("area_m2_std")
                       )
)

df_stats.select("norm_amount_usd", "norm_area_m2").show(3)
```

                                                                                    

    +--------------------+--------------------+
    |     norm_amount_usd|        norm_area_m2|
    +--------------------+--------------------+
    | -0.1973299472301128|-0.22972093599364965|
    |-0.05524295867839553|-0.23858078173842762|
    | 0.05132228273539241|-0.13816919663094365|
    +--------------------+--------------------+
    only showing top 3 rows
    


Comprobación. Los valores de la media prácticamente 0 y los de la deviación estándar son prácticamente 1.


```python
df_test = (df_stats
                .agg(
                    f.mean("norm_amount_usd").alias("mean norm amount_usd"),
                    f.stddev("norm_amount_usd").alias("stddev amount_usd_std"),
                    f.mean("norm_area_m2").alias("mean area_m2_mean"),
                    f.stddev("norm_area_m2").alias("std area_m2_std")
                )
)
df_test.show(truncate = False)
```

    [Stage 36:>                                                         (0 + 8) / 8]

    +----------------------+---------------------+---------------------+-----------------+
    |mean norm amount_usd  |stddev amount_usd_std|mean area_m2_mean    |std area_m2_std  |
    +----------------------+---------------------+---------------------+-----------------+
    |-3.260158409740177E-16|1.0000000000000033   |5.141276292026965E-15|0.999999999999996|
    +----------------------+---------------------+---------------------+-----------------+
    


                                                                                    

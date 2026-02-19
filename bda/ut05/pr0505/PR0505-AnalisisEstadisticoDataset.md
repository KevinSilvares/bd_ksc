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
    26/02/19 08:45:39 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession inciada correctamente.


    26/02/19 08:45:52 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors


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

    [Stage 4:=======>                                                   (1 + 7) / 8]

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
                  f.kurtosis("amount_usd").alias("kurtosis amount_usd")
             )
)

df_metrics.show()
```

    [Stage 7:=============================>                             (4 + 4) / 8]

    +-------------------+-------------------+
    |skewness amount_usd|kurtosis amount_usd|
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

    [Stage 10:=====================>                                    (3 + 5) / 8]

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

    [Stage 20:===========================================>              (6 + 2) / 8]

    +----------------------+---------------------+---------------------+-----------------+
    |mean norm amount_usd  |stddev amount_usd_std|mean area_m2_mean    |std area_m2_std  |
    +----------------------+---------------------+---------------------+-----------------+
    |-3.260158409740177E-16|1.0000000000000033   |5.141276292026965E-15|0.999999999999996|
    +----------------------+---------------------+---------------------+-----------------+
    


                                                                                    

### 3.2.- Gestión de outliers (kurtosis)


```python
quantile_98 = df_stats.approxQuantile("amount_usd", [0.98], 0.01)[0]
print(quantile_98)
```

    [Stage 64:=====================>                                    (3 + 5) / 8]

    522000.0


                                                                                    


```python
df_stats = (df_stats
            .withColumn("amount_usd", 
                       f.when(col("amount_usd") > quantile_98, quantile_98)
                       .otherwise(col("amount_usd"))
                       )
)
df_stats.select("amount_usd").show(10)
```

                                                                                    

    +----------+
    |amount_usd|
    +----------+
    |   50400.0|
    |  117600.0|
    |  168000.0|
    |   30000.0|
    |  192000.0|
    |   54000.0|
    |   19800.0|
    |   72000.0|
    |   72000.0|
    |  192000.0|
    +----------+
    only showing top 10 rows
    



```python
(df_stats
    .agg(
        f.kurtosis("amount_usd").alias("kurtosis amount_usd")
    )
).show()
```

    [Stage 58:>                                                         (0 + 8) / 8]

    +-------------------+
    |kurtosis amount_usd|
    +-------------------+
    | 2.6874337988728474|
    +-------------------+
    


                                                                                    

Al poner el percentil `99` no ocurría ningún cambio (era un valor demasiado grande). Al probar con el percentil `98` ocurren cambios muy grandes.

La kurtosis ha bajado de `91491.177` a `2.687`.

Esto ha aplanado muchísimo la kurtosis en comparación a los datos originales. Se debe a que el 2% de los datos son extremadamente altos y son capaces de mover toda la media.

## 4.- Análisis de segmentos (grouping & aggregation)

### 4.1.- Ingeniería de varaible (Extracción de `BHK` - Bedroom-Hall-Kitchen)


```python
df_stats = (df_stats
            .withColumn("num_bedrooms", f.split(col("title"), " ")[0])
)

df_stats.select("num_bedrooms").show(3)
```

                                                                                    

    +------------+
    |num_bedrooms|
    +------------+
    |           1|
    |           2|
    |           2|
    +------------+
    only showing top 3 rows
    


### 4.2.- Cálculo de estadísticas por grupo


```python
df_group_stats = (df_stats.groupBy("num_bedrooms")
                    .agg(
                        f.mean("amount_usd").alias("mean amount_usd"),
                        f.stddev("amount_usd").alias("stddev amount_usd"),
                        f.skewness("amount_usd").alias("skewness amount_usd")
                    )
)

df_group_stats.show()
```

    [Stage 85:==================================================>       (7 + 1) / 8]

    +------------+------------------+------------------+--------------------+
    |num_bedrooms|   mean amount_usd| stddev amount_usd| skewness amount_usd|
    +------------+------------------+------------------+--------------------+
    |           7|365714.28571428574|175392.59472883763| -0.4535274057936664|
    |           3|159792.60432422813|102307.33367249861|  1.4862748420224012|
    |           8|          481320.0|128079.07557442784| -3.1823856250984415|
    |           5|421445.37313432834|122973.35364247691| -1.3049367666576699|
    |           6| 378769.5652173913|163999.10194013725| -0.5550698823138144|
    |           9|396857.14285714284|146823.50921137547| -0.5632707818439866|
    |           1|  42372.8883087824|32255.951762206594|   4.034451609718177|
    |          10|335345.45454545453|160865.68536289126| -0.2959601334705853|
    |           4|  312863.955922865|146091.91560877932|0.010915875785437705|
    |            |53031.347962382446| 73502.53267617724|   4.276823580082054|
    |           >|          421500.0|127536.92275833954| -0.9667383140399325|
    |           2| 73373.51949599864| 46557.80693436289|  2.6693929793525335|
    |          "4|          119400.0|              NULL|                NULL|
    |          "3|           58800.0|              NULL|                NULL|
    +------------+------------------+------------------+--------------------+
    


                                                                                    

Existe algún dato con nombre y valores extraños que convendría limpiar o tratar de alguna manera.

### 4.3.- Preguntas de análisis para el modelo

#### A. Análisis de variabilidad (Desviación Estándar)

**Pregunta:** Si la desviación es mucho mayor en los pisos de 3 BHK que en los de 1 BHK, ¿qué nos indica esto sobre la homogeneidad del producto?

Supondría que las viviendas no son demasiado parecidas entre sí. Aunque faltan datos, podríamos suponer que incluso cuando el número de habitaciones no varía demasiados, quizá hay otras calidades, materiales de construcción, infraestructura alrededor del inmueble, comodidades, etc, que pueden hacer que estos pisos se encarezcan mucho más. Por lo que podríamos deducir que en el dataset hay datos muy variados y poco similares.

#### B. Confiabilidad del precio promedio

**Pregunta:** Basándote en lo anterior, ¿en qué segmento (1 BHK o 3 BHK) dirías que el “Precio Promedio” es un indicador más fiable del valor real de una propiedad? Es decir, si tuvieras que tasar una propiedad “a ciegas” usando solo el promedio del mercado, ¿en qué tipo de apartamento tendrías más riesgo de equivocarte drásticamente por exceso o por defecto?

Sería más sencillo fijarse en las de `1 BHK` porque la media es de `42.372,88` y la desviación estándar es de `32.255,95`. Esto quiere decir que el `68%` precio de las casas sube o baja `32.255`, por lo que hay mucho menos riesgo de equivocarse.

En el caso de las `3 BHK` la media es de `159.792.60` y la desviación estándar es de `102.307.33`. Esto implica que, al igual que en el caso anterior, el `68%` precio de las casas sube o baja del precio de la media el valor de la desviación estándar.

#### C. Detección de anomalías de mercado

**Pregunta:** ¿Qué segmento tiene una curtosis más alta (colas más pesadas)?

El segmento de `1 BHK` (`4.03`).

**Pregunta:** Si el segmento de 3 BHK tiene una curtosis muy elevada, significa que existen propiedades con precios desorbitados que rompen la norma. ¿Consideras que estas “mansiones” representan la realidad del barrio, o son excepciones que deberían analizarse en un estudio de mercado aparte para no distorsionar la visión general?

Probablemente sean excepciones que elevan la kurtosis y haría falta más estudio para no meter valores extremos en el estudio/modelo. De todos modos, en el ejemplo, el segmento de `3 BHK` tiene una kurtosis relativamente menos elevada que en el caso anterior (`1.48`). Claramente existen estos valores extremos, pero son datos manejables y no son tan extremos con el caso del segmento `1 BHK`.

# PR0507 - Creación de un motor de recomendación gastronómico


```python
!pip install numpy
```

    Requirement already satisfied: numpy in /usr/local/lib/python3.10/site-packages (2.2.6)
    [33mWARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv[0m[33m
    [0m
    [1m[[0m[34;49mnotice[0m[1;39;49m][0m[39;49m A new release of pip is available: [0m[31;49m23.0.1[0m[39;49m -> [0m[32;49m26.0.1[0m
    [1m[[0m[34;49mnotice[0m[1;39;49m][0m[39;49m To update, run: [0m[32;49mpip install --upgrade pip[0m



```python
from pyspark.sql import SparkSession, Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType, DecimalType, TimestampType
from pyspark.sql.functions import col, lit
from pyspark.ml.recommendation import ALS # necesita numpy
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.evaluation import RegressionEvaluator
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
!head -n 10000 ratings.csv > ratings_small.csv
# Es un dataset gigante y en el ordenador del centro tarda demasiado. Haré las pruebas con uno reducido.
```


```python
def load_dataset(spark):
    schema = StructType([
        StructField("user_id", IntegerType(), False),
        StructField("venue_id", DoubleType(), False),
        StructField("rating", DoubleType(), False),
    ])

    df = (spark.read
            .format("csv")
            .schema(schema)
            .option("header", "true")
            .option("delimiter", ",")
            .load("ratings_small.csv")
         )
    return df
```

## 1.- Preparación de datos


```python
spark = connect_spark()
df = load_dataset(spark)
df.show(3)
```

    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
    26/03/05 09:37:10 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


    SparkSession inciada correctamente.


                                                                                    

    +-------+--------+------+
    |user_id|venue_id|rating|
    +-------+--------+------+
    |      1|     1.0|   5.0|
    |      1|    51.0|   4.0|
    |      1|    51.0|   2.0|
    +-------+--------+------+
    only showing top 3 rows
    



```python
train, test = (df
               .randomSplit([0.8, 0.2], seed = 42)
              )
print(f"Entrenamiento: {train.count()}")
print(f"Test: {test.count()}")
```

                                                                                    

    Entrenamiento: 8078
    Test: 1921


## 2.- Construcción y búsqueda de un modelo óptimo


```python
# userCol, itemCol, ratingCol | coldStartStragey
als = ALS(
    # maxIter = 0,
    # regParam = 1.5,
    # rank = 2,
    userCol = "user_id",
    itemCol = "venue_id",
    ratingCol = "rating",
    coldStartStrategy = "drop"
)

evaluador = RegressionEvaluator(
    metricName = "rmse",
    labelCol = "rating",
    predictionCol = "prediction"
)

grid_params = (ParamGridBuilder()
               .addGrid(als.rank, [5, 10, 15])
               .addGrid(als.regParam, [0.01, 0.1])
               .addGrid(als.maxIter, [10])
               .build()
)

validador_cruzado = CrossValidator(
    estimator = als,
    estimatorParamMaps = grid_params,
    evaluator = evaluador,
    numFolds = 3
)

modelo = validador_cruzado.fit(df)
print("Modelo entrenado.")
```

    26/03/05 09:37:28 WARN GarbageCollectionMetrics: To enable non-built-in garbage collector(s) List(G1 Concurrent GC), users should configure it(them) to spark.eventLog.gcMetrics.youngGenerationGarbageCollectors or spark.eventLog.gcMetrics.oldGenerationGarbageCollectors
                                                                                    

    Modelo entrenado.


## 4.- Puesta en Producción


```python
ventana = Window.partitionBy("user_id").orderBy(col("rating").desc())

user_ratings = (df
                .filter(col("user_id") == 1)
                .withColumn("rankings", f.rank().over(ventana))
               )
user_ratings.show(15)
```

    +-------+--------+------+--------+
    |user_id|venue_id|rating|rankings|
    +-------+--------+------+--------+
    |      1|     1.0|   5.0|       1|
    |      1|    51.0|   5.0|       1|
    |      1|    52.0|   5.0|       1|
    |      1|    53.0|   5.0|       1|
    |      1|    54.0|   5.0|       1|
    |      1|    55.0|   5.0|       1|
    |      1|    56.0|   5.0|       1|
    |      1|    57.0|   5.0|       1|
    |      1|    58.0|   5.0|       1|
    |      1|    59.0|   5.0|       1|
    |      1|    51.0|   4.0|      11|
    |      1|    55.0|   4.0|      11|
    |      1|    60.0|   4.0|      11|
    |      1|    61.0|   4.0|      11|
    |      1|    62.0|   4.0|      11|
    +-------+--------+------+--------+
    only showing top 15 rows
    


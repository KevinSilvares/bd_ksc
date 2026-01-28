# PR0503 - Limpieza de datos sobre dataset de cultivos

## Conexión e importaciones


```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType
from pyspark.sql.functions import col, lit, split, upper, concat, concat_ws, lpad, log, round, greatest, to_date, date_add, month
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

    return df
```

### 1.- Creación de un ID único


```python
spark = connect_spark()
df = load_crops_df(spark)
            # CODIGO_XXC-MAIZE

# df_eng = (df
#             .withColumn("Crop_ID", 
#                         concat(
#                             lit("CODIGO_"),
#                             split(col("region"), "_")[1],
#                             lit("-"),
#                             upper(col("crop"))
#                         )
#             )
#          )

df_eng = (df
            .withColumn("Crop_ID", split(col("region"), "_")[1])
            .withColumn("Crop_ID", lpad(col("Crop_ID"), 3, "X"))
            .withColumn("Crop_ID", concat_ws("_", col("Crop_ID"), upper(col("crop"))))
            .withColumn("Crop_ID", concat(lit("CODIGO_"), col("Crop_ID")))
         )
df_eng.show(3)
```

    SparkSession inciada correctamente.
    +------+--------+---------+-------+-----------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+
    |  crop|  region|soil_type|soil_ph|rainfall_mm|temperature_C|humidity_pct|fertilizer_used_kg|irrigation|pesticides_used_kg|planting_density|previous_crop|yield_ton_per_ha|          Crop_ID|
    +------+--------+---------+-------+-----------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+
    | Maize|Region_C|    Sandy|   7.01|     1485.4|         19.7|        40.3|             105.1|      Drip|              10.2|            23.2|         Rice|          101.48| CODIGO_XXC_MAIZE|
    |Barley|Region_D|     Loam|   5.79|      399.4|         29.1|        55.4|             221.8| Sprinkler|              35.5|             7.4|       Barley|          127.39|CODIGO_XXD_BARLEY|
    |  Rice|Region_C|     Clay|   7.24|      980.9|         30.5|        74.4|              61.2| Sprinkler|              40.0|             5.1|        Wheat|           68.99|  CODIGO_XXC_RICE|
    +------+--------+---------+-------+-----------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+
    only showing top 3 rows
    


### 2.- Transformación matemática


```python
df_eng = (df_eng
          .withColumn("rainfall_mm", log(col("rainfall_mm")))
          .withColumn("bround", col("yield_ton_per_ha"))
          .withColumn("yield_ton_per_ha", round(col("yield_ton_per_ha"), 1))
         )
df_eng.show(3)
```

    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+
    |  crop|  region|soil_type|soil_ph|      rainfall_mm|temperature_C|humidity_pct|fertilizer_used_kg|irrigation|pesticides_used_kg|planting_density|previous_crop|yield_ton_per_ha|          Crop_ID|bround|
    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+
    | Maize|Region_C|    Sandy|   7.01|7.303439375235196|         19.7|        40.3|             105.1|      Drip|              10.2|            23.2|         Rice|           101.5| CODIGO_XXC_MAIZE|101.48|
    |Barley|Region_D|     Loam|   5.79|5.989963420981715|         29.1|        55.4|             221.8| Sprinkler|              35.5|             7.4|       Barley|           127.4|CODIGO_XXD_BARLEY|127.39|
    |  Rice|Region_C|     Clay|   7.24| 6.88847051757027|         30.5|        74.4|              61.2| Sprinkler|              40.0|             5.1|        Wheat|            69.0|  CODIGO_XXC_RICE| 68.99|
    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+
    only showing top 3 rows
    


### 3.- Comparación de insumos


```python
df_eng = (df_eng
            .withColumn("max_quimico_kg", greatest(col("fertilizer_used_kg"), col("pesticides_used_kg")))
            )
df_eng.show(3)
```

    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+--------------+
    |  crop|  region|soil_type|soil_ph|      rainfall_mm|temperature_C|humidity_pct|fertilizer_used_kg|irrigation|pesticides_used_kg|planting_density|previous_crop|yield_ton_per_ha|          Crop_ID|bround|max_quimico_kg|
    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+--------------+
    | Maize|Region_C|    Sandy|   7.01|7.303439375235196|         19.7|        40.3|             105.1|      Drip|              10.2|            23.2|         Rice|           101.5| CODIGO_XXC_MAIZE|101.48|         105.1|
    |Barley|Region_D|     Loam|   5.79|5.989963420981715|         29.1|        55.4|             221.8| Sprinkler|              35.5|             7.4|       Barley|           127.4|CODIGO_XXD_BARLEY|127.39|         221.8|
    |  Rice|Region_C|     Clay|   7.24| 6.88847051757027|         30.5|        74.4|              61.2| Sprinkler|              40.0|             5.1|        Wheat|            69.0|  CODIGO_XXC_RICE| 68.99|          61.2|
    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+--------------+
    only showing top 3 rows
    


### 4.- Simulación de fechas


```python
df_eng = (df_eng
            .withColumn("fecha_siembra", lit("2023-04-01")) 
            .withColumn("fecha_siembra", to_date(col("fecha_siembra"), "yyyy-MM-dd"))
            .withColumn("fecha_estimada_cosecha", date_add(col("fecha_siembra"), 150))
            .withColumn("mes_cosecha", month(col("fecha_estimada_cosecha")))
        )

df_eng.show(3)
```

    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+--------------+-------------+----------------------+-----------+
    |  crop|  region|soil_type|soil_ph|      rainfall_mm|temperature_C|humidity_pct|fertilizer_used_kg|irrigation|pesticides_used_kg|planting_density|previous_crop|yield_ton_per_ha|          Crop_ID|bround|max_quimico_kg|fecha_siembra|fecha_estimada_cosecha|mes_cosecha|
    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+--------------+-------------+----------------------+-----------+
    | Maize|Region_C|    Sandy|   7.01|7.303439375235196|         19.7|        40.3|             105.1|      Drip|              10.2|            23.2|         Rice|           101.5| CODIGO_XXC_MAIZE|101.48|         105.1|   2023-04-01|            2023-08-29|          8|
    |Barley|Region_D|     Loam|   5.79|5.989963420981715|         29.1|        55.4|             221.8| Sprinkler|              35.5|             7.4|       Barley|           127.4|CODIGO_XXD_BARLEY|127.39|         221.8|   2023-04-01|            2023-08-29|          8|
    |  Rice|Region_C|     Clay|   7.24| 6.88847051757027|         30.5|        74.4|              61.2| Sprinkler|              40.0|             5.1|        Wheat|            69.0|  CODIGO_XXC_RICE| 68.99|          61.2|   2023-04-01|            2023-08-29|          8|
    +------+--------+---------+-------+-----------------+-------------+------------+------------------+----------+------------------+----------------+-------------+----------------+-----------------+------+--------------+-------------+----------------------+-----------+
    only showing top 3 rows
    


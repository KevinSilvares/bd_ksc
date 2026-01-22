# PR0502 - Manipulación básica de dataframes

Partimos de la PR 501.

## Conexión e importaciones


```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, DoubleType
from pyspark.sql.functions import col, lit
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

### 1.- Selección de características


```python
spark = connect_spark()
df = load_crops_df(spark)

df_sel = df.select("crop", "region", "temperature_C", "rainfall_mm", "irrigation", "yield_ton_per_ha")
df_sel.show(3)
```

    SparkSession inciada correctamente.
    +------+--------+-------------+-----------+----------+----------------+
    |  crop|  region|temperature_C|rainfall_mm|irrigation|yield_ton_per_ha|
    +------+--------+-------------+-----------+----------+----------------+
    | Maize|Region_C|         19.7|     1485.4|      Drip|          101.48|
    |Barley|Region_D|         29.1|      399.4| Sprinkler|          127.39|
    |  Rice|Region_C|         30.5|      980.9| Sprinkler|           68.99|
    +------+--------+-------------+-----------+----------+----------------+
    only showing top 3 rows
    


### 2.- Normalización de nombres


```python
df_renamed = (df_sel
              .withColumnRenamed("temperature_C", "Temperatura")
              .withColumnRenamed("rainfall_mm", "Lluvia")
              .withColumnRenamed("yield_ton_per_ha", "Rendimiento")
             )
df_renamed.show(3)
```

    +------+--------+-----------+------+----------+-----------+
    |  crop|  region|Temperatura|Lluvia|irrigation|Rendimiento|
    +------+--------+-----------+------+----------+-----------+
    | Maize|Region_C|       19.7|1485.4|      Drip|     101.48|
    |Barley|Region_D|       29.1| 399.4| Sprinkler|     127.39|
    |  Rice|Region_C|       30.5| 980.9| Sprinkler|      68.99|
    +------+--------+-----------+------+----------+-----------+
    only showing top 3 rows
    


### 3.- Filtrado de datos (filter)


```python
df_renamed.filter((col("crop") == "Maize") & (col("Temperatura") > 25)).show()
```

    +-----+--------+-----------+------+----------+-----------+
    | crop|  region|Temperatura|Lluvia|irrigation|Rendimiento|
    +-----+--------+-----------+------+----------+-----------+
    |Maize|Region_D|       26.4|1054.3|      Drip|     169.06|
    |Maize|Region_C|       32.4| 846.1|      None|      162.2|
    |Maize|Region_A|       26.6| 362.5| Sprinkler|      95.23|
    |Maize|Region_C|       33.7|1193.3|      None|     110.57|
    |Maize|Region_C|       27.8| 695.2|     Flood|     143.84|
    |Maize|Region_D|       30.2|1001.4|     Flood|     138.61|
    |Maize|Region_A|       27.7| 747.7| Sprinkler|     114.58|
    |Maize|Region_B|       28.9|1392.9|      Drip|     169.23|
    |Maize|Region_B|       34.7| 694.4|      Drip|      96.08|
    |Maize|Region_D|       29.5| 848.8|     Flood|      93.45|
    |Maize|Region_D|       32.8|1067.7|     Flood|      154.6|
    |Maize|Region_A|       28.5| 406.1| Sprinkler|      55.26|
    |Maize|Region_D|       26.0| 391.4| Sprinkler|     100.34|
    |Maize|Region_C|       25.9|1444.8| Sprinkler|      135.8|
    |Maize|Region_D|       27.8| 823.3| Sprinkler|     161.48|
    |Maize|Region_D|       28.7| 955.8|     Flood|       91.4|
    |Maize|Region_A|       33.2| 248.4|      None|     149.49|
    |Maize|Region_B|       34.3| 410.4|     Flood|      37.78|
    |Maize|Region_A|       27.1| 763.9|      Drip|     110.63|
    |Maize|Region_C|       28.8|1215.0|     Flood|     127.89|
    +-----+--------+-----------+------+----------+-----------+
    only showing top 20 rows
    


### 4.- Encadenamiento


```python
(df
    .select("crop", "region", "temperature_C", "rainfall_mm", "irrigation", "yield_ton_per_ha")
    .withColumnRenamed("temperature_C", "Temperatura")
    .withColumnRenamed("rainfall_mm", "Lluvia")
    .withColumnRenamed("yield_ton_per_ha", "Rendimiento")
    .filter((col("crop") == "Maize") & (col("Temperatura") > 25))
).show()
```

    +-----+--------+-----------+------+----------+-----------+
    | crop|  region|Temperatura|Lluvia|irrigation|Rendimiento|
    +-----+--------+-----------+------+----------+-----------+
    |Maize|Region_D|       26.4|1054.3|      Drip|     169.06|
    |Maize|Region_C|       32.4| 846.1|      None|      162.2|
    |Maize|Region_A|       26.6| 362.5| Sprinkler|      95.23|
    |Maize|Region_C|       33.7|1193.3|      None|     110.57|
    |Maize|Region_C|       27.8| 695.2|     Flood|     143.84|
    |Maize|Region_D|       30.2|1001.4|     Flood|     138.61|
    |Maize|Region_A|       27.7| 747.7| Sprinkler|     114.58|
    |Maize|Region_B|       28.9|1392.9|      Drip|     169.23|
    |Maize|Region_B|       34.7| 694.4|      Drip|      96.08|
    |Maize|Region_D|       29.5| 848.8|     Flood|      93.45|
    |Maize|Region_D|       32.8|1067.7|     Flood|      154.6|
    |Maize|Region_A|       28.5| 406.1| Sprinkler|      55.26|
    |Maize|Region_D|       26.0| 391.4| Sprinkler|     100.34|
    |Maize|Region_C|       25.9|1444.8| Sprinkler|      135.8|
    |Maize|Region_D|       27.8| 823.3| Sprinkler|     161.48|
    |Maize|Region_D|       28.7| 955.8|     Flood|       91.4|
    |Maize|Region_A|       33.2| 248.4|      None|     149.49|
    |Maize|Region_B|       34.3| 410.4|     Flood|      37.78|
    |Maize|Region_A|       27.1| 763.9|      Drip|     110.63|
    |Maize|Region_C|       28.8|1215.0|     Flood|     127.89|
    +-----+--------+-----------+------+----------+-----------+
    only showing top 20 rows
    


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
    ])

    df = (spark.read
            .format("csv")
            .schema(schema)
            .option("header", "true")
            .load("world_famous_places_2024.csv")
         )
    return df
```

### 1.- Selección de datos críticos


```python
spark = connect_spark()
df = load_world_places_df(spark)

df_base = df.select("place_name", "country", "unesco_world_heritage", "entry_fee_usd", "annual_visitors_million")
df_base.show(3)
```

### 2.- Traducción y simplificación


```python
df_es = (df_base
            .withColumnRenamed("place_name", "Lugar")
            .withColumnRenamed("unesco_world_heritage", "Es_UNESCO")
            .withColumnRenamed("entry_fee_usd", "Precio_Entrada")
            .withColumnRenamed("annual_visitors_million", "Visitanes_Millones")
        )
df_es.show(3)
```

    +-------------+-------------+---------+--------------+------------------+
    |        Lugar|      country|Es_UNESCO|Precio_Entrada|Visitanes_Millones|
    +-------------+-------------+---------+--------------+------------------+
    | Eiffel Tower|       France|       No|          35.0|               7.0|
    | Times Square|United States|       No|           0.0|              50.0|
    |Louvre Museum|       France|      Yes|          22.0|               8.7|
    +-------------+-------------+---------+--------------+------------------+
    only showing top 3 rows
    


### 3.- Filtrado


```python
df_filtered = (df_es
                .filter((col("Es_UNESCO") == "Yes") & (col("Precio_Entrada") < 20))
              )
df_filtered.show()
```

    +--------------------+--------------+---------+--------------+------------------+
    |               Lugar|       country|Es_UNESCO|Precio_Entrada|Visitanes_Millones|
    +--------------------+--------------+---------+--------------+------------------+
    | Great Wall of China|         China|      Yes|          10.0|              10.0|
    |           Taj Mahal|         India|      Yes|          15.0|               7.5|
    |           Colosseum|         Italy|      Yes|          18.0|              7.65|
    |      Forbidden City|         China|      Yes|           8.0|               9.0|
    |Notre-Dame Cathedral|        France|      Yes|           0.0|              13.0|
    |           Acropolis|        Greece|      Yes|          13.0|               4.0|
    |             Big Ben|United Kingdom|      Yes|           0.0|               5.5|
    +--------------------+--------------+---------+--------------+------------------+
    


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
    return df
```

### 1.- Selección y saneamiento


```python
spark = connect_spark()
df = load_cyl_turistic_places(spark)

df_contactos = df.select("nombre", "tipo", "provincia", "web", "email")
df_contactos.show(3)
```

    SparkSession inciada correctamente.


                                                                                    

    +--------------------+--------------------+---------+--------------------+--------------------+
    |              nombre|                tipo|provincia|                 web|               email|
    +--------------------+--------------------+---------+--------------------+--------------------+
    |BERNARDO MORO MEN...|Profesional de Tu...| Asturias|                NULL|bernardomoro@hotm...|
    |        LA SASTRERÍA|Casa Rural de Alq...|    Ávila|www.lasastreriade...|                NULL|
    |         LAS HAZANAS|Casa Rural de Alq...|    Ávila|                NULL|lashazanas@hotmai...|
    +--------------------+--------------------+---------+--------------------+--------------------+
    only showing top 3 rows
    


### 2.- Renombrado estándar


```python
df_limpio = (df_contactos
                .withColumnRenamed("nombre", "nombre_establecimiento")
                .withColumnRenamed("tipo", "categoria_actividad")
                .withColumnRenamed("web", "sitio_web")
                .withColumnRenamed("email", "correo_electronico")
            )
df_limpio.show(3)
```

    +----------------------+--------------------+---------+--------------------+--------------------+
    |nombre_establecimiento| categoria_actividad|provincia|           sitio_web|  correo_electronico|
    +----------------------+--------------------+---------+--------------------+--------------------+
    |  BERNARDO MORO MEN...|Profesional de Tu...| Asturias|                NULL|bernardomoro@hotm...|
    |          LA SASTRERÍA|Casa Rural de Alq...|    Ávila|www.lasastreriade...|                NULL|
    |           LAS HAZANAS|Casa Rural de Alq...|    Ávila|                NULL|lashazanas@hotmai...|
    +----------------------+--------------------+---------+--------------------+--------------------+
    only showing top 3 rows
    


### 3.- Filtrado de texto


```python
df_final = (df_limpio
               .filter((col("provincia") == "Burgos")  &
                        (col("categoria_actividad").like("%Bodegas%")) &
                        (col("sitio_web").isNotNull())
                      )
           )
df_final.show()
```

    +----------------------+--------------------+---------+--------------------+--------------------+
    |nombre_establecimiento| categoria_actividad|provincia|           sitio_web|  correo_electronico|
    +----------------------+--------------------+---------+--------------------+--------------------+
    |        BODEGAS TARSUS|g - Bodegas y los...|   Burgos|  www.tarsusvino.com|                NULL|
    |  BODEGAS DOMINIO D...|g - Bodegas y los...|   Burgos|www.dominiodecair...|bodegas@dominiode...|
    |    TERRITORIO LUTHIER|g - Bodegas y los...|   Burgos|territorioluthier...|luthier@territori...|
    |    BODEGA COVARRUBIAS|g - Bodegas y los...|   Burgos| http://valdable.com|   info@valdable.com|
    |  BODEGAS PASCUAL, ...|g - Bodegas y los...|   Burgos|222.bodegaspascua...|export@bodegaspas...|
    |   BODEGAS VINUM VITAE|g - Bodegas y los...|   Burgos|      www.avañate.es|vinum.vitae.bodeg...|
    |  VIÑEDOS Y BODEGAS...|g - Bodegas y los...|   Burgos|     www.ferratus.es|administracion@fe...|
    |  BODEGAS Y VIÑEDOS...|g - Bodegas y los...|   Burgos|     www.pradorey.es|   info@pradorey.com|
    |       BODEGAS ARROCAL|g - Bodegas y los...|   Burgos|     www.arrocal.com|  blanca@arrocal.com|
    |           VIÑA ARNÁIZ|g - Bodegas y los...|   Burgos|  www.vinaarnaiz.com|   enoturismo@jgc.es|
    |    BODEGAS MONTE AMÁN|g - Bodegas y los...|   Burgos|   www.monteaman.com|bodegas@monteaman...|
    |  BODEGAS PALACIO D...|g - Bodegas y los...|   Burgos|www.palaciodelerm...|info@palaciodeler...|
    |         ALONSO ANGULO|g - Bodegas y los...|   Burgos|www.alonsoangulo.com|info@alonsoangulo...|
    |  VIÑA MAMBRILLA, S.L.|g - Bodegas y los...|   Burgos|   www.mambrilla.com| bodegamambrilla.com|
    |  BODEGAS TRASLASCU...|g - Bodegas y los...|   Burgos|www.bodegastrasla...|administracion@bo...|
    |  BODEGAS RODERO, S.L.|g - Bodegas y los...|   Burgos|www.bodegasrodero...|rodero@bodegasrod...|
    |  BODEGAS HERMANOS ...|g - Bodegas y los...|   Burgos|www.perezpascuas.com|viñapedrosa@perez...|
    |    BOSQUE DE MATASNOS|g - Bodegas y los...|   Burgos|https://bosquedem...|administracion@bo...|
    |  BODEGAS PRADO DE ...|g - Bodegas y los...|   Burgos|www.pradodeolmedo...|pradodeolmedo@pra...|
    |  VISITAS ENOTURÍST...|g - Bodegas y los...|   Burgos|www.lopezcristoba...|bodega@lopezcrist...|
    +----------------------+--------------------+---------+--------------------+--------------------+
    only showing top 20 rows
    


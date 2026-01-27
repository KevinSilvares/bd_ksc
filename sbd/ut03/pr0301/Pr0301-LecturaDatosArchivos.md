# PR0301: Lectura de datos de archivos


```python
!pip install openpyxl
# !pip install xlrd
```

    Requirement already satisfied: openpyxl in /opt/conda/lib/python3.11/site-packages (3.1.2)
    Requirement already satisfied: et-xmlfile in /opt/conda/lib/python3.11/site-packages (from openpyxl) (1.1.0)



```python
import pandas as pd
import json

df_norte = pd.read_csv(
                        "ventas_norte.csv",
                        names=["id", "date", "product", "quantity", "unit_price"],
                        header=0,
                        sep=";"
                        )
df_norte["id"] = pd.to_numeric(df_norte["id"], errors="coerce")

df_sur = pd.read_excel(
                        "ventas_sur.xlsx",
                        sheet_name=None,
                        header=0,
                        usecols="A:E",
                        names=["id", "date", "product", "quantity", "unit_price"],
                        parse_dates=["date"],
                        engine="openpyxl"
                        )

df_sur = pd.concat(
                df_sur,
                ignore_index=True
        )

df_sur["id"] = pd.to_numeric(df_sur["id"], errors="coerce")

with open ("ventas_este.json") as f:
    data = json.load(f)

df = pd.json_normalize(
    data
)

df_este = df.drop(columns=["detalles_producto.categoria", "cliente.nombre", "cliente.email"])
df_este.rename(columns={
    "id_orden": "id", 
    "timestamp": "date", 
    "detalles_producto.nombre":"product", 
    "detalles_producto.specs.cantidad":"quantity", 
    "detalles_producto.specs.precio":"unit_price"
    },
    inplace=True)

df_este["id"] = df_este["id"].str.replace("ORD-", "")
df_este["id"] = pd.to_numeric(df_este["id"], errors="coerce")

print(f"Ventas norte:\n {df_norte.head(5)}")
print("----------------------------------------")
print(f"Ventas sur:\n {df_sur}")
print("----------------------------------------")
print(f"Ventas este:\n {df_este.head(5)}")
```

    Ventas norte:
          id        date  product  quantity  unit_price
    0  1000  2023-02-21   Laptop         4         423
    1  1001  2023-01-15   Laptop         2         171
    2  1002  2023-03-13   Laptop         3          73
    3  1003  2023-03-02  Teclado         1         139
    4  1004  2023-01-21  Monitor         4         692
    ----------------------------------------
    Ventas sur:
            id       date  product  quantity  unit_price
    0    2000 2023-03-01  Monitor         6         624
    1    2001 2023-03-04   Laptop         7         941
    2    2002 2023-03-26    Mouse         3         989
    3    2003 2023-02-01   Webcam         3         621
    4    2004 2023-03-28    Mouse         5         437
    ..    ...        ...      ...       ...         ...
    145  2045 2023-03-25    Mouse         5         192
    146  2046 2023-03-29  Teclado         9         319
    147  2047 2023-03-10   Laptop         1         664
    148  2048 2023-02-03   Laptop         5         345
    149  2049 2023-01-06  Monitor         6         429
    
    [150 rows x 5 columns]
    ----------------------------------------
    Ventas este:
          id                 date  product  quantity  unit_price
    0  3000  2023-03-09 00:00:00  Monitor         2         244
    1  3001  2023-01-20 00:00:00   Laptop         2         578
    2  3002  2023-01-01 00:00:00    Mouse         2         339
    3  3003  2023-02-07 00:00:00   Webcam         2         158
    4  3004  2023-03-18 00:00:00  Monitor         1         692



```python
df_total = pd.concat([df_norte, df_sur, df_este], ignore_index = True)
df_total["region"] = df_total["id"].apply(detect_region)
df_total
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>date</th>
      <th>product</th>
      <th>quantity</th>
      <th>unit_price</th>
      <th>region</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1000</td>
      <td>2023-02-21</td>
      <td>Laptop</td>
      <td>4</td>
      <td>423</td>
      <td>Norte</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1001</td>
      <td>2023-01-15</td>
      <td>Laptop</td>
      <td>2</td>
      <td>171</td>
      <td>Norte</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1002</td>
      <td>2023-03-13</td>
      <td>Laptop</td>
      <td>3</td>
      <td>73</td>
      <td>Norte</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1003</td>
      <td>2023-03-02</td>
      <td>Teclado</td>
      <td>1</td>
      <td>139</td>
      <td>Norte</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1004</td>
      <td>2023-01-21</td>
      <td>Monitor</td>
      <td>4</td>
      <td>692</td>
      <td>Norte</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>345</th>
      <td>3095</td>
      <td>2023-03-28 00:00:00</td>
      <td>Webcam</td>
      <td>1</td>
      <td>857</td>
      <td>Este</td>
    </tr>
    <tr>
      <th>346</th>
      <td>3096</td>
      <td>2023-01-18 00:00:00</td>
      <td>Webcam</td>
      <td>2</td>
      <td>375</td>
      <td>Este</td>
    </tr>
    <tr>
      <th>347</th>
      <td>3097</td>
      <td>2023-02-10 00:00:00</td>
      <td>Mouse</td>
      <td>1</td>
      <td>696</td>
      <td>Este</td>
    </tr>
    <tr>
      <th>348</th>
      <td>3098</td>
      <td>2023-01-25 00:00:00</td>
      <td>Mouse</td>
      <td>2</td>
      <td>618</td>
      <td>Este</td>
    </tr>
    <tr>
      <th>349</th>
      <td>3099</td>
      <td>2023-03-27 00:00:00</td>
      <td>Webcam</td>
      <td>1</td>
      <td>844</td>
      <td>Este</td>
    </tr>
  </tbody>
</table>
<p>350 rows × 6 columns</p>
</div>




```python
def detect_region(id):
    if id < 2000:
        return "Norte"
    elif id >= 2000 and id < 3000:
        return "Sur"
    elif id > 3000:
        return "Este"
```


```python
df_total.to_csv("ventas_consolidadas.csv", sep = ",", index = False)
```

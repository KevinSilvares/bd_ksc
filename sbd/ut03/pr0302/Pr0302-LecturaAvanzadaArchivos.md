# PR0302: Lectura avanzada de datos de archivos


```python
import pandas as pd
```

### Carga CSV


```python
df_norte = pd.read_csv("ventas_norte_v2.csv", sep = ";")
df_norte["Total_Factura"] = df_norte["Total_Factura"].str.replace("$", "")
df_norte["Total_Factura"] = pd.to_numeric(df_norte["Total_Factura"], errors = "coerce")

print(f"Tipo Total_Factura: {df_norte['Total_Factura'].dtype}")
df_norte
```

    Tipo Total_Factura: float64





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
      <th>ID_Pedido</th>
      <th>Fecha_Transaccion</th>
      <th>Cliente_Nombre</th>
      <th>Direccion_Envio</th>
      <th>Producto</th>
      <th>Unidades</th>
      <th>Precio_Unitario</th>
      <th>Total_Factura</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>N-1000</td>
      <td>2023-05-10 03:00:00</td>
      <td>Usuario_0</td>
      <td>Gran Vía, 49, Piso 4</td>
      <td>Laptop Gamer</td>
      <td>1</td>
      <td>970</td>
      <td>970.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>N-1001</td>
      <td>2023-06-18 09:00:00</td>
      <td>Usuario_1</td>
      <td>Av. Libertad, 30, Piso 4</td>
      <td>Mouse Ergonómico</td>
      <td>4</td>
      <td>927</td>
      <td>3708.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>N-1002</td>
      <td>2023-03-10 05:00:00</td>
      <td>Usuario_2</td>
      <td>Av. Libertad, 98, Piso 2</td>
      <td>Monitor 4K</td>
      <td>2</td>
      <td>1410</td>
      <td>2820.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>N-1003</td>
      <td>2023-05-10 03:00:00</td>
      <td>Usuario_3</td>
      <td>Paseo Gracia, 94, Piso 7</td>
      <td>Webcam HD</td>
      <td>2</td>
      <td>1269</td>
      <td>2538.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>N-1004</td>
      <td>2023-02-25 17:00:00</td>
      <td>Usuario_4</td>
      <td>Calle Mayor, 80, Piso 8</td>
      <td>Webcam HD</td>
      <td>2</td>
      <td>454</td>
      <td>908.0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>145</th>
      <td>N-1145</td>
      <td>2023-04-17 10:00:00</td>
      <td>Usuario_145</td>
      <td>Paseo Gracia, 99, Piso 10</td>
      <td>Teclado Mecánico</td>
      <td>4</td>
      <td>1051</td>
      <td>4204.0</td>
    </tr>
    <tr>
      <th>146</th>
      <td>N-1146</td>
      <td>2023-04-08 00:00:00</td>
      <td>Usuario_146</td>
      <td>Paseo Gracia, 64, Piso 4</td>
      <td>Monitor 4K</td>
      <td>2</td>
      <td>1229</td>
      <td>2458.0</td>
    </tr>
    <tr>
      <th>147</th>
      <td>N-1147</td>
      <td>2023-02-01 22:00:00</td>
      <td>Usuario_147</td>
      <td>Calle Mayor, 81, Piso 1</td>
      <td>Monitor 4K</td>
      <td>1</td>
      <td>1040</td>
      <td>1040.0</td>
    </tr>
    <tr>
      <th>148</th>
      <td>N-1148</td>
      <td>2023-06-13 03:00:00</td>
      <td>Usuario_148</td>
      <td>Calle Mayor, 56, Piso 1</td>
      <td>Laptop Gamer</td>
      <td>1</td>
      <td>297</td>
      <td>297.0</td>
    </tr>
    <tr>
      <th>149</th>
      <td>N-1149</td>
      <td>2023-02-24 01:00:00</td>
      <td>Usuario_149</td>
      <td>Paseo Gracia, 25, Piso 1</td>
      <td>Monitor 4K</td>
      <td>1</td>
      <td>909</td>
      <td>909.0</td>
    </tr>
  </tbody>
</table>
<p>150 rows × 8 columns</p>
</div>



### Carga XLSX


```python
df_sur = pd.read_excel(
                "ventas_sur_v2.xlsx",
                sheet_name=None,
                header=0,
                usecols="A:H",
                names=["Ref_Venta", "Fecha_Alta", "Articulo", "Cantidad", "Precio_Base", "Descuento_Aplicado", "Es_Cliente_Corporativo", "Estado_Envio"],
                parse_dates=["Fecha_Alta"],
                engine="openpyxl",
                dtype={
                    "Cantidad":int,
                    "Precio_Base":float,
                    "Descuento_Aplicado":float,
                    "Es_Cliente_Coporativo":bool
                      }
                )
df_sur = pd.concat(
                df_sur,
                ignore_index=True
        )

df_sur
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
      <th>Ref_Venta</th>
      <th>Fecha_Alta</th>
      <th>Articulo</th>
      <th>Cantidad</th>
      <th>Precio_Base</th>
      <th>Descuento_Aplicado</th>
      <th>Es_Cliente_Corporativo</th>
      <th>Estado_Envio</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>S-5000</td>
      <td>2023-02-11 00:00:00</td>
      <td>Webcam HD</td>
      <td>9</td>
      <td>425.12</td>
      <td>0.20</td>
      <td>False</td>
      <td>Enviado</td>
    </tr>
    <tr>
      <th>1</th>
      <td>S-5001</td>
      <td>2023-02-03 12:00:00</td>
      <td>Teclado Mecánico</td>
      <td>8</td>
      <td>599.60</td>
      <td>0.00</td>
      <td>True</td>
      <td>Devuelto</td>
    </tr>
    <tr>
      <th>2</th>
      <td>S-5002</td>
      <td>2023-04-06 07:00:00</td>
      <td>Mouse Ergonómico</td>
      <td>6</td>
      <td>971.36</td>
      <td>0.00</td>
      <td>False</td>
      <td>Completado</td>
    </tr>
    <tr>
      <th>3</th>
      <td>S-5003</td>
      <td>2023-04-02 05:00:00</td>
      <td>Monitor 4K</td>
      <td>1</td>
      <td>799.66</td>
      <td>0.10</td>
      <td>True</td>
      <td>Pendiente</td>
    </tr>
    <tr>
      <th>4</th>
      <td>S-5004</td>
      <td>2023-06-17 12:00:00</td>
      <td>Mouse Ergonómico</td>
      <td>2</td>
      <td>619.99</td>
      <td>0.05</td>
      <td>True</td>
      <td>Devuelto</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>155</th>
      <td>S-5075</td>
      <td>2023-05-17 22:00:00</td>
      <td>Monitor 4K</td>
      <td>2</td>
      <td>1150.01</td>
      <td>0.10</td>
      <td>False</td>
      <td>Enviado</td>
    </tr>
    <tr>
      <th>156</th>
      <td>S-5076</td>
      <td>2023-01-29 13:00:00</td>
      <td>Webcam HD</td>
      <td>1</td>
      <td>874.12</td>
      <td>0.10</td>
      <td>True</td>
      <td>Devuelto</td>
    </tr>
    <tr>
      <th>157</th>
      <td>S-5077</td>
      <td>2023-06-09 11:00:00</td>
      <td>Mouse Ergonómico</td>
      <td>1</td>
      <td>145.92</td>
      <td>0.00</td>
      <td>True</td>
      <td>Devuelto</td>
    </tr>
    <tr>
      <th>158</th>
      <td>S-5078</td>
      <td>2023-02-07 13:00:00</td>
      <td>Monitor 4K</td>
      <td>2</td>
      <td>1152.24</td>
      <td>0.00</td>
      <td>False</td>
      <td>Enviado</td>
    </tr>
    <tr>
      <th>159</th>
      <td>S-5079</td>
      <td>2023-05-01 11:00:00</td>
      <td>Docking Station</td>
      <td>7</td>
      <td>261.88</td>
      <td>0.10</td>
      <td>True</td>
      <td>Enviado</td>
    </tr>
  </tbody>
</table>
<p>160 rows × 8 columns</p>
</div>




```python
# https://www.statology.org/pandas-apply-function-to-multiple-columns/ REVISAR

df_sur["Total"] = df_sur.apply(lambda x: calculate_total(x.Precio_Base, x.Cantidad, x.Descuento_Aplicado), axis = 1)
df_sur
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
      <th>Ref_Venta</th>
      <th>Fecha_Alta</th>
      <th>Articulo</th>
      <th>Cantidad</th>
      <th>Precio_Base</th>
      <th>Descuento_Aplicado</th>
      <th>Es_Cliente_Corporativo</th>
      <th>Estado_Envio</th>
      <th>Total</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>S-5000</td>
      <td>2023-02-11 00:00:00</td>
      <td>Webcam HD</td>
      <td>9</td>
      <td>425.12</td>
      <td>0.20</td>
      <td>False</td>
      <td>Enviado</td>
      <td>3060.864</td>
    </tr>
    <tr>
      <th>1</th>
      <td>S-5001</td>
      <td>2023-02-03 12:00:00</td>
      <td>Teclado Mecánico</td>
      <td>8</td>
      <td>599.60</td>
      <td>0.00</td>
      <td>True</td>
      <td>Devuelto</td>
      <td>4796.800</td>
    </tr>
    <tr>
      <th>2</th>
      <td>S-5002</td>
      <td>2023-04-06 07:00:00</td>
      <td>Mouse Ergonómico</td>
      <td>6</td>
      <td>971.36</td>
      <td>0.00</td>
      <td>False</td>
      <td>Completado</td>
      <td>5828.160</td>
    </tr>
    <tr>
      <th>3</th>
      <td>S-5003</td>
      <td>2023-04-02 05:00:00</td>
      <td>Monitor 4K</td>
      <td>1</td>
      <td>799.66</td>
      <td>0.10</td>
      <td>True</td>
      <td>Pendiente</td>
      <td>719.694</td>
    </tr>
    <tr>
      <th>4</th>
      <td>S-5004</td>
      <td>2023-06-17 12:00:00</td>
      <td>Mouse Ergonómico</td>
      <td>2</td>
      <td>619.99</td>
      <td>0.05</td>
      <td>True</td>
      <td>Devuelto</td>
      <td>1177.981</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>155</th>
      <td>S-5075</td>
      <td>2023-05-17 22:00:00</td>
      <td>Monitor 4K</td>
      <td>2</td>
      <td>1150.01</td>
      <td>0.10</td>
      <td>False</td>
      <td>Enviado</td>
      <td>2070.018</td>
    </tr>
    <tr>
      <th>156</th>
      <td>S-5076</td>
      <td>2023-01-29 13:00:00</td>
      <td>Webcam HD</td>
      <td>1</td>
      <td>874.12</td>
      <td>0.10</td>
      <td>True</td>
      <td>Devuelto</td>
      <td>786.708</td>
    </tr>
    <tr>
      <th>157</th>
      <td>S-5077</td>
      <td>2023-06-09 11:00:00</td>
      <td>Mouse Ergonómico</td>
      <td>1</td>
      <td>145.92</td>
      <td>0.00</td>
      <td>True</td>
      <td>Devuelto</td>
      <td>145.920</td>
    </tr>
    <tr>
      <th>158</th>
      <td>S-5078</td>
      <td>2023-02-07 13:00:00</td>
      <td>Monitor 4K</td>
      <td>2</td>
      <td>1152.24</td>
      <td>0.00</td>
      <td>False</td>
      <td>Enviado</td>
      <td>2304.480</td>
    </tr>
    <tr>
      <th>159</th>
      <td>S-5079</td>
      <td>2023-05-01 11:00:00</td>
      <td>Docking Station</td>
      <td>7</td>
      <td>261.88</td>
      <td>0.10</td>
      <td>True</td>
      <td>Enviado</td>
      <td>1649.844</td>
    </tr>
  </tbody>
</table>
<p>160 rows × 9 columns</p>
</div>




```python
def calculate_total(precio_base, cantidad, descuento):
    return precio_base * cantidad * (1 - descuento)
```

### Cargar JSON


```python
import json

with open("ventas_este_v2.json") as f:
    data = json.load(f)

df_este = pd.json_normalize(
    data,
    record_path = ["data"]
    )

df_este
```


    ---------------------------------------------------------------------------

    TypeError                                 Traceback (most recent call last)

    Cell In[88], line 6
          3 with open("ventas_este_v2.json") as f:
          4     data = json.load(f)
    ----> 6 df_este = pd.json_normalize(
          7     data,
          8     record_path = ["data"]
          9     )
         11 df_este


    File /opt/conda/lib/python3.11/site-packages/pandas/io/json/_normalize.py:517, in json_normalize(data, record_path, meta, meta_prefix, record_prefix, errors, sep, max_level)
        514                 meta_vals[key].append(meta_val)
        515             records.extend(recs)
    --> 517 _recursive_extract(data, record_path, {}, level=0)
        519 result = DataFrame(records)
        521 if record_prefix is not None:


    File /opt/conda/lib/python3.11/site-packages/pandas/io/json/_normalize.py:499, in json_normalize.<locals>._recursive_extract(data, path, seen_meta, level)
        497 else:
        498     for obj in data:
    --> 499         recs = _pull_records(obj, path[0])
        500         recs = [
        501             nested_to_record(r, sep=sep, max_level=max_level)
        502             if isinstance(r, dict)
        503             else r
        504             for r in recs
        505         ]
        507         # For repeating the metadata later


    File /opt/conda/lib/python3.11/site-packages/pandas/io/json/_normalize.py:429, in json_normalize.<locals>._pull_records(js, spec)
        427         result = []
        428     else:
    --> 429         raise TypeError(
        430             f"{js} has non list value {result} for path {spec}. "
        431             "Must be list or null."
        432         )
        433 return result


    TypeError: {'metadata': {'source_system': 'API_v2', 'latency_ms': 34}, 'data': {'id_registro': 'E-8000', 'payload': {'fecha_evento': '2023-06-29 00:00:00', 'comprador': {'perfil': {'id_usuario': 'USR_442', 'tipo_suscripcion': 'Gold'}, 'ubicacion': {'ciudad': 'Sevilla', 'codigo_postal': '51213'}}, 'transaccion': {'detalles_producto': {'sku': 'G6YATHNF', 'nombre_comercial': 'Monitor 4K', 'precio_lista': 503, 'impuestos': {'iva_percent': 21, 'monto_iva': 105.63}}, 'cantidad_comprada': 1, 'metodo_pago': 'Bizum', 'tags': ['lujo', 'envio_gratis']}}}} has non list value {'id_registro': 'E-8000', 'payload': {'fecha_evento': '2023-06-29 00:00:00', 'comprador': {'perfil': {'id_usuario': 'USR_442', 'tipo_suscripcion': 'Gold'}, 'ubicacion': {'ciudad': 'Sevilla', 'codigo_postal': '51213'}}, 'transaccion': {'detalles_producto': {'sku': 'G6YATHNF', 'nombre_comercial': 'Monitor 4K', 'precio_lista': 503, 'impuestos': {'iva_percent': 21, 'monto_iva': 105.63}}, 'cantidad_comprada': 1, 'metodo_pago': 'Bizum', 'tags': ['lujo', 'envio_gratis']}}} for path data. Must be list or null.


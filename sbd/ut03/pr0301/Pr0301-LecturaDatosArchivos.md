# PR0301: Lectura de datos de archivos


```python
!pip install openpyxl
# !pip install xlrd
```

    Requirement already satisfied: openpyxl in /opt/conda/lib/python3.11/site-packages (3.1.2)
    Requirement already satisfied: et-xmlfile in /opt/conda/lib/python3.11/site-packages (from openpyxl) (1.1.0)



```python
import pandas as pd

df_norte = pd.read_csv(
                        "ventas_norte.csv",
                        names=["id", "date", "product", "quantity", "unit_price"],
                        sep=";"
                        )

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

este_json = pd.read_json("ventas_este.json")
df_este = pd.json_normalize(este_json)

print(f"Ventas norte:\n {df_norte.head(5)}")
print("----------------------------------------")
print(f"Ventas sur:\n {df_sur}")
print("----------------------------------------")
print(f"Ventas este:\n {df_este.head(5)}")
```

    Ventas norte:
                    id         date       product          quantity   unit_price
    0  ID_Transaccion  Fecha_Venta  Nom_Producto  Cantidad_Vendida  Precio_Unit
    1            1000   2023-02-21        Laptop                 4          423
    2            1001   2023-01-15        Laptop                 2          171
    3            1002   2023-03-13        Laptop                 3           73
    4            1003   2023-03-02       Teclado                 1          139
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
     Empty DataFrame
    Columns: []
    Index: [0, 1, 2, 3]



```python
df_sur
```




    {'Enero':       id       date  product  quantity  unit_price
     0   2000 2023-03-01  Monitor         6         624
     1   2001 2023-03-04   Laptop         7         941
     2   2002 2023-03-26    Mouse         3         989
     3   2003 2023-02-01   Webcam         3         621
     4   2004 2023-03-28    Mouse         5         437
     5   2005 2023-02-02    Mouse         6         134
     6   2006 2023-03-08   Laptop         9         636
     7   2007 2023-01-18  Teclado         5         922
     8   2008 2023-01-25    Mouse         1         215
     9   2009 2023-02-23  Monitor         4         845
     10  2010 2023-02-27  Teclado         5         520
     11  2011 2023-03-08   Webcam         5         645
     12  2012 2023-02-15   Laptop         7         512
     13  2013 2023-01-24   Webcam         4          94
     14  2014 2023-02-01  Teclado         1         432
     15  2015 2023-02-16  Teclado         5         395
     16  2016 2023-03-27  Teclado         7         439
     17  2017 2023-01-23   Webcam         6         748
     18  2018 2023-03-07  Teclado         5         296
     19  2019 2023-01-27   Webcam         4         780
     20  2020 2023-01-02  Teclado         2         695
     21  2021 2023-03-31  Monitor         4         413
     22  2022 2023-01-17  Teclado         3         888
     23  2023 2023-02-02   Webcam         1         476
     24  2024 2023-01-09    Mouse         8         939
     25  2025 2023-02-12  Teclado         5         211
     26  2026 2023-02-17    Mouse         4         758
     27  2027 2023-02-08  Monitor         8         708
     28  2028 2023-02-11   Laptop         7         118
     29  2029 2023-01-26  Monitor         2         567
     30  2030 2023-02-19  Teclado         1         997
     31  2031 2023-01-25    Mouse         4         115
     32  2032 2023-01-24    Mouse         8         683
     33  2033 2023-01-13   Webcam         2         682
     34  2034 2023-03-01    Mouse         3         209
     35  2035 2023-01-07   Webcam         1         755
     36  2036 2023-02-26   Laptop         1          56
     37  2037 2023-02-05  Teclado         3         799
     38  2038 2023-02-14   Webcam         5         388
     39  2039 2023-01-20   Laptop         3         714
     40  2040 2023-03-06    Mouse         1         544
     41  2041 2023-01-08    Mouse         1         298
     42  2042 2023-01-16   Laptop         8         236
     43  2043 2023-01-14    Mouse         2         886
     44  2044 2023-03-17   Laptop         3         892
     45  2045 2023-03-28   Webcam         2         817
     46  2046 2023-01-15   Webcam         3         292
     47  2047 2023-03-07   Laptop         7         900
     48  2048 2023-02-01   Webcam         1          81
     49  2049 2023-03-28   Webcam         8         615,
     'Febrero':       id       date  product  quantity  unit_price
     0   2000 2023-03-30    Mouse         5         798
     1   2001 2023-03-27    Mouse         4         872
     2   2002 2023-01-13   Webcam         3         301
     3   2003 2023-02-28   Webcam         3          82
     4   2004 2023-01-19   Webcam         4         236
     5   2005 2023-02-18  Monitor         9         873
     6   2006 2023-01-12   Webcam         2         846
     7   2007 2023-03-02   Laptop         9         814
     8   2008 2023-01-19  Teclado         1         708
     9   2009 2023-03-17   Laptop         1         480
     10  2010 2023-01-09   Laptop         5         948
     11  2011 2023-03-12   Webcam         6         629
     12  2012 2023-01-28  Teclado         6         124
     13  2013 2023-03-19  Teclado         3         118
     14  2014 2023-02-21  Teclado         7         530
     15  2015 2023-03-24  Monitor         9         404
     16  2016 2023-01-16   Webcam         8         424
     17  2017 2023-03-10  Teclado         6         842
     18  2018 2023-01-12  Monitor         8         537
     19  2019 2023-01-25    Mouse         5         495
     20  2020 2023-02-21    Mouse         8         996
     21  2021 2023-03-26  Monitor         4         728
     22  2022 2023-02-22  Monitor         8         882
     23  2023 2023-01-23   Webcam         2         664
     24  2024 2023-01-16   Webcam         5         889
     25  2025 2023-02-26    Mouse         9         790
     26  2026 2023-02-08  Teclado         4         456
     27  2027 2023-02-22    Mouse         6          42
     28  2028 2023-02-11  Teclado         1         584
     29  2029 2023-02-27  Teclado         9         696
     30  2030 2023-02-08   Webcam         1         733
     31  2031 2023-01-14   Laptop         5         477
     32  2032 2023-01-05   Laptop         4         102
     33  2033 2023-02-04  Monitor         3         164
     34  2034 2023-03-28   Webcam         6         104
     35  2035 2023-03-16  Teclado         2          97
     36  2036 2023-01-18   Laptop         3         476
     37  2037 2023-03-17  Teclado         5         897
     38  2038 2023-01-09   Laptop         9          20
     39  2039 2023-03-15   Laptop         2          70
     40  2040 2023-02-27   Laptop         8         704
     41  2041 2023-01-17   Webcam         2         736
     42  2042 2023-01-07    Mouse         5         791
     43  2043 2023-02-15  Teclado         7         465
     44  2044 2023-01-13   Webcam         8         468
     45  2045 2023-02-09   Webcam         1         900
     46  2046 2023-02-11   Webcam         6         507
     47  2047 2023-01-09   Webcam         1         819
     48  2048 2023-02-19   Webcam         2          53
     49  2049 2023-01-27  Monitor         1         367,
     'Marzo':       id       date  product  quantity  unit_price
     0   2000 2023-03-13   Webcam         4         296
     1   2001 2023-02-08    Mouse         8         729
     2   2002 2023-01-26   Webcam         6         601
     3   2003 2023-02-03  Monitor         7         522
     4   2004 2023-02-23  Monitor         8         643
     5   2005 2023-01-03  Monitor         2         535
     6   2006 2023-02-19  Monitor         8         369
     7   2007 2023-01-12   Laptop         3         862
     8   2008 2023-03-06  Monitor         7         465
     9   2009 2023-02-23  Teclado         3         849
     10  2010 2023-01-05  Teclado         7         369
     11  2011 2023-02-26   Laptop         2         626
     12  2012 2023-01-17  Monitor         6         683
     13  2013 2023-02-16  Monitor         3         842
     14  2014 2023-01-23  Monitor         3         156
     15  2015 2023-03-20   Webcam         9         778
     16  2016 2023-03-26    Mouse         7         918
     17  2017 2023-01-14   Webcam         5         262
     18  2018 2023-03-07    Mouse         7         562
     19  2019 2023-03-16  Monitor         9          59
     20  2020 2023-02-20  Monitor         1         248
     21  2021 2023-02-07   Webcam         7         567
     22  2022 2023-03-05   Webcam         6         939
     23  2023 2023-02-07    Mouse         9         242
     24  2024 2023-02-19  Teclado         1          25
     25  2025 2023-03-23    Mouse         4         341
     26  2026 2023-01-30   Webcam         9         487
     27  2027 2023-03-20   Webcam         4         751
     28  2028 2023-02-20   Laptop         3          94
     29  2029 2023-03-04   Webcam         9          23
     30  2030 2023-02-21   Laptop         2         866
     31  2031 2023-02-07  Teclado         4         665
     32  2032 2023-03-29    Mouse         6         137
     33  2033 2023-03-20    Mouse         2         900
     34  2034 2023-01-30   Laptop         8         625
     35  2035 2023-02-20    Mouse         8         523
     36  2036 2023-03-22   Webcam         1         966
     37  2037 2023-01-05  Monitor         3         593
     38  2038 2023-01-29   Laptop         9         460
     39  2039 2023-01-04    Mouse         5         213
     40  2040 2023-01-10   Laptop         6         866
     41  2041 2023-02-25   Laptop         4         734
     42  2042 2023-01-17  Monitor         2         411
     43  2043 2023-03-15   Webcam         8          45
     44  2044 2023-01-17   Laptop         6         454
     45  2045 2023-03-25    Mouse         5         192
     46  2046 2023-03-29  Teclado         9         319
     47  2047 2023-03-10   Laptop         1         664
     48  2048 2023-02-03   Laptop         5         345
     49  2049 2023-01-06  Monitor         6         429}



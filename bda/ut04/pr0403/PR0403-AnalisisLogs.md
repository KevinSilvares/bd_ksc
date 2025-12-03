# PR0403: Análisis de logs con MapReduce


```python
!hdfs dfs -mkdir /analisis_logs
```


```python
!hdfs dfs -put logfiles.log /analisis_logs
```


```python
!head -n 100 > test_logfiles.log
```

## 1. Estadísticas básicas


```python
%%writefile mapper_code_count.py
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    words = line.strip().split()
    print(f"{words[8]}\t1")
```

    Overwriting mapper_code_count.py



```python
!cat test_logfiles.log | python3 mapper_code_count.py | sort | python3 reducer_code_count.py
```

    200: 22
    303: 20
    304: 25
    403: 13
    404: 19
    500: 18
    502: 21



```python
%%writefile reducer_code_count.py
#!/usr/bin/env python3

import sys

current_code = 0
current_count = 0

for line in sys.stdin:
    code, count = line.strip().split("\t")
    code = int(code)

    if code == current_code:
        current_count += 1
    else:
        if current_code:
            print(f"{current_code}: {current_count}")
        current_code = code
        current_count = 0

if current_code:
     print(f"{current_code}: {current_count}")
```

    Overwriting reducer_code_count.py



```python

```

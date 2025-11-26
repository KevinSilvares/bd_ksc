# PR0402 - Datos del clima


```python
!hdfs dfs -mkdir /datos_clima
```

    mkdir: `/datos_clima': File exists



```python
!hdfs dfs -put city_temperature.csv /datos_clima
```

    put: `/datos_clima/city_temperature.csv': File exists


### Datos reducidos para test

He creado una versión muy reducida del csv para poder realizar pruebas de forma mucho más rápida.


```python
!hdfs dfs -put test_city_temperature.csv /datos_clima
```

    put: `/datos_clima/test_city_temperature.csv': File exists



```python
!hdfs dfs -ls /datos_clima
```

    Found 2 items
    -rw-r--r--   3 root supergroup  140600832 2025-11-18 09:36 /datos_clima/city_temperature.csv
    -rw-r--r--   3 root supergroup       2905 2025-11-19 11:02 /datos_clima/test_city_temperature.csv


### Ejercicio 1: Temperatura máxima por ciudad 


```python
%%writefile mapper.py
#!/usr/bin/env python3

import sys, csv

# reader = csv.DictReader(sys.stdin)
# for line in reader:
    
#    print(f"{line['City']}\t{line['AvgTemperature']}")

# entrada = sys.stdin
# i = 0
# city_index = 0
# temp_index = 0

# for line in entrada:
#     data = line.strip().split(',')
#     # En la primera línea recoge los índices que usaremos después
#     if i == 0:
#         city_index = data.index('City')
#         temp_index = data.index('AvgTemperature')
#     else:
#         print(f"{data[city_index]}\t{data[temp_index]}")
        
#     i += 1
    
header = None

for line in sys.stdin:
    if header is None:
        # Evita la primera línea que actúa como cabecera
        if "City" in line and "AvgTemperature" in line:
            header = line.strip().split(",")
        continue

    reader = csv.DictReader([line], fieldnames=header)
    for row in reader:
        try:
            print(f"{row['City']}\t{row['AvgTemperature']}")
        except KeyError:
            # La primera línea es la cabecera. Como no encuentra los datos salta esta excepción. Con esta línea la capturo y omito.
            continue
```

    Overwriting mapper.py



```python
%%writefile reducer.py
#!/usr/bin/env python3

import sys, math

current_city = None
max_temp = -math.inf
#cities = set()

for line in sys.stdin:   
    city, temp = line.strip().split("\t", 1)
    temp = float(temp)

    if current_city == city:
        #cities.add(city)
        if temp > max_temp:
            max_temp = temp
    else:
        if current_city:
                print(f"{current_city}: {max_temp}")
        max_temp = -math.inf
        current_city = city
        #cities = {city}
        
if current_city:
    print(f"{current_city}: {max_temp}")
```

    Overwriting reducer.py



```python
!hdfs dfs -rm -r /salida_temp
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper.py \
-file reducer.py \
-mapper mapper.py \
-reducer reducer.py \
-input /datos_clima/city_temperature.csv \
-output /salida_temp
```

    Deleted /salida_temp
    2025-11-25 12:11:44,364 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper.py, reducer.py, /tmp/hadoop-unjar12191069673507748/] [] /tmp/streamjob8531739585675762369.jar tmpDir=null
    2025-11-25 12:11:46,240 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.4:8032
    2025-11-25 12:11:46,485 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.4:8032
    2025-11-25 12:11:46,813 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764071839686_0005
    2025-11-25 12:11:47,465 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-11-25 12:11:47,492 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.6:9866
    2025-11-25 12:11:47,493 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.3:9866
    2025-11-25 12:11:47,493 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.5:9866
    2025-11-25 12:11:47,493 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.2:9866
    2025-11-25 12:11:47,606 INFO mapreduce.JobSubmitter: number of splits:2
    2025-11-25 12:11:48,695 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764071839686_0005
    2025-11-25 12:11:48,696 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-11-25 12:11:49,960 INFO conf.Configuration: resource-types.xml not found
    2025-11-25 12:11:49,961 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-11-25 12:11:50,341 INFO impl.YarnClientImpl: Submitted application application_1764071839686_0005
    2025-11-25 12:11:50,563 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764071839686_0005/
    2025-11-25 12:11:50,567 INFO mapreduce.Job: Running job: job_1764071839686_0005
    2025-11-25 12:11:58,862 INFO mapreduce.Job: Job job_1764071839686_0005 running in uber mode : false
    2025-11-25 12:11:58,864 INFO mapreduce.Job:  map 0% reduce 0%
    2025-11-25 12:12:10,124 INFO mapreduce.Job:  map 50% reduce 0%
    2025-11-25 12:12:19,250 INFO mapreduce.Job:  map 72% reduce 0%
    2025-11-25 12:12:24,309 INFO mapreduce.Job:  map 100% reduce 0%
    2025-11-25 12:12:28,364 INFO mapreduce.Job:  map 100% reduce 100%
    2025-11-25 12:12:31,439 INFO mapreduce.Job: Job job_1764071839686_0005 completed successfully
    2025-11-25 12:12:31,626 INFO mapreduce.Job: Counters: 56
    	File System Counters
    		FILE: Number of bytes read=23851842
    		FILE: Number of bytes written=48646064
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=140605138
    		HDFS: Number of bytes written=2778
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Killed map tasks=1
    		Launched map tasks=3
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Rack-local map tasks=1
    		Total time spent by all maps in occupied slots (ms)=34929
    		Total time spent by all reduces in occupied slots (ms)=15723
    		Total time spent by all map tasks (ms)=34929
    		Total time spent by all reduce tasks (ms)=15723
    		Total vcore-milliseconds taken by all map tasks=34929
    		Total vcore-milliseconds taken by all reduce tasks=15723
    		Total megabyte-milliseconds taken by all map tasks=35767296
    		Total megabyte-milliseconds taken by all reduce tasks=16100352
    	Map-Reduce Framework
    		Map input records=2906328
    		Map output records=1541840
    		Map output bytes=20768156
    		Map output materialized bytes=23851848
    		Input split bytes=210
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=178
    		Reduce shuffle bytes=23851848
    		Reduce input records=1541840
    		Reduce output records=178
    		Spilled Records=3083680
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=554
    		CPU time spent (ms)=19330
    		Physical memory (bytes) snapshot=866312192
    		Virtual memory (bytes) snapshot=7638228992
    		Total committed heap usage (bytes)=770703360
    		Peak Map Physical memory (bytes)=332554240
    		Peak Map Virtual memory (bytes)=2557902848
    		Peak Reduce Physical memory (bytes)=236064768
    		Peak Reduce Virtual memory (bytes)=2551123968
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=140604928
    	File Output Format Counters 
    		Bytes Written=2778
    2025-11-25 12:12:31,627 INFO streaming.StreamJob: Output directory: /salida_temp



```python
!hdfs dfs -ls /salida_temp
```

    Found 2 items
    -rw-r--r--   3 root supergroup          0 2025-11-25 12:12 /salida_temp/_SUCCESS
    -rw-r--r--   3 root supergroup       2778 2025-11-25 12:12 /salida_temp/part-00000


!cat city_temperature.csv | python3 mapper.py | sort | python3 reducer.py

## Ejercicio 2: Media histórica por país

El `mapper` es exactamente el mismo del ejercicio 1. Cambia el `reducer`.


```python
%%writefile reducer_avg_temp.py
#!/usr/bin/env python3

import sys, math

current_city = None
temps = []

for line in sys.stdin:   
    city, temp = line.strip().split("\t", 1)
    temps.append(float(temp))

    if current_city == city:
        temps.append(float(temp))
    else:
        if current_city:
                avg_temp = sum(temps) / len(temps)
                print(f"{current_city}: {avg_temp}")
        temps.clear()
        current_city = city
        
if current_city:
    print(f"{current_city}: {avg_temp}")
```

    Overwriting reducer_avg_temp.py



```python
!hdfs dfs -rm -r /salida_avg_temp
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper.py \
-file reducer_avg_temp.py \
-mapper mapper.py \
-reducer reducer_avg_temp.py \
-input /datos_clima/city_temperature.csv \
-output /salida_avg_temp
```

    Deleted /salida_avg_temp
    2025-11-25 12:10:55,994 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper.py, reducer_avg_temp.py, /tmp/hadoop-unjar7646296943622686048/] [] /tmp/streamjob1044830220720077824.jar tmpDir=null
    2025-11-25 12:10:57,207 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.4:8032
    2025-11-25 12:10:57,467 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.4:8032
    2025-11-25 12:10:57,950 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764071839686_0004
    2025-11-25 12:10:59,128 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-11-25 12:10:59,216 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.3:9866
    2025-11-25 12:10:59,219 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.5:9866
    2025-11-25 12:10:59,219 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.6:9866
    2025-11-25 12:10:59,219 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.2:9866
    2025-11-25 12:10:59,536 INFO mapreduce.JobSubmitter: number of splits:2
    2025-11-25 12:10:59,829 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764071839686_0004
    2025-11-25 12:10:59,830 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-11-25 12:11:00,096 INFO conf.Configuration: resource-types.xml not found
    2025-11-25 12:11:00,097 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-11-25 12:11:00,277 INFO impl.YarnClientImpl: Submitted application application_1764071839686_0004
    2025-11-25 12:11:00,347 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764071839686_0004/
    2025-11-25 12:11:00,351 INFO mapreduce.Job: Running job: job_1764071839686_0004
    2025-11-25 12:11:09,780 INFO mapreduce.Job: Job job_1764071839686_0004 running in uber mode : false
    2025-11-25 12:11:09,781 INFO mapreduce.Job:  map 0% reduce 0%
    2025-11-25 12:11:19,145 INFO mapreduce.Job:  map 50% reduce 0%
    2025-11-25 12:11:29,277 INFO mapreduce.Job:  map 72% reduce 0%
    2025-11-25 12:11:34,386 INFO mapreduce.Job:  map 100% reduce 0%
    2025-11-25 12:11:38,438 INFO mapreduce.Job:  map 100% reduce 100%
    2025-11-25 12:11:39,466 INFO mapreduce.Job: Job job_1764071839686_0004 completed successfully
    2025-11-25 12:11:39,614 INFO mapreduce.Job: Counters: 55
    	File System Counters
    		FILE: Number of bytes read=23851842
    		FILE: Number of bytes written=48646184
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=140605138
    		HDFS: Number of bytes written=5092
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Killed map tasks=1
    		Launched map tasks=3
    		Launched reduce tasks=1
    		Data-local map tasks=3
    		Total time spent by all maps in occupied slots (ms)=33587
    		Total time spent by all reduces in occupied slots (ms)=16544
    		Total time spent by all map tasks (ms)=33587
    		Total time spent by all reduce tasks (ms)=16544
    		Total vcore-milliseconds taken by all map tasks=33587
    		Total vcore-milliseconds taken by all reduce tasks=16544
    		Total megabyte-milliseconds taken by all map tasks=34393088
    		Total megabyte-milliseconds taken by all reduce tasks=16941056
    	Map-Reduce Framework
    		Map input records=2906328
    		Map output records=1541840
    		Map output bytes=20768156
    		Map output materialized bytes=23851848
    		Input split bytes=210
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=178
    		Reduce shuffle bytes=23851848
    		Reduce input records=1541840
    		Reduce output records=178
    		Spilled Records=3083680
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=288
    		CPU time spent (ms)=19760
    		Physical memory (bytes) snapshot=929406976
    		Virtual memory (bytes) snapshot=7635058688
    		Total committed heap usage (bytes)=890765312
    		Peak Map Physical memory (bytes)=356560896
    		Peak Map Virtual memory (bytes)=2555604992
    		Peak Reduce Physical memory (bytes)=271867904
    		Peak Reduce Virtual memory (bytes)=2552733696
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=140604928
    	File Output Format Counters 
    		Bytes Written=5092
    2025-11-25 12:11:39,614 INFO streaming.StreamJob: Output directory: /salida_avg_temp



```python
!hdfs dfs -ls /salida_avg_temp
```

    Found 2 items
    -rw-r--r--   3 root supergroup          0 2025-11-25 12:11 /salida_avg_temp/_SUCCESS
    -rw-r--r--   3 root supergroup       5092 2025-11-25 12:11 /salida_avg_temp/part-00000



```python
!cat test_city_temperature.csv | python3 mapper.py | sort | python3 reducer_avg_temp.py
```

## Ejercicio 3: Conteo de días calurosos por ciudad

El `mapper` es exactamente el mismo del ejercicio 1. Cambia el `reducer`.


```python
%%writefile reducer_hottest_days.py
#!/usr/bin/env python3

import sys

current_city = None
hottest_days = 0

for line in sys.stdin:   
    city, temp = line.strip().split("\t", 1)

    if current_city == city:
        if float(temp) > 30:
            hottest_days += 1
    else:
        if current_city:
                print(f"{current_city}: {hottest_days}")
        hottest_days = 0
        current_city = city
        
if current_city:
    print(f"{current_city}: {hottest_days}")
```

    Overwriting reducer_hottest_days.py


En este caso he utilizado el `csv` de pruebas que he creado porque el original tardaba mucho en ejecutarse y no terminaba (+15 minutos), pero los datos son perfectamente extrapolables.


```python
!hdfs dfs -rm -r /salida_hottest_days
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper.py \
-file reducer_hottest_days.py \
-mapper mapper.py \
-reducer reducer_hottest_days.py \
-input /datos_clima/test_city_temperature.csv \
-output /salida_hottest_days
```

    Deleted /salida_hottest_days
    2025-11-26 10:53:51,324 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper.py, reducer_hottest_days.py, /tmp/hadoop-unjar6738922459156900750/] [] /tmp/streamjob8695252191641365957.jar tmpDir=null
    2025-11-26 10:53:53,199 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-11-26 10:53:53,575 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-11-26 10:53:54,346 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764154390139_0001
    2025-11-26 10:53:55,888 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-11-26 10:53:56,047 INFO mapreduce.JobSubmitter: number of splits:2
    2025-11-26 10:53:56,351 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764154390139_0001
    2025-11-26 10:53:56,351 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-11-26 10:53:56,684 INFO conf.Configuration: resource-types.xml not found
    2025-11-26 10:53:56,685 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-11-26 10:53:57,636 INFO impl.YarnClientImpl: Submitted application application_1764154390139_0001
    2025-11-26 10:53:57,698 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764154390139_0001/
    2025-11-26 10:53:57,701 INFO mapreduce.Job: Running job: job_1764154390139_0001
    2025-11-26 10:54:11,061 INFO mapreduce.Job: Job job_1764154390139_0001 running in uber mode : false
    2025-11-26 10:54:11,063 INFO mapreduce.Job:  map 0% reduce 0%
    2025-11-26 10:54:29,724 INFO mapreduce.Job:  map 100% reduce 0%
    2025-11-26 10:54:41,845 INFO mapreduce.Job:  map 100% reduce 100%
    2025-11-26 10:54:41,858 INFO mapreduce.Job: Job job_1764154390139_0001 completed successfully
    2025-11-26 10:54:42,145 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=603
    		FILE: Number of bytes written=943781
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=4578
    		HDFS: Number of bytes written=55
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=27695
    		Total time spent by all reduces in occupied slots (ms)=7549
    		Total time spent by all map tasks (ms)=27695
    		Total time spent by all reduce tasks (ms)=7549
    		Total vcore-milliseconds taken by all map tasks=27695
    		Total vcore-milliseconds taken by all reduce tasks=7549
    		Total megabyte-milliseconds taken by all map tasks=28359680
    		Total megabyte-milliseconds taken by all reduce tasks=7730176
    	Map-Reduce Framework
    		Map input records=58
    		Map output records=35
    		Map output bytes=527
    		Map output materialized bytes=609
    		Input split bytes=220
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=4
    		Reduce shuffle bytes=609
    		Reduce input records=35
    		Reduce output records=4
    		Spilled Records=70
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=401
    		CPU time spent (ms)=2650
    		Physical memory (bytes) snapshot=859365376
    		Virtual memory (bytes) snapshot=7633375232
    		Total committed heap usage (bytes)=740294656
    		Peak Map Physical memory (bytes)=309682176
    		Peak Map Virtual memory (bytes)=2542731264
    		Peak Reduce Physical memory (bytes)=241131520
    		Peak Reduce Virtual memory (bytes)=2547990528
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=4358
    	File Output Format Counters 
    		Bytes Written=55
    2025-11-26 10:54:42,146 INFO streaming.StreamJob: Output directory: /salida_hottest_days



```python
!cat test_city_temperature.csv | python3 mapper.py | sort | python3 reducer_hottest_days.py
```

    Algiers: 8
    Calcutta: 12
    Kuala Lumpur: 11
    Lisbon: 9
    Santo Domingo: 12


## Ejercicio 4: Rango de temperaturas por ciudad (Min/Max)

El `mapper` es exactamente el mismo del ejercicio 1. Cambia el `reducer`.


```python
%%writefile reducer_min_max_temps.py
#!/usr/bin/env python3

import sys, math

current_city = None
max_temp = -math.inf
min_temp = math.inf

for line in sys.stdin:   
    city, temp = line.strip().split("\t", 1)
    temp = float(temp)

    if current_city == city:
        if temp > max_temp:
            max_temp = temp
        if temp < min_temp:
            min_temp = temp
    else:
        if current_city:
                print(f"{current_city}:\n Máxima temperatura: {max_temp}\n Mínima temperatura: {min_temp}")
        max_temp = -math.inf
        min_temp = math.inf
        current_city = city
        
if current_city:
    print(f"{current_city}:\n Máxima temperatura: {max_temp}\n Mínima temperatura: {min_temp}")
```

    Writing reducer_min_max_temps.py



```python
!hdfs dfs -rm -r /salida_min_max_temps
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper.py \
-file reducer_min_max_temps.py \
-mapper mapper.py \
-reducer reducer_min_max_temps.py \
-input /datos_clima/city_temperature.csv \
-output /salida_min_max_temps
```

    rm: `/salida_min_max_temps': No such file or directory
    2025-11-25 12:33:38,508 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper.py, reducer_min_max_temps.py, /tmp/hadoop-unjar1370912196923679813/] [] /tmp/streamjob3799970160648703890.jar tmpDir=null
    2025-11-25 12:33:40,017 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-11-25 12:33:40,510 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-11-25 12:33:41,378 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764073814666_0001
    2025-11-25 12:33:43,573 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-11-25 12:33:43,675 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.5:9866
    2025-11-25 12:33:43,677 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.2:9866
    2025-11-25 12:33:43,677 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.4:9866
    2025-11-25 12:33:43,677 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.3:9866
    2025-11-25 12:33:43,864 INFO mapreduce.JobSubmitter: number of splits:2
    2025-11-25 12:33:44,243 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764073814666_0001
    2025-11-25 12:33:44,243 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-11-25 12:33:44,591 INFO conf.Configuration: resource-types.xml not found
    2025-11-25 12:33:44,592 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-11-25 12:33:45,333 INFO impl.YarnClientImpl: Submitted application application_1764073814666_0001
    2025-11-25 12:33:45,412 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764073814666_0001/
    2025-11-25 12:33:45,416 INFO mapreduce.Job: Running job: job_1764073814666_0001
    2025-11-25 12:33:59,823 INFO mapreduce.Job: Job job_1764073814666_0001 running in uber mode : false
    2025-11-25 12:33:59,824 INFO mapreduce.Job:  map 0% reduce 0%
    2025-11-25 12:34:12,018 INFO mapreduce.Job:  map 50% reduce 0%
    2025-11-25 12:34:30,325 INFO mapreduce.Job:  map 74% reduce 17%
    2025-11-25 12:34:35,390 INFO mapreduce.Job:  map 100% reduce 17%
    2025-11-25 12:34:36,410 INFO mapreduce.Job:  map 100% reduce 34%
    2025-11-25 12:34:39,435 INFO mapreduce.Job:  map 100% reduce 100%
    2025-11-25 12:34:39,450 INFO mapreduce.Job: Job job_1764073814666_0001 completed successfully
    2025-11-25 12:34:39,617 INFO mapreduce.Job: Counters: 55
    	File System Counters
    		FILE: Number of bytes read=23851842
    		FILE: Number of bytes written=48646259
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=140605138
    		HDFS: Number of bytes written=12034
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Killed map tasks=1
    		Launched map tasks=3
    		Launched reduce tasks=1
    		Data-local map tasks=3
    		Total time spent by all maps in occupied slots (ms)=45738
    		Total time spent by all reduces in occupied slots (ms)=24950
    		Total time spent by all map tasks (ms)=45738
    		Total time spent by all reduce tasks (ms)=24950
    		Total vcore-milliseconds taken by all map tasks=45738
    		Total vcore-milliseconds taken by all reduce tasks=24950
    		Total megabyte-milliseconds taken by all map tasks=46835712
    		Total megabyte-milliseconds taken by all reduce tasks=25548800
    	Map-Reduce Framework
    		Map input records=2906328
    		Map output records=1541840
    		Map output bytes=20768156
    		Map output materialized bytes=23851848
    		Input split bytes=210
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=178
    		Reduce shuffle bytes=23851848
    		Reduce input records=1541840
    		Reduce output records=534
    		Spilled Records=3083680
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=484
    		CPU time spent (ms)=19960
    		Physical memory (bytes) snapshot=954286080
    		Virtual memory (bytes) snapshot=7638306816
    		Total committed heap usage (bytes)=836239360
    		Peak Map Physical memory (bytes)=366039040
    		Peak Map Virtual memory (bytes)=2557992960
    		Peak Reduce Physical memory (bytes)=281423872
    		Peak Reduce Virtual memory (bytes)=2552295424
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=140604928
    	File Output Format Counters 
    		Bytes Written=12034
    2025-11-25 12:34:39,617 INFO streaming.StreamJob: Output directory: /salida_min_max_temps


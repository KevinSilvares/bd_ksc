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
!hdfs dfs -cat /salida_temp/part-00000
```

    Abidjan: 88.6	
    Abu Dhabi: 107.3	
    Addis Ababa: 77.0	
    Algiers: 96.6	
    Almaty: 90.9	
    Amman: 95.4	
    Amsterdam: 85.5	
    Anchorage: 75.3	
    Ankara: 87.9	
    Antananarivo: 78.5	
    Ashabad: 102.2	
    Athens: 94.3	
    Auckland: 75.4	
    Bangkok: 93.0	
    Bangui: 93.7	
    Banjul: 93.6	
    Barcelona: 86.6	
    Beijing: 92.9	
    Beirut: 91.1	
    Belfast: 77.6	
    Belgrade: 91.9	
    Belize City: 92.9	
    Bern: 83.7	
    Bilbao: 94.6	
    Birmingham: 91.0	
    Bishkek: 91.1	
    Bissau: 100.1	
    Bogota: 66.7	
    Bombay (Mumbai): 92.6	
    Bonn: 86.9	
    Bordeaux: 88.8	
    Brasilia: 87.7	
    Bratislava: 85.5	
    Brazzaville: 88.7	
    Bridgetown: 88.0	
    Brisbane: 87.3	
    Brussels: 85.4	
    Bucharest: 91.4	
    Budapest: 88.2	
    Buenos Aires: 90.9	
    Bujumbura: 89.1	
    Cairo: 100.2	
    Calcutta: 96.8	
    Calgary: 79.1	
    Canberra: 93.2	
    Capetown: 83.8	
    Caracas: 89.9	
    Chengdu: 90.6	
    Chennai (Madras): 97.9	
    Colombo: 88.3	
    Conakry: 89.6	
    Copenhagen: 77.5	
    Cotonou: 88.6	
    Dakar: 87.0	
    Damascus: 95.5	
    Dar Es Salaam: 90.4	
    Delhi: 103.7	
    Dhahran: 107.8	
    Dhaka: 91.4	
    Doha: 108.5	
    Dubai: 107.5	
    Dublin: 70.1	
    Dusanbe: 97.6	
    Edmonton: 82.8	
    Fairbanks: 79.5	
    Flagstaff: 83.5	
    Frankfurt: 85.2	
    Freetown: 88.7	
    Geneva: 85.2	
    Georgetown: 90.6	
    Guadalajara: 88.5	
    Guangzhou: 94.7	
    Guatemala City: 79.8	
    Guayaquil: 90.0	
    Halifax: 80.5	
    Hamburg: 89.8	
    Hamilton: 85.4	
    Hanoi: 96.0	
    Havana: 88.3	
    Helsinki: 79.8	
    Hong Kong: 92.4	
    Huntsville: 91.5	
    Islamabad: 102.4	
    Istanbul: 88.7	
    Jakarta: 90.6	
    Juneau: 72.0	
    Kampala: 82.9	
    Karachi: 99.7	
    Katmandu: 86.6	
    Kiev: 86.9	
    Kuala Lumpur: 89.6	
    Kuwait: 110.0	
    La Paz: 63.4	
    Lagos: 93.2	
    Libreville: 86.8	
    Lilongwe: 90.7	
    Lima: 81.8	
    Lisbon: 96.3	
    Lome: 90.1	
    London: 83.4	
    Lusaka: 93.2	
    Madrid: 91.0	
    Managua: 93.9	
    Manama: 103.3	
    Manila: 91.9	
    Maputo: 95.6	
    Melbourne: 92.8	
    Mexico City: 77.0	
    Milan: 87.4	
    Minsk: 83.5	
    Mobile: 88.9	
    Monterrey: 103.4	
    Montgomery: 91.2	
    Montreal: 84.6	
    Montvideo: 87.4	
    Moscow: 87.3	
    Munich: 81.8	
    Muscat: 105.9	
    Nairobi: 82.4	
    Nassau: 91.8	
    Niamey: 102.8	
    Nicosia: 102.5	
    Nouakchott: 99.5	
    Osaka: 93.0	
    Oslo: 77.1	
    Ottawa: 84.9	
    Panama City: 90.6	
    Paramaribo: 90.5	
    Paris: 91.5	
    Perth: 95.2	
    Phoenix: 107.7	
    Port au Prince: 97.4	
    Prague: 83.6	
    Pristina: 89.6	
    Pyongyang: 89.4	
    Quebec: 82.9	
    Quito: 69.0	
    Rabat: 97.0	
    Rangoon: 99.3	
    Regina: 83.2	
    Reykjavik: 69.7	
    Riga: 81.2	
    Rio de Janeiro: 93.4	
    Riyadh: 105.0	
    Rome: 85.8	
    San Jose: 85.6	
    Santo Domingo: 87.4	
    Sao Paulo: 89.2	
    Sapporo: 82.5	
    Seoul: 90.0	
    Shanghai: 96.8	
    Shenyang: 90.7	
    Singapore: 88.5	
    Skopje: 88.0	
    Sofia: 86.0	
    Stockholm: 79.2	
    Sydney: 96.8	
    Taipei: 94.0	
    Tashkent: 95.4	
    Tbilisi: 90.6	
    Tegucigalpa: 88.0	
    Tel Aviv: 88.5	
    Tirana: 92.5	
    Tokyo: 90.6	
    Toronto: 88.8	
    Tucson: 101.6	
    Tunis: 96.4	
    Ulan-bator: 87.5	
    Vancouver: 83.1	
    Vienna: 86.2	
    Vientiane: 97.0	
    Warsaw: 84.4	
    Windhoek: 92.2	
    Winnipeg: 86.6	
    Yerevan: 91.8	
    Yuma: 104.3	
    Zagreb: 87.5	
    Zurich: 82.4	



```python
!cat city_temperature.csv | python3 mapper.py | sort | python3 reducer.py
```

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
!hdfs dfs -cat /salida_avg_temp/part-00000
```

    Abidjan: 75.1398197614812	
    Abu Dhabi: 82.19085316496732	
    Addis Ababa: 25.452670934423686	
    Algiers: 63.75590092277833	
    Almaty: 49.32025473581944	
    Amman: 64.16002374399635	
    Amsterdam: 50.8167880848305	
    Anchorage: 37.75395865939927	
    Ankara: 50.90550429010864	
    Antananarivo: 63.44672170956882	
    Ashabad: 62.04525929523497	
    Athens: 59.63615484067216	
    Auckland: 58.91440828881299	
    Bangkok: 72.46335095567325	
    Bangui: 67.01901138632614	
    Banjul: 59.664577353406244	
    Barcelona: 61.26888996816112	
    Beijing: 54.71827748097774	
    Beirut: 69.39622794236656	
    Belfast: 49.65008364362405	
    Belgrade: 54.03263720252593	
    Belize City: 73.47476383265831	
    Bern: 49.034569100426225	
    Bilbao: 58.6960822405701	
    Birmingham: 63.29183442171747	
    Bishkek: 51.377596194889335	
    Bissau: 2.386007231126249	
    Bogota: 55.24561545518355	
    Bombay (Mumbai): 81.52145054233492	
    Bonn: -46.83535514764556	
    Bordeaux: 56.45363445038021	
    Brasilia: 70.36465921968572	
    Bratislava: 51.446527440505164	
    Brazzaville: 69.3170597441849	
    Bridgetown: 77.00247614587573	
    Brisbane: 68.06960768442102	
    Brussels: 51.057811235227604	
    Bucharest: 52.36715773568613	
    Budapest: 51.09863472019858	
    Buenos Aires: 62.295601964275995	
    Bujumbura: -65.37594936708857	
    Cairo: 71.95545302466141	
    Calcutta: 78.86903027359499	
    Calgary: 39.3858933727727	
    Canberra: 55.57895958124223	
    Capetown: 61.94134693216763	
    Caracas: 78.32395164337089	
    Chengdu: 62.60739301710626	
    Chennai (Madras): 82.84672710593036	
    Colombo: 74.24141708488523	
    Conakry: 49.38634720198594	
    Copenhagen: 46.9607198748046	
    Cotonou: 76.15079596352064	
    Dakar: 75.55632723544367	
    Damascus: 62.80520805224311	
    Dar Es Salaam: 65.30325964176166	
    Delhi: 75.79967078633477	
    Dhahran: 79.6293508175487	
    Dhaka: 10.104397968844177	
    Doha: 82.23735362365781	
    Dubai: 82.97030381522897	
    Dublin: 49.06745453564273	
    Dusanbe: 35.152252981490605	
    Edmonton: 38.77939963491304	
    Fairbanks: 28.293475093097218	
    Flagstaff: 46.107835455435904	
    Frankfurt: -13.699601015596624	
    Freetown: -9.800708705806628	
    Geneva: 51.373028978468426	
    Georgetown: -22.09392832461251	
    Guadalajara: 2.62162572212162	
    Guangzhou: 72.82867087583037	
    Guatemala City: 56.91117586746527	
    Guayaquil: 73.71999892072722	
    Halifax: 43.81485810858405	
    Hamburg: -13.372970806333084	
    Hamilton: 66.9698380743983	
    Hanoi: 74.73761804543759	
    Havana: 72.63858692718797	
    Helsinki: 42.24660838594808	
    Hong Kong: 75.06204738006608	
    Huntsville: 61.48635112526268	
    Islamabad: 65.36522208430021	
    Istanbul: 59.45605741730101	
    Jakarta: 35.98386313346622	
    Juneau: 42.064606832532895	
    Kampala: 44.14160505154113	
    Karachi: 77.93611635814196	
    Katmandu: 49.48979437638268	
    Kiev: 47.66447034698616	
    Kuala Lumpur: 78.95348335222063	
    Kuwait: 79.49092871404696	
    La Paz: 44.868593168204484	
    Lagos: 38.57111111111111	
    Libreville: 70.38777999676144	
    Lilongwe: -20.564637681159496	
    Lima: 66.6343997902054	
    Lisbon: 61.8580756570078	
    Lome: 71.56734660838525	
    London: 52.36704980842909	
    Lusaka: 55.899698340875176	
    Madrid: 58.44305757919141	
    Managua: 71.85170642003348	
    Manama: 80.63445577680636	
    Manila: 81.54105552857351	
    Maputo: 62.78369641224243	
    Melbourne: 64.71816955372039	
    Mexico City: 62.050288736574736	
    Milan: 54.19300631374398	
    Minsk: 41.824914988935	
    Mobile: 66.72217065141122	
    Monterrey: 74.80798208214134	
    Montgomery: 64.92013060607692	
    Montreal: 45.216892778993326	
    Montvideo: 60.975937618045315	
    Moscow: 41.92463979277959	
    Munich: 46.13699326851174	
    Muscat: 21.905181405259988	
    Nairobi: 23.449917677907116	
    Nassau: 76.57340385341892	
    Niamey: 81.94105013221126	
    Nicosia: 23.80424666017873	
    Nouakchott: 73.41321158765116	
    Osaka: 62.03561599481979	
    Oslo: 40.92692487167542	
    Ottawa: 43.94439124005372	
    Panama City: 79.56894932815248	
    Paramaribo: 47.53205287294291	
    Paris: 52.93898872160177	
    Perth: 62.25038583994329	
    Phoenix: 75.15129256840626	
    Port au Prince: 16.678403021311002	
    Prague: 47.605407155577154	
    Pristina: 42.38673573617391	
    Pyongyang: 48.213172521720374	
    Quebec: 39.61772356846013	
    Quito: 42.43465258248211	
    Rabat: 62.734202147752626	
    Rangoon: 71.50988613674376	
    Regina: 36.809799794938414	
    Reykjavik: 41.08413469321719	
    Riga: 44.13847067076791	
    Rio de Janeiro: 73.19601165740235	
    Riyadh: 78.67243537855477	
    Rome: 60.22447250553093	
    San Jose: 70.37603475257666	
    Santo Domingo: 65.21391872200354	
    Sao Paulo: 66.83197344989514	
    Sapporo: 44.45750364254471	
    Seoul: 52.881128919108626	
    Shanghai: 62.87241379310355	
    Shenyang: 46.89235252846858	
    Singapore: 81.65329987588356	
    Skopje: 54.00601219709583	
    Sofia: 45.20407965031587	
    Stockholm: 45.094058604500695	
    Sydney: 57.55066645081227	
    Taipei: 69.3311100318392	
    Tashkent: 58.8115104419626	
    Tbilisi: 46.5103597944031	
    Tegucigalpa: 68.53163149657307	
    Tel Aviv: 54.01753043853038	
    Tirana: 33.17089741514245	
    Tokyo: 61.06175597647178	
    Toronto: 47.60209140201386	
    Tucson: 69.989357223811	
    Tunis: 66.47656359613654	
    Ulan-bator: 29.699552101883206	
    Vancouver: 50.378691641433214	
    Vienna: 51.04832442933429	
    Vientiane: 79.96494522691792	
    Warsaw: 47.77905131941073	
    Windhoek: 57.98774485996466	
    Winnipeg: 37.56491092176575	
    Yerevan: 53.70353433576219	
    Yuma: 68.52801696440055	
    Zagreb: 46.9286739705324	
    Zurich: 46.9286739705324	



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
!hdfs dfs -cat /salida_hottest_days/part-00000
```

    Algiers: 8	
    Calcutta: 12	
    Kuala Lumpur: 11	
    Lisbon: 0	


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



```python
!hdfs dfs -cat /salida_min_max_temps/part-00000
# Existen datos con -99 en el csv. Por eso la temperatura mínima es -99 en tantos.
```

    Abidjan:	
     Máxima temperatura: 88.6	
     Mínima temperatura: -99.0	
    Abu Dhabi:	
     Máxima temperatura: 107.3	
     Mínima temperatura: -99.0	
    Addis Ababa:	
     Máxima temperatura: 77.0	
     Mínima temperatura: -99.0	
    Algiers:	
     Máxima temperatura: 96.6	
     Mínima temperatura: -99.0	
    Almaty:	
     Máxima temperatura: 90.9	
     Mínima temperatura: -99.0	
    Amman:	
     Máxima temperatura: 95.4	
     Mínima temperatura: -99.0	
    Amsterdam:	
     Máxima temperatura: 85.5	
     Mínima temperatura: -99.0	
    Anchorage:	
     Máxima temperatura: 75.3	
     Mínima temperatura: -99.0	
    Ankara:	
     Máxima temperatura: 87.9	
     Mínima temperatura: -99.0	
    Antananarivo:	
     Máxima temperatura: 78.5	
     Mínima temperatura: -99.0	
    Ashabad:	
     Máxima temperatura: 102.2	
     Mínima temperatura: -99.0	
    Athens:	
     Máxima temperatura: 94.3	
     Mínima temperatura: -99.0	
    Auckland:	
     Máxima temperatura: 75.4	
     Mínima temperatura: -99.0	
    Bangkok:	
     Máxima temperatura: 93.0	
     Mínima temperatura: -99.0	
    Bangui:	
     Máxima temperatura: 93.7	
     Mínima temperatura: -99.0	
    Banjul:	
     Máxima temperatura: 93.6	
     Mínima temperatura: -99.0	
    Barcelona:	
     Máxima temperatura: 86.6	
     Mínima temperatura: -99.0	
    Beijing:	
     Máxima temperatura: 92.9	
     Mínima temperatura: -99.0	
    Beirut:	
     Máxima temperatura: 91.1	
     Mínima temperatura: -99.0	
    Belfast:	
     Máxima temperatura: 77.6	
     Mínima temperatura: -99.0	
    Belgrade:	
     Máxima temperatura: 91.9	
     Mínima temperatura: -99.0	
    Belize City:	
     Máxima temperatura: 92.9	
     Mínima temperatura: -99.0	
    Bern:	
     Máxima temperatura: 83.7	
     Mínima temperatura: -99.0	
    Bilbao:	
     Máxima temperatura: 94.6	
     Mínima temperatura: -99.0	
    Birmingham:	
     Máxima temperatura: 91.0	
     Mínima temperatura: -99.0	
    Bishkek:	
     Máxima temperatura: 91.1	
     Mínima temperatura: -99.0	
    Bissau:	
     Máxima temperatura: 100.1	
     Mínima temperatura: -99.0	
    Bogota:	
     Máxima temperatura: 66.7	
     Mínima temperatura: -99.0	
    Bombay (Mumbai):	
     Máxima temperatura: 92.6	
     Mínima temperatura: -99.0	
    Bonn:	
     Máxima temperatura: 86.9	
     Mínima temperatura: -99.0	
    Bordeaux:	
     Máxima temperatura: 88.8	
     Mínima temperatura: -99.0	
    Brasilia:	
     Máxima temperatura: 87.7	
     Mínima temperatura: -99.0	
    Bratislava:	
     Máxima temperatura: 85.5	
     Mínima temperatura: -99.0	
    Brazzaville:	
     Máxima temperatura: 88.7	
     Mínima temperatura: -99.0	
    Bridgetown:	
     Máxima temperatura: 88.0	
     Mínima temperatura: -99.0	
    Brisbane:	
     Máxima temperatura: 87.3	
     Mínima temperatura: -99.0	
    Brussels:	
     Máxima temperatura: 85.4	
     Mínima temperatura: -99.0	
    Bucharest:	
     Máxima temperatura: 91.4	
     Mínima temperatura: -99.0	
    Budapest:	
     Máxima temperatura: 88.2	
     Mínima temperatura: -99.0	
    Buenos Aires:	
     Máxima temperatura: 90.9	
     Mínima temperatura: -99.0	
    Bujumbura:	
     Máxima temperatura: 89.1	
     Mínima temperatura: -99.0	
    Cairo:	
     Máxima temperatura: 100.2	
     Mínima temperatura: -99.0	
    Calcutta:	
     Máxima temperatura: 96.8	
     Mínima temperatura: -99.0	
    Calgary:	
     Máxima temperatura: 79.1	
     Mínima temperatura: -99.0	
    Canberra:	
     Máxima temperatura: 93.2	
     Mínima temperatura: -99.0	
    Capetown:	
     Máxima temperatura: 83.8	
     Mínima temperatura: -99.0	
    Caracas:	
     Máxima temperatura: 89.9	
     Mínima temperatura: -99.0	
    Chengdu:	
     Máxima temperatura: 90.6	
     Mínima temperatura: -99.0	
    Chennai (Madras):	
     Máxima temperatura: 97.9	
     Mínima temperatura: -99.0	
    Colombo:	
     Máxima temperatura: 88.3	
     Mínima temperatura: -99.0	
    Conakry:	
     Máxima temperatura: 89.6	
     Mínima temperatura: -99.0	
    Copenhagen:	
     Máxima temperatura: 77.5	
     Mínima temperatura: -99.0	
    Cotonou:	
     Máxima temperatura: 88.6	
     Mínima temperatura: -99.0	
    Dakar:	
     Máxima temperatura: 87.0	
     Mínima temperatura: -99.0	
    Damascus:	
     Máxima temperatura: 95.5	
     Mínima temperatura: -99.0	
    Dar Es Salaam:	
     Máxima temperatura: 90.4	
     Mínima temperatura: -99.0	
    Delhi:	
     Máxima temperatura: 103.7	
     Mínima temperatura: -99.0	
    Dhahran:	
     Máxima temperatura: 107.8	
     Mínima temperatura: -99.0	
    Dhaka:	
     Máxima temperatura: 91.4	
     Mínima temperatura: -99.0	
    Doha:	
     Máxima temperatura: 108.5	
     Mínima temperatura: -99.0	
    Dubai:	
     Máxima temperatura: 107.5	
     Mínima temperatura: -99.0	
    Dublin:	
     Máxima temperatura: 70.1	
     Mínima temperatura: -99.0	
    Dusanbe:	
     Máxima temperatura: 97.6	
     Mínima temperatura: -99.0	
    Edmonton:	
     Máxima temperatura: 82.8	
     Mínima temperatura: -99.0	
    Fairbanks:	
     Máxima temperatura: 79.5	
     Mínima temperatura: -99.0	
    Flagstaff:	
     Máxima temperatura: 83.5	
     Mínima temperatura: -99.0	
    Frankfurt:	
     Máxima temperatura: 85.2	
     Mínima temperatura: -99.0	
    Freetown:	
     Máxima temperatura: 88.7	
     Mínima temperatura: -99.0	
    Geneva:	
     Máxima temperatura: 85.2	
     Mínima temperatura: -99.0	
    Georgetown:	
     Máxima temperatura: 90.6	
     Mínima temperatura: -99.0	
    Guadalajara:	
     Máxima temperatura: 88.5	
     Mínima temperatura: -99.0	
    Guangzhou:	
     Máxima temperatura: 94.7	
     Mínima temperatura: -99.0	
    Guatemala City:	
     Máxima temperatura: 79.8	
     Mínima temperatura: -99.0	
    Guayaquil:	
     Máxima temperatura: 90.0	
     Mínima temperatura: -99.0	
    Halifax:	
     Máxima temperatura: 80.5	
     Mínima temperatura: -99.0	
    Hamburg:	
     Máxima temperatura: 89.8	
     Mínima temperatura: -99.0	
    Hamilton:	
     Máxima temperatura: 85.4	
     Mínima temperatura: -99.0	
    Hanoi:	
     Máxima temperatura: 96.0	
     Mínima temperatura: -99.0	
    Havana:	
     Máxima temperatura: 88.3	
     Mínima temperatura: -99.0	
    Helsinki:	
     Máxima temperatura: 79.8	
     Mínima temperatura: -99.0	
    Hong Kong:	
     Máxima temperatura: 92.4	
     Mínima temperatura: -99.0	
    Huntsville:	
     Máxima temperatura: 91.5	
     Mínima temperatura: -99.0	
    Islamabad:	
     Máxima temperatura: 102.4	
     Mínima temperatura: -99.0	
    Istanbul:	
     Máxima temperatura: 88.7	
     Mínima temperatura: -99.0	
    Jakarta:	
     Máxima temperatura: 90.6	
     Mínima temperatura: -99.0	
    Juneau:	
     Máxima temperatura: 72.0	
     Mínima temperatura: -99.0	
    Kampala:	
     Máxima temperatura: 82.9	
     Mínima temperatura: -99.0	
    Karachi:	
     Máxima temperatura: 99.7	
     Mínima temperatura: -99.0	
    Katmandu:	
     Máxima temperatura: 86.6	
     Mínima temperatura: -99.0	
    Kiev:	
     Máxima temperatura: 86.9	
     Mínima temperatura: -99.0	
    Kuala Lumpur:	
     Máxima temperatura: 89.6	
     Mínima temperatura: -99.0	
    Kuwait:	
     Máxima temperatura: 110.0	
     Mínima temperatura: -99.0	
    La Paz:	
     Máxima temperatura: 63.4	
     Mínima temperatura: -99.0	
    Lagos:	
     Máxima temperatura: 93.2	
     Mínima temperatura: -99.0	
    Libreville:	
     Máxima temperatura: 86.8	
     Mínima temperatura: -99.0	
    Lilongwe:	
     Máxima temperatura: 90.7	
     Mínima temperatura: -99.0	
    Lima:	
     Máxima temperatura: 81.8	
     Mínima temperatura: -99.0	
    Lisbon:	
     Máxima temperatura: 96.3	
     Mínima temperatura: -99.0	
    Lome:	
     Máxima temperatura: 90.1	
     Mínima temperatura: -99.0	
    London:	
     Máxima temperatura: 83.4	
     Mínima temperatura: -99.0	
    Lusaka:	
     Máxima temperatura: 93.2	
     Mínima temperatura: -99.0	
    Madrid:	
     Máxima temperatura: 91.0	
     Mínima temperatura: -99.0	
    Managua:	
     Máxima temperatura: 93.9	
     Mínima temperatura: -99.0	
    Manama:	
     Máxima temperatura: 103.3	
     Mínima temperatura: -99.0	
    Manila:	
     Máxima temperatura: 91.9	
     Mínima temperatura: -99.0	
    Maputo:	
     Máxima temperatura: 95.6	
     Mínima temperatura: -99.0	
    Melbourne:	
     Máxima temperatura: 92.8	
     Mínima temperatura: -99.0	
    Mexico City:	
     Máxima temperatura: 77.0	
     Mínima temperatura: -99.0	
    Milan:	
     Máxima temperatura: 87.4	
     Mínima temperatura: -99.0	
    Minsk:	
     Máxima temperatura: 83.5	
     Mínima temperatura: -99.0	
    Mobile:	
     Máxima temperatura: 88.9	
     Mínima temperatura: -99.0	
    Monterrey:	
     Máxima temperatura: 103.4	
     Mínima temperatura: -99.0	
    Montgomery:	
     Máxima temperatura: 91.2	
     Mínima temperatura: -99.0	
    Montreal:	
     Máxima temperatura: 84.6	
     Mínima temperatura: -99.0	
    Montvideo:	
     Máxima temperatura: 87.4	
     Mínima temperatura: -99.0	
    Moscow:	
     Máxima temperatura: 87.3	
     Mínima temperatura: -99.0	
    Munich:	
     Máxima temperatura: 81.8	
     Mínima temperatura: -99.0	
    Muscat:	
     Máxima temperatura: 105.9	
     Mínima temperatura: -99.0	
    Nairobi:	
     Máxima temperatura: 82.4	
     Mínima temperatura: -99.0	
    Nassau:	
     Máxima temperatura: 91.8	
     Mínima temperatura: -99.0	
    Niamey:	
     Máxima temperatura: 102.8	
     Mínima temperatura: -99.0	
    Nicosia:	
     Máxima temperatura: 102.5	
     Mínima temperatura: -99.0	
    Nouakchott:	
     Máxima temperatura: 99.5	
     Mínima temperatura: -99.0	
    Osaka:	
     Máxima temperatura: 93.0	
     Mínima temperatura: -99.0	
    Oslo:	
     Máxima temperatura: 77.1	
     Mínima temperatura: -99.0	
    Ottawa:	
     Máxima temperatura: 84.9	
     Mínima temperatura: -99.0	
    Panama City:	
     Máxima temperatura: 90.6	
     Mínima temperatura: -99.0	
    Paramaribo:	
     Máxima temperatura: 90.5	
     Mínima temperatura: -99.0	
    Paris:	
     Máxima temperatura: 91.5	
     Mínima temperatura: -99.0	
    Perth:	
     Máxima temperatura: 95.2	
     Mínima temperatura: -99.0	
    Phoenix:	
     Máxima temperatura: 107.7	
     Mínima temperatura: -99.0	
    Port au Prince:	
     Máxima temperatura: 97.4	
     Mínima temperatura: -99.0	
    Prague:	
     Máxima temperatura: 83.6	
     Mínima temperatura: -99.0	
    Pristina:	
     Máxima temperatura: 89.6	
     Mínima temperatura: -99.0	
    Pyongyang:	
     Máxima temperatura: 89.4	
     Mínima temperatura: -99.0	
    Quebec:	
     Máxima temperatura: 82.9	
     Mínima temperatura: -99.0	
    Quito:	
     Máxima temperatura: 69.0	
     Mínima temperatura: -99.0	
    Rabat:	
     Máxima temperatura: 97.0	
     Mínima temperatura: -99.0	
    Rangoon:	
     Máxima temperatura: 99.3	
     Mínima temperatura: -99.0	
    Regina:	
     Máxima temperatura: 83.2	
     Mínima temperatura: -99.0	
    Reykjavik:	
     Máxima temperatura: 69.7	
     Mínima temperatura: -99.0	
    Riga:	
     Máxima temperatura: 81.2	
     Mínima temperatura: -99.0	
    Rio de Janeiro:	
     Máxima temperatura: 93.4	
     Mínima temperatura: -99.0	
    Riyadh:	
     Máxima temperatura: 105.0	
     Mínima temperatura: -99.0	
    Rome:	
     Máxima temperatura: 85.8	
     Mínima temperatura: -99.0	
    San Jose:	
     Máxima temperatura: 85.6	
     Mínima temperatura: -99.0	
    Santo Domingo:	
     Máxima temperatura: 87.4	
     Mínima temperatura: -99.0	
    Sao Paulo:	
     Máxima temperatura: 89.2	
     Mínima temperatura: -99.0	
    Sapporo:	
     Máxima temperatura: 82.5	
     Mínima temperatura: -99.0	
    Seoul:	
     Máxima temperatura: 90.0	
     Mínima temperatura: -99.0	
    Shanghai:	
     Máxima temperatura: 96.8	
     Mínima temperatura: -99.0	
    Shenyang:	
     Máxima temperatura: 90.7	
     Mínima temperatura: -99.0	
    Singapore:	
     Máxima temperatura: 88.5	
     Mínima temperatura: -99.0	
    Skopje:	
     Máxima temperatura: 88.0	
     Mínima temperatura: -99.0	
    Sofia:	
     Máxima temperatura: 86.0	
     Mínima temperatura: -99.0	
    Stockholm:	
     Máxima temperatura: 79.2	
     Mínima temperatura: -99.0	
    Sydney:	
     Máxima temperatura: 96.8	
     Mínima temperatura: -99.0	
    Taipei:	
     Máxima temperatura: 94.0	
     Mínima temperatura: -99.0	
    Tashkent:	
     Máxima temperatura: 95.4	
     Mínima temperatura: -99.0	
    Tbilisi:	
     Máxima temperatura: 90.6	
     Mínima temperatura: -99.0	
    Tegucigalpa:	
     Máxima temperatura: 88.0	
     Mínima temperatura: -99.0	
    Tel Aviv:	
     Máxima temperatura: 88.5	
     Mínima temperatura: -99.0	
    Tirana:	
     Máxima temperatura: 92.5	
     Mínima temperatura: -99.0	
    Tokyo:	
     Máxima temperatura: 90.6	
     Mínima temperatura: -99.0	
    Toronto:	
     Máxima temperatura: 88.8	
     Mínima temperatura: -99.0	
    Tucson:	
     Máxima temperatura: 101.6	
     Mínima temperatura: -99.0	
    Tunis:	
     Máxima temperatura: 96.4	
     Mínima temperatura: -99.0	
    Ulan-bator:	
     Máxima temperatura: 87.5	
     Mínima temperatura: -99.0	
    Vancouver:	
     Máxima temperatura: 83.1	
     Mínima temperatura: -99.0	
    Vienna:	
     Máxima temperatura: 86.2	
     Mínima temperatura: -99.0	
    Vientiane:	
     Máxima temperatura: 97.0	
     Mínima temperatura: -99.0	
    Warsaw:	
     Máxima temperatura: 84.4	
     Mínima temperatura: -99.0	
    Windhoek:	
     Máxima temperatura: 92.2	
     Mínima temperatura: -99.0	
    Winnipeg:	
     Máxima temperatura: 86.6	
     Mínima temperatura: -99.0	
    Yerevan:	
     Máxima temperatura: 91.8	
     Mínima temperatura: -99.0	
    Yuma:	
     Máxima temperatura: 104.3	
     Mínima temperatura: -99.0	
    Zagreb:	
     Máxima temperatura: 87.5	
     Mínima temperatura: -99.0	
    Zurich:	
     Máxima temperatura: 82.4	
     Mínima temperatura: -99.0	


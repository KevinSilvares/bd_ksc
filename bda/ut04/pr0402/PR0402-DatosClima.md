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

# sys.stdin.readline() lee la primera linea y la ignora

# for line in sys.stdin:
#    region, country, state, city, month, day, year, temp = line.strip().split(",")
#    print(f"{city}, {temp})

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


```python
%%writefile mapper_2.py
#!/usr/bin/env python3

import sys, csv

header = None

for line in sys.stdin:
    if header is None:
        # Evita la primera línea que actúa como cabecera
        if "Country" in line and "AvgTemperature" in line:
            header = line.strip().split(",")
        continue

    reader = csv.DictReader([line], fieldnames=header)
    for row in reader:
        try:
            print(f"{row['Country']}\t{row['AvgTemperature']}")
        except KeyError:
            # La primera línea es la cabecera. Como no encuentra los datos salta esta excepción. Con esta línea la capturo y omito.
            continue
```

    Writing mapper_2.py



```python
%%writefile reducer_avg_temp.py
#!/usr/bin/env python3

import sys, math

current_country = None
temps = []

for line in sys.stdin:   
    country, temp = line.strip().split("\t", 1)
    temps.append(float(temp))

    if current_country == country:
        temps.append(float(temp))
    else:
        if current_country:
                avg_temp = sum(temps) / len(temps)
                print(f"{current_country}: {avg_temp}")
        temps.clear()
        current_country = country
        
if current_country:
    print(f"{current_country}: {avg_temp}")
```

    Overwriting reducer_avg_temp.py



```python
!hdfs dfs -rm -r /salida_avg_temp
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_2.py \
-file reducer_avg_temp.py \
-mapper mapper_2.py \
-reducer reducer_avg_temp.py \
-input /datos_clima/city_temperature.csv \
-output /salida_avg_temp
```

    Deleted /salida_avg_temp
    2025-11-26 11:39:30,250 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_2.py, reducer_avg_temp.py, /tmp/hadoop-unjar2709013200162500361/] [] /tmp/streamjob6865543215658514710.jar tmpDir=null
    2025-11-26 11:39:31,406 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-11-26 11:39:31,607 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-11-26 11:39:31,910 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764156930469_0002
    2025-11-26 11:39:32,513 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-11-26 11:39:32,543 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.4:9866
    2025-11-26 11:39:32,544 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.2:9866
    2025-11-26 11:39:32,544 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.3:9866
    2025-11-26 11:39:32,544 INFO net.NetworkTopology: Adding a new node: /default-rack/172.19.0.5:9866
    2025-11-26 11:39:32,666 INFO mapreduce.JobSubmitter: number of splits:2
    2025-11-26 11:39:32,889 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764156930469_0002
    2025-11-26 11:39:32,890 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-11-26 11:39:33,593 INFO conf.Configuration: resource-types.xml not found
    2025-11-26 11:39:33,594 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-11-26 11:39:33,832 INFO impl.YarnClientImpl: Submitted application application_1764156930469_0002
    2025-11-26 11:39:33,995 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764156930469_0002/
    2025-11-26 11:39:34,006 INFO mapreduce.Job: Running job: job_1764156930469_0002
    2025-11-26 11:39:42,221 INFO mapreduce.Job: Job job_1764156930469_0002 running in uber mode : false
    2025-11-26 11:39:42,224 INFO mapreduce.Job:  map 0% reduce 0%
    2025-11-26 11:39:51,460 INFO mapreduce.Job:  map 50% reduce 0%
    2025-11-26 11:40:00,585 INFO mapreduce.Job:  map 72% reduce 0%
    2025-11-26 11:40:05,663 INFO mapreduce.Job:  map 100% reduce 0%
    2025-11-26 11:40:08,707 INFO mapreduce.Job:  map 100% reduce 100%
    2025-11-26 11:40:09,733 INFO mapreduce.Job: Job job_1764156930469_0002 completed successfully
    2025-11-26 11:40:09,850 INFO mapreduce.Job: Counters: 55
    	File System Counters
    		FILE: Number of bytes read=23753461
    		FILE: Number of bytes written=48449443
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=140605138
    		HDFS: Number of bytes written=3642
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Killed map tasks=1
    		Launched map tasks=3
    		Launched reduce tasks=1
    		Data-local map tasks=3
    		Total time spent by all maps in occupied slots (ms)=30124
    		Total time spent by all reduces in occupied slots (ms)=15442
    		Total time spent by all map tasks (ms)=30124
    		Total time spent by all reduce tasks (ms)=15442
    		Total vcore-milliseconds taken by all map tasks=30124
    		Total vcore-milliseconds taken by all reduce tasks=15442
    		Total megabyte-milliseconds taken by all map tasks=30846976
    		Total megabyte-milliseconds taken by all reduce tasks=15812608
    	Map-Reduce Framework
    		Map input records=2906328
    		Map output records=1541840
    		Map output bytes=20669775
    		Map output materialized bytes=23753467
    		Input split bytes=210
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=125
    		Reduce shuffle bytes=23753467
    		Reduce input records=1541840
    		Reduce output records=125
    		Spilled Records=3083680
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=365
    		CPU time spent (ms)=19280
    		Physical memory (bytes) snapshot=956522496
    		Virtual memory (bytes) snapshot=7631822848
    		Total committed heap usage (bytes)=863502336
    		Peak Map Physical memory (bytes)=358526976
    		Peak Map Virtual memory (bytes)=2556022784
    		Peak Reduce Physical memory (bytes)=281493504
    		Peak Reduce Virtual memory (bytes)=2550157312
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
    		Bytes Written=3642
    2025-11-26 11:40:09,850 INFO streaming.StreamJob: Output directory: /salida_avg_temp



```python
!hdfs dfs -cat /salida_avg_temp/part-00000
```

    Albania: 33.17078409152236	
    Algeria: 63.75446009389678	
    Argentina: 62.306097890022	
    Australia: 61.63451904294222	
    Austria: 51.04746101127842	
    Bahamas: 76.57320416644127	
    Bahrain: 80.63413199503516	
    Bangladesh: 10.104148377657351	
    Barbados: 77.0008370895045	
    Belarus: 41.820575376477436	
    Belgium: 51.05730397711927	
    Belize: 73.47787314439928	
    Benin: 76.15142194161199	
    Bermuda: 66.96951422319485	
    Bolivia: 44.868075117370665	
    Brazil: 70.13138164876939	
    Bulgaria: 45.193049484647275	
    Burundi: -65.37823885525572	
    Canada: 42.00553845739333	
    Central African Republic: 67.01835303005792	
    China: 59.9834033046609	
    Colombia: 55.24527008796091	
    Congo: 69.31675211830093	
    Costa Rica: 70.37446980735005	
    Croatia: 46.92855523773532	
    Cuba: 72.6312408916711	
    Cyprus: 23.80081394320081	
    Czech Republic: 47.60424693756433	
    Denmark: 46.96123252927531	
    Dominican Republic: 65.20562361703305	
    Egypt: 71.97248394582104	
    Equador: 59.9441514904405	
    Ethiopia: 25.452305126687847	
    Finland: 42.245993200582475	
    France: 54.696972722121636	
    Gabon: 70.39731742861733	
    Gambia: 59.66214047214608	
    Georgia: 46.50163335237006	
    Germany: 6.427018138530741	
    Greece: 59.63568332192521	
    Guatemala: 56.91197452916761	
    Guinea: 49.38811181263805	
    Guinea-Bissau: 2.377659057795128	
    Guyana: -22.075891006022303	
    Haiti: 16.680798489344667	
    Honduras: 68.53243024448228	
    Hong Kong: 75.06083859478738	
    Hungary: 51.098068102099184	
    Iceland: 41.083319842426256	
    India: 79.76241079258192	
    Indonesia: 35.98437044632726	
    Ireland: 49.06760023743983	
    Israel: 54.01610817799786	
    Italy: 57.210468661467864	
    Ivory Coast: 75.1371917327721	
    Japan: 55.854510297688456	
    Jordan: 64.15679671901098	
    Kazakhstan: 49.32423768147207	
    Kenya: 23.44728946887003	
    Kuwait: 79.49555879337352	
    Kyrgyzstan: 51.37347399231673	
    Laos: 79.9650207759967	
    Latvia: 44.13876207436176	
    Lebanon: 69.39783066213344	
    Macedonia: 54.00916401316807	
    Madagascar: 63.43595056931731	
    Malawi: -20.56312692138777	
    Malaysia: 78.95306783228116	
    Mauritania: 73.41447266670608	
    Mexico: 47.614733287820485	
    Mongolia: 29.69222923749382	
    Morocco: 62.734310075009645	
    Mozambique: 62.78375558065736	
    Myanmar (Burma): 71.51080351842803	
    Namibia: 57.988851114349266	
    Nepal: 49.49138107830914	
    New Zealand: 58.91453780152138	
    Nicaragua: 71.85044080263998	
    Nigeria: 61.99105951583332	
    North Korea: 48.20776536614334	
    Norway: 40.92372582568583	
    Oman: 21.884517467616206	
    Pakistan: 71.65138562832199	
    Panama: 79.57843073768316	
    Peru: 66.6331803579627	
    Philippines: 81.53986832874624	
    Poland: 47.77873293400247	
    Portugal: 61.858302304247076	
    Qatar: 82.23422912956791	
    Romania: 52.369305488100984	
    Russia: 44.963739342752724	
    Saudi Arabia: 79.1509241022049	
    Senegal: 75.55493497382865	
    Serbia-Montenegro: 42.372712680578175	
    Sierra Leone: -9.798171861157927	
    Singapore: 81.65215045059597	
    Slovakia: 51.447736225784105	
    South Africa: 61.93867033619357	
    South Korea: 52.87893799579033	
    Spain: 59.46887669754426	
    Sri Lanka: 74.24080189951947	
    Suriname: 47.511006204478036	
    Sweden: 45.095834007878445	
    Switzerland: 49.82893245795491	
    Syria: 62.80551028118052	
    Taiwan: 69.33068371917317	
    Tajikistan: 35.146403324159515	
    Tanzania: 65.31367866171797	
    Thailand: 72.49011793411972	
    The Netherlands: 50.81994495709885	
    Togo: 71.56815066645099	
    Tunisia: 66.47918622848182	
    Turkey: 55.178061678763264	
    Turkmenistan: 62.04813016027209	
    US: 56.72507663773526	
    Uganda: 44.13916563225247	
    Ukraine: 47.6664885866929	
    United Arab Emirates: 82.58118069233515	
    United Kingdom: 51.00741440250401	
    Uruguay: 60.97469645458976	
    Uzbekistan: 58.80487291565538	
    Venezuela: 78.3240056128237	
    Vietnam: 74.74076412497928	
    Yugoslavia: 54.030408504667776	
    Zambia: 54.030408504667776	



```python
!cat test_city_temperature.csv | python3 mapper_2.py | sort | python3 reducer_avg_temp.py
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


# PR0403: Análisis de logs con MapReduce


```python
!hdfs dfs -mkdir /analisis_logs
```


```python
!hdfs dfs -put logfiles.log /analisis_logs
```


```python
!head -n 100 logfiles.log > test_logfiles.log
```

## 1. Estadísticas básicas

### Contador de códigos


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

    200: 14
    303: 14
    304: 16
    403: 7
    404: 11
    500: 14
    502: 17



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
!hdfs dfs -rm -r /analisis_logs/salida
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_code_count.py \
-file reducer_code_count.py \
-mapper mapper_code_count.py \
-reducer reducer_code_count.py \
-input /analisis_logs/logfiles.log \
-output /analisis_logs/salida
```

    rm: `/analisis_logs/salida': No such file or directory
    2025-12-04 11:18:33,736 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_code_count.py, reducer_code_count.py, /tmp/hadoop-unjar8009058023898264362/] [] /tmp/streamjob6396366509413446861.jar tmpDir=null
    2025-12-04 11:18:35,011 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-04 11:18:35,419 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-04 11:18:36,112 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764846567674_0001
    2025-12-04 11:18:37,945 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-04 11:18:38,132 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-04 11:18:38,427 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764846567674_0001
    2025-12-04 11:18:38,427 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-04 11:18:38,910 INFO conf.Configuration: resource-types.xml not found
    2025-12-04 11:18:38,911 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-04 11:18:40,852 INFO impl.YarnClientImpl: Submitted application application_1764846567674_0001
    2025-12-04 11:18:40,952 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764846567674_0001/
    2025-12-04 11:18:40,955 INFO mapreduce.Job: Running job: job_1764846567674_0001
    2025-12-04 11:19:01,963 INFO mapreduce.Job: Job job_1764846567674_0001 running in uber mode : false
    2025-12-04 11:19:01,966 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-04 11:19:23,998 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-04 11:19:34,104 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-04 11:19:34,113 INFO mapreduce.Job: Job job_1764846567674_0001 completed successfully
    2025-12-04 11:19:34,231 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=1697990
    		FILE: Number of bytes written=4338630
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=51384518
    		HDFS: Number of bytes written=84
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=34650
    		Total time spent by all reduces in occupied slots (ms)=6612
    		Total time spent by all map tasks (ms)=34650
    		Total time spent by all reduce tasks (ms)=6612
    		Total vcore-milliseconds taken by all map tasks=34650
    		Total vcore-milliseconds taken by all reduce tasks=6612
    		Total megabyte-milliseconds taken by all map tasks=35481600
    		Total megabyte-milliseconds taken by all reduce tasks=6770688
    	Map-Reduce Framework
    		Map input records=212248
    		Map output records=212248
    		Map output bytes=1273488
    		Map output materialized bytes=1697996
    		Input split bytes=198
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=7
    		Reduce shuffle bytes=1697996
    		Reduce input records=212248
    		Reduce output records=7
    		Spilled Records=424496
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=1410
    		CPU time spent (ms)=8170
    		Physical memory (bytes) snapshot=935579648
    		Virtual memory (bytes) snapshot=7628521472
    		Total committed heap usage (bytes)=751828992
    		Peak Map Physical memory (bytes)=445526016
    		Peak Map Virtual memory (bytes)=2541789184
    		Peak Reduce Physical memory (bytes)=260464640
    		Peak Reduce Virtual memory (bytes)=2549645312
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=51384320
    	File Output Format Counters 
    		Bytes Written=84
    2025-12-04 11:19:34,232 INFO streaming.StreamJob: Output directory: /analisis_logs/salida



```python
!hdfs dfs -cat /analisis_logs/salida/part-00000
```

    200: 30407	
    303: 30078	
    304: 30373	
    403: 30501	
    404: 30024	
    500: 30179	
    502: 30679	


### Tráfico total por IP


```python
%%writefile mapper_ip_traffic.py
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    words = line.strip().split()
    print(f"{words[0]}\t{words[9]}")
```

    Overwriting mapper_ip_traffic.py



```python
!cat test_logfiles.log | python3 mapper_ip_traffic.py | sort | python3 reducer_ip_traffic.py | python3 mapper_ip_traffic_sort.py | sort | python3 reducer_ip_traffic_sort.py
```

    238.217.83.154 05152.0



```python
%%writefile reducer_ip_traffic.py
#!/usr/bin/env python3

import sys

current_ip = None
current_byte_count = 0

for line in sys.stdin:
    ip, byte_count = line.strip().split("\t")
    
    try:
        byte_count = float(byte_count)
    except ValueError:
        # Si encuentra un "-" se cuenta como 0
        byte_count = 0
    
    if current_ip == ip:
        current_byte_count += byte_count
    else:
        if current_ip:
            print(f"{current_ip}\t{current_byte_count}")
            
        current_ip = ip
        current_byte_count = byte_count

print(f"{current_ip}\t{current_byte_count}")
```

    Overwriting reducer_ip_traffic.py



```python
%%writefile mapper_ip_traffic_sort.py
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    ip, byte_count = line.strip().split("\t")
    byte_count = byte_count.zfill(7)
    
    print(f"{byte_count}\t{ip}")
```

    Overwriting mapper_ip_traffic_sort.py



```python
%%writefile reducer_ip_traffic_sort.py
#!/usr/bin/env python3

import sys

data = None

# Guardo cada entrada e imprimo la última de todas. Los datos ya están ordenados, así que es la ip con más bytes de consumo
for line in sys.stdin:
    data = line.strip().split("\t")
    
print(data[1], data[0])
```

    Overwriting reducer_ip_traffic_sort.py



```python
!hdfs dfs -rm -r /analisis_logs/salida/ip_bytes

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_ip_traffic.py \
-file reducer_ip_traffic.py \
-mapper mapper_ip_traffic.py \
-reducer reducer_ip_traffic.py \
-input /analisis_logs/logfiles.log \
-output /analisis_logs/salida/ip_bytes

!hdfs dfs -rm -r /analisis_logs/salida/ip_bytes/max

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_ip_traffic_sort.py \
-file reducer_ip_traffic_sort.py \
-mapper mapper_ip_traffic_sort.py \
-reducer reducer_ip_traffic_sort.py \
-input /analisis_logs/salida/ip_bytes/part-00000 \
-output /analisis_logs/salida/ip_bytes/max
```

    Deleted /analisis_logs/salida/ip_bytes
    2025-12-04 12:17:29,400 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_ip_traffic.py, reducer_ip_traffic.py, /tmp/hadoop-unjar5439262644866635278/] [] /tmp/streamjob1352813603275872425.jar tmpDir=null
    2025-12-04 12:17:30,849 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-12-04 12:17:31,061 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-12-04 12:17:31,561 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764850610596_0001
    2025-12-04 12:17:34,376 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-04 12:17:34,773 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-04 12:17:35,874 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764850610596_0001
    2025-12-04 12:17:35,875 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-04 12:17:36,241 INFO conf.Configuration: resource-types.xml not found
    2025-12-04 12:17:36,242 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-04 12:17:37,137 INFO impl.YarnClientImpl: Submitted application application_1764850610596_0001
    2025-12-04 12:17:37,440 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764850610596_0001/
    2025-12-04 12:17:37,443 INFO mapreduce.Job: Running job: job_1764850610596_0001
    2025-12-04 12:17:50,865 INFO mapreduce.Job: Job job_1764850610596_0001 running in uber mode : false
    2025-12-04 12:17:50,866 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-04 12:18:11,397 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-04 12:18:18,473 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-04 12:18:18,485 INFO mapreduce.Job: Job job_1764850610596_0001 completed successfully
    2025-12-04 12:18:18,605 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=4516733
    		FILE: Number of bytes written=9976143
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=51384518
    		HDFS: Number of bytes written=4516625
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=30366
    		Total time spent by all reduces in occupied slots (ms)=4660
    		Total time spent by all map tasks (ms)=30366
    		Total time spent by all reduce tasks (ms)=4660
    		Total vcore-milliseconds taken by all map tasks=30366
    		Total vcore-milliseconds taken by all reduce tasks=4660
    		Total megabyte-milliseconds taken by all map tasks=31094784
    		Total megabyte-milliseconds taken by all reduce tasks=4771840
    	Map-Reduce Framework
    		Map input records=212248
    		Map output records=212248
    		Map output bytes=4092231
    		Map output materialized bytes=4516739
    		Input split bytes=198
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=212243
    		Reduce shuffle bytes=4516739
    		Reduce input records=212248
    		Reduce output records=212243
    		Spilled Records=424496
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=705
    		CPU time spent (ms)=6650
    		Physical memory (bytes) snapshot=864464896
    		Virtual memory (bytes) snapshot=7645073408
    		Total committed heap usage (bytes)=729808896
    		Peak Map Physical memory (bytes)=327462912
    		Peak Map Virtual memory (bytes)=2547224576
    		Peak Reduce Physical memory (bytes)=215785472
    		Peak Reduce Virtual memory (bytes)=2552147968
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=51384320
    	File Output Format Counters 
    		Bytes Written=4516625
    2025-12-04 12:18:18,605 INFO streaming.StreamJob: Output directory: /analisis_logs/salida/ip_bytes
    rm: `/analisis_logs/salida/ip_bytes/max': No such file or directory
    2025-12-04 12:18:22,805 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_ip_traffic_sort.py, reducer_ip_traffic_sort.py, /tmp/hadoop-unjar7864900794245529448/] [] /tmp/streamjob3296155435192179724.jar tmpDir=null
    2025-12-04 12:18:24,250 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-12-04 12:18:24,580 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-12-04 12:18:25,020 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764850610596_0002
    2025-12-04 12:18:25,834 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-04 12:18:26,033 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-04 12:18:26,246 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764850610596_0002
    2025-12-04 12:18:26,247 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-04 12:18:26,497 INFO conf.Configuration: resource-types.xml not found
    2025-12-04 12:18:26,498 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-04 12:18:26,620 INFO impl.YarnClientImpl: Submitted application application_1764850610596_0002
    2025-12-04 12:18:26,684 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764850610596_0002/
    2025-12-04 12:18:26,687 INFO mapreduce.Job: Running job: job_1764850610596_0002
    2025-12-04 12:18:45,178 INFO mapreduce.Job: Job job_1764850610596_0002 running in uber mode : false
    2025-12-04 12:18:45,184 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-04 12:18:56,778 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-04 12:19:14,972 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-04 12:19:15,001 INFO mapreduce.Job: Job job_1764850610596_0002 completed successfully
    2025-12-04 12:19:15,126 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=5153356
    		FILE: Number of bytes written=11249571
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=4520947
    		HDFS: Number of bytes written=24
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=19586
    		Total time spent by all reduces in occupied slots (ms)=12523
    		Total time spent by all map tasks (ms)=19586
    		Total time spent by all reduce tasks (ms)=12523
    		Total vcore-milliseconds taken by all map tasks=19586
    		Total vcore-milliseconds taken by all reduce tasks=12523
    		Total megabyte-milliseconds taken by all map tasks=20056064
    		Total megabyte-milliseconds taken by all reduce tasks=12823552
    	Map-Reduce Framework
    		Map input records=212243
    		Map output records=212243
    		Map output bytes=4728864
    		Map output materialized bytes=5153362
    		Input split bytes=226
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=414
    		Reduce shuffle bytes=5153362
    		Reduce input records=212243
    		Reduce output records=1
    		Spilled Records=424486
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=579
    		CPU time spent (ms)=8840
    		Physical memory (bytes) snapshot=897765376
    		Virtual memory (bytes) snapshot=7634255872
    		Total committed heap usage (bytes)=793247744
    		Peak Map Physical memory (bytes)=327983104
    		Peak Map Virtual memory (bytes)=2542813184
    		Peak Reduce Physical memory (bytes)=246726656
    		Peak Reduce Virtual memory (bytes)=2549739520
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=4520721
    	File Output Format Counters 
    		Bytes Written=24
    2025-12-04 12:19:15,126 INFO streaming.StreamJob: Output directory: /analisis_logs/salida/ip_bytes/max



```python
!hdfs dfs -cat /analisis_logs/salida/ip_bytes/max/part-00000
```

    65.235.103.102 10099.0	


## 2. Análisis de comportamiento

### URLs más populares


```python
%%writefile mapper_url.py
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    words = line.strip().split()
    print(f"{words[5]}{words[6]}{words[7]}\t1")
```

    Overwriting mapper_url.py



```python
!cat test_logfiles.log | python3 mapper_url.py | sort | python3 reducer_url.py
```


```python
%%writefile reducer_url.py
#!/usr/bin/env python3

import sys

current_url = None
current_count = 0

for line in sys.stdin:
    url, count = line.strip().split("\t")

    if current_url == url:
        current_count += 1
    else:
        if current_url:
            print(f"{current_url}: {current_count}")
        
        current_url = url
        current_count = 0

print(f"{current_url}: {current_count}")
```

    Overwriting reducer_url.py



```python
!hdfs dfs -rm -r /analisis_logs/salida/urls

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_url.py \
-file reducer_url.py \
-mapper mapper_url.py \
-reducer reducer_url.py \
-input /analisis_logs/logfiles.log \
-output /analisis_logs/salida/urls
```

    rm: `/analisis_logs/salida/urls': No such file or directory
    2025-12-04 12:31:51,297 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_url.py, reducer_url.py, /tmp/hadoop-unjar6238276547948537226/] [] /tmp/streamjob8488414693736229156.jar tmpDir=null
    2025-12-04 12:31:52,574 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-12-04 12:31:52,825 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.6:8032
    2025-12-04 12:31:53,327 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764850610596_0003
    2025-12-04 12:31:53,997 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-04 12:31:54,144 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-04 12:31:54,387 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764850610596_0003
    2025-12-04 12:31:54,387 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-04 12:31:54,844 INFO conf.Configuration: resource-types.xml not found
    2025-12-04 12:31:54,845 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-04 12:31:55,496 INFO impl.YarnClientImpl: Submitted application application_1764850610596_0003
    2025-12-04 12:31:55,755 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764850610596_0003/
    2025-12-04 12:31:55,804 INFO mapreduce.Job: Running job: job_1764850610596_0003
    2025-12-04 12:32:06,688 INFO mapreduce.Job: Job job_1764850610596_0003 running in uber mode : false
    2025-12-04 12:32:06,723 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-04 12:32:19,049 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-04 12:32:28,220 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-04 12:32:28,233 INFO mapreduce.Job: Job job_1764850610596_0003 completed successfully
    2025-12-04 12:32:28,358 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=6450008
    		FILE: Number of bytes written=13842513
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=51384518
    		HDFS: Number of bytes written=688
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=20247
    		Total time spent by all reduces in occupied slots (ms)=5337
    		Total time spent by all map tasks (ms)=20247
    		Total time spent by all reduce tasks (ms)=5337
    		Total vcore-milliseconds taken by all map tasks=20247
    		Total vcore-milliseconds taken by all reduce tasks=5337
    		Total megabyte-milliseconds taken by all map tasks=20732928
    		Total megabyte-milliseconds taken by all reduce tasks=5465088
    	Map-Reduce Framework
    		Map input records=212248
    		Map output records=212248
    		Map output bytes=6025506
    		Map output materialized bytes=6450014
    		Input split bytes=198
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=20
    		Reduce shuffle bytes=6450014
    		Reduce input records=212248
    		Reduce output records=20
    		Spilled Records=424496
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=500
    		CPU time spent (ms)=6900
    		Physical memory (bytes) snapshot=780238848
    		Virtual memory (bytes) snapshot=7639511040
    		Total committed heap usage (bytes)=674758656
    		Peak Map Physical memory (bytes)=302481408
    		Peak Map Virtual memory (bytes)=2543669248
    		Peak Reduce Physical memory (bytes)=260747264
    		Peak Reduce Virtual memory (bytes)=2554617856
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=51384320
    	File Output Format Counters 
    		Bytes Written=688
    2025-12-04 12:32:28,358 INFO streaming.StreamJob: Output directory: /analisis_logs/salida/urls



```python
!hdfs dfs -cat /analisis_logs/salida/urls/part-00000
```

    "DELETE/usr/admin/developerHTTP/1.0": 10608	
    "DELETE/usr/adminHTTP/1.0": 10673	
    "DELETE/usr/loginHTTP/1.0": 10648	
    "DELETE/usr/registerHTTP/1.0": 10447	
    "DELETE/usrHTTP/1.0": 10578	
    "GET/usr/admin/developerHTTP/1.0": 10617	
    "GET/usr/adminHTTP/1.0": 10559	
    "GET/usr/loginHTTP/1.0": 10702	
    "GET/usr/registerHTTP/1.0": 10765	
    "GET/usrHTTP/1.0": 10681	
    "POST/usr/admin/developerHTTP/1.0": 10496	
    "POST/usr/adminHTTP/1.0": 10560	
    "POST/usr/loginHTTP/1.0": 10615	
    "POST/usr/registerHTTP/1.0": 10470	
    "POST/usrHTTP/1.0": 10680	
    "PUT/usr/admin/developerHTTP/1.0": 10610	
    "PUT/usr/adminHTTP/1.0": 10547	
    "PUT/usr/loginHTTP/1.0": 10607	
    "PUT/usr/registerHTTP/1.0": 10755	
    "PUT/usrHTTP/1.0": 10610	


### Mostrar solo las TOP 10 (Opcional)


```python
## TODO
```

### Distribución por Método HTTP


```python
%%writefile mapper_http.py
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    words = line.strip().split()
    print(f"{words[5]}\t1")
```

    Overwriting mapper_http.py



```python
!cat test_logfiles.log | python3 mapper_http.py | sort | python3 reducer_http.py
```

    "DELETE: 22
    "GET: 24
    "POST: 23
    "PUT: 27



```python
%%writefile reducer_http.py
#!/usr/bin/env python3

import sys

current_http = None
current_count = 0

for line in sys.stdin:
    http, count = line.strip().split("\t")

    if current_http == http:
        current_count += 1
    else:
        if current_http:
            print(f"{current_http}: {current_count}")
        
        current_http = http
        current_count = 0

print(f"{current_http}: {current_count}")
```

    Writing reducer_http.py



```python
!hdfs dfs -rm -r /analisis_logs/salida/http

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_http.py \
-file reducer_http.py \
-mapper mapper_http.py \
-reducer reducer_http.py \
-input /analisis_logs/logfiles.log \
-output /analisis_logs/salida/http
```

    rm: `/analisis_logs/salida/http': No such file or directory
    2025-12-09 08:48:50,570 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_http.py, reducer_http.py, /tmp/hadoop-unjar4892502937826802651/] [] /tmp/streamjob4749477645011929626.jar tmpDir=null
    2025-12-09 08:48:51,928 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-09 08:48:52,218 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-09 08:48:53,396 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1765269474125_0001
    2025-12-09 08:48:57,339 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-09 08:48:57,595 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-09 08:48:58,429 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1765269474125_0001
    2025-12-09 08:48:58,430 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-09 08:48:59,213 INFO conf.Configuration: resource-types.xml not found
    2025-12-09 08:48:59,213 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-09 08:49:01,393 INFO impl.YarnClientImpl: Submitted application application_1765269474125_0001
    2025-12-09 08:49:01,505 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1765269474125_0001/
    2025-12-09 08:49:01,511 INFO mapreduce.Job: Running job: job_1765269474125_0001
    2025-12-09 08:49:19,160 INFO mapreduce.Job: Job job_1765269474125_0001 running in uber mode : false
    2025-12-09 08:49:19,159 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-09 08:49:42,613 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-09 08:49:48,685 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-09 08:49:49,703 INFO mapreduce.Job: Job job_1765269474125_0001 completed successfully
    2025-12-09 08:49:49,856 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=2121941
    		FILE: Number of bytes written=5186403
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=51384518
    		HDFS: Number of bytes written=56
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=34420
    		Total time spent by all reduces in occupied slots (ms)=4342
    		Total time spent by all map tasks (ms)=34420
    		Total time spent by all reduce tasks (ms)=4342
    		Total vcore-milliseconds taken by all map tasks=34420
    		Total vcore-milliseconds taken by all reduce tasks=4342
    		Total megabyte-milliseconds taken by all map tasks=35246080
    		Total megabyte-milliseconds taken by all reduce tasks=4446208
    	Map-Reduce Framework
    		Map input records=212248
    		Map output records=212248
    		Map output bytes=1697439
    		Map output materialized bytes=2121947
    		Input split bytes=198
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=4
    		Reduce shuffle bytes=2121947
    		Reduce input records=212248
    		Reduce output records=4
    		Spilled Records=424496
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=328
    		CPU time spent (ms)=8150
    		Physical memory (bytes) snapshot=895176704
    		Virtual memory (bytes) snapshot=7634976768
    		Total committed heap usage (bytes)=803209216
    		Peak Map Physical memory (bytes)=322772992
    		Peak Map Virtual memory (bytes)=2542145536
    		Peak Reduce Physical memory (bytes)=260677632
    		Peak Reduce Virtual memory (bytes)=2551271424
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=51384320
    	File Output Format Counters 
    		Bytes Written=56
    2025-12-09 08:49:49,856 INFO streaming.StreamJob: Output directory: /analisis_logs/salida/http



```python
!hdfs dfs -cat /analisis_logs/salida/http/part-00000
```

    "DELETE: 52958	
    "GET: 53328	
    "POST: 52825	
    "PUT: 53133	


### Análisis de navegadores


```python
%%writefile mapper_browser.py
#!/usr/bin/env python3

import sys

#line_count = 1
for line in sys.stdin:
    words = line.strip().split()
    try:
        # Me quedo con el último campo según hemos visto en clase
        browser, port = words[-2].split("/")
        print(f"{browser}\t1")
        #line_count += 1
    except ValueError:
        continue
        #print("Fallo", line_count, words[-2])
```

    Overwriting mapper_browser.py


El último log está incompleto y rompe el mapper. Dejo el código que he utilizado para detectarlo comentado.


```python
!cat logfiles.log | python3 mapper_browser.py | sort | python3 reducer_browser.py
```

    Edg: 21179
    EdgA: 21371
    Firefox: 42220
    OPR: 42457
    Safari: 85015



```python
%%writefile reducer_browser.py
#!/usr/bin/env python3

import sys

current_browser = None
current_count = 0

for line in sys.stdin:
    browser, count = line.strip().split("\t")

    if current_browser == browser:
        current_count += 1
    else:
        if current_browser:
            print(f"{current_browser}: {current_count}")
        
        current_browser = browser
        current_count = 0

print(f"{current_browser}: {current_count}")
```

    Overwriting reducer_browser.py



```python
!hdfs dfs -rm -r /analisis_logs/salida/browser

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_browser.py \
-file reducer_browser.py \
-mapper mapper_browser.py \
-reducer reducer_browser.py \
-input /analisis_logs/logfiles.log \
-output /analisis_logs/salida/browser
```

    Deleted /analisis_logs/salida/browser
    2025-12-09 09:15:54,033 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_browser.py, reducer_browser.py, /tmp/hadoop-unjar6665039652051486846/] [] /tmp/streamjob3540671342381125192.jar tmpDir=null
    2025-12-09 09:15:55,327 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-09 09:15:55,548 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-09 09:15:55,879 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1765269474125_0004
    2025-12-09 09:15:57,360 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-09 09:15:57,541 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-09 09:15:57,749 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1765269474125_0004
    2025-12-09 09:15:57,750 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-09 09:15:58,030 INFO conf.Configuration: resource-types.xml not found
    2025-12-09 09:15:58,031 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-09 09:15:58,160 INFO impl.YarnClientImpl: Submitted application application_1765269474125_0004
    2025-12-09 09:15:58,236 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1765269474125_0004/
    2025-12-09 09:15:58,238 INFO mapreduce.Job: Running job: job_1765269474125_0004
    2025-12-09 09:16:14,618 INFO mapreduce.Job: Job job_1765269474125_0004 running in uber mode : false
    2025-12-09 09:16:14,620 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-09 09:16:23,850 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-09 09:16:32,960 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-09 09:16:34,000 INFO mapreduce.Job: Job job_1765269474125_0004 completed successfully
    2025-12-09 09:16:34,210 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=2143286
    		FILE: Number of bytes written=5229174
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=51384518
    		HDFS: Number of bytes written=68
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=14891
    		Total time spent by all reduces in occupied slots (ms)=6742
    		Total time spent by all map tasks (ms)=14891
    		Total time spent by all reduce tasks (ms)=6742
    		Total vcore-milliseconds taken by all map tasks=14891
    		Total vcore-milliseconds taken by all reduce tasks=6742
    		Total megabyte-milliseconds taken by all map tasks=15248384
    		Total megabyte-milliseconds taken by all reduce tasks=6903808
    	Map-Reduce Framework
    		Map input records=212248
    		Map output records=212247
    		Map output bytes=1718786
    		Map output materialized bytes=2143292
    		Input split bytes=198
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=5
    		Reduce shuffle bytes=2143292
    		Reduce input records=212247
    		Reduce output records=5
    		Spilled Records=424494
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=240
    		CPU time spent (ms)=6190
    		Physical memory (bytes) snapshot=814256128
    		Virtual memory (bytes) snapshot=7635738624
    		Total committed heap usage (bytes)=769654784
    		Peak Map Physical memory (bytes)=302977024
    		Peak Map Virtual memory (bytes)=2544017408
    		Peak Reduce Physical memory (bytes)=211238912
    		Peak Reduce Virtual memory (bytes)=2548781056
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=51384320
    	File Output Format Counters 
    		Bytes Written=68
    2025-12-09 09:16:34,210 INFO streaming.StreamJob: Output directory: /analisis_logs/salida/browser



```python
!hdfs dfs -cat /analisis_logs/salida/browser/part-00000
```

    Edg: 21179	
    EdgA: 21371	
    Firefox: 42220	
    OPR: 42457	
    Safari: 85015	


## 3. Análisis temporal y de sesión

### Picos de tráfico por hora


```python
%%writefile mapper_datetime.py
#!/usr/bin/env python3

from datetime import datetime
import sys

for line in sys.stdin:
    words = line.strip().split()
    
    # Extrae la fecha y le recorta el "[" del principio para parsearla
    datetime_string = words[3][1:]
    date_time = datetime.strptime(datetime_string, "%d/%b/%Y:%H:%M:%S")
    
    print(f"{date_time.hour}\t1")
```

    Overwriting mapper_datetime.py



```python
%%writefile reducer_datetime.py
#!/usr/bin/env python3

import sys

current_hour = None
current_count = 0

for line in sys.stdin:
    hour, count = line.strip().split("\t")

    if current_hour == hour:
        current_count += 1
    else:
        if current_hour:
            print(f"{current_hour}: {current_count}")
        
        current_hour = hour
        current_count = 0

print(f"{current_hour}: {current_count}")
```

    Writing reducer_datetime.py



```python
!hdfs dfs -rm -r /analisis_logs/salida/hour

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_datetime.py \
-file reducer_datetime.py \
-mapper mapper_datetime.py \
-reducer reducer_datetime.py \
-input /analisis_logs/logfiles.log \
-output /analisis_logs/salida/hour
```

    rm: `/analisis_logs/salida/hour': No such file or directory
    2025-12-10 08:07:55,328 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_datetime.py, reducer_datetime.py, /tmp/hadoop-unjar8394597996170090578/] [] /tmp/streamjob3649712701361942089.jar tmpDir=null
    2025-12-10 08:07:56,600 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-10 08:07:56,956 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-12-10 08:07:58,006 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1765353186997_0001
    2025-12-10 08:08:00,641 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-10 08:08:00,844 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-10 08:08:01,219 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1765353186997_0001
    2025-12-10 08:08:01,219 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-10 08:08:01,711 INFO conf.Configuration: resource-types.xml not found
    2025-12-10 08:08:01,712 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-10 08:08:03,460 INFO impl.YarnClientImpl: Submitted application application_1765353186997_0001
    2025-12-10 08:08:03,543 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1765353186997_0001/
    2025-12-10 08:08:03,546 INFO mapreduce.Job: Running job: job_1765353186997_0001
    2025-12-10 08:08:19,994 INFO mapreduce.Job: Job job_1765353186997_0001 running in uber mode : false
    2025-12-10 08:08:20,000 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-10 08:08:37,541 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-10 08:08:44,639 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-10 08:08:45,657 INFO mapreduce.Job: Job job_1765353186997_0001 completed successfully
    2025-12-10 08:08:45,813 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=1485742
    		FILE: Number of bytes written=3914101
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=51384518
    		HDFS: Number of bytes written=12
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=23968
    		Total time spent by all reduces in occupied slots (ms)=4757
    		Total time spent by all map tasks (ms)=23968
    		Total time spent by all reduce tasks (ms)=4757
    		Total vcore-milliseconds taken by all map tasks=23968
    		Total vcore-milliseconds taken by all reduce tasks=4757
    		Total megabyte-milliseconds taken by all map tasks=24543232
    		Total megabyte-milliseconds taken by all reduce tasks=4871168
    	Map-Reduce Framework
    		Map input records=212248
    		Map output records=212248
    		Map output bytes=1061240
    		Map output materialized bytes=1485748
    		Input split bytes=198
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=1
    		Reduce shuffle bytes=1485748
    		Reduce input records=212248
    		Reduce output records=1
    		Spilled Records=424496
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=430
    		CPU time spent (ms)=6370
    		Physical memory (bytes) snapshot=881582080
    		Virtual memory (bytes) snapshot=7631949824
    		Total committed heap usage (bytes)=780664832
    		Peak Map Physical memory (bytes)=319627264
    		Peak Map Virtual memory (bytes)=2543349760
    		Peak Reduce Physical memory (bytes)=248303616
    		Peak Reduce Virtual memory (bytes)=2547924992
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=51384320
    	File Output Format Counters 
    		Bytes Written=12
    2025-12-10 08:08:45,813 INFO streaming.StreamJob: Output directory: /analisis_logs/salida/hour



```python
!hdfs dfs -cat /analisis_logs/salida/hour/part-00000
```

    12: 212247	


### Tasa de error por endpoint


```python
%%writefile mapper_endpoint_error.py
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    words = line.strip().split()
    url, http_code = words[6], int(words[8])

    status = None
    if http_code >= 400:
        status = "0,1"
    elif http_code < 400:
        status = "1,0"
    
    print(f"{url}\t{status}")
```

    Overwriting mapper_endpoint_error.py



```python
!cat test_logfiles.log | python3 mapper_endpoint_error.py | sort | python3 reducer_endpoint_error.py
```

    /usr: 45.45454545454545%
    /usr/admin: 43.75%
    /usr/admin/developer: 64.70588235294117%
    /usr/login: 60.0%
    /usr/register: 0%



```python
%%writefile reducer_endpoint_error.py
#!/usr/bin/env python3

import sys

# Entrada -> /usr/admin 0,1

current_url = None
total_success = 0
total_errors = 0
error_percent = 0

for line in sys.stdin:
    try:
        url, statuses = line.strip().split("\t") 
        status_success, status_error = statuses.split(",")

        status_success = int(status_success)
        status_error = int(status_error)

        if current_url == url:
            total_success += status_success
            total_errors += status_error
        else:
            if current_url:
                # Calculo el porcentaje de error diviendo los errores entre el total de intentos (que es la suma de errores y éxitos) * 100
                error_percent = (total_errors / (total_errors + total_success)) * 100
                print(f"{current_url}: {error_percent}%")
            
            current_url = url
            total_success = 0
            total_errors = 0
            error_percent = 0
    except ValueError:
        print("Fallo", status_success, status_error)

print(f"{current_url}: {error_percent}%")
```

    Overwriting reducer_endpoint_error.py



```python
!hdfs dfs -rm -r /analisis_logs/salida/error_percent

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_endpoint_error.py \
-file reducer_endpoint_error.py \
-mapper mapper_endpoint_error.py \
-reducer reducer_endpoint_error.py \
-input /analisis_logs/logfiles.log \
-output /analisis_logs/salida/error_percent
```

    Deleted /analisis_logs/salida/error_percent
    2025-12-16 09:01:11,479 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_endpoint_error.py, reducer_endpoint_error.py, /tmp/hadoop-unjar5234398849988002144/] [] /tmp/streamjob2666786636969729259.jar tmpDir=null
    2025-12-16 09:01:12,836 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-12-16 09:01:13,064 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-12-16 09:01:14,022 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1765874991030_0001
    2025-12-16 09:01:17,077 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-16 09:01:17,276 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-16 09:01:17,584 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1765874991030_0001
    2025-12-16 09:01:17,585 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-16 09:01:17,928 INFO conf.Configuration: resource-types.xml not found
    2025-12-16 09:01:17,929 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-16 09:01:19,076 INFO impl.YarnClientImpl: Submitted application application_1765874991030_0001
    2025-12-16 09:01:19,163 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1765874991030_0001/
    2025-12-16 09:01:19,166 INFO mapreduce.Job: Running job: job_1765874991030_0001
    2025-12-16 09:01:35,548 INFO mapreduce.Job: Job job_1765874991030_0001 running in uber mode : false
    2025-12-16 09:01:35,550 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-16 09:01:49,896 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-16 09:01:56,974 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-16 09:01:57,989 INFO mapreduce.Job: Job job_1765874991030_0001 completed successfully
    2025-12-16 09:01:58,106 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=3903577
    		FILE: Number of bytes written=8749945
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=51384518
    		HDFS: Number of bytes written=154
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=22034
    		Total time spent by all reduces in occupied slots (ms)=4816
    		Total time spent by all map tasks (ms)=22034
    		Total time spent by all reduce tasks (ms)=4816
    		Total vcore-milliseconds taken by all map tasks=22034
    		Total vcore-milliseconds taken by all reduce tasks=4816
    		Total megabyte-milliseconds taken by all map tasks=22562816
    		Total megabyte-milliseconds taken by all reduce tasks=4931584
    	Map-Reduce Framework
    		Map input records=212248
    		Map output records=212248
    		Map output bytes=3479075
    		Map output materialized bytes=3903583
    		Input split bytes=198
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=5
    		Reduce shuffle bytes=3903583
    		Reduce input records=212248
    		Reduce output records=5
    		Spilled Records=424496
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=392
    		CPU time spent (ms)=6640
    		Physical memory (bytes) snapshot=876548096
    		Virtual memory (bytes) snapshot=7635357696
    		Total committed heap usage (bytes)=792723456
    		Peak Map Physical memory (bytes)=323080192
    		Peak Map Virtual memory (bytes)=2545377280
    		Peak Reduce Physical memory (bytes)=244727808
    		Peak Reduce Virtual memory (bytes)=2549657600
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=51384320
    	File Output Format Counters 
    		Bytes Written=154
    2025-12-16 09:01:58,106 INFO streaming.StreamJob: Output directory: /analisis_logs/salida/error_percent



```python
!hdfs dfs -cat /analisis_logs/salida/error_percent/part-00000
```

    /usr: 57.15360030080843%	
    /usr/admin: 57.413442917198054%	
    /usr/admin/developer: 56.992015873765766%	
    /usr/login: 57.456253669994126%	
    /usr/register: 0%	


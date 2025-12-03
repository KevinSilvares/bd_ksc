# PR0401: MapReduce (I)


```python
!hdfs dfs -mkdir /quijote
```


```python
!hdfs dfs -put quijote.txt /quijote
```


```python
!hdfs dfs -ls /quijote
```

    Found 1 items
    -rw-r--r--   3 root supergroup    2141519 2025-11-27 08:42 /quijote/quijote.txt



```python
!head -n 100 > test_quijote.txt
```


```python
!head -n 10 test_quijote.txt
```

## Ejercicio 1: Contando palabras


```python
%%writefile mapper_word_count.py
#!/usr/bin/env python3

import sys, re

for line in sys.stdin:
    words = line.strip().split()
    for word in words:
        # Expresión regular que solo admite letras con tildes
        word = re.sub(r'[^\w]', '', word).lower()
        if word:
            # Este if es necesario porque por defecto la expresión regular va a devolver un espacio en blanco cuando no encuentre el patrón.
            # El patrón son letras, en mayúsculas o minúsculas.
            print(f"{word}\t1")
```

    Overwriting mapper_word_count.py



```python
%%writefile reducer_word_count.py
#!/usr/bin/env python3

import sys

current_word = None
current_count = 0

for line in sys.stdin:
    word, count = line.strip().split("\t", 1)
    count = int(count)
    
    if word == current_word:
        current_count += 1
    else:
        if current_word:
            print(f"{current_word}\t{current_count}")

        current_word = word
        current_count = count

if current_word:
    print(f"{current_word}\t{current_count}")
```

    Overwriting reducer_word_count.py



```python
!hdfs dfs -rm -r /quijote/salida
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_word_count.py \
-file reducer_word_count.py \
-mapper mapper_word_count.py \
-reducer reducer_word_count.py \
-input /quijote/quijote.txt \
-output /quijote/salida
```

    Deleted /quijote/salida
    2025-11-27 09:21:46,967 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_word_count.py, reducer_word_count.py, /tmp/hadoop-unjar1528436018903657975/] [] /tmp/streamjob6326661118854027009.jar tmpDir=null
    2025-11-27 09:21:48,317 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-11-27 09:21:48,620 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-11-27 09:21:49,086 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764232704066_0002
    2025-11-27 09:21:49,966 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-11-27 09:21:50,108 INFO mapreduce.JobSubmitter: number of splits:2
    2025-11-27 09:21:50,313 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764232704066_0002
    2025-11-27 09:21:50,313 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-11-27 09:21:50,665 INFO conf.Configuration: resource-types.xml not found
    2025-11-27 09:21:50,666 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-11-27 09:21:50,842 INFO impl.YarnClientImpl: Submitted application application_1764232704066_0002
    2025-11-27 09:21:50,947 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764232704066_0002/
    2025-11-27 09:21:50,951 INFO mapreduce.Job: Running job: job_1764232704066_0002
    2025-11-27 09:22:07,517 INFO mapreduce.Job: Job job_1764232704066_0002 running in uber mode : false
    2025-11-27 09:22:07,519 INFO mapreduce.Job:  map 0% reduce 0%
    2025-11-27 09:22:17,817 INFO mapreduce.Job:  map 100% reduce 0%
    2025-11-27 09:22:25,895 INFO mapreduce.Job:  map 100% reduce 100%
    2025-11-27 09:22:26,920 INFO mapreduce.Job: Job job_1764232704066_0002 completed successfully
    2025-11-27 09:22:27,118 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=3588305
    		FILE: Number of bytes written=8119179
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=2145799
    		HDFS: Number of bytes written=257804
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=14851
    		Total time spent by all reduces in occupied slots (ms)=5519
    		Total time spent by all map tasks (ms)=14851
    		Total time spent by all reduce tasks (ms)=5519
    		Total vcore-milliseconds taken by all map tasks=14851
    		Total vcore-milliseconds taken by all reduce tasks=5519
    		Total megabyte-milliseconds taken by all map tasks=15207424
    		Total megabyte-milliseconds taken by all reduce tasks=5651456
    	Map-Reduce Framework
    		Map input records=37453
    		Map output records=381215
    		Map output bytes=2825869
    		Map output materialized bytes=3588311
    		Input split bytes=184
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=22949
    		Reduce shuffle bytes=3588311
    		Reduce input records=381215
    		Reduce output records=22949
    		Spilled Records=762430
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=261
    		CPU time spent (ms)=6400
    		Physical memory (bytes) snapshot=802201600
    		Virtual memory (bytes) snapshot=7635410944
    		Total committed heap usage (bytes)=767557632
    		Peak Map Physical memory (bytes)=295669760
    		Peak Map Virtual memory (bytes)=2542559232
    		Peak Reduce Physical memory (bytes)=212992000
    		Peak Reduce Virtual memory (bytes)=2550984704
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=2145615
    	File Output Format Counters 
    		Bytes Written=257804
    2025-11-27 09:22:27,119 INFO streaming.StreamJob: Output directory: /quijote/salida



```python
!hdfs dfs -cat /quijote/salida/part-00000
# Limpio el output de las celdas porque ocupan muchísimo espacio y solo molestan, pero las dejo para que se puedan ejecutar 
```

## Ejercicio 2: Filtrado de palabras representativas


```python
%%writefile mapper_relevant_word.py
#!/usr/bin/env python3

import sys, re

relevant_words = ["a", "con", "de", "desde", "en", "hacia", "hasta", "mediante" \
                  "para", "por", "según", "sin", "so", "sobre", "tras", "versus", "vía", "de", "la", "el", "y", "en", "que", "los", "del", "se"]

for line in sys.stdin:
    words = line.strip().split()
    for word in words:
        # Expresión regular que solo admite letras con tildes
        word = re.sub(r'[^\w]', '', word).lower()
        if word and word not in relevant_words:
            # Este if es necesario porque por defecto la expresión regular va a devolver un espacio en blanco cuando no encuentre el patrón.
            # El patrón son letras, en mayúsculas o minúsculas.
            print(f"{word}\t1")
```

    Overwriting mapper_relevant_word.py



```python
!hdfs dfs -rm -r /quijote/salida/relevantes
!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_relevant_word.py \
-file reducer_word_count.py \
-mapper mapper_relevant_word.py \
-reducer reducer_word_count.py \
-input /quijote/quijote.txt \
-output /quijote/salida/relevantes
```

    rm: `/quijote/salida/relevantes': No such file or directory
    2025-11-27 09:31:20,196 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_relevant_word.py, reducer_word_count.py, /tmp/hadoop-unjar4094360871012928036/] [] /tmp/streamjob7059665977599925786.jar tmpDir=null
    2025-11-27 09:31:22,004 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-11-27 09:31:22,209 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.2:8032
    2025-11-27 09:31:22,558 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764232704066_0003
    2025-11-27 09:31:24,304 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-11-27 09:31:24,532 INFO mapreduce.JobSubmitter: number of splits:2
    2025-11-27 09:31:25,184 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764232704066_0003
    2025-11-27 09:31:25,184 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-11-27 09:31:25,463 INFO conf.Configuration: resource-types.xml not found
    2025-11-27 09:31:25,464 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-11-27 09:31:25,645 INFO impl.YarnClientImpl: Submitted application application_1764232704066_0003
    2025-11-27 09:31:25,758 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764232704066_0003/
    2025-11-27 09:31:25,768 INFO mapreduce.Job: Running job: job_1764232704066_0003
    2025-11-27 09:31:35,291 INFO mapreduce.Job: Job job_1764232704066_0003 running in uber mode : false
    2025-11-27 09:31:35,293 INFO mapreduce.Job:  map 0% reduce 0%
    2025-11-27 09:31:47,580 INFO mapreduce.Job:  map 100% reduce 0%
    2025-11-27 09:31:56,712 INFO mapreduce.Job:  map 100% reduce 100%
    2025-11-27 09:31:57,735 INFO mapreduce.Job: Job job_1764232704066_0003 completed successfully
    2025-11-27 09:31:57,901 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=2761530
    		FILE: Number of bytes written=6465698
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=2145799
    		HDFS: Number of bytes written=257620
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=19001
    		Total time spent by all reduces in occupied slots (ms)=6678
    		Total time spent by all map tasks (ms)=19001
    		Total time spent by all reduce tasks (ms)=6678
    		Total vcore-milliseconds taken by all map tasks=19001
    		Total vcore-milliseconds taken by all reduce tasks=6678
    		Total megabyte-milliseconds taken by all map tasks=19457024
    		Total megabyte-milliseconds taken by all reduce tasks=6838272
    	Map-Reduce Framework
    		Map input records=37453
    		Map output records=264987
    		Map output bytes=2231550
    		Map output materialized bytes=2761536
    		Input split bytes=184
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=22928
    		Reduce shuffle bytes=2761536
    		Reduce input records=264987
    		Reduce output records=22928
    		Spilled Records=529974
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=685
    		CPU time spent (ms)=5760
    		Physical memory (bytes) snapshot=655613952
    		Virtual memory (bytes) snapshot=7639638016
    		Total committed heap usage (bytes)=517472256
    		Peak Map Physical memory (bytes)=228302848
    		Peak Map Virtual memory (bytes)=2546429952
    		Peak Reduce Physical memory (bytes)=205946880
    		Peak Reduce Virtual memory (bytes)=2551037952
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=2145615
    	File Output Format Counters 
    		Bytes Written=257620
    2025-11-27 09:31:57,902 INFO streaming.StreamJob: Output directory: /quijote/salida/relevantes



```python
!hdfs dfs -cat /quijote/salida/relevantes/part-00000
```

## Ejercicio 3:  Ordenación por Frecuencia (Top-N)


```python
%%writefile mapper_top_n.py
#!/usr/bin/env python3

import sys, re

# Número de dígitos que deben tener todos los números
digits = 5
# Esto es necesario porque lo que imprime el reducer es un string aunque sean números

for line in sys.stdin:
    word, count = line.strip().split("\t")
    length_count = len(count)

    new_count = ""
    if length_count < digits:
        for i in range(digits - length_count):
            new_count += "0"
# sfill()
        new_count += count
        print(f"{new_count}\t{word}")
```

    Overwriting mapper_top_n.py



```python
!cat test_quijote.txt | python3 mapper_word_count.py | sort | python3 reducer_word_count.py > temp.txt
```


```python
!cat temp.txt | python3 mapper_top_n.py | sort | python3 reducer_top_n.py
```

    00136 de



```python
%%writefile reducer_top_n.py
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    # Si no hay siguiente línea se ha llegado al final, por lo tanto, la palabra más repetida
    if not sys.stdin.readline():
        word, count = line.strip().split("\t")
        print(word, count)
```

    Overwriting reducer_top_n.py



```python
!hdfs dfs -rm -r /quijote/salida/top_n

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_word_count.py \
-file reducer_word_count.py \
-mapper mapper_word_count.py \
-reducer reducer_word_count.py \
-input /quijote/quijote.txt \
-output /quijote/salida/top_n/count

!hdfs dfs -rm -r /quijote/salida/top_n/sort

!hadoop jar \
/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar \
-file mapper_top_n.py \
-file reducer_top_n.py \
-mapper mapper_top_n.py \
-reducer reducer_top_n.py \
-input /quijote/salida/top_n/count/part-00000 \
-output /quijote/salida/top_n/sort
```

    Deleted /quijote/salida/top_n
    2025-12-03 11:18:49,436 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_word_count.py, reducer_word_count.py, /tmp/hadoop-unjar8283093737294015652/] [] /tmp/streamjob5205267033361853870.jar tmpDir=null
    2025-12-03 11:18:50,532 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-12-03 11:18:50,854 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-12-03 11:18:51,349 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764759555848_0003
    2025-12-03 11:18:52,213 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-03 11:18:52,402 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-03 11:18:52,636 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764759555848_0003
    2025-12-03 11:18:52,637 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-03 11:18:52,956 INFO conf.Configuration: resource-types.xml not found
    2025-12-03 11:18:52,956 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-03 11:18:53,367 INFO impl.YarnClientImpl: Submitted application application_1764759555848_0003
    2025-12-03 11:18:53,520 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764759555848_0003/
    2025-12-03 11:18:53,524 INFO mapreduce.Job: Running job: job_1764759555848_0003
    2025-12-03 11:19:11,102 INFO mapreduce.Job: Job job_1764759555848_0003 running in uber mode : false
    2025-12-03 11:19:11,105 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-03 11:19:21,386 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-03 11:19:29,497 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-03 11:19:30,516 INFO mapreduce.Job: Job job_1764759555848_0003 completed successfully
    2025-12-03 11:19:30,641 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=3588305
    		FILE: Number of bytes written=8119215
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=2145799
    		HDFS: Number of bytes written=257804
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=15797
    		Total time spent by all reduces in occupied slots (ms)=5541
    		Total time spent by all map tasks (ms)=15797
    		Total time spent by all reduce tasks (ms)=5541
    		Total vcore-milliseconds taken by all map tasks=15797
    		Total vcore-milliseconds taken by all reduce tasks=5541
    		Total megabyte-milliseconds taken by all map tasks=16176128
    		Total megabyte-milliseconds taken by all reduce tasks=5673984
    	Map-Reduce Framework
    		Map input records=37453
    		Map output records=381215
    		Map output bytes=2825869
    		Map output materialized bytes=3588311
    		Input split bytes=184
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=22949
    		Reduce shuffle bytes=3588311
    		Reduce input records=381215
    		Reduce output records=22949
    		Spilled Records=762430
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=276
    		CPU time spent (ms)=6410
    		Physical memory (bytes) snapshot=854863872
    		Virtual memory (bytes) snapshot=7632805888
    		Total committed heap usage (bytes)=774373376
    		Peak Map Physical memory (bytes)=295108608
    		Peak Map Virtual memory (bytes)=2541780992
    		Peak Reduce Physical memory (bytes)=264847360
    		Peak Reduce Virtual memory (bytes)=2550059008
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=2145615
    	File Output Format Counters 
    		Bytes Written=257804
    2025-12-03 11:19:30,641 INFO streaming.StreamJob: Output directory: /quijote/salida/top_n/count
    rm: `/quijote/salida/top_n/sort': No such file or directory
    2025-12-03 11:19:35,309 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead.
    packageJobJar: [mapper_top_n.py, reducer_top_n.py, /tmp/hadoop-unjar3906567220781872708/] [] /tmp/streamjob2417375876988219418.jar tmpDir=null
    2025-12-03 11:19:36,973 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-12-03 11:19:37,366 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at yarnmanager/172.19.0.5:8032
    2025-12-03 11:19:37,740 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1764759555848_0004
    2025-12-03 11:19:38,543 INFO mapred.FileInputFormat: Total input files to process : 1
    2025-12-03 11:19:38,739 INFO mapreduce.JobSubmitter: number of splits:2
    2025-12-03 11:19:39,044 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1764759555848_0004
    2025-12-03 11:19:39,044 INFO mapreduce.JobSubmitter: Executing with tokens: []
    2025-12-03 11:19:39,513 INFO conf.Configuration: resource-types.xml not found
    2025-12-03 11:19:39,515 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
    2025-12-03 11:19:39,887 INFO impl.YarnClientImpl: Submitted application application_1764759555848_0004
    2025-12-03 11:19:40,102 INFO mapreduce.Job: The url to track the job: http://yarnmanager:8088/proxy/application_1764759555848_0004/
    2025-12-03 11:19:40,104 INFO mapreduce.Job: Running job: job_1764759555848_0004
    2025-12-03 11:19:48,456 INFO mapreduce.Job: Job job_1764759555848_0004 running in uber mode : false
    2025-12-03 11:19:48,457 INFO mapreduce.Job:  map 0% reduce 0%
    2025-12-03 11:19:57,691 INFO mapreduce.Job:  map 100% reduce 0%
    2025-12-03 11:20:04,768 INFO mapreduce.Job:  map 100% reduce 100%
    2025-12-03 11:20:04,781 INFO mapreduce.Job: Job job_1764759555848_0004 completed successfully
    2025-12-03 11:20:04,979 INFO mapreduce.Job: Counters: 54
    	File System Counters
    		FILE: Number of bytes read=392000
    		FILE: Number of bytes written=1726536
    		FILE: Number of read operations=0
    		FILE: Number of large read operations=0
    		FILE: Number of write operations=0
    		HDFS: Number of bytes read=260194
    		HDFS: Number of bytes written=9
    		HDFS: Number of read operations=11
    		HDFS: Number of large read operations=0
    		HDFS: Number of write operations=2
    		HDFS: Number of bytes read erasure-coded=0
    	Job Counters 
    		Launched map tasks=2
    		Launched reduce tasks=1
    		Data-local map tasks=2
    		Total time spent by all maps in occupied slots (ms)=12655
    		Total time spent by all reduces in occupied slots (ms)=4460
    		Total time spent by all map tasks (ms)=12655
    		Total time spent by all reduce tasks (ms)=4460
    		Total vcore-milliseconds taken by all map tasks=12655
    		Total vcore-milliseconds taken by all reduce tasks=4460
    		Total megabyte-milliseconds taken by all map tasks=12958720
    		Total megabyte-milliseconds taken by all reduce tasks=4567040
    	Map-Reduce Framework
    		Map input records=22949
    		Map output records=22945
    		Map output bytes=346104
    		Map output materialized bytes=392006
    		Input split bytes=220
    		Combine input records=0
    		Combine output records=0
    		Reduce input groups=349
    		Reduce shuffle bytes=392006
    		Reduce input records=22945
    		Reduce output records=1
    		Spilled Records=45890
    		Shuffled Maps =2
    		Failed Shuffles=0
    		Merged Map outputs=2
    		GC time elapsed (ms)=429
    		CPU time spent (ms)=3870
    		Physical memory (bytes) snapshot=851333120
    		Virtual memory (bytes) snapshot=7632232448
    		Total committed heap usage (bytes)=734003200
    		Peak Map Physical memory (bytes)=302342144
    		Peak Map Virtual memory (bytes)=2543386624
    		Peak Reduce Physical memory (bytes)=247664640
    		Peak Reduce Virtual memory (bytes)=2547306496
    	Shuffle Errors
    		BAD_ID=0
    		CONNECTION=0
    		IO_ERROR=0
    		WRONG_LENGTH=0
    		WRONG_MAP=0
    		WRONG_REDUCE=0
    	File Input Format Counters 
    		Bytes Read=259974
    	File Output Format Counters 
    		Bytes Written=9
    2025-12-03 11:20:04,980 INFO streaming.StreamJob: Output directory: /quijote/salida/top_n/sort



```python
!hdfs dfs -cat /quijote/salida/top_n/sort/part-00000
```

    09823 a	


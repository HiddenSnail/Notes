# ycsb测试工具学习



## 1. 工具介绍



## 2. 安装



## 3. workload文件

workload文件是用来配置测试性质的文件，文件样例如下：

```
# Yahoo! Cloud System Benchmark
# Workload A: Update heavy workload
#   Application example: Session store recording recent actions
#
#   Read/update ratio: 50/50
#   Default data size: 1 KB records (10 fields, 100 bytes each, plus key)
#   Request distribution: zipfian

# 总操作记录数
recordcount=10000
# 总操作次数
operationcount=10000
# 要使用的工作负载类
workload=site.ycsb.workloads.CoreWorkload
# ycsb客户端的线程数，默认为1
threadcount=2
# 读取时是否读取所有字段
readallfields=true
# 每条记录字段的个数，默认10
fieldcount=100
# 每个字段的长度，默认100
fieldlength=10000
# 读取操作的比例
readproportion=0.1
# 扫描操作的比例
scanproportion=0
# 更新操作的比例
updateproportion=0
# 插入操作的比例
insertproportion=0.9
# 请求的分布规则, 可选项有--均匀分布(uniform)、齐夫分布(zipfian)等
requestdistribution=zipfian
```



所有属性如下：

> ## Core YCSB properties
>
> All workload files can specify the following properties:
>
> - **workload**: workload class to use (e.g. com.yahoo.ycsb.workloads.CoreWorkload)
> - **recordcount**: the number of records in the dataset at the start of the workload. used when loading for all workloads. (default: 1000)
> - **operationcount**: the number of operations to perform in the workload (default: 1000)
> - **db**: database class to use. Alternatively this may be specified on the command line. (default: com.yahoo.ycsb.BasicDB)
> - **exporter**: measurements exporter class to use (default: com.yahoo.ycsb.measurements.exporter.TextMeasurementsExporter)
> - **exportfile**: path to a file where output should be written instead of to stdout (default: undefined/write to stdout)
> - **threadcount**: number of YCSB client threads. Alternatively this may be specified on the command line. (default: 1)
> - **measurementtype**: supported measurement types are hdrhistogram, histogram and timeseries (default: hdrhistogram)
>
> ## Core workload package properties
>
> The property files used with the core workload generator can specify values for the following properties:
>
> - **fieldcount**: the number of fields in a record (default: 10)
> - **fieldlength**: the size of each field (default: 100)
> - **minfieldlength**: the minimum size of each field (default: 1)
> - **readallfields**: should reads read all fields (true) or just one (false) (default: true)
> - **writeallfields**: should updates and read/modify/writes update all fields (true) or just one (false) (default: false)
> - **readproportion**: what proportion of operations should be reads (default: 0.95)
> - **updateproportion**: what proportion of operations should be updates (default: 0.05)
> - **insertproportion**: what proportion of operations should be inserts (default: 0)
> - **scanproportion**: what proportion of operations should be scans (default: 0)
> - **readmodifywriteproportion**: what proportion of operations should be read a record, modify it, write it back (default: 0)
> - **requestdistribution**: what distribution should be used to select the records to operate on – uniform, zipfian, hotspot, sequential, exponential or latest (default: uniform)
> - **minscanlength**: for scans, what is the minimum number of records to scan (default: 1)
> - **maxscanlength**: for scans, what is the maximum number of records to scan (default: 1000)
> - **scanlengthdistribution**: for scans, what distribution should be used to choose the number of records to scan, for each scan, between 1 and maxscanlength (default: uniform)
> - **insertstart**: for parallel loads and runs, defines the starting record for this YCSB instance (default: 0)
> - **insertcount**: for parallel loads and runs, defines the number of records for this YCSB instance (default: recordcount)
> - **zeropadding**: for generating a record sequence compatible with string sort order by 0 padding the record number. Controls the number of 0s to use for padding. (default: 1)
>   For example for row 5, with zeropadding=1 you get ‘user5’ key and with zeropading=8 you get ‘user00000005’ key. In order to see its impact, zeropadding needs to be bigger than number of digits in the record number.
> - **insertorder**: should records be inserted in order by key (“ordered”), or in hashed order (“hashed”) (default: hashed)
> - **fieldnameprefix**: what should be a prefix for field names, the shorter may decrease the required storage size (default: “field”)
>
> ## Measurement properties
>
> These properties apply to each measurement type:
>
> ### hdrhistogram
>
> - **hdrhistogram.percentiles**: comma seperated list of percentile values to be calculated for each measurement (default: 95,99)
> - **hdrhistogram.fileoutput=true|false** This option will enable periodical writes of the interval histogram into an output file. The path can be set through the ‘hdrhistogram.output.path’ property.
>
> ### histogram
>
> - **histogram.buckets**: number of buckets for histogram output (default: 1000)
>
> ### timeseries
>
> - **timeseries.granularity**: granularity for the timeseries output (default: 1000)



## 4. 使用方式

### Step1 建立数据库和数据表

ycsb在启动时需要数据库中存在名为**ycsb**的数据库，且这个库里存在有一张名为**usertable**的表。对于某些数据库来说，ycsb可以在启动时自动创建，而有些数据库则不能。因此建议，在启动ycsb之前先将对应数据库和table建立好。

在测试分片集群的时候，手动给测试的数据库和Collection进行分片设置。否则ycsb会插入失败。（注：需要研究一下为什么）

### Step2 执行ycsb命令

执行时分为2步，第一步是加载数据，第二步是执行才操作；

加载数据

```shell
# ./bin/ycsb command database [options]
$ ./bin/ycsb load mongodb -P workloads/workloada  -p mongodb.url=mongodb://root:caih123@10.19.1.37:20000,10.19.1.38:20000,10.19.1.39:20000/admin?w=1 -threads 2 -s > outputLoad.txt

# 参数解释
# load：执行的command为load操作
# mongodb: 指明所用的数据库类型
# -P: 指明需要的配置文件的周期
# -p: 表示显示修改ycsb内置的默认配置，包括workload中的配置
# -threads: 配置的并发线程数
# -s: 将信息输出到标准输出流中
```



执行操作

```shell
# ./bin/ycsb command database [options]
$ ./bin/ycsb run mongodb -P workloads/workloada  -p mongodb.url=mongodb://root:caih123@10.19.1.37:20000,10.19.1.38:20000,10.19.1.39:20000/admin?w=1 -threads 2 -s > outputRun.txt

# 参数解释：
# run：执行的command为run操作
# mongodb: 指明所用的数据库类型
# -P: 指明需要的配置文件的周期
# -p: 表示显示修改ycsb内置的默认配置，包括workload中的配置
# -threads: 配置的并发线程数
# -s: 将信息输出到标准输出流中
```



## 5. 数据查看


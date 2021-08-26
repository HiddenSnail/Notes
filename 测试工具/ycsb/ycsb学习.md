# ycsb测试工具学习



## 1. 工具介绍



## 2. 安装



## 3. workload文件

用来配置测试流程的文件

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
# ???
workload=site.ycsb.workloads.CoreWorkload
# 读取时是否读取所有字段
readallfields=true
# 每条记录字段的个数，默认10
fieldcount=100
# 每个字段的长度，默认100
fieldlength=10000
# 读取操作的比例
readproportion=0.1
# 更新操作的比例
updateproportion=0
# 扫描操作的比例
scanproportion=0
# 插入操作的比例
insertproportion=0.9
# 请求的分布规则
requestdistribution=zipfian
```


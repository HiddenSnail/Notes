# MongoDB学习

## 0. CRUD

## 1. Aggregation
Aggregation Pipeline(以下简称AP)是Mongo用于处理合并数据的方式之一，调用方式：
```MongoSh
db.<Collection>.aggregate([
	{<stage1>},
	{<stage2>}
])
```
[Aggregation API](https://docs.mongodb.com/manual/meta/aggregation-quick-reference/#std-label-aggregation-accumulator-operators)

AP的性能和可用性优于Map-Reduce，针对Map-Reduce自定义函数操作的能力，AP提供了` $accumulator`和`$function`两个接口。

---
## 2. DataModeling
数据建模的关键问题就是如何在*应用程序需求*、*数据库性能*和*数据检索模式*3者之间进行平衡。当我们为数据进行建模时，需要从程序是如何使用数据的以及数据本身固有的结构出发，进行设计。

---
#### 2.1 Flexible Schema
与SQL不同，MongoDB在同一个Collection下Document的格式可以不相同，并且可以随意增删改Document的字段。
当然，你可以要求Collection下的Document都保持一致的结构，通过使用[document validation rules](https://docs.mongodb.com/manual/core/schema-validation/),这样在插入或更新Collection时就会进行检查。

---
#### 2.2 Document Structure
支持Document的内嵌，也支持通过 _id关联多个document

---
#### 2.3 Atomicity of Write Operations
在MongoDB中写操作在单个Document是原子性的，即使修改了一个Document下的多个嵌入式Document那么它也是原子性的。

当进行多Document写时，MongoDB只能保证单个Document的写流程时原子性的，而整体的最终结果是非原子性的，而且不能保证每个Document写的顺序。

MongoDB为了保证多Document的写原子性，4.0版本开始，设计了基于副本集的多Document操作。

大多数情况下，multi-document transcation 会导致与single-document相比更大的性能损耗，因此合理的使用嵌入式Document设计，尽量减少multi-document transactions操作，是一个好的选择。

---
#### 2.4 Data Use and Performance
为数据建模的时候，要考虑应用程序会怎么使用数据，比如你的APP只是经常性地插入数据，那么请考虑使用[Capped Collection](https://docs.mongodb.com/manual/core/capped-collections/)

## 3、副本集（Replica Set）

---
#### 3.1 副本集的组成
一个副本集会由一个主节点，多个从节点，多个仲裁节点组成。
- 主节点：负责读写数据
- 从节点：负责从主节点复制数据，并可以读取数据
- 仲裁节点：用来充当投票节点，不存储数据

---
#### 3.2 副本集的开启
```
rs.slaveOk() // 在设置好对应的副本节点后，需要在副本节点上手动激活
rs.secondaryOk() // 效果同上
```



---
#### 3.3 主节点的选举机制
主节点的选举基本依据：
获得半数成员以上的投票的节点将被选举为主节点

主节点的选举额外参考：
1. 若多个节点同时能当选主节点，则priority大的当选
2. 若priority也相同，则oplog最新的节点当选

每个节点都拥有2种属性：
- priority会影响该节点获得的票数
- votes将会影响该节点能投出的票数

---
#### 3.4 故障模型
场景：1主、1从、1仲裁
|	 |主节点|从节点|仲裁节点|描述|
|----|----|----|----|----|
|状态1|不可用|可用|可用|从节点当选为主节点|
|状态2|可用|不可用|可用|主节点状态不变|
|状态3|可用|可用|不可用|主节点状态不变|
|状态4|不可用|不可用|可用|服务不可用，原因是没有存储数据的节点|
|状态5|可用|不可用|不可用|主节点服务降级，变为从节点，原因是票数少于半数|
|状态6|不可用|可用|不可用|从节点不会升级为主节点，原因是票数未多于半数|

## 4、分片集群（Sharded Cluster）

---
#### 4.1 分片集群的组成
一般分为3层：
- 第一层：路由节点Mongos，路由到具体分片节点

- 第二层：配置节点Mongod，一般是一个副本集，存储一些元数据

- 第三层：分片节点Mongod，一般是一个副本集，存储数据
  
  ![分片集合](https://docs.mongodb.com/manual/images/sharded-cluster-production-architecture.bakedsvg.svg)

  

---
## 5、配置文件

[配置参数参考](https://blog.csdn.net/zhanaolu4821/article/details/87614708)

### 5.1 Shard节点配置

```conf
# 数据库存放目录
dbpath=/app/mongodb/data/shard_27019
# 日志存放目录
logpath=/app/mongodb/logs/shard_27019/shard_27019.log
# 日志模式为追加
logappend = true
# 启用日志文件，默认启用
journal = true
# unix域套接字代替目录, 默认为tmp
unixSocketPrefix=/app/mongodb/data/shard_27019
# PID File的完整路径，如果没有设置，则没有PID文件
pidfilepath=/app/mongodb/data/shard_27019/shard_27019.pid
# 绑定端口号
port = 27019
# 0.0.0.0在服务器的环境中，指的就是服务器上所有的ipv4地址，如果机器上有2个ip 192.168.30.10 和 
# 10.0.2.15，mongo在配置中，如果配置监听在0.0.0.0这个地址上，那么通过这2个ip地址都是能够到达这个
# 服务的。同时呢，访问本地的127.0.0.1也是能够访问到该服务
bind_ip=0.0.0.0
# 以服务的形式在后台运行
fork = true
# mongod服务能占用的最大内存
wiredTigerCacheSizeGB=1
# 集群的私钥的完整路径，只对于Replica Set 架构有效
keyFile=/app/mongodb/keyFile/data_27019key
# 副本集名称
replSet=shard2
# 声明这是一个集群的分片
shardsvr=true
# 最大同时连接数
maxConns=20000
# 设置oplog的大小(MB)
oplogSize=100
```

### 5.2 Config节点配置

```conf
# 数据库存放目录
dbpath=/app/mongodb/data/config
# 日志存放目录
logpath=/app/mongodb/logs/configsrv.log
# unix域套接字代替目录, 默认为tmp
unixSocketPrefix=/app/mongodb/data/config
# PID File的完整路径，如果没有设置，则没有PID文件
pidfilepath=/app/mongodb/data/config/config.pid
# 日志模式为追加
logappend = true
# 启用日志文件，默认启用
#journal = true
# 以服务的形式在后台运行
fork = true
# 集群的私钥的完整路径，只对于Replica Set 架构有效
keyFile=/app/mongodb/keyFile/mongo_key
# 副本集名称
replSet=cfg_repset
# 声明这是一个集群的config服务
configsvr=true
# 启用验证
#auth = true
# 绑定端口
port = 21000
# 监听本机所有IP
bind_ip=0.0.0.0
# 最大同时连接数
maxConns=20000
```

### 5.3 Route节点配置

```conf
# 日志存放目录
logpath=/app/mongodb/logs/mongos_route.log
# unix域套接字代替目录, 默认为tmp
unixSocketPrefix=/app/mongodb/data/mongos
# PID File的完整路径，如果没有设置，则没有PID文件
pidfilepath=/app/mongodb/data/mongos/mongos_route.pid
# 日志模式为追加
logappend = true
# 以服务的形式在后台运行
fork = true
# 集群的私钥的完整路径，只对于Replica Set 架构有效
keyFile=/app/mongodb/keyFile/mongo_key
# 绑定端口
port = 20000
# 监听本机所有IP
bind_ip=0.0.0.0
# 最大同时连接数
maxConns=20000
# 连接的配置节点
configdb=cfg_repset/10.19.1.37:21000,10.19.1.38:21000,10.19.1.39:21000
# 连接池最大大小
#taskExecutorPoolSize=20
# 连接池最小大小
#ShardingTaskExecutorPoolMinSize=20

```


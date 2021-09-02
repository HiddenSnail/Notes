

# MongoDB学习

## 0. Help帮助使用

在mongo shell中，对于内置函数的使用不太清楚含义或者使用方式是都可以使用help命令进行查看

```shell
# 查看db下的方法
> db.help

# 查看db.auth方法的参数
> db.auth.help
db.auth(username, password):
Allows a user to authenticate to the database from within the shell.
For more information on usage: https://docs.mongodb.com/manual/reference/method/db.auth
```



## 1. CRUD

### 1.1 创建（Create）

#### 1.1.1 ObjectId

mongo中_id是一个12字节（24个16进制数）的数字，其结构如下：

```
时间戳	  	  |	机器码    | PID	| 计数器
61 2d 9d 23 | 1c 7e 6a | 0d 2e | fe eb 57
61 2d 9d 2d | 1c 7e 6a | 0d 2e | fe eb 58
```

时间戳保证，不同时间，_id不冲突；

机器码保证，同一时间，不同机器，_id不冲突；

PID保证，同一时间，同一机器，不同进程，_id不冲突；

计数器保证，同一时间，同一机器，同一进程，_id不冲突；

### 1.2 查询（Read）

#### 1.2.1 聚合框架（Aggregation）
Aggregation Pipeline(以下简称AP)是Mongo用于处理合并数据的方式之一，调用方式：
```MongoSh
db.<Collection>.aggregate([
	{<stage1>},
	{<stage2>}
])
```
[Aggregation API](https://docs.mongodb.com/manual/meta/aggregation-quick-reference/#std-label-aggregation-accumulator-operators)

AP的性能和可用性优于Map-Reduce，针对Map-Reduce自定义函数操作的能力，AP提供了` $accumulator`和`$function`两个接口。

### 1.3 更新（Update）

####  1.3.1 写入安全机制（WriteConcern）

>  MongoDB的写入安全机制结构
>
>  { w: <value>, j: <boolean>, wtimeout: <number> }



w的取值有：

| Value      | 含义                                                         |
| ---------- | ------------------------------------------------------------ |
| "majority" | 大多数成员写入确认后，才通知客户端写入成功                   |
| <number>   | 指定成员个数为number（包括主节点）写入确认后，才通知客户端写入成功。<br>w=1，主节点写入成功后立刻通知客户端; <br>w=0, 对客户端的写入不发送任何确认，但性能较高 |



j的取值有：

| Value | 含义                                                        |
| ----- | ------------------------------------------------------------|
| true  | 写操作journal持久化后才向客户端发送确认。<br>假如w=0，j=true，则j=true优先级高 |
| false | 默认值，不需要journal持久化                                  |



wtimeout取值为任意正整数，用于设置写操作的时间门限，仅在w不为0时生效。

### 1.4 删除（Delete）

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

## 3. 副本集（Replica Set）

### 3.1 副本集的组成
一个副本集会由一个主节点，多个从节点，多个仲裁节点组成。
- 主节点：负责读写数据
- 从节点：负责从主节点复制数据，并可以读取数据
- 仲裁节点：用来充当投票节点，不存储数据

### 3.2 副本集的开启
```
# 默认设置是关，原因是为了保护应用程序意外连接到了副本节点，读取到过期数据
rs.slaveOk() // 在设置好对应的副本节点后，需要在副本节点上手动激活
rs.secondaryOk() // 效果同上
```

关键概念：

>+ 客户端在单台服务器上可执行的请求，都可以发送到主节点执行（读、写、执行命令、创建索引）
>
>+ 客户端不能在备份节点上执行写操作
>+ 默认情况下，客户端不能从备份节点读取数据，除非在备份节点上显示地执行rs.secondaryOk()

### 3.3 主节点的选举机制
主节点的选举基本依据：
获得半数成员以上的投票的节点将被选举为主节点，也叫"大多数"原则，这原则可以避免出现多个主节点。如下图情况，假如不按照"大多数"原则，在左右两边将各自选出一个主节点，那么数据就会发生混乱。

![image-20210901101807156](MongoDB学习.assets/image-20210901101807156.png)

否决机制：

在主节点挂掉后，每个副本节点都可以申请成为主节点，而不能推荐其它节点。当某副本节点A申请作为主节点时，其它任一节点会对比A与自身的oplog的时间，若发现A的操作时间不是最新的，则否决本次选举；等到A同步完最新操作后，再重新发起选举，直到它的操作时间是所有节点最新的，则能获得其它节点的本次投票。



主节点的选举额外参考：

1. 若多个节点同时能当选主节点，则priority大的当选
2. 若priority也相同，则oplog最新的节点当选

每个节点都拥有2种属性：
- priority会影响该节点获得的票数
- votes将会影响该节点能投出的票数



### 3.4 仲裁节点

特点：不保存数据，不为客户端提供服务，占用较少的资源

作用：解决偶数节点副本集，无法选举出主节点的情况

添加方式：

```shell
> rs.addArb("<ip>:<port>")
```



注意事项：

+ ==最多使用一个仲裁节点==。仲裁节点使用的原因一定是保证节点的总数为奇数个，假如当前副本集节点已经是奇数个，则不需要添加仲裁节点。理由是，节点越多，选举的耗时越长。
+ ==仲裁者的缺点==：在小副本集上使用仲裁节点会导致一些操作性的任务变得困难，比如一主一从一仲裁的场景， 当一个数据成员挂掉后，那么就只剩一个主节点一个仲裁节点，若此时需要把数据备份到一个新的副本节点，那么只有主节点能用，而此时主节点不仅要处理客户端请求还有进行数据复制，那么压力就很大了。因此，小副本集场景如果可能尽量使用奇数节点而不要使用副本集。



### 3.5 优先级

优先级表示一个成员渴望作为主节点的程度，范围是0~100，默认是1。优先级为0的节点永远无法当选主节点，成为”被动成员“。若当前副本集中，其它成员优先级都为1，有一个成员A的优先级为2，那么一旦A的数据是最新的，则当前主节点会退位，A当选主节点。

因此，一般会把服务器性能较强的节点优先级适当调高，以提高当选主节点的概率。



### 3.6 隐藏成员

客户端不会向隐藏的成员发送请求，且隐藏的成员不会成为复制源（除非其它复制源不可用了），因此一般会将服务能力不够强大或者备份服务器隐藏起来。

隐藏节点可以通过` rs.status()`或`rs.config()`查看

```shell
shard1:PRIMARY> rs.config()
{
        "_id" : "shard1",
        "version" : 3,
        "protocolVersion" : NumberLong(1),
        "writeConcernMajorityJournalDefault" : true,
        "members" : [
                {
                        "_id" : 0,
                        "host" : "10.19.1.39:27018",
                        # 表示是否是仲裁节点
                        "arbiterOnly" : false,
                        # 表示是否创建索引
                        "buildIndexes" : true,
                        # 表示成员是否隐藏了
                        "hidden" : false,
                        "priority" : 1,
                        # 描述服务器的标识，用于自定义复制规则
                        "tags" : {

                        },
                        # 表示延迟备份的时间
                        "slaveDelay" : NumberLong(0),
                        "votes" : 1
                },
				...
}
```

 如果节点被隐藏了，`rs.isMaster()`是观察不到隐藏节点的。



### 3.7 延迟备份节点

延迟备份节点的数据会比主节点的数据延迟指定时间，这个是为了避免主节点的数据遭遇破坏，还能将数据从之前的备份节点恢复过来。由`rs.config()`中的`slaveDelay`字段决定，单位为秒。`slaveDelay`要求成员的优先级为0，并且应该设为隐藏节点，避免被应用路由到。



### 3.8 创建索引

备份节点有时并不需要与主节点一样拥有相同的索引，如果它的用途仅仅是做数据备份或者是离线的批量任务，那么甚至可以不需要索引。那么我们可以在`rs.config()`中指定`buildIndex`为`false`。

它要求成员的优先级为0，且这个是个永久的选项，如果需要恢复索引功能，需要把备份节点移除，删除所有数据后再添加回来。



### 3.9 回滚

当主节点A进行一个写操作后挂掉，而其它副本节点未能即使同步该opLog时，则新选举出来的主节点B将不会记录本次操作。当A恢复时，会将此操作回滚至与B某个opLog一致的节点后再开始进行同步。

![image-20210901152530593](MongoDB学习.assets/image-20210901152530593.png)

被回滚的操作和数据并不会丢失，而是会保存在特殊的回滚文件中，需要手动应用到当前的主节点。




### 3.10 getLastError命令

该命令用于检查上次操作的成功与否，形式如下：

```shell
# 场景为向my_db.students集合中插入_id相同的数据

# 方式一，表示大多数节点再500ms同步成功后，则返回成功，否则返回错误
> db.runCommand({"getLastError":"1", "w":"majority", "wtimeout":"500"})

{
        "err" : "E11000 duplicate key error collection: my_db.students index: _id_ dup key: { : 1.0 }",
        "code" : 11000,
        "codeName" : "DuplicateKey",
        "n" : 0,
        "singleShard" : "10.19.1.38:27019",
        "ok" : 1,
        "operationTime" : Timestamp(1630483411, 1),
        "$clusterTime" : {
                "clusterTime" : Timestamp(1630483417, 1),
                "signature" : {
                        "hash" : BinData(0,"IeQOjx1uT5EmRpzAxnepHONpEE0="),
                        "keyId" : NumberLong("6946966076357869598")
                }
        }
}

# 方式二
> db.getLastError("majoriy", 500)
E11000 duplicate key error collection: my_db.students index: _id_ dup key: { : 1.0 }

```



`w`参数的作用在1.3节已经有过介绍，其实它就是用于**控制集群的写入速度**。MongoDB的写入主节点的速度"过快"，导致备份节点跟不上。阻止这种行为，常用的方法就是：定期调用`getLastError` 方法，将w参数设置为大于1的值，这样就会阻塞这个连接上的写操作，直到指定个数的备份节点复制完成后，才返回成功。**注意，阻塞只会影响本连接，而不会影响其它连接，其它连接在默认情况下依旧是操作执行完后立即返回**。

**对于重要数据，强烈建议使用"majority"选项确认写入操作**，理由是当大多数备份节点在完成最新数据写入后，再返回成功，即使当前主节点挂后，也不需要回滚数据，因为大多数备份节点的数据已经是最新的了。



`wtimeout`参数设置操作超时的时长，这个参数同样重要。考虑在一个只有主节点和仲裁节点的副本集上，在调用getLastError方法，当`w`设置为大于1，而不设置`wtimeout`，那么应用将会一直等待下去，因为数据没有复制到足够数量的副本节点。

最后，`getLastError`方法因超时返回失败，并不意味着写入失败，很有可能是因为在规定时间内，没有把数据同步到指定数量的副本节点中。

### 3.11 自定义复制规则

在`rs.config()`中每个member存在一个`tags`字段，形式为`<tag>:<name>`可以用来标记节点：

```shell
shard1:PRIMARY> rs.config()
{
        "_id" : "shard1",
        "version" : 3,
        "protocolVersion" : NumberLong(1),
        "writeConcernMajorityJournalDefault" : true,
        "members" : [
                {
                        "_id" : 0,
                        "host" : "10.19.1.39:27018",
                        # 表示是否是仲裁节点
                        "arbiterOnly" : false,
                        # 表示是否创建索引
                        "buildIndexes" : true,
                        # 表示成员是否隐藏了
                        "hidden" : false,
                        "priority" : 1,
                        # 描述服务器的标识，用于自定义复制规则
                        "tags" : {

                        },
                        # 表示延迟备份的时间
                        "slaveDelay" : NumberLong(0),
                        "votes" : 1
                },
				...
		],
        "settings" : {
                "chainingAllowed" : true,
                "heartbeatIntervalMillis" : 2000,
                "heartbeatTimeoutSecs" : 10,
                "electionTimeoutMillis" : 10000,
                "catchUpTimeoutMillis" : -1,
                "catchUpTakeoverDelayMillis" : 30000,
                # 自定义规则
                "getLastErrorModes" : {
                },
                "getLastErrorDefaults" : {
                        "w" : 1,
                        "wtimeout" : 0
                },
                "replicaSetId" : ObjectId("60688e7fe57ef161078eaf50")
      }

}
```

假设现在有5个节点，最后一个节点为隐藏节点，现在我们需要执行写操作，当操作同步到可见节点超过3个时，则返回成功，需要执行一下几步：

+ 为可见节点添加标签

  ```
  > var config = rs.config()
  > config.members[0].tags = {"normal":"A"}
  > config.members[1].tags = {"normal":"B"}
  > config.members[2].tags = {"normal":"C"}
  > config.members[3].tags = {"normal":"D"}
  ```
  
+ 设置写入规则

  ```
  > config.settings.getLastErrorModes = {"visibleMajority": {"normal":3}}
  ```

+ 写入配置

  ```
  > rs.reconfig(config)
  ```

+ 应用规则

  ```
  > db.foo.insert({"x": 1})
  > db.runCommand({"getLastError":1, "w":"visibleMajority", "wtimeout":1000})
  ```

  

### 3.12 副本集的管理

#### 3.12.1 创建副本集

`rs.initiate(config)`

#### 3.12.2 修改副本集成员

`rs.add("<ip>:<port>")`用于添加新成员，

`rs.reconfig(config)`可以修改副本集成员的属性，但有如下限制：

+ 不能修改成员的"_id"字段
+ 不能将接受`rs.reconfig`命令的节点优先级置为0
+ 不能将仲裁者变为非仲裁者，反之亦然
+ 不能修改`buildIndexes`的状态

#### 3.12.4 把主节点变为备份节点

`rs.stepDown(60)`把主节点退化为备份节点60秒

#### 3.12.5 阻止选举

 `rs.freeze(100)`让对应节点保持备份状态100秒

`rs.freeze(0)`接触保持状态



### 故障模型

场景：1主、1从、1仲裁
|	 |主节点|从节点|仲裁节点|描述|
|----|----|----|----|----|
|状态1|不可用|可用|可用|从节点当选为主节点|
|状态2|可用|不可用|可用|主节点状态不变|
|状态3|可用|可用|不可用|主节点状态不变|
|状态4|不可用|不可用|可用|服务不可用，原因是没有存储数据的节点|
|状态5|可用|不可用|不可用|主节点服务降级，变为从节点，原因是票数少于半数|
|状态6|不可用|可用|不可用|从节点不会升级为主节点，原因是票数未多于半数|



### 常用操作

```shell
# 查看节点是否为主节点，以及其它节点信息
> db.isMaster()

# 查看副本集信息
> rs.config()

# 修改副本集配置
> rs.reconfig(<config>)

# 添加副本节点
> rs.add("<servername>:<port>")

# 删除副本节点
> rs.remove("<servername>:<port>")

# 查看上一次操作的错误
> db.getLastError(<w>, <wtimeout>)

# 查看当前服务的启动方式
> db.serverCmdLineOpts()

```





## 4. 分片集群（Sharded Cluster）

---
#### 4.1 分片集群的组成
一般分为3层：
- 第一层：路由节点Mongos，路由到具体分片节点

- 第二层：配置节点Mongod，一般是一个副本集，存储一些元数据

- 第三层：分片节点Mongod，一般是一个副本集，存储数据
  
  ![image-20210901110636323](MongoDB学习.assets/image-20210901110636323.png)

  

---
## 5. 配置文件

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

## 6. 鉴权

### 6.1 相关概念

MongoDB的鉴权系统有4个概念：

资源（Resource）：可以指一个数据库、集合、或者一个集群，即任何可以被操作的事物都可以被当作资源

动作（Action）：指对资源的一个执行行为，比如读写数据库

权限（Privilege）：指对某一类或某些资源执行某些动作的许可

角色（Role）：角色往往代表一组权限的集合

用户（User）：可登录的实体，一个用户可以被赋予多个角色


### 6.2 内置角色
**数据库访问**

| 角色名称  | 拥有权限                 |
| --------- | ------------------------ |
| read      | 允许读取指定数据库的角色 |
| readWrite | 允许读写指定数据库的角色 |

**数据库管理**

| 角色名称  | 拥有权限                                                     |
| --------- | ------------------------------------------------------------ |
| dbAdmin   | 允许用户在指定数据库中执行管理函数，如索引创建、删除，查看统计或访问system.profile |
| userAdmin | 允许管理当前数据库的用户，如创建用户、为用户授权             |
| dbOwner   | 数据库拥有者(最高)，集合了dbAdmin/userAdmin/readWrite角色权限 |

**集群管理**

| 角色名称       | 拥有权限                                                     |
| -------------- | ------------------------------------------------------------ |
| clusterAdmin   | 集群最高管理员，集合clusterManager/clusterMonitor/hostManager角色权限 |
| clusterManager | 集群管理角色，允许对分片和副本集集群执行管理操作，如addShard，resync等 |
| clusterMonitor | 集群监控角色，允许对分片和副本集集群进行监控，如查看serverStatus |
| hostManager    | 节点管理角色，允许监控和管理节点，比如killOp、shutdown操作   |

**备份恢复**

| 角色名称 | 拥有权限                           |
| -------- | ---------------------------------- |
| backup   | 备份权限，允许执行mongodump操作    |
| restore  | 恢复权限，允许执行mongoresotre操作 |

**数据库通用角色**

| 角色名称             | 拥有权限                 |
| -------------------- | ------------------------ |
| readAnyDatabase      | 允许读取所有数据库       |
| readWriteAnyDatabase | 允许读写所有数据库       |
| userAdminAnyDatabase | 允许管理所有数据库的用户 |
| dbAdminAnyDatabase   | 允许管理所有数据库       |

**特殊角色**

| 角色名称 | 拥有权限                     |
| -------- | ---------------------------- |
| root     | 超级管理员，拥有所有权限     |
| __system | 内部角色，用于集群间节点通讯 |

### 6.2 创建用户

```shell
# 在admin数据库下创建名为xiaohu的用户，并为其赋予root角色
$ db.createUser( {
	user: "xiaohu",
    pwd: "12345",
    roles: [ { role: "root", db: "admin" } ]
  });
```

### 6.3 登录数据库

Mongo的用户是归属在某个数据库下的，因此用户需要在所属数据库中进行鉴权

```shell
# 切换数据库
$ use admin
# 认证
$ db.auth("xiaohu", "12345")
```

Mongodb 的用户及角色数据一般位于当前实例的 admin数据库，system.users存放了所有数据；

**其中角色为root的admin数据库下的用户，拥有最高的权限，可以操作查看其它数据库中的数据；**

**存在例外的情况是分片集群，应用接入mongos节点，鉴权数据则存放于config节点。因此有时候为了方便分片集群管理，会单独为分片内部节点创建独立的管理操作用户；**

## 7. 索引



## 8. 了解应用动态

### 8.1 使用系统分析器








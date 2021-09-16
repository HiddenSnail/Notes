

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

## 2. DataModeling
数据建模的关键问题就是如何在*应用程序需求*、*数据库性能*和*数据检索模式*3者之间进行平衡。当我们为数据进行建模时，需要从程序是如何使用数据的以及数据本身固有的结构出发，进行设计。

### 2.1 Flexible Schema
与SQL不同，MongoDB在同一个Collection下Document的格式可以不相同，并且可以随意增删改Document的字段。
当然，你可以要求Collection下的Document都保持一致的结构，通过使用[document validation rules](https://docs.mongodb.com/manual/core/schema-validation/),这样在插入或更新Collection时就会进行检查。

### 2.2 Document Structure
支持Document的内嵌，也支持通过 _id关联多个document

### 2.3 Atomicity of Write Operations
在MongoDB中写操作在单个Document是原子性的，即使修改了一个Document下的多个嵌入式Document那么它也是原子性的。

当进行多Document写时，MongoDB只能保证单个Document的写流程时原子性的，而整体的最终结果是非原子性的，而且不能保证每个Document写的顺序。

MongoDB为了保证多Document的写原子性，4.0版本开始，设计了基于副本集的多Document操作。

大多数情况下，multi-document transcation 会导致与single-document相比更大的性能损耗，因此合理的使用嵌入式Document设计，尽量减少multi-document transactions操作，是一个好的选择。

### 2.4 Data Use and Performance
为数据建模的时候，要考虑应用程序会怎么使用数据，比如你的APP只是经常性地插入数据，那么请考虑使用[Capped Collection](https://docs.mongodb.com/manual/core/capped-collections/)

### 2.5 MongoDB的系统默认数据库和默认集合

[官网介绍](https://docs.mongodb.com/manual/reference/system-collections/)

+ **`admin`数据库**
系统默认的用户管理数据库，包含一下几张表
admin.system.roles:保存用户自定义的角色
admin.system.users:保存用户账户信息
admin.system.version:保存这数据库内部操作的一些元数据

+ **`local`数据库**
只保存在本地的数据库，不会被备份节点复制
oplog.rs: 保存oplog的集合

+ **`+config`数据库**
config.system.indexBuilds:保存着正在进行的索引建立相关信息

+ **`<database>.system`命名空间下的其它集合**
\<database\>.system.profile: 存储着数据库分析的相关信息
\<database\>.system.js: 存储着特殊的js代码
\<database\>.system.views: 存储着数据库集合的view信息


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

### 3.12 心跳
Mongo中每个成员都需要知道其它成员的状态: 哪个是主节点、哪个可以作为同步源、哪个挂掉了。每个成员每隔2s就会向其它成员发送**心跳请求**。它重要的功能就是让主节点知道自己是否还满足"大多数"成员的支持，如果不是则退位，变为备份节点。

### 3.13 成员状态
```shell
# 主节点状态，默认情况下读写请求都会优先发送到这里
> PRIMARY

# 备份节点状态
> SECONDARY

# 仲裁节点状态
> ARBITER

# 成员刚启动时处于这个状态，这个状态下，MongoDB会尝试加载成员副本集的配置，配置加载成功后就进入STARTUP2状态
> STARTUP

# 整个初始化同步过程都处于这个状态，但是假如时普通成员，这个状态只会持续几秒钟。在这个状态下，MongoDB会创建几个线程用于进行复制和选举
> STARTUP2

# 此状态表明成员运转正常，但暂时不能处理读请求，如果有成员处于这种状态，可能会造成系统轻微过载
# 当一个成员与其它成员数据差异过大时，也会进入这个状态，此时需要人为干预，尽快进行重同步
> RECOVERING

# 如果成员正在进行数据回滚，那么它就处于该状态。回滚完成后先进入RECOVERING, 然后进入SECONDARY
> ROLLBACK


# 系统出现问题时会出现以下状态

# 表示此成员无法将状态信息传递给副本集的其它成员，一般是由于网络故障导致的
> UNKNOWN 

# 失去与副本集连接的成员，会被其它成员视为DOWN状态
> DOWN

# 从副本集中删除的成员会进入 REMOVED 状态。 当成员进入 REMOVED 状态时，日志将使用 replSet REMOVED 消息条目标记此事件。
> REMOVED
```


### 3.14 副本集的管理

#### 3.14.1 创建副本集

`rs.initiate(config)`

#### 3.14.2 修改副本集成员

`rs.add("<ip>:<port>")`用于添加新成员，

`rs.reconfig(config)`可以修改副本集成员的属性，但有如下限制：

+ 不能修改成员的"_id"字段
+ 不能将接受`rs.reconfig`命令的节点优先级置为0
+ 不能将仲裁者变为非仲裁者，反之亦然
+ 不能修改`buildIndexes`的状态

#### 3.14.4 把主节点变为备份节点

`rs.stepDown(60)`把主节点退化为备份节点60秒

#### 3.14.5 阻止选举

`rs.freeze(100)`让对应节点保持备份状态100秒

`rs.freeze(0)`解除阻止选举状态

#### 3.14.6 获取状态

```shell
shard1:PRIMARY> rs.status()
{
        "set" : "shard1",
        "date" : ISODate("2021-09-02T03:19:05.061Z"),
        "myState" : 1,
        "term" : NumberLong(6),
        # 表示当前成员从哪个成员进行复制
        "syncingTo" : "",
        "syncSourceHost" : "",
        "syncSourceId" : -1,
        "heartbeatIntervalMillis" : NumberLong(2000),
        "optimes" : {
                "lastCommittedOpTime" : {
                        "ts" : Timestamp(1630552735, 1),
                        "t" : NumberLong(6)
                },
                "readConcernMajorityOpTime" : {
                        "ts" : Timestamp(1630552735, 1),
                        "t" : NumberLong(6)
                },
                "appliedOpTime" : {
                        "ts" : Timestamp(1630552735, 1),
                        "t" : NumberLong(6)
                },
                "durableOpTime" : {
                        "ts" : Timestamp(1630552735, 1),
                        "t" : NumberLong(6)
                }
        },
        "lastStableCheckpointTimestamp" : Timestamp(1630552725, 1),
        "members" : [
                {
                        "_id" : 0,
                        "name" : "10.19.1.39:27018",
                        # 是否可达，0不可达，1可达
                        "health" : 1,
                        "state" : 2,
                        "stateStr" : "SECONDARY",
                        "uptime" : 240261,
                        "optime" : {
                                "ts" : Timestamp(1630552735, 1),
                                "t" : NumberLong(6)
                        },
                        "optimeDurable" : {
                                "ts" : Timestamp(1630552735, 1),
                                "t" : NumberLong(6)
                        },
                        "optimeDate" : ISODate("2021-09-02T03:18:55Z"),
                        "optimeDurableDate" : ISODate("2021-09-02T03:18:55Z"),
                        # 当前成员最后一次收到其它成员心跳的时间
                        "lastHeartbeat" : ISODate("2021-09-02T03:19:04.882Z"),
                        "lastHeartbeatRecv" : ISODate("2021-09-02T03:19:03.573Z"),
                        # 当前服务器到达某个成员所花费的平均时间，可以根据这个字段选择从哪个成员进行同步
                        "pingMs" : NumberLong(0),
                        "lastHeartbeatMessage" : "",
                        # 表示当前成员从哪个成员进行复制
                        "syncingTo" : "10.19.1.38:27018",
                        "syncSourceHost" : "10.19.1.38:27018",
                        "syncSourceId" : 1,
                        "infoMessage" : "",
                        "configVersion" : 5
                },
                {
                        "_id" : 1,
                        "name" : "10.19.1.38:27018",
                        "health" : 1,
                        "state" : 1,
                        # 描述不同成员的状态
                        "stateStr" : "PRIMARY",
                        # 该成员可用一直到现在经历的时长，单位秒
                        "uptime" : 758544,
                        "optime" : {
                                "ts" : Timestamp(1630552735, 1),
                                "t" : NumberLong(6)
                        },
                        # 成员OpLog中最后一个操作发生的时间
                        "optimeDate" : ISODate("2021-09-02T03:18:55Z"),
                        "syncingTo" : "",
                        "syncSourceHost" : "",
                        "syncSourceId" : -1,
                        "infoMessage" : "",
                        "electionTime" : Timestamp(1630312275, 1),
                        "electionDate" : ISODate("2021-08-30T08:31:15Z"),
                        "configVersion" : 5,
                        # 只会出现在执行该命令的成员中
                        "self" : true,
                        "lastHeartbeatMessage" : ""
                },
                {
                        "_id" : 2,
                        "name" : "10.19.1.37:27018",
                        "health" : 1,
                        "state" : 7,
                        "stateStr" : "ARBITER",
                        "uptime" : 758537,
                        "lastHeartbeat" : ISODate("2021-09-02T03:19:03.839Z"),
                        "lastHeartbeatRecv" : ISODate("2021-09-02T03:19:05.058Z"),
                        "pingMs" : NumberLong(0),
                        "lastHeartbeatMessage" : "",
                        "syncingTo" : "",
                        "syncSourceHost" : "",
                        "syncSourceId" : -1,
                        "infoMessage" : "",
                        "configVersion" : 5
                }
        ],
        "ok" : 1,
        "operationTime" : Timestamp(1630552735, 1),
        "$gleStats" : {
                "lastOpTime" : Timestamp(0, 0),
                "electionId" : ObjectId("7fffffff0000000000000006")
        },
        "lastCommittedOpTime" : Timestamp(1630552735, 1),
        "$configServerState" : {
                "opTime" : {
                        "ts" : Timestamp(1630552735, 1),
                        "t" : NumberLong(5)
                }
        },
        "$clusterTime" : {
                "clusterTime" : Timestamp(1630552735, 1),
                "signature" : {
                        "hash" : BinData(0,"B1wnXxnMtUalE3CajZK3qNv3qBI="),
                        "keyId" : NumberLong("6946966076357869598")
                }
        }
}
```

#### 3.14.7 复制源
`rs.status()`中的`syncingTo`字段是可以说明对应节点的复制源是哪个，那么如何修改这个复制源呢？
使用`rs.syncFrom(<host>)`或者`db.adminCommand({"replSetSyncFrom":"<host>"})`，大概会花费上几秒中的时间切换到目标复制源。

在使用该条命令时，要警惕出现复制循环，即A从B同步数据，B从C同步数据，C从A同步数据，原因是**复制环中的的成员都不可能成为主节点**（why？），数据只能越来越落后。

####  3.14.8 禁用复制链
当一个成员节点以另一个成员节点作为复制源时，就会形成复制链，而复制链会导致数据同步的速度变慢。可以禁用复制链，即将`rs.config()`中的`setting.chainingAllowed`字段设置为`false`即可。
这样做的结果就是，所有成员都会从主节点上复制数据，如果主节点不可用，再从其它备份节点获取数据。

#### 3.14.9 延迟计算
`db.printReplicationInfo()`函数可以看到当前节点oplog当前的大小和覆盖的时间，以及其op的起止时间。

```shell
shard1:PRIMARY> db.printReplicationInfo()
configured oplog size:   100MB
log length start to end: 191897secs (53.3hrs)
oplog first event time:  Tue Aug 31 2021 10:10:29 GMT+0800 (CST)
oplog last event time:   Thu Sep 02 2021 15:28:46 GMT+0800 (CST)
now:                     Thu Sep 02 2021 15:28:49 GMT+0800 (CST)
```

`db.printSlaveReplicationInfo()`函数可以看到当前节点的复制源以及当前成员相对于复制源的落后程度信息
```shell
# 为什么主节点（10.19.1.38:27018）的复制源不是自己？？
shard1:PRIMARY> db.printSlaveReplicationInfo()
source: 10.19.1.39:27018
        syncedTo: Thu Sep 02 2021 15:48:26 GMT+0800 (CST)
        0 secs (0 hrs) behind the primary
```

#### 3.14.10 调整oplog的大小
主节点oplog的长度可以看作是维护工作的时间窗，默认情况下MongoDB会以磁盘容量的5%作为oplog的上限。要调整oplog的上线，可按照如下步骤：
1. 假如当前节点是主节点，则使其退位
2. 关闭当前服务器
3. 将当前服务器作为单机启动
4. 将最后一条写操作的记录从local.oplog.rs集合中取出，临时保存到一个变量
   ```shell
   use local
   # 筛选出插入操作
   var cursor = db.oplog.rs.find({"op":"i"}) 
   var lastWriteOp = cursor.sort({"$natural":-1}).limit(1).next()
   db.tempLastOp.save(lastInsert)
   # 确认保存成功，很重要
   db.tempLastOp.findOne()
   ```
5. 删除当前的oplog
   ```shell
   db.oplog.rs.drop()
   ```
6. 创建新的oplog
   ```shell
   db.createCollection("oplog.rs", {"capped":true, "size":10000})
   ```
7. 将最后一条记录写回oplog
   ```shell
   var temp = db.tempLastOp.findOne()
   db.oplog.rs.insert(temp)
   #  要确保成功插入, 如果有成功插入，那么把当前服务器添加为副本集之后，它会删除所有数据然后进行全量同步
   db.oplog.rs.findOne()
   ```
8. 最后将当前服务器作为副本集成员重新启动，因为这时只有一条oplog数据，因此我们在一段时间内无法得知实际oplog的长度

通常不应该减少oplog的大小，即使oplog可能会有几个月那么长，但是通常是有足够的硬盘空间来保存oplog的，而且oplog并不会占用珍贵的资源，如CPU、RAM等

####  3.14.11 数据恢复
+ 方法一：
  + 1. 关闭除延迟备份节点外的其它节点
  + 2. 删除其它成员数据目录中的所有数据（即启动时配置的data目录）
  + 3. 重启所有成员，它们会从备份节点中自动全量同步数据
  + 缺点: 延迟备份节点可能会负载压力大

+ 方法二：
  + 1. 关闭所有成员，包括延迟备份节点
  + 2. 删除其它成员数据目录中的所有数据
  + 3. 将延迟备份节点的数据文件复制到其它服务器上
  + 4. 重启所有成员
  + 缺点：这样会导致所有服务器都与延迟备份节点拥有同样大小的oplog

#### 3.14.12 创建索引
如果在主节点中发送创建索引的命令，主节点会正常的创建索引，然后备份节点在复制"创建索引"操作时，同样也会创建索引。创建索引是一个需要消耗大量资源从操作，如果所有节点都在同一时段内开始创建索引，那么久几乎所有成员都会不可用，知道索引创建完成。

解决的方式是，一次只在一个成员上创建索引：
1. 关闭一个备份系欸但服务器，并以单机模式启动它
2. 在单机模式下创建索引
3. 索引创建完成后，将服务器作为副本集成员重新启动
4. 对其余节点重复1~3步骤

对于主节点上的索引创建，有一下两种方式：
+ 方式一：假如系统有空闲期，可以使用空闲期在主节点创建索引，与此同时修改读取首选项，在主节点创建索引的期间将读请求转发（如何转发呢）到备份节点上。在主节点创建索引时，备份节点仍会复制这个操作，但是因为之前已经创建了同样的索引，实际上不会再次创建

+ 方式二：让主节点退化成为备份节点，然后对这个服务器重复上面1~3步，然后创建完成后再添加会副本集。

这种创建索引的技术，可以让不同的节点拥有不同的索引，但是如果某备份节点的索引与其它成员不同，那么应该将它的优先级置为0，使其永远不会成为主节点。

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

# 查看上一次操作的结果
> db.getLastError(<w>, <wtimeout>)

# 查看当前服务的启动方式
> db.serverCmdLineOpts()

```





## 4. 分片集群（Sharded Cluster）

### 4.1 分片集群的架构
一般分为3层：
- 第一层：路由节点Mongos，路由到具体分片节点

- 第二层：配置节点Mongod，一般是一个副本集，存储一些元数据

- 第三层：分片节点Mongod，一般是一个副本集，存储数据
  
  ![image-20210901110636323](MongoDB学习.assets/image-20210901110636323.png)


### 4.2 启动分片
```shell
# userdb数据库启动分片
sh.enableSharding("userdb")

# 在数据库集合users上创建索引，该索引用于做为分片的片键
db.users.ensureIndex({"username": 1})

# 创建users的集合分片
sh.shardCollection("userdb.users", {"username":1})
```

### 4.3 分片的数据查询
```shell
# explain命令, 用于查看查询命令的细节
db.users.find({"username":"123456"}).explain()
```

当使用片键进行查询时，mongos可以指定到某一分片进行查找，称为**定向查询**。如果在查询中没有使用片键，那么这些查询必须发送给所有分片，称为**分散-聚集查询**。

### 4.4 分片集群的元素
#### 4.4.1 配置服务器
配置服务器保存着分片集群的元数据，每个数据存储在哪个分片上全靠它来找了。在3.2版本前，配置服务器只能独立镜像部署（SCCC），3.2-3.4版本支持独立镜像部署(SCCC)和副本集方式部署(CSRS), 3.4版本后只支持副本集方式部署(CSRS)。

部署为CSRS模式约束条件：
+ 必须使用WiredTiger存储引擎
+ 不能有仲裁者
+ 不能存在延迟备份节点
+ 所有成员不能禁用索引

#### 4.4.2 路由服务器
路由节点Mongos不存储数据，因此可以不设置数据路径，但是要设置日志路径


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
$ db.createUser({
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

```shell
mongostat -h 127.0.0.1:27018 -u root -p caih123 --authenticationDatabase admin
```


## 9. MongoDB URI
用于客户端连接MongoDB，它遵守URI的基本格式
```md
                    hierarchical part
        ┌───────────────────┴─────────────────────┐
                    authority               path
        ┌───────────────┴───────────────┐┌───┴────┐
  abc://username:password@example.com:123/path/data?key=value&key2=value2#fragid1
  └┬┘   └───────┬───────┘ └────┬────┘ └┬┘           └─────────┬─────────┘ └──┬──┘
scheme  user information     host     port                  query         fragment

  urn:example:mammal:monotreme:echidna
  └┬┘ └──────────────┬───────────────┘
scheme              path
```

```shell
# 连接副本集样例，authSource表示用于在哪个数据库上做鉴权
mongodb://root:123456@10.19.1.20:27018,10.19.1.21:27018,10.19.1.22:27018/newdb?authSource=admin&replicaSet=replset

```

## 10. MongoDB GridFS

### 10.1 基本概念
MongoDB GridFS 是一种用于存储和检索超过16 MB的 BSON 文档大小限制的文件的规范。让可以把文件分成很多chunk，然后存储起来。它在指定存放文件的数据库中默认生成fs.files和fs.chunk两个collection。fs.files保存的是文件的元数据，fs.chunks保存的是被拆分后文件的数据块。

一个fs.files的一项数据，对应fs.chunks里的多项数据，对应方式如下图：
![files元素](MongoDB学习.assets/files元素.png)
![chunks元素](MongoDB学习.assets/chunks元素.png)


### 10.2 mongofiles
mongofiles是MongoDB提供的使用GridFS的命令行工具，使用示例如下：
```shell
# 将本地文件me.txt以名为gridfs.txt保存到数据库hello中，
[me@Computer ~]$ mongofiles --uri "mongodb://root:123456@10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018/hello?authSource=admin&replicaSet=shard1" -d hello -l ~/me.txt put gridfs.txt 
2021-09-10T09:05:34.869+0800	connected to: localhost
2021-09-10T09:05:34.869+0800	added file: gridfs.txt
```

**命令使用方式：**
```shell
# 格式
mongofiles <options> <command> <filename or _id or string>

# command项
list: 列出指定前缀的文件
search: 列出包含指定字符串的文件
put: 上传文件时指定文件名
put_id: 上传文件时指定文件名和_id
get: 获取指定文件名的文件
get_id: 获取指定_id的文件
delete：删除指定文件名的文件
delete_id: 删除指定_id的文件

# options 项
-v, --verbose=<等级>: 显示详细log信息
    --quiet：隐藏所有log信息

-h, --host=<主机名 or 主机名:端口>：针对副本集格式为(setname/host1, host2)
    --port=<端口>

-u, --username=<用户名>：数据库用户名
-p, --password=<密码>：数据密码
    --authenticationDatabase=<数据库名>：认证用户名/密码的数据库

    --uri=<mongodburi>：使用uri连接mongodb，记得使用双引号把uri括起来

-d, --db=<数据库名>：指定存储文件的数据
-l, --local=<文件路径>：需要上传的文件路径
-t, --type=<文件格式后缀>: 上传的文件格式
-r, --replace：使用put命令时，删除同名文件，再进行上传
    --prefix=<collection前缀>: 默认是fs
    --writeConcern=<write-concern>: 例如 --writeConcern='{w:3, wtimeout: 500, fsync: true, journal: true}'
```


**使用示例**
```shell
# 使用短参数连接副本集，put命令上传文件
[me@Computer ~]$ mongofiles -h "shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018" -u "root" -p "123456" --authenticationDatabase "admin" -d "fileDB" -l ~/me.txt put myfile.txt
2021-09-10T10:22:56.075+0800	connected to: shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018
2021-09-10T10:22:56.076+0800	added file: myfile.txt

# 使用uri连接副本集，put_id命令上传指定_id的文件
[me@Computer ~]$ mongofiles --uri "mongodb://root:123456@10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018/?authSource=admin&replicaSet=shard1" -d "fileDB" -l ~/me.txt put_id hello.txt "ObjectId('666666666666666666666666')"
2021-09-10T10:35:01.459+0800	connected to: localhost
2021-09-10T10:35:01.460+0800	added file: hello.txt

# list命令
[me@Computer ~]$ mongofiles -h "shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018" -u "root" -p "123456" --authenticationDatabase "admin" -d "fileDB" list myfile
2021-09-10T10:25:15.283+0800	connected to: shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018
myfile.txt	13
myfile.txt	13
myfile2.md	13

# search命令
[me@Computer ~]$ mongofiles -h "shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018" -u "root" -p "123456" --authenticationDatabase "admin" -d "fileDB" search "txt"
2021-09-10T10:27:35.576+0800	connected to: shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018
myfile.txt	13
myfile.txt	13

# get_id命令
[me@Computer ~]$ mongofiles -h "shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018" -u "root" -p "123456" --authenticationDatabase "admin" -d "fileDB" get_id "ObjectId('666666666666666666666666')"
2021-09-10T10:40:51.179+0800	connected to: shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018
2021-09-10T10:40:51.203+0800	finished writing to: hello.txt

# delete_id命令
[me@Computer ~]$ mongofiles -h "shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018" -u "root" -p "123456" --authenticationDatabase "admin" -d "fileDB" delete_id "ObjectId('666666666666666666666666')"
2021-09-10T10:47:56.449+0800	connected to: shard1/10.19.1.37:27018,10.19.1.38:27018,10.19.1.39:27018
2021-09-10T10:47:56.483+0800	successfully deleted file with _id ObjectId('666666666666666666666666') from GridFS
```


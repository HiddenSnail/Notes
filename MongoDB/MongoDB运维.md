
## 一、生产说明

### 并发性
WiredTiger 支持同时读写同一个collection的同一个document，并且支持多个线程修改同一个collection的不同document

### 数据持久性

#### *ReadConcern*
3.6+版本，readConcern默认为majority，3.6.1-3.6.x 可以通过设置`--enableMajorityReadConcern=false`来禁用它，**在部署PSA架构时需要这样操作**

为了使用readConcern=majority, 副本集必须使用WiredTiger引擎，选举协议使用protocol version 1

### 网络

#### *禁用HTTP接口*
MongoDB 3.6删除了连接到MongoDB的HTTP API 和 REST API

#### *管理连接池大小*
为了避免mongos/mongod的连接实例过载，请调整连接池大小，一般调整为实际连接数的110%-115%
查看当前副本集连接数
`db.runCommand( { "connPoolStats" : 1 } )`

### 硬件注意事项

MongoDB 服务端运行小端机器上，客户端可以运行在大端或者小端机器上

WiredTiger是多线程的，可以充分利用额外的CPU核心：
+ 其吞吐量会随着并发操作数的增长而增加，直到并发操作数达到CPU数目。
+ 其吞吐量会随着并发操作超出CPU数目的某个阈值后而降低

吞吐量可通过`mongostat` 的 `reads/writes (ar|aw)`列查看

### 时钟同步
MongoDB 自身会维护逻辑时钟，来支持依赖时间顺序的操作。推荐使用NTP进行时钟同步，可以少时钟不一致带来的风险。

+ 系统时钟给两个MongoDB成员授时的时差超过1年时，成员间的通信会变得不可靠或完全停止，`maxAcceptableLogicalClockDriftSecs `参数可以控制可接受的时钟偏差
+ 从两个集群成员需要返回当前系统时间或集群时间时，会导致获取结果不一致
+ 如果集群中MongoDB成员发生了时钟偏移，那么某些依赖计时的特性则会变得不可靠或行为无法预期

在使用版本号小于或等于3.4.6或3.2.17的MongoDB的WiredTiger引擎时，必须使用NTP同步，否则会出现checkpoint挂死的问题。

### 特定平台注意事项
#### *Linux平台*
##### _内核与文件系统_
如果使用WiredTiger引擎，强烈推荐使用XFS文件系统，它可以避免WigedTiger在EXT4上可能会出现的性能问题：
> + 如果使用XFS文件系统，请确保Linux内核版本至少为2.6.25
> + 如果使用EXT4文件系统，请确保Linux内核版本至少为2.6.28
> + 如果运行在Red Hat Enterprise Linux 和 CentOS, 请确保Linux内核至少为2.6.18-194版本

##### _glibc_
MongoDB使用了Linux的glibc, 虽然每个Linux发行版都会配套对应的glibc版本，但是还是建议及时更新到当前发行版支持的最新glibc版本
```bash
# RHEL/CentOS
sudo yum install glibc

# Ubuntu/Debian
sudo apt-get install libc6
```

##### _支持目录级的fsync()系统调用_
MongoDB需要支持目录级fsync的文件系统，若使用HGFS和Virtual Box的共享文件夹，则无法满足该要求

##### _设置 `vm.swappiness` 为 `0` 或 `1`_
`swappiness` 是一个可以影响Linux虚拟内存管理的一个配置，它可配置范围为0-100，这个值越高表示系统越倾向于将数据从内存页面交换到磁盘而不是从内存中删除。
> + 0: 表示完全禁用内存交换，
> + 1：表示仅当内存不足时，允许内核进行交换
> + 60：表示内核应该频繁地进行内存交换，这个是众多Linux发行版的默认配置
> + 100：表示内核应该优先进行内存交换

MongoDB在内存交换被完全禁用或值较低时，能有更好的性能表现。因此，应该将`vm.swappiness`设置为`0`或`1`。如果运行MongoDB的服务器上还运行着其它服务，则应该配置为`1`，当然最好是在一台服务器上单独运行MongoDB。
配置方式如下：
```bash
sudo vim /etc/sysctl.conf # 添加vm.swappiness = 1
sudo sysctl -p
cat /proc/sys/vm/swappiness
```

##### _推荐配置_
+ 对于使用任何存储引擎的MongoDB
  + 在集群模式下，必须使用NTP同步时间
+ 对于仅使用WiredTiger存储引擎的MongoDB
  + 禁用存储数据的磁盘的`atime`机制，可以提高读性能。原因是每次读取系统都会取刷新atime。
    ```bash
    # 配置fstab文件
    vim /etc/fstab
    # default后需要添加一个noatime属性
    # /dev/mapper/datavg01-app    /app    ext4    defaults,noatime	 0 2

    # 重新mount
    mount -o remount /app
    ```
  
  + 配置ulimit文件, Linux系统默认会对应用程序进行资源限制，需要针对MongoDB配置限制值。需要注意的是针对以下配置文件，必须使用名为`mongodb`的用户启动MongoDB进程才能生效。
    ```bash
    # 针对CentOS的配置
    [root@linux /]# cat /etc/security/limits.d/99-mongodb-nproc.conf 
    mongodb soft fsize unlimited 
    mongodb soft cpu unlimited 
    mongodb soft as unlimited
    mongodb soft memlock unlimited 
    mongodb soft nofile 64000 
    mongodb soft nproc 64000 
    mongodb hard fsize unlimited 
    mongodb hard cpu unlimited 
    mongodb hard as unlimited 
    mongodb hard memlock unlimited
    mongodb hard nofile 64000 
    mongodb hard nproc 64000
    ```
  + 禁用Transparent Huge Pages
    由于数据库是稀疏的内存访问方式，因此启用THP特性不利于数据库的工作。
    禁用方式见部署规范。

  + 禁用NUMA
    MongoDB运行在Non-Uniform Memory Access (NUMA)结构的系统上时，可能会导致许多操作性问题，如：一段时间内性能下降和系统进程使用率增高。
     
    > 具体说明：
    > Linux系统的内存访问结构会分为UMA(一致性内存访问结构)和NUMA(非一致性内存访问结构)。
    >
    > UMA结构是指在多CPU场景，所有CPU都可以通过同一总线访问到同一片内存区域。该结构的三个要素CPU-总线-内存，任何一个受限，都会影响整体的访问速度。由于所有CPU都通过相同的内存总线访问相同的内存资源，当CPU超过一定数量时，会大大增加内存访问冲突的概率。经验值是，在一台UMA架构的机器，CPU数量最多一般为4个。
    >
    >为了解决UMA的问题NUMA应运而生。NUMA的是将多个CPU作为一个Node，将一定量的内存分配给该Node，也称为该Node的本地内存，而其余的内存相对于该Node称为远端内存。多个Node互联模块相互连接，保证每个Node的可以访问所有内存地址。该设计优势很明显，避免了CPU过多导致内存访问冲突的出现，缺点是访问不同Node的内存时，速度会有明显下降。如果将某程序固定运行在一个Node里，则访问的都是本地内存，那么可以避免NUMA的缺点。
    >
    > NUMA的内存分配策略有:localalloc(默认)、preferred、membind、interleave。localalloc规定进程从当前node上请求分配内存；preferred比较宽松地指定了一个推荐的node来获取内存，如果被推荐的node上没有足够内存，进程可以尝试别的node。membind可以指定若干个node，进程只能从这些指定的node上请求分配内存。interleave规定进程从指定的若干个node上以RR算法交织地请求分配内存。
    >
    > MongoDB服务是内存独占型服务，基本需要占用服务器的所有内存。如果在NUMA架构机器上运行，在localalloc场景下，当某个Node内存耗尽时，Linux又将该Node的分配给其它需要使用内存的线程或者进程，那么该就会产生Swap，而尽管其它Node还有未使用的内存。因此需要解决的问题就是，如何在NUMA架构下，让MongoDB分到所有地址范围的内存。

    禁用NUMA需要完成以下2步：
    ```bash
    # step1: 修改vm.zone_reclaim_mode为0
    # 0：关闭zone_reclaim_mode，表示可以从其它NUMA节点回收内存
    # 1: 表示打开zone_reclaim模式，这样内存回收只会发生在本地节点内存
    # 2: 在本地回收内存时，可以将cache中的脏数据写回硬盘，以回收内存
    # 3: 可以用swap方式回收内存
    echo 0 | sudo tee /proc/sys/vm/zone_reclaim_mode

    # step2: 使用numactrl的interleave=all模式启动mongod进程
    /usr/bin/numactl --interleave=all /usr/bin/mongod --config /etc/mongod.conf
    ```


  + 如果使用的系统是SELinux，则需要进一步配置：比如禁用Java脚本执行器

### 实用工具

#### *iostat*
用于查看磁盘的读写状态
(https://www.cnblogs.com/ftl1012/p/iostat.html)
(https://zhuanlan.zhihu.com/p/370442698)
```bash
iostat -d <磁盘> -cmx 5 1
iostat 5 1
iostat -dmx 1 1
```

#### *mongostat*
用于查看mongo的读写状态
```bash
/usr/local/mongodb/bin/mongostat --authenticationDatabase admin --port=20000 -uroot -proot -i --discover
```

#### *mongotop*
```bash
mongotop -h localhost:27018 -uroot -pcaih123 --authenticationDatabase admin 20 -vvvv
```

#### *mongoperf*

#### *perf*
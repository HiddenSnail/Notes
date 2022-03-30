# MongoDB常用命令



## 1. 信息查看

```shell
# 查看当前DB
db

# 查看当前数据库状态
db.stats()

# 列出所有数据库
show dbs

# 列出当前数据库所有collections
show collections

# 列出当前数据库所有用户信息
show users

# 列出当前数据库所有角色
show roles

# 列出最近5次操作
show profile

# 列出当前正在执行的操作
db.currentOp()
db.currenOp().inprog.length

# 查看所有配置参数
db.adminCommand({ getParameter : "*" })

# 可以获取统计信息
db.serverStatus().metrics.commands
```

## 2. 数据统计
```shell
# 查看collection的document数
# 快，只能得到近似统计
$ db.<coll>.count()
# 慢，可以得到精确统计
$ db.<coll>.countDocuments()
```

## 3. 删除操作
```shell
# 删除数据库, w默认是majority, 如果写入的数字比majority要小，则使用majority
# 不然才使用指定的数量。在1主1副1仲裁配置下，kill掉一个存储节点是无法drop数据库的
# 此命令不会删除与数据库关联的用户
$ db.dropDatabase({ w: <value>, j: <boolean>, wtimeout: <number> })

```

## 4. 用户维护
```shell
# 查看mongo服务的内存占用情况
top -p $(pidof mongod)

# 以单机模式启动副本集节点
mongod --bind_ip 127.0.0.1 --port 33333 --dbpath /app/mongodb/data/shard_27018 --fork 

# 新建用户, 该用户在mydb下认证，且在admin库下有clusterAdmin的角色，其它所有库有readWrite角色
# https://www.mongodb.com/docs/manual/reference/built-in-roles/#cluster-administration-roles
# https://blog.csdn.net/ls_call520/article/details/103915836
use mydb
db.createUser({
	"user": "loop",
	"pwd": "loop",
	"roles": [{role: "clusterAdmin", db: "admin"}, "readWrite"]}, 
    {w:"majority", wtimeout: 5000})

# 查看用户
use admin
db.system.users.find()

# 删除单个用户
use admin
db.dropUser("username")

# 删除所有用户
db.system.users.remove({})
```

## 5. 副本集
```shell
# 查看复制源
db.adminCommand({"replSetGetStatus":1})['syncingTo']

# 查看当前节点落后主节点的时间
rs.printSlaveReplicationInfo()

# 获取Oplog的配置大小
rs.printReplicationInfo()

# 获取oplog的开始时间和结束时间 tFirst开始，tLast结束
db.getReplicationInfo()

# 配置oplog大小
db.adminCommand({replSetResizeOplog:1, size:51200})

# 禁用复制链
cfg=rs.config()
cfg.settings.chainingAllowed=false
rs.reconfig(cfg)

# 副本集新增节点
# 添加时需要隐藏节点，待其同步完成后再取消隐藏
rs.add({host: "10.19.1.84:27022", hidden: true, priority: 0, votes: 0})
# 同步完成后再执行
conf=rs.conf()
conf.memers[3].hidden=false
conf.memers[3].priority=1
conf.memers[3].votes=1
rs.reconfig(conf)

```

## 6. 日志
```bash
# 日志文件过大，使用新日志进行记录
db.adminCommand({logRotate: 1})

# 查看启动配置
cat <日志文件> | grep "wiredtiger_open config"

# 获取1000ms以上的慢查询 
sudo tail data_27019.log -n 1000000 | grep ms | grep op_msg | grep find | grep -v "oplog.rs" | grep -v "getMore" | egrep "[3-9][0-9]{2,}ms" > /tmp/slow_op.log

# 统计一段时间内的慢查询次数
cat /app/mongodb/logs/archive/2022-03/shard_27018/shard_27018.log.2022-03-01T16-00-01 | grep "command: insert" | grep "2022-03-01T20:" | wc -l
```

## 7. 索引
```bash
# 后台模式建立索引，1表示升序，-1表示降序
db.CTL_MT_AXB_BIND_INFO.createIndex({"accessKey":1,"telX":1}, {background: true})
```

## 8. 数据导出/导入
```bash
# 数据导出
nohup mongodump -h 'repset1/192.168.20.1:27017,192.168.20.2:27017,192.168.20.3:27017' -u 'root' -p 'root' --authenticationDatabase 'admin' -d bbw -o /app/backup/ &

# 数据导入
nohup mongorestore -h 'repset1/192.168.20.1:27017,192.168.20.2:27017,192.168.20.3:27017' -u 'root' -p 'root' --authenticationDatabase 'admin' -d bbw --dir /app/backup/bbw &
```
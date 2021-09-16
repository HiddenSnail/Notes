# MongoDB常用命令



## 1. 信息查看

```shell
# 查看当前DB
$ db

# 查看当前数据库状态
$ db.stats()

# 列出所有数据库
$ show dbs

# 列出当前数据库所有collections
$ show collections

# 列出当前数据库所有用户信息
$ show users

# 列出当前数据库所有角色
$ show roles

# 列出最近5次操作
$ show profile

```

### 2. 数据统计
```shell
# 查看collection的document数
$ db.<coll>.count()


```

### 3. 删除操作
```shell
# 删除数据库, w默认是majority, 如果写入的数字比majority要小，则使用majority
# 不然才使用指定的数量。在1主1副1仲裁配置下，kill掉一个存储节点是无法drop数据库的
# 此命令不会删除与数据库关联的用户
$ db.dropDatabase({ w: <value>, j: <boolean>, wtimeout: <number> })

```
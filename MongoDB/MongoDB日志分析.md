## 日志结构

```bash
{
    "timestamp": "Thu Apr  2 07:51:50.985"  // 日期和时间, ISO8601格式
    "severityLevel": "I"  // 日志级别 I代表info的意思，其他的还有F,E,W,D等
    "components": "COMMAND"  //组件类别，不同组件打印出的日志带不同的标签，便于日志分类
    "namespace": "animal.MongoUser_58"  //查询的命名空间，即<databse.collection>
    "operation": "find" //操作类别，可能是[find,insert,update,remove,getmore,command]
    "command": { find: "MongoUser_58", filter: {fc: { $lt: 120 }}, limit: 30 } //具体的操作命令细节
    "planSummary": "IXSCAN { lv: -1 }", // 命令执行计划的简要说明，当前使用了 lv 这个字段的索引。如果是全表扫描，则是COLLSCAN
    "keysExamined": 20856, // 该项表明为了找出最终结果MongoDB搜索了索引中的多少个key
    "docsExamined": 20856, // 该项表明为了找出最终结果MongoDB搜索了多少个文档
    "cursorExhausted": 1, // 该项表明本次查询中游标耗尽的次数
    "keyUpdates":0,  // 该项表名有多少个index key在该操作中被更改，更改索引键也会有少量的性能消耗，因为数据库不单单要删除旧Key，还要插入新的Key到B-Tree索引中
    "writeConflicts":0, // 写冲突发生的数量，例如update一个正在被别的update操作的文档
    "numYields":6801, // 为了让别的操作完成而屈服的次数，一般发生在需要访问的数据尚未被完全读取到内存中，MongoDB会优先完成在内存中的操作
    "nreturned":0, // 该操作最终返回文档的数量
    "reslen":110, // 结果返回的大小，单位为bytes，该值如果过大，则需考虑limit()等方式减少输出结果
    "locks": { // 在操作中产生的锁，锁的种类有多种，如下
        Global: { acquireCount: { r: 13604 } },   //具体每一种锁请求锁的次数
        Database: { acquireCount: { r: 6802 } }, 
        Collection: { acquireCount: { r: 6802 } } 
    },
    "protocol": "op_command", //  消息的协议
    "millis" : 69132, // 从 MongoDB 操作开始到结束耗费的时间，单位为ms
}
```
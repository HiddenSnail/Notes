
# MongoDB 配置选项

```bash

# 全量checkpoint时间间隔(会移除无用的journal)
# 默认值：1min
storage.syncPeriodSecs 

# journal刷盘时间间隔(保存journal本身到磁盘上)
默认值：100ms
storage.journal.commitInternalMs


```
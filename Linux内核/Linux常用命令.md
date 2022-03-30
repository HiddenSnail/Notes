
## 进程相关

```
# 


```

## 磁盘相关
```bash
# 查看磁盘是不是ssd
# 1表示机械盘，0表示ssd
grep ^ /sys/block/*/queue/rotational

# 查看硬盘设备挂载状态以及格式
lsblk -f

# 格式化磁盘
mkfs.ext4 /dev/data01/app

```

## 防火墙相关

1.firewalld的基本使用
```bash
启动：  systemctl start firewalld
查看状态：systemctl status firewalld 
停止：  systemctl disable firewalld
禁用：  systemctl stop firewalld
在开机时启用一个服务：systemctl enable firewalld.service
在开机时禁用一个服务：systemctl disable firewalld.service
查看服务是否开机启动：systemctl is-enabled firewalld.service
查看已启动的服务列表：systemctl list-unit-files|grep enabled
查看启动失败的服务列表：systemctl --failed
```

2.配置firewalld-cmd
```bash
查看版本： firewall-cmd --version
查看帮助： firewall-cmd --help
显示状态： firewall-cmd --state
查看防火墙规则： firewall-cmd --list-all 
查看所有打开的端口： firewall-cmd --zone=public --list-ports
更新防火墙规则： firewall-cmd --reload
查看区域信息:  firewall-cmd --get-active-zones
查看指定接口所属区域： firewall-cmd --get-zone-of-interface=eth0
拒绝所有包：firewall-cmd --panic-on
取消拒绝状态： firewall-cmd --panic-off
查看是否拒绝： firewall-cmd --query-panic
```

3.通过firewall-cmd 开放端口
```bash
firewall-cmd --permanent --zone=public --add-port=16379/tcp
firewall-cmd --permanent --zone=public --add-port=16379/tcp --add-source=ip,ip

#作用域是public，开放tcp协议的80端口，一直有效
firewall-cmd --zone=public --add-port=80/tcp --permanent
#作用域是public，批量开放tcp协议的80-90端口，一直有效
firewall-cmd --zone=public --add-port=80-90/tcp --permanent
#作用域是public，批量开放tcp协议的80、90端口，一直有效
firewall-cmd --zone=public --add-port=80/tcp  --add-port=90/tcp --permanent
#开放的服务是http协议，一直有效
firewall-cmd --zone=public --add-service=http --permanent
# 重新载入，更新防火墙规则，这样才生效。通过systemctl restart firewall 也可以达到
firewall-cmd --reload
#查看tcp协议的80端口是否生效
firewall-cmd --zone= public --query-port=80/tcp
# 删除
firewall-cmd --zone= public --remove-port=80/tcp --permanent

firewall-cmd --list-services
firewall-cmd --get-services
firewall-cmd --add-service=<service>
firewall-cmd --delete-service=<service>
```
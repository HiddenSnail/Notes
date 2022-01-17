 # DEB制作及安装

.deb文件格式为Debian系统下的专用安装包，下面介绍它的简单制作过程



## 一、制作工具dpkg介绍

dpkg为Debian系统下的包管理工具，当然也可以制作.deb安装包



## 二、制作步骤

比如当前有一份编译好的`arm`版本的`nginx`程序需要打包成deb，结构如下

```bash
[root@armcompilevm nginx]# ls
conf  html  lib  logs  sbin
```

简单制作流程如下

```bash
# nginx-deb为虚拟根目录，可以视为打包过程中的/目录，命名随意
# nginx-deb/DEBIAN保存打包所需的配置文件目录，命名固定
# nginx-deb/opt为nginx软件包安装时的目录，安装后，nginx整个文件夹会被安装到/opt目录下
mkdir -p nginx-deb/{DEBIAN,opt}

# control文件为打包的配置文件
vim nginx-deb/DEBIAN/control
Source: nginx
Section: utils
Priority: optional
Maintainer: root
Standards-Version: 4.6.0
Rules-Requires-Root: no
Package: nginx # 包名
Version: 1.12.2 # 版本
Architecture: arm64 # 架构
Description: nginx 1.12.2

# 打包, 会在当前目录生成nginx-1.12.2-arm64.deb
dpkg -i ./nginx-deb nginx-1.12.2-arm64.deb
```



## 三、安装及卸载

```bash
# 安装
dpkg -i nginx-1.12.2-arm64.deb

# 查看是否安装nginx
dpkg -l | grep nginx
ii  nginx                      1.12.2                       arm64        nginx 1.12.2

# 卸载
dpkg -r nginx
```


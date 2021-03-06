# RPM的制作及安装

本文通过介绍如何通过RPM的方式打包自己开发的脚本，来介绍RPM的制作与安装。
下文中的`get_id.sh`、`cmp.sh`为自定义脚本。

## 一、rpmbuild介绍

rpmbuild顾名思义是用来制作rpm包的工具软件，机器没有自带的情况下需要手动安装

```shell
yum install rpmbuild
```

安装完毕后需要建立工作区目录
```shell
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
# BUILD:构建目录,构建包时需要获取的文件都可放这里
# BUILDROOT:虚拟根目录，可以理解为构建时的根目录
# RPMS:生成的rpm包
# SOURCES:源码软件包,存放的都是tar.gz压缩包,构建开始后会解压拷贝到BUILD目录
# SPECS:构建流程的配置文件
# SRPMS:软件最终的rpm源码格式存放路径
```

## 二、配置文件编写

执行构建过程，需要编写配置文件，配置文件一般放置在SPECS文件夹下，下面是一份简单的将脚本打包成rpm的示例：

```shell
Name: mongoid_check # 包名 
Version: 1.0.0 # 版本
Release: 1%{?dist}
Summary:mongoid check rpm package # 概述

Group:  Applications/Archiving
License:GPLv2

%define _unpackaged_files_terminate_build 0 #变量定义，有些是内置变量，比如_unpackaged_files_terminate_build，当然也可以自定义变量
%define	_prefix /opt/mongoid_check

#BuildRequires:  # 这个不是注释，下面是构建的前置依赖

%description # 【详细描述】
this is for install mongoid check

%prep # 【构建前置处理】一般是处理源码配置文件等
echo "pre install nothing..."

%build # 【构建部分】一般就是进行源码的编译等
echo "build nothing..."

%install # 【安装部分】构建完毕后会生成可执行文件等，需要把可执行文件拷贝到虚拟根目录下
mkdir -p %{buildroot}%{_prefix}
install -m 755 get_id.sh %{buildroot}%{_prefix}/get_id.sh
install -m 755 cmp.sh %{buildroot}%{_prefix}/cmp.sh

%files # 【打包部分】需要把虚拟根目录下的哪些文件打包到rpm包中。注意此处默认是以虚拟根目录作为前缀执行的，因此不要再加上%{buildroot}前缀。
%{_prefix} # 把/opt/mongoid_check目录下的东西都打包起来

%changelog

%preun # 【卸载前执行部分】

%postun # 【卸载后执行部分】
rm -rf %{_prefix}  
```

## 三、RPM构建命令

```shell
# 进入构建目录
cd rpmbuild

# target是计算机架构名, 会体现在做出来的包名上, 不写默认是本机架构。机器架构与包名上的架构不一致，会导致拒绝安装。
rpmbuild --target=x86_64 -bb SPECS/mongoid_check.spec
```

## 四、RPM的安装、查看及卸载

```shell
# 目录下会生成对应的RPM包
tree ./RPMS
./
├── aarch64
│   ├── mongoid_check-1.0.0-1.el7.centos.aarch64.rpm
│   └── nginx-1.12.2-1.el7.centos.aarch64.rpm
├── mips64
│   └── nginx-1.12.2-1.el7.centos.mips64.rpm
├── mips64el
│   └── nginx-1.12.2-1.el7.centos.mips64el.rpm
├── mips64r2
│   └── nginx-1.12.2-1.el7.centos.mips64r2.rpm
├── mipsel
│   └── nginx-1.12.2-1.el7.centos.mipsel.rpm
├── noarch
│   └── nginx-1.12.2-1.el7.centos.noarch.rpm
└── x86_64
    └── mongoid_check-1.0.0-1.el7.centos.x86_64.rpm

7 directories, 8 files

# 安装
rpm -ivh ./RPMS/x86_64/mongoid_check-1.0.0-1.el7.centos.x86_64.rpm

# 查看是否安装对应包
rpm -qa | grep mongoid_check

# 查看安装路径
rpm -ql mongoid_check

# 卸载, 按tab会有提示
rpm -e mognoid_check
```


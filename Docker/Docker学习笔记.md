# Dorker学习笔记

## 1. 概念 

+ Image：镜像，包含一系列app和环境变量的镜像
+ Container：容器，Image运行状态，Image和Container的关系可以比喻为类和对象的关系
+ Dockerfile：一个指令脚本，用于构建容器镜像

## 2. 常用命令

### 2.1 Image相关

#### 构建Image
```shell
docker build -t <image名称> <Dockerfile路径>
```

#### 列出Image
```shell
docker images
```

#### 推送Image
```shell
# step1：登录docker
docker login

# step2：给镜像打标签
# eg. docker tag getting-started hiddensnail/getting-started:v1.0
docker tag <镜像名> <用户名>/<镜像名>:<版本号>

# step3: 推送
# eg. docker push hiddensnail/getting-started:v1.0
docker push <用户名>/<镜像名>:<版本号>
```

#### 删除Image
```shell
# 删除单个image
docker rmi <image-id>

# 删除所有image
docker rmi `docker images -q`
```

#### 搜索Image 
```
docker search <镜像名>
```

#### 导出Image
```shell
docker save -o <导出镜像名> <镜像名>:<标签>
```

#### 导入Image
```shell
docker load -i <导入镜像名>
```

#### Container保存为Image
```shell
docker commit <容器名|容器ID> <镜像名>:<标签>
```

### 2.2 Container相关

#### 创建Container
```shell
# 正常启动
# 访问容器需要使用<主机IP>:<主机端口>进行访问
docker run -dp <主机端口>:<容器端口> <image名称>

# 以交互方式启动，-i：即使没有交互保持不退出，-t：分配伪终端并直接进入容器
# 容器内执行exit，容器会直接退出
docker run -i -t --name=<容器名> <镜像名> /bin/bash

# 以守护进程方式启动，-d：deamon
# 容器内执行exit，容器不会退出
docker run -i -d --name=<容器名> <镜像名>
```

#### 访问Container
```shell
# eg. docker exec -i -t 1245pdc /bin/bash
docker exec -i -t <容器名|容器id> <程序>
```

#### 列出Container进程
```shell
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a
```

#### 查看Container信息
```shell
docker inspect <容器名|容器id>
```

#### 启动Container
```shell
docker start <容器名|容器id>
```

#### 停止Container
```shell
# 停止container
docker stop <容器名|容器id>
```

#### 删除Container
```shell
# 删除container 
docker rm <容器名|容器id>

# 停止+删除container
docker rm -f <容器名|容器id>
```

### 2.3 Volume相关

#### 挂载Volume
```shell
# 容器目录路径必须使用绝对路径
# eg. docker run -id --name=playlinux2 -v C:\dockerData:/app centos
docker run ... -v <宿主机目录>:<容器目录> ...

# 从已知容器中挂载其volumes
# eg. docker run -id --name=playlinux2 --volumes-from=playlinux centos
docker run ... --volumes-from=<容器名|容器id> ...
```

## 3. Dockerfile

```
# 基于scratch镜像构建
FROM scratch

# 添加文件
ADD centos-8-x86_64.tar.xz /

# Copy文件
COPY 

# 执行命令
RUN

# 容器启动执行的命令
CMD ["/bin/bash"]

# 暴露的端口
EXPOSE 80

# 设置环境变量
ENV 

# 定义外部可挂载的数据卷
VOLUME

# 工作目录
WORKDIR

# 执行执行用户
USER

# 执行Shell脚本
SHELL
```


阅读到: https://docs.docker.com/get-started/05_persisting_data/
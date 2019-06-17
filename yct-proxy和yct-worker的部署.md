---
title: yct_proxy和yct_worker的部署地址
date: 2019-06-17 13:30:13

categories: 
- Docker

tags:
- Docker
---

### 代码地址 

yct_proxy代码:https://github.com/HU-A-U/my-proxy

yct_worker代码:https://github.com/HU-A-U/yct_worker

分支 aliyun 是 部署在阿里云上的服务的代码内容，不需要合并

---

### 阿里云RabbitMQ后台管理地址

http://47.102.218.137:15672

用户名：cic_admin

密码：JYcxys@3030

---

### 本地服务器 cic-odoo

#### 服务器地址
```
ssh root@192.168.1.230 
```

#### 镜像地址（此处为我自己的打包好的镜像地址，最好后面自己重新打包镜像，重新部署一遍）

本地服务proxy镜像地址

daocloud.io/huhuhuhu/new_proxy:latest

本地服务worker镜像地址


#### 运行的容器名称

redis容器，yct_redis,做数据缓存

proxy容器，yct_proxy,做代理服务

worker容器，worker_c 做数据缓存到redis中，worker_a 做数据解析 ，worker_s 做数据存库到mysql

aliyun_worker容器，to_save 处理阿里云代理的数据存到本地数据库

##### 连接RabbitMQ的地址 yct
```python
RABBITMQ_HOST = '47.102.218.137'
RABBITMQ_PORT = 5672
BROKER_URL = 'amqp://cic_admin:JYcxys@3030@{}:{}/yct'.format(RABBITMQ_HOST,RABBITMQ_PORT)
```

```
bee85252f246        daocloud.io/huhuhuhu/new_proxy:latest                "/bin/sh -c /code/..."   5 hours ago         Up 5 hours                  0.0.0.0:8888->8080/tcp             yct_proxy
30a27b1a1504        daocloud.io/huhuhuhu/yct_worker:latest               "/bin/sh -c /code/..."   2 days ago          Up 2 days                                                      worker_s
feff1b804441        daocloud.io/huhuhuhu/yct_worker:latest               "/bin/sh -c /code/..."   2 days ago          Up 2 days                                                      worker_a
937bda5c14b7        daocloud.io/huhuhuhu/yct_worker:latest               "/bin/sh -c /code/..."   2 days ago          Up 2 days                                                      worker_c
b461871a137b        docker.io/redis                                      "docker-entrypoint..."   2 weeks ago         Up 2 weeks                  6379/tcp                           yct_redis
666ead4ef827        daocloud.io/huhuhuhu/aliyun_yct_worker:latest        "/bin/sh -c /code/..."   4 days ago          Up 4 days                                                      to_save
```

---

### 阿里云服务器 newprocy-yuanqu01

#### 部署容器地址
```
ssh root@47.103.197.163
```

#### 运行容器名称

redis容器，yct_redis,做数据缓存

proxy容器，yct_proxy,做代理服务

worker容器，to_create 做数据缓存到redis中，to_analysis 做数据解析解析出需要的字段，将解析后的数据作为参数传递到to_save消息队列，供本地的服务器的to_save容器存库

##### 连接RabbitMQ的地址 newprocy-yuanqu01
```python
RABBITMQ_HOST = '47.102.218.137'
RABBITMQ_PORT = 5672
BROKER_URL = 'amqp://cic_admin:JYcxys@3030@{}:{}/newprocy-yuanqu01'.format(RABBITMQ_HOST,RABBITMQ_PORT)
```

```
[root@newprocy-yuanqu01 ~]# docker ps -a
CONTAINER ID        IMAGE                                                COMMAND                  CREATED             STATUS              PORTS                    NAMES
0cf0c9952b4b        daocloud.io/huhuhuhu/yct_white_list:latest           "/bin/sh -c 'nginx -…"   3 days ago          Up 3 days           0.0.0.0:9999->6666/tcp   white_list
5251bcc0e7d6        daocloud.io/huhuhuhu/aliyun_yct_worker:latest        "/bin/sh -c /code/do…"   4 days ago          Up 4 days                                    to_analysis
d5542e638405        daocloud.io/huhuhuhu/aliyun_yct_worker:latest        "/bin/sh -c /code/do…"   4 days ago          Up 4 days                                    to_create
44f9d01fb72a        daocloud.io/huhuhuhu/aliyun01_proxy:aliyun-c0ecb62   "/bin/sh -c /code/do…"   4 days ago          Up 4 days           0.0.0.0:8888->8080/tcp   yct_proxy
15df20e8da42        redis:3.2.12                                         "docker-entrypoint.s…"   2 weeks ago         Up 6 days           6379/tcp                 yct_redis
```


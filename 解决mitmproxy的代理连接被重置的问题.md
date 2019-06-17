---
title: 小记--关于mitmproxy的代理连接被重置的问题

date: 2019-05-27 14:41:38

categories: 
- python

tags:
- mitmproxy
---

### 概述
在浏览器设置proxy的代理之后，访问网页显示连接被重置，然后查看日志，报错信息如下：

```
[root@procy ~]# docker logs test_proxy
Loading script /code/start_script.py
Proxy server listening at http://*:8080
172.104.123.101:58074: clientconnect
Client connection from ::ffff:172.104.123.101 killed by block_global
172.104.123.101:58074: Connection killed
172.104.123.101:58074: clientdisconnect
```
可以看到 'killed by block_global' 连接被kill掉

### 解决
去官网找到[解决办法](https://discourse.mitmproxy.org/t/connection-killed-by-block-global-when-trying-to-connect-remotely/1215)

启动参数 添加 --set block_global=false 将block_global设为false

试了一下
```
mitmdump --set block_global=false -s /code/start_script.py
```
-s 参数是使用启动脚本进行启动

又恢复正常，至于原因不是很清楚，因为之前一直运行很正常，可能是跟网络有关。


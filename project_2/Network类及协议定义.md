
# 乱七八糟的文档

此文档旨在归纳一些乱七八糟代码的功能便于查阅。（顺便在写实验报告的时候省点事）

## 数据交换协议

为了便于数据交换，基于第一次Project的基础定义了一个简单的类HTTP应用层数据交换协议。协议定义如下

- 头部
  - Method/Status Code
  - Source IP
  - Source Port
  - Dest IP
  - Dest Port
  - Keep Alive
  - Body Len
- 数据体

## Network类

Network类是一个基于socket编程封装了若干网络访问功能以便于复用的类。
Network类能够实现以下功能

- 监听/停止监听指定端口
- 并行接受多个被监听端口的连接请求并调用指定的处理函数进行处理
- 与指定地址的指定端口建立/断开连接
- 在已建立的连接上发送请求/接受回应

### Network类图



# Nginx学习

## 1. 基本概念
在Web应用开发种会涉及到2种server，一种是WebServer，另一种是AppServer。

WebServer是用来解析用户的Http请求，然后返回响应的模块；至于如何处理这个请求，则需要交给AppServer进行处理，AppServer里面跑着像PHP、Python、Java的脚本。

Web Server和Application Server之间需要通过协议沟通，比如CGI、WSGI这类东西。虽然一些Application Server也能充当Web Server，但是它们对HTTP协议的实现并不完整，因此生产环境下不会这么用。

典型的WebServer：Nginx、Apache
典型的AppServer：Tomcat

**总结：WebServer是实现了Http协议的模块，AppServer是处理请求执行业务的模块，两个模块之间一般是通过CGI或类似的接口规范进行交互**


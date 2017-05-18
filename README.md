# NaiveHTTPServer
A naive HTTP server with No dependent. Just a hundred lines
## QuickStart

### 让他运行起来
创建一个简单的Server: `app = NaiveServer('127.0.0.1', 80)`
运行Server: `app.run()`

### 添加URL映射
参考Flask的装饰器的URL映射，这个简单的HTTPServer也是这种模式，在你的函数前加上路由装饰器，就变成了相应URL的映射！
```
@app.route("/")
def index():
    return Response('Hello World')
```

### Response对象
每个URL映射的函数都需要返回一个Response对象·
`Response(status_num=200, status_notes="OK", header=None, content="")`
依次为状态码，解释，请求头，正文
header部分为请求头，是一个字典。


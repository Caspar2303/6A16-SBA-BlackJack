from flask import Flask

# 1. 初始化 Flask 应用程序
app = Flask(__name__)

# 2. 定义一个最简单的路由（网址路径）
@app.route('/')
def health_check():
    # 当你在浏览器打开网址时，会看到这段文字
    return """
    <h1>✅ Flask 运行正常！</h1>
    <p>你的 SBA 项目环境已经准备就绪。</p>
    <hr>
    <ul>
        <li><b>步骤 1:</b> 环境检查已完成</li>
        <li><b>下一步:</b> 编写 21 点游戏逻辑</li>
    </ul>
    """

# 3. 启动服务器
if __name__ == '__main__':
    # 运行在 5000 端口，并开启调试模式
    app.run(debug=True)
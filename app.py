# 【關鍵步奏 1】導入 Flask 的核心組件
# 你需要從 flask 庫中「拿」出 Flask、render_template 和 request
from flask import Flask, render_template, request, redirect, url_for

# 【關鍵步奏 2】初始化你的 App
# 這行代碼定義了什麼是 "app"，這就是為什麼之前會報錯說 "app" 未定義
app = Flask(__name__)

# 首頁路由：顯示登入頁面
@app.route('/')
def index():
    return render_template('login.html')

# --- 在這裡插入 lobby 路由 ---
@app.route('/lobby')
def lobby():
    # 直接讀取並顯示 templates/lobby.html
    return render_template('lobby.html')

# 註冊頁面路由：當點擊「申請入會」按鈕時會來到這裡
@app.route('/register')
def register():
    # 這裡我們讓它去讀取 register.html
    return render_template('register.html')

# 處理註冊請求：當用戶在註冊頁面點擊「確認註冊」時會來到這裡
@app.route('/do_register', methods=['POST'])
def do_register():
    # 從表單中拿取用戶設定的資料
    new_user = request.form.get('username')
    new_pwd = request.form.get('password')
    
    # 目前我們先做一個簡單的反饋，確保數據有傳過來
    return f"<h1>註冊成功！</h1><p>歡迎 {new_user} 加入俱樂部。</p><a href='/'>返回登入頁面</a>"

# 【關鍵步奏 3】處理登入請求
@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd = request.form.get('password')

    # 暫時的測試邏輯：之後我們會改為檢查 users.txt
    if user == "admin" and pwd == "1234":
        # 修正：使用 redirect 讓網址跳轉到 /lobby
        # 這會去觸發你剛剛在 image_75f951.png 加入的那個 lobby() 函數
        return redirect(url_for('lobby'))
    else:
        # 登入失敗：維持原本的紅色警告 UI
        return f"""
        <body style="background-color: #1a0a0a; color: #ff4444; font-family: sans-serif; text-align: center; padding-top: 100px;">
            <h1 style="font-size: 48px;">❌ Log In Fail</h1>
            <p style="color: white; font-size: 20px;">Wrong Password Or Username</p>
            <br>
            <a href="/" style="color: #888; text-decoration: none; border: 1px solid #444; padding: 10px 20px; border-radius: 5px;">返回登入頁面重試</a>
        </body>
        """

# 這裡插入處理開始遊戲的路由
@app.route('/start_game', methods=['POST'])
def start_game():
    ai_count = request.form.get('ai_count')
    return f"""
    <body style="background-color: #0a1f12; color: white; font-family: sans-serif; text-align: center; padding-top: 100px;">
        
        <!-- ✅ 左上角 Logo 代碼放在這裡 -->
        <img src="/static/images/wesley_logo.png" 
             style="position: absolute; top: 20px; left: 20px; width: 100px; height: auto;">
        
        <h1>🃏 遊戲開始！</h1>
        <p style="font-size: 20px;">您選擇了與 {ai_count} 名電腦對戰。</p>
        
        <!-- 將文字改為按鈕 -->
        <div style="margin: 30px 0;">
            <button onclick="window.location.href='/game'" style="background: #d4af37; color: black; border: none; padding: 15px 40px; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 20px;">
                ✅ 我準備好了！
            </button>
        </div>

        <hr style="width: 300px; border: 0.5px solid #444;">
        
        <button onclick="window.location.href='/lobby'" style="color: #888; background: none; border: none; cursor: pointer; font-size: 16px;">
            ⬅️ 返回重新選擇
        </button>
    </body>
    """

# 登出功能：將玩家重定向回登入頁面
@app.route('/logout')
def logout():
    # 這裡未來可以加入「清除 Session」的動作
    return redirect(url_for('index'))

@app.route('/game')
def game():
    return """
    <body style="background-color: #062111; color: white; font-family: sans-serif; text-align: center; padding-top: 100px;">
        <img src="/static/images/wesley_logo.png" style="position: absolute; top: 20px; left: 20px; width: 100px; height: auto;">
        
        <h1 style="color: #d4af37;">🃏 遊戲桌 (Game Table)</h1>
        <p>正在初始化遊戲設定...</p>
        <p style="color: #888;">(明天我們將在這裡完成洗牌與發牌 UI)</p>
        <br>
        <button onclick="window.location.href='/lobby'" style="padding: 10px 20px; background: none; border: 1px solid #444; color: #888; cursor: pointer; border-radius: 5px;">
            終止遊戲並返回大廳
        </button>
    </body>
    """

# 【關鍵步奏 4】啟動伺服器 (這一段永遠放在檔案的最底層)
if __name__ == '__main__':
    app.run(debug=True)
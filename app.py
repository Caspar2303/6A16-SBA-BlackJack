import os
import json
import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# 設定 Session 加密金鑰
app.secret_key = 'black_jack_secret_key_wesley'

# ---------------------------------------------------------
# SBA 學術免責聲明組件（顯示於每個頁面底部）
# ---------------------------------------------------------
SBA_NOTICE_HTML = """
<footer style="margin-top: 50px; padding: 20px 0; border-top: 1px solid #333; text-align: center; color: #888; font-size: 14px;">
    <p style="margin: 5px 0;">Minors are strictly prohibited from participating in gambling activities.</p>
    <p style="margin: 5px 0; color: #aaa; font-weight: bold;">*Just For School SBA - No Real Money Gambling Included*</p>
</footer>
"""

# ---------------------------------------------------------
# JSON 資料庫持久化儲存邏輯 (Data Persistence)
# ---------------------------------------------------------
DB_FILE = 'users.json'

def load_users():
    """從 JSON 檔案讀取所有使用者帳號與資料，若檔案不存在則自動建立預設 Admin"""
    if not os.path.exists(DB_FILE):
        default_data = {
            "admin": {"password": "1234", "role": "admin", "bank": 1000}
        }
        save_users(default_data)
        return default_data
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users_db):
    """將最新的使用者資料寫回 users.json 檔案進行存檔"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------------
# 撲克牌洗牌與 21 點點數計算演算法
# ---------------------------------------------------------

def create_deck():
    """建立一副全新的 52 張撲克牌並完成隨機洗牌"""
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = []
    for suit in suits:
        color = 'red' if suit in ['♥', '♦'] else 'black'
        for rank in ranks:
            deck.append({'suit': suit, 'rank': rank, 'color': color})
    random.shuffle(deck)
    return deck

def render_card_html(card, is_back=False):
    """將撲克牌資料轉換為前端 HTML/CSS 視覺卡片"""
    if is_back:
        return '<div class="card back"></div>'
    red_class = ' red' if card['color'] == 'red' else ''
    return f"""
    <div class="card{red_class}">
        <div style="font-size: 18px;">{card['rank']}</div>
        <div style="font-size: 26px; text-align: center; margin-top: 5px;">{card['suit']}</div>
    </div>
    """

def calculate_score(hand):
    """計算手牌點數（包含 Ace 牌自動在 11 分與 1 分之間轉換的邏輯）"""
    score = 0
    aces = 0
    for card in hand:
        rank = card['rank']
        if rank in ['J', 'Q', 'K']:
            score += 10
        elif rank == 'A':
            score += 11
            aces += 1
        else:
            score += int(rank)
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score

# ---------------------------------------------------------
# 網頁路由邏輯 (Flask Web Routes)
# ---------------------------------------------------------

# 首頁路由直接導向登入頁面
@app.route('/')
def home():
    return render_template('login.html')

# 登入頁面路由
@app.route('/login_page')
def index():
    return render_template('login.html')

# 註冊頁面
@app.route('/register')
def register():
    return render_template('register.html')

# 處理使用者註冊請求
@app.route('/do_register', methods=['POST'])
def do_register():
    new_user = request.form.get('username')
    new_pwd = request.form.get('password')

    if not new_user or not new_pwd:
        return f"""
        <body style="background-color: #0a1f12; color: white; text-align: center; padding-top: 100px; font-family: sans-serif;">
            <h1>Registration Failed</h1><p>Please enter both username and password.</p>
            <a href='/register' style="color: #d4af37;">Try Again</a>
            {SBA_NOTICE_HTML}
        </body>
        """

    users_db = load_users()
    if new_user in users_db:
        return f"""
        <body style="background-color: #0a1f12; color: white; text-align: center; padding-top: 100px; font-family: sans-serif;">
            <h1>Registration Failed</h1><p>Username <strong>{new_user}</strong> is already taken!</p>
            <a href='/register' style="color: #d4af37;">Try Again</a>
            {SBA_NOTICE_HTML}
        </body>
        """

    users_db[new_user] = {
        "password": new_pwd,
        "role": "player",
        "bank": 1000
    }
    save_users(users_db)
    
    return f"""
    <body style="background-color: #0a1f12; color: white; text-align: center; padding-top: 100px; font-family: sans-serif;">
        <h1 style="color: #2ed573;">🎉 Registration Successful!</h1>
        <p>Welcome, <strong>{new_user}</strong>! Your starting balance is $1000.</p>
        <br>
        <a href="/" style="color: #d4af37; font-size: 18px; text-decoration: none; border: 1px solid #d4af37; padding: 10px 20px; border-radius: 5px;">Go to Login</a>
        {SBA_NOTICE_HTML}
    </body>
    """

# 處理登入驗證邏輯
@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pwd = request.form.get('password')

    users_db = load_users()
    if user in users_db and users_db[user]['password'] == pwd:
        session['user'] = user
        session['role'] = users_db[user]['role']
        session['bank'] = users_db[user]['bank']
        return redirect(url_for('lobby'))
    else:
        return f"""
        <body style="background-color: #1a0a0a; color: #ff4444; font-family: sans-serif; text-align: center; padding-top: 100px;">
            <h1 style="font-size: 48px;">❌ Login Failed</h1>
            <p style="color: white; font-size: 20px;">Invalid Username or Password</p>
            <br>
            <a href="/" style="color: #888; text-decoration: none; border: 1px solid #444; padding: 10px 20px; border-radius: 5px;">Back to Login Page</a>
            {SBA_NOTICE_HTML}
        </body>
        """

# 遊戲主大廳
@app.route('/lobby')
def lobby():
    if 'user' not in session:
        return redirect(url_for('home'))

    current_user = session['user']
    role = session['role']

    users_db = load_users()
    if current_user in users_db:
        session['bank'] = users_db[current_user]['bank']

    admin_btn_html = ""
    if role == 'admin':
        admin_btn_html = """
        <a href="/admin_panel" style="position: absolute; top: 20px; right: 120px; background: #d4af37; color: black; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold;">
            👑 Admin Panel
        </a>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background-color: #0a1f12; color: white; font-family: sans-serif; text-align: center; padding-top: 50px; position: relative; }}
            .btn {{ background: #2ed573; color: white; border: none; padding: 12px 30px; font-size: 18px; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }}
            .logout-btn {{ position: absolute; top: 20px; right: 20px; background: #ff4757; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        {admin_btn_html}
        <a href="/logout" class="logout-btn">Log Out</a>

        <h1>🎰 Welcome to Blackjack Lobby</h1>
        <p style="font-size: 20px;">Current Player: <strong>{current_user}</strong> ({'Super Admin' if role == 'admin' else 'Player'})</p>
        <p style="font-size: 18px; color: #ffd700;">Current Bank: ${session.get('bank', 1000)}</p>

        <div style="margin-top: 40px;">
            <form action="/start_game" method="POST">
                <label for="ai_count" style="font-size: 18px;">Select Bot Teammates Count:</label>
                <select name="ai_count" id="ai_count" style="padding: 8px; font-size: 16px; border-radius: 5px;">
                    <option value="1">1 Bot</option>
                    <option value="2">2 Bots</option>
                    <option value="3">3 Bots</option>
                </select>
                <br><br>
                <button type="submit" class="btn">🚀 Start Game Test</button>
            </form>
        </div>

        {SBA_NOTICE_HTML}
    </body>
    </html>
    """

# 超級管理員專屬後台
@app.route('/admin_panel')
def admin_panel():
    if session.get('role') != 'admin':
        return f"""
        <body style="background-color: #111; color: white; text-align: center; padding-top: 100px; font-family: sans-serif;">
            <h1>🚫 Access Denied! Only Admin can view user data.</h1>
            <a href='/lobby' style="color: #d4af37;">Back to Lobby</a>
            {SBA_NOTICE_HTML}
        </body>
        """

    users_db = load_users()
    rows_html = ""
    for username, info in users_db.items():
        role_badge = "👑 Admin" if info['role'] == 'admin' else '👤 Player'
        rows_html += f"""
        <tr>
            <td style="padding: 12px; border: 1px solid #444;">{username}</td>
            <td style="padding: 12px; border: 1px solid #444;">{info['password']}</td>
            <td style="padding: 12px; border: 1px solid #444;">{role_badge}</td>
            <td style="padding: 12px; border: 1px solid #444; color: #2ed573; font-weight: bold;">${info['bank']}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background-color: #111; color: white; font-family: sans-serif; text-align: center; padding: 40px; }}
            table {{ width: 80%; margin: 20px auto; border-collapse: collapse; background: #222; }}
            th {{ background: #d4af37; color: black; padding: 12px; font-size: 18px; }}
        </style>
    </head>
    <body>
        <h1 style="color: #d4af37;">👑 Admin User Management Panel</h1>
        <p>List of all registered accounts and user details:</p>

        <table>
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Password</th>
                    <th>Role Permission</th>
                    <th>Current Bank ($)</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <br>
        <a href="/lobby" style="color: #888; text-decoration: none; border: 1px solid #666; padding: 10px 20px; border-radius: 5px;">⬅️ Back to Lobby</a>

        {SBA_NOTICE_HTML}
    </body>
    </html>
    """

# 對局準備頁面
@app.route('/start_game', methods=['POST'])
def start_game():
    ai_count = request.form.get('ai_count', 1)
    return f"""
    <body style="background-color: #0a1f12; color: white; font-family: sans-serif; text-align: center; padding-top: 100px;">
        <h1>🃏 Preparing Match</h1>
        <p style="font-size: 20px;">Playing with {ai_count} Bot(s).</p>
        <form action="/game" method="POST">
            <input type="hidden" name="ai_count" value="{ai_count}">
            <button type="submit" style="background: #d4af37; color: black; border: none; padding: 12px 30px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 18px;">
                ✅ Enter Table
            </button>
        </form>

        {SBA_NOTICE_HTML}
    </body>
    """

# 登出邏輯
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# 21 點核心遊戲邏輯
@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'user' not in session:
        return redirect(url_for('home'))

    ai_count = int(request.form.get('ai_count', session.get('ai_count', 1)))
    session['ai_count'] = ai_count
    action = request.form.get('action', 'bet_phase')

    quit_btn_html = """
    <a href="/lobby" style="position: absolute; top: 20px; right: 20px; background: rgba(255, 71, 87, 0.2); color: #ff4757; border: 1px solid #ff4757; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">
        🚪 Quit Table
    </a>
    """

    if action == 'bet_phase':
        if session.get('bank', 0) <= 0:
            session['bank'] = 1000
            users_db = load_users()
            if session['user'] in users_db:
                users_db[session['user']]['bank'] = 1000
                save_users(users_db)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ background-color: #116235; font-family: Arial, sans-serif; color: white; margin: 0; padding: 20px; text-align: center; position: relative; }}
                .table {{ max-width: 600px; margin: 60px auto 20px; background: rgba(0,0,0,0.2); padding: 40px; border-radius: 20px; border: 2px solid #2ed573; }}
                .bet-input {{ padding: 12px; font-size: 20px; width: 120px; text-align: center; border-radius: 8px; border: none; font-weight: bold; margin: 10px; }}
                .btn-deal {{ background: #2ed573; border: none; color: white; padding: 12px 35px; font-size: 20px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; }}
                .bank-tag {{ position: fixed; bottom: 10px; left: 10px; background: #1e272e; padding: 8px 16px; border-radius: 5px; font-size: 16px; font-weight: bold; }}
            </style>
        </head>
        <body>
            {quit_btn_html}

            <div class="table">
                <h1 style="color: #2ed573;">💰 Place Your Bet</h1>
                <p style="font-size: 18px;">Player <strong>{session['user']}</strong> Current Balance: <strong>${session['bank']}</strong></p>
                
                <form action="/game" method="POST">
                    <input type="hidden" name="action" value="start_round">
                    <div style="margin: 20px 0;">
                        <label style="font-size: 18px;">Enter Bet Amount ($):</label><br>
                        <input type="number" name="bet" value="100" min="1" max="{session['bank']}" class="bet-input" required oninvalid="this.setCustomValidity('Value must be greater than or equal to 1.')" oninput="this.setCustomValidity('')">
                    </div>
                    <button type="submit" class="btn-deal">🃏 Deal</button>
                </form>
            </div>

            <div class="bank-tag">
                Bank: <span style="color: white;">${session['bank']}</span>
            </div>

            {SBA_NOTICE_HTML}
        </body>
        </html>
        """

    if action == 'start_round':
        bet = int(request.form.get('bet', 100))
        session['bet'] = bet
        session['deck'] = create_deck()
        session['dealer_hand'] = [session['deck'].pop(), session['deck'].pop()]
        session['player_hand'] = [session['deck'].pop(), session['deck'].pop()]
        session['bots_hands'] = [[session['deck'].pop(), session['deck'].pop()] for _ in range(ai_count)]
        session['game_over'] = False
        session['result_msg'] = ""

    elif action == 'hit' and not session.get('game_over', False):
        session['player_hand'].append(session['deck'].pop())
        if calculate_score(session['player_hand']) > 21:
            session['game_over'] = True
            session['bank'] -= session['bet']
            session['result_msg'] = "💥 You Busted!"

            if session['bank'] <= 0:
                session['bank'] = 0
                session['result_msg'] += "<br><span style='color: #fffa65; font-size: 20px;'>⚠️ You are bankrupt! Click the button below to receive $1000 rescue fund.</span>"

            users_db = load_users()
            if session['user'] in users_db:
                users_db[session['user']]['bank'] = session['bank']
                save_users(users_db)

            session.modified = True

    elif action == 'stand' and not session.get('game_over', False):
        session['game_over'] = True
        while calculate_score(session['dealer_hand']) < 17:
            session['dealer_hand'].append(session['deck'].pop())
            
        p_score = calculate_score(session['player_hand'])
        d_score = calculate_score(session['dealer_hand'])
        
        if d_score > 21:
            session['bank'] += session['bet']
            session['result_msg'] = "🎉 Dealer Busted! You Win!"
        elif p_score > d_score:
            session['bank'] += session['bet']
            session['result_msg'] = "🎉 You Win!"
        elif p_score < d_score:
            session['bank'] -= session['bet']
            session['result_msg'] = "❌ You Lose!"
        else:
            session['result_msg'] = "🤝 Push!"

        if session['bank'] <= 0:
            session['bank'] = 0
            session['result_msg'] += "<br><span style='color: #fffa65; font-size: 20px;'>⚠️ You are bankrupt! Click the button below to receive $1000 rescue fund.</span>"

        users_db = load_users()
        if session['user'] in users_db:
            users_db[session['user']]['bank'] = session['bank']
            save_users(users_db)

        session.modified = True

    game_over = session.get('game_over', False)
    player_hand = session.get('player_hand', [])
    dealer_hand = session.get('dealer_hand', [])
    bots_hands = session.get('bots_hands', [])
    bet = session.get('bet', 100)

    dealer_cards_html = ""
    if game_over:
        for card in dealer_hand:
            dealer_cards_html += render_card_html(card)
        dealer_score_str = str(calculate_score(dealer_hand))
    else:
        dealer_cards_html = render_card_html(dealer_hand[0], is_back=True) + render_card_html(dealer_hand[1])
        dealer_score_str = "?"

    ai_players_html = ""
    for i, b_hand in enumerate(bots_hands, 1):
        b_cards_html = "".join([render_card_html(c, is_back=not game_over) for c in b_hand])
        b_score = calculate_score(b_hand) if game_over else "?"
        ai_players_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center;">
            <div class="card-container">{b_cards_html}</div>
            <div class="score-badge">{b_score} <span>Bot {i}</span></div>
        </div>
        """

    player_cards_html = "".join([render_card_html(c) for c in player_hand])
    player_score = calculate_score(player_hand)

    if not game_over:
        action_area = f"""
        <div class="chip-area">
            <form action="/game" method="POST" style="display: inline;">
                <input type="hidden" name="action" value="hit">
                <button type="submit" class="btn-action">➕ Hit</button>
            </form>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div class="chip">BET</div>
                <span style="font-size: 22px; font-weight: bold;">${bet}</span>
            </div>
            <form action="/game" method="POST" style="display: inline;">
                <input type="hidden" name="action" value="stand">
                <button type="submit" class="btn-action btn-stand">✋ Stand</button>
            </form>
        </div>
        """
    else:
        btn_text = "💰 Claim $1000 Rescue Fund & Play Again" if session.get('bank', 0) <= 0 else "🔄 Play Again"
        action_area = f"""
        <div style="margin: 20px 0;">
            <h2 style="color: #ffd700; font-size: 24px; margin-bottom: 15px;">{session.get('result_msg', '')}</h2>
            <form action="/game" method="POST" style="display: inline;">
                <input type="hidden" name="action" value="bet_phase">
                <button type="submit" class="btn-action" style="padding: 12px 30px; font-size: 18px; background: #2ed573;">{btn_text}</button>
            </form>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background-color: #116235; font-family: Arial, sans-serif; color: white; margin: 0; padding: 20px; user-select: none; position: relative; }}
            .table {{ max-width: 900px; margin: 0 auto; text-align: center; position: relative; }}
            .dealer-area {{ margin-bottom: 30px; }}
            .players-area {{ display: flex; justify-content: center; align-items: flex-end; gap: 40px; margin-top: 20px; }}
            .card-container {{ display: flex; justify-content: center; margin: 10px 0; }}
            .card {{ width: 75px; height: 110px; background: white; color: black; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.5); margin: 0 -15px; position: relative; padding: 5px; box-sizing: border-box; font-weight: bold; }}
            .card.red {{ color: #d63031; }}
            .card.back {{ background: #d63031; border: 3px solid white; background-image: repeating-linear-gradient(45deg, #b22222 0, #b22222 10px, #d63031 10px, #d63031 20px); }}
            .score-badge {{ display: inline-block; background: rgba(0,0,0,0.4); padding: 6px 14px; border-radius: 20px; font-size: 16px; font-weight: bold; }}
            .score-badge span {{ color: #2ed573; margin-left: 5px; }}
            .chip-area {{ margin: 20px 0; display: flex; justify-content: center; align-items: center; gap: 20px; }}
            .chip {{ width: 55px; height: 55px; background: #2ed573; border: 4px dashed white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; }}
            .btn-action {{ background: #2ed573; border: none; color: white; padding: 10px 22px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; }}
            .btn-stand {{ background: #e17055; }}
            .bank-tag {{ position: fixed; bottom: 10px; left: 10px; background: #1e272e; padding: 8px 16px; border-radius: 5px; font-size: 16px; font-weight: bold; }}
        </style>
    </head>
    <body>
        {quit_btn_html}

        <div class="table">
            <div class="dealer-area">
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div class="card-container">{dealer_cards_html}</div>
                    <div class="score-badge">{dealer_score_str} <span style="color: #ff4757;">Dealer</span></div>
                </div>
            </div>

            {action_area}

            <div class="players-area">
                {ai_players_html}
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div class="card-container">{player_cards_html}</div>
                    <div class="score-badge">{player_score} <span>{session['user']}</span></div>
                </div>
            </div>
        </div>

        <div class="bank-tag">
            Bank: <span style="color: white;">${session['bank']}</span>
        </div>

        {SBA_NOTICE_HTML}
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
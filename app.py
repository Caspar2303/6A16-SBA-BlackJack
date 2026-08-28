import os
import json
import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'black_jack_secret_key_wesley'

# 頁尾免責聲明與 Logo 標籤
SBA_NOTICE_HTML = """
<footer style="margin-top: 50px; padding: 20px 0; border-top: 1px solid #333; text-align: center; color: #888; font-size: 14px;">
    <p style="margin: 5px 0;">Minors are strictly prohibited from participating in gambling activities.</p>
    <p style="margin: 5px 0; color: #aaa; font-weight: bold;">*Just For School SBA - No Real Money Gambling Included*</p>
</footer>
"""

LOGO_HTML = '<img src="/static/images/wesley_logo.png" style="position: absolute; top: 20px; left: 20px; width: 100px; height: auto;" alt="Logo">'
DB_FILE = 'users.json'

# --- [資料庫操作] ---
def load_users():
    if not os.path.exists(DB_FILE):
        default_data = {"admin": {"password": "1234", "role": "admin", "bank": 1000}}
        save_users(default_data)
        return default_data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users_db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, ensure_ascii=False, indent=4)

def linear_search_user(target_username, users_db):
    user_list = list(users_db.keys())
    i = 0
    found = False
    while i < len(user_list) and not found:
        if user_list[i].lower() == target_username.lower():
            found = True
        i += 1
    return found

def bubble_sort_leaderboard(users_data_list):
    n = len(users_data_list)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if users_data_list[j]['bank'] < users_data_list[j + 1]['bank']:
                temp = users_data_list[j]
                users_data_list[j] = users_data_list[j + 1]
                users_data_list[j + 1] = temp
    return users_data_list

def validate_bet_amount(bet_input, player_bank):
    if bet_input is None or str(bet_input).strip() == "":
        return False, "Bet amount is required."
    try:
        bet_val = int(bet_input)
    except ValueError:
        return False, "Bet amount must be an integer."
    if bet_val < 1 or bet_val > player_bank:
        return False, f"Bet must be between $1 and ${player_bank}."
    return True, bet_val

# --- [撲克牌遊戲邏輯] ---
def create_deck():
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
    if not hand:
        return 0
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

# --- [路由區域] ---

@app.route('/')
@app.route('/login_page')
def home():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/do_register', methods=['POST'])
def do_register():
    new_user = request.form.get('username', '').strip()
    new_pwd = request.form.get('password', '').strip()

    if not new_user or not new_pwd:
        return render_template('register.html', error="Please enter both username and password.")

    users_db = load_users()
    if linear_search_user(new_user, users_db):
        return render_template('register.html', error=f"Username '{new_user}' is already taken!")

    users_db[new_user] = {"password": new_pwd, "role": "player", "bank": 1000}
    save_users(users_db)
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username', '').strip()
    pwd = request.form.get('password', '').strip()

    users_db = load_users()
    if user in users_db and users_db[user]['password'] == pwd:
        session['user'] = user
        session['role'] = users_db[user]['role']
        session['bank'] = users_db[user]['bank']
        return redirect(url_for('lobby'))
    else:
        return render_template('login.html', error="Invalid username or password.")

@app.route('/lobby')
def lobby():
    if 'user' not in session:
        return redirect(url_for('home'))

    current_user = session['user']
    users_db = load_users()
    if current_user in users_db:
        session['bank'] = users_db[current_user]['bank']

    return render_template('lobby.html', current_user=current_user, role=session['role'], bank=session.get('bank', 1000))

@app.route('/start_game', methods=['POST'])
def start_game():
    ai_count = request.form.get('ai_count', 1)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ready to Play</title>
        <style>
            body {{ background-color: #0a1f12; color: white; font-family: sans-serif; text-align: center; padding-top: 100px; margin: 0; }}
            .btn-enter {{ background: #d4af37; color: black; border: none; padding: 12px 30px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 18px; width: 180px; margin-bottom: 15px; }}
            .btn-quit {{ background: #e74c3c; color: white; border: none; padding: 10px 25px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; width: 180px; text-decoration: none; display: inline-block; }}
        </style>
    </head>
    <body>
        {LOGO_HTML}
        <h1>🃏 Ready to Start</h1>
        <p style="font-size: 20px;">Playing with {ai_count} Bot(s) at the table.</p>
        
        <form action="/game" method="POST">
            <input type="hidden" name="ai_count" value="{ai_count}">
            <button type="submit" class="btn-enter">✅ Enter Table</button>
        </form>
        <br>
        <a href="/lobby" class="btn-quit">🚪 Quit to Lobby</a>

        {SBA_NOTICE_HTML}
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'user' not in session:
        return redirect(url_for('home'))

    ai_count = int(request.form.get('ai_count', session.get('ai_count', 1)))
    session['ai_count'] = ai_count
    action = request.form.get('action', 'bet_phase')

    quit_btn_html = """
    <a href="/lobby" style="position: absolute; top: 20px; right: 20px; background: rgba(255, 71, 87, 0.2); color: #ff4757; border: 1px solid #ff4757; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px;">
        🚪 Quit to Lobby
    </a>
    """

    if action == 'bet_phase':
        refilled_modal_html = ""
        if session.get('bank', 0) <= 0:
            session['bank'] = 1000
            refilled_modal_html = """
            <div id="refillModal" style="position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center;">
                <div style="background: #0a1f12; border: 2px solid #d4af37; padding: 30px; border-radius: 15px; text-align: center; max-width: 400px; color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.5);">
                    <h2 style="color: #d4af37; margin-top: 0;">💰 System Notice</h2>
                    <p style="font-size: 16px; line-height: 1.5;">Your bank becomes 0, we auto-reload your bank to 1000!</p>
                    <button onclick="document.getElementById('refillModal').style.display='none'" style="background: #2ed573; color: white; border: none; padding: 10px 25px; font-size: 16px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 15px;">OK!</button>
                </div>
            </div>
            """
            users_db = load_users()
            if session['user'] in users_db:
                users_db[session['user']]['bank'] = 1000
                save_users(users_db)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Place Your Bet</title>
            <style>
                body {{ background-color: #116235; font-family: Arial, sans-serif; color: white; margin: 0; padding: 20px; text-align: center; position: relative; }}
                .table {{ max-width: 600px; margin: 60px auto 20px; background: rgba(0,0,0,0.2); padding: 40px; border-radius: 20px; border: 2px solid #2ed573; }}
                .bet-input {{ padding: 12px; font-size: 24px; width: 140px; text-align: center; border-radius: 8px; border: none; font-weight: bold; margin: 10px; }}
                .chip-btn {{ background: #d4af37; color: black; border: none; padding: 8px 15px; margin: 5px; border-radius: 20px; font-weight: bold; cursor: pointer; font-size: 14px; }}
                .chip-btn:hover {{ background: #f1c40f; }}
                .btn-deal {{ background: #2ed573; border: none; color: white; padding: 12px 35px; font-size: 20px; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 20px; }}
            </style>
            <script>
                function addBet(amount) {{
                    var input = document.getElementById('bet_input');
                    var current = parseInt(input.value) || 0;
                    var maxBank = {session['bank']};
                    var newVal = current + amount;
                    if (newVal > maxBank) newVal = maxBank;
                    input.value = newVal;
                }}
                function clearBet() {{
                    document.getElementById('bet_input').value = 0;
                }}
            </script>
        </head>
        <body>
            {refilled_modal_html}
            {LOGO_HTML}
            {quit_btn_html}
            <div class="table">
                <h1 style="color: #2ed573;">💰 Place Your Bet</h1>
                <p style="font-size: 18px;">Player <strong>{session['user']}</strong> Balance: <strong>${session['bank']}</strong></p>
                
                <form action="/game" method="POST">
                    <input type="hidden" name="action" value="start_round">
                    <input type="number" id="bet_input" name="bet" value="100" min="1" max="{session['bank']}" class="bet-input" required><br>
                    
                    <div style="margin: 15px 0;">
                        <button type="button" class="chip-btn" onclick="addBet(10)">+10</button>
                        <button type="button" class="chip-btn" onclick="addBet(20)">+20</button>
                        <button type="button" class="chip-btn" onclick="addBet(50)">+50</button>
                        <button type="button" class="chip-btn" onclick="addBet(100)">+100</button>
                        <button type="button" class="chip-btn" style="background:#ff4757; color:white;" onclick="clearBet()">Clear</button>
                    </div>

                    <button type="submit" class="btn-deal">🃏 Deal</button>
                </form>
            </div>
            {SBA_NOTICE_HTML}
        </body>
        </html>
        """

    if action == 'start_round':
        bet_raw = request.form.get('bet')
        is_valid, bet_or_msg = validate_bet_amount(bet_raw, session.get('bank', 1000))
        if not is_valid:
            return f"<script>alert('{bet_or_msg}'); window.history.back();</script>"
            
        session['bet'] = bet_or_msg
        session['deck'] = create_deck()
        session['dealer_hand'] = [session['deck'].pop(), session['deck'].pop()]
        session['player_hand'] = [session['deck'].pop(), session['deck'].pop()]
        session['player_hand2'] = []
        session['active_hand'] = 1
        session['is_split'] = False
        session['bots_hands'] = [[session['deck'].pop(), session['deck'].pop()] for _ in range(ai_count)]
        session['game_over'] = False

    elif action == 'split' and not session.get('game_over', False):
        p_hand = session.get('player_hand', [])
        current_bank = session.get('bank', 0)
        current_bet = session.get('bet', 0)

        if len(p_hand) == 2 and p_hand[0]['rank'] == p_hand[1]['rank'] and current_bank >= current_bet * 2:
            session['is_split'] = True
            session['player_hand2'] = [p_hand.pop()]
            session['player_hand'].append(session['deck'].pop())
            session['player_hand2'].append(session['deck'].pop())

    elif action == 'hit' and not session.get('game_over', False):
        active_hand = session.get('active_hand', 1)
        if active_hand == 1:
            session['player_hand'].append(session['deck'].pop())
            if calculate_score(session['player_hand']) > 21:
                if session.get('is_split', False):
                    session['active_hand'] = 2
                else:
                    session['game_over'] = True
                    process_game_settlement()
        else:
            session['player_hand2'].append(session['deck'].pop())
            if calculate_score(session['player_hand2']) > 21:
                session['game_over'] = True
                process_game_settlement()

    elif action == 'stand' and not session.get('game_over', False):
        active_hand = session.get('active_hand', 1)
        if active_hand == 1 and session.get('is_split', False):
            session['active_hand'] = 2
        else:
            session['game_over'] = True
            process_game_settlement()

    return render_game_screen(ai_count, quit_btn_html)

def process_game_settlement():
    for i in range(len(session.get('bots_hands', []))):
        while calculate_score(session['bots_hands'][i]) < 17:
            session['bots_hands'][i].append(session['deck'].pop())

    while calculate_score(session['dealer_hand']) < 17:
        session['dealer_hand'].append(session['deck'].pop())

    d_score = calculate_score(session['dealer_hand'])
    p1_score = calculate_score(session['player_hand'])
    p2_score = calculate_score(session['player_hand2'])
    is_split = session.get('is_split', False)
    bet = session.get('bet', 0)

    total_change = 0
    msg = ""

    if p1_score > 21:
        total_change -= bet
        msg += "Hand 1: 💥Bust | "
    elif d_score > 21 or p1_score > d_score:
        total_change += bet
        msg += "Hand 1: 🎉Win | "
    elif p1_score < d_score:
        total_change -= bet
        msg += "Hand 1: ❌Loss | "
    else:
        msg += "Hand 1: 🤝Push | "

    if is_split:
        if p2_score > 21:
            total_change -= bet
            msg += "Hand 2: 💥Bust"
        elif d_score > 21 or p2_score > d_score:
            total_change += bet
            msg += "Hand 2: 🎉Win"
        elif p2_score < d_score:
            total_change -= bet
            msg += "Hand 2: ❌Loss"
        else:
            msg += "Hand 2: 🤝Push"

    session['bank'] += total_change
    session['result_msg'] = msg

    users_db = load_users()
    if session['user'] in users_db:
        users_db[session['user']]['bank'] = session['bank']
        save_users(users_db)

def render_game_screen(ai_count, quit_btn_html):
    game_over = session.get('game_over', False)
    dealer_hand = session.get('dealer_hand', [])
    player_hand = session.get('player_hand', [])
    player_hand2 = session.get('player_hand2', [])
    is_split = session.get('is_split', False)
    active_hand = session.get('active_hand', 1)
    bank = session.get('bank', 0)
    bet = session.get('bet', 0)

    dealer_cards = "".join([render_card_html(c, is_back=not game_over and i==0) for i, c in enumerate(dealer_hand)])
    player_cards = "".join([render_card_html(c) for c in player_hand])
    player_cards2 = "".join([render_card_html(c) for c in player_hand2]) if is_split else ""

    bots_html = ""
    for idx, bot_hand in enumerate(session.get('bots_hands', [])):
        bot_cards = "".join([render_card_html(c, is_back=not game_over) for c in bot_hand])
        bot_score_str = f" ({calculate_score(bot_hand)} pts)" if game_over else ""
        bots_html += f"""
        <div style='background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; min-width: 180px;'>
            <h4>🤖 Bot {idx+1}{bot_score_str}</h4>
            <div>{bot_cards}</div>
        </div>
        """

    can_split = (len(player_hand) == 2 and player_hand[0]['rank'] == player_hand[1]['rank'] and not is_split and bank >= bet * 2)

    split_btn = f"""
    <form action="/game" method="POST" style="display:inline;">
        <input type="hidden" name="action" value="split">
        <button type="submit" style="padding:10px 20px; font-size:16px; cursor:pointer; background:#f39c12; color:white; border:none; border-radius:5px; margin: 0 5px;">✂️ Split</button>
    </form>
    """ if can_split and not game_over else ""

    action_buttons = f"""
    {split_btn}
    <form action="/game" method="POST" style="display:inline;">
        <input type="hidden" name="action" value="hit">
        <button type="submit" style="padding:10px 20px; font-size:16px; cursor:pointer; background:#2ed573; color:white; border:none; border-radius:5px; margin: 0 5px;">➕ Hit</button>
    </form>
    <form action="/game" method="POST" style="display:inline;">
        <input type="hidden" name="action" value="stand">
        <button type="submit" style="padding:10px 20px; font-size:16px; cursor:pointer; background:#e74c3c; color:white; border:none; border-radius:5px; margin: 0 5px;">✋ Stand</button>
    </form>
    """ if not game_over else f"""
    <h2 style="color: #f1c40f;">{session.get('result_msg')}</h2>
    <form action="/game" method="POST">
        <input type="hidden" name="action" value="bet_phase">
        <button type="submit" style="padding:10px 20px; font-size:16px; cursor:pointer; background:#d4af37; border:none; border-radius:5px; font-weight:bold;">🔄 Play Again</button>
    </form>
    """

    dealer_score_display = calculate_score(dealer_hand) if game_over else "?"

    p1_active_border = "border: 2px solid #f1c40f;" if (is_split and active_hand == 1 and not game_over) else "border: 1px solid rgba(255,255,255,0.2);"
    p2_active_border = "border: 2px solid #f1c40f;" if (is_split and active_hand == 2 and not game_over) else "border: 1px solid rgba(255,255,255,0.2);"

    player_info = f"{session['user']} (${bank})"

    player_hands_display = f"""
    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; {p1_active_border} min-width: 180px;">
        <h3>{('Hand 1 - ' if is_split else '') + player_info} ({calculate_score(player_hand)} pts)</h3>
        <div>{player_cards}</div>
    </div>
    """
    if is_split:
        player_hands_display += f"""
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; {p2_active_border} min-width: 180px;">
            <h3>Hand 2 ({calculate_score(player_hand2)} pts)</h3>
            <div>{player_cards2}</div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blackjack Table</title>
        <style>
            body {{ background-color: #116235; font-family: Arial, sans-serif; color: white; text-align: center; padding: 20px; margin: 0; }}
            .card {{ width: 75px; height: 110px; background: white; color: black; border-radius: 8px; display: inline-block; margin: 5px; padding: 5px; font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }}
            .card.red {{ color: red; }}
            .card.back {{ background: #d63031; }}
            .players-container {{ display: flex; justify-content: center; align-items: flex-start; gap: 20px; flex-wrap: wrap; margin: 30px auto; max-width: 1200px; }}
        </style>
    </head>
    <body>
        {LOGO_HTML}
        {quit_btn_html}
        <h1>🃏 Blackjack Table</h1>
        <div style="background: rgba(0,0,0,0.3); display: inline-block; padding: 15px 30px; border-radius: 15px;">
            <h3>Dealer ({dealer_score_display} pts)</h3>
            <div>{dealer_cards}</div>
        </div>
        <div class="players-container">
            {bots_html}
            {player_hands_display}
        </div>
        <br>
        {action_buttons}
        {SBA_NOTICE_HTML}
    </body>
    </html>
    """

@app.route('/admin')
def admin_panel():
    if 'user' not in session or session.get('role') != 'admin':
        return f"{LOGO_HTML}<h1>Access Denied</h1><p>Admin rights required.</p><a href='/lobby'>Back to Lobby</a>"

    users_db = load_users()
    users_list = [
        {
            'username': k, 
            'password': v.get('password', '****'), 
            'bank': v.get('bank', 0)
        } for k, v in users_db.items()
    ]
    sorted_users = bubble_sort_leaderboard(users_list)

    rows = ""
    for u in sorted_users:
        rows += f"""
        <tr>
            <td style='padding:10px; border:1px solid #444;'>{u['username']}</td>
            <td style='padding:10px; border:1px solid #444;'>{u['password']}</td>
            <td style='padding:10px; border:1px solid #444;'>${u['bank']}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body {{ background-color: #0a1f12; color: white; font-family: sans-serif; text-align: center; padding: 40px; margin: 0; }}
            table {{ margin: 20px auto; border-collapse: collapse; width: 70%; background: rgba(255,255,255,0.05); border: 1px solid #2ed573; }}
            th {{ background: #d4af37; color: black; padding: 12px; font-size: 16px; }}
        </style>
    </head>
    <body>
        {LOGO_HTML}
        <h1>👑 Admin Control Panel</h1>
        <h3>User Management & Balance List</h3>
        <table>
            <tr>
                <th>Username</th>
                <th>Password</th>
                <th>Bank Balance</th>
            </tr>
            {rows}
        </table>
        <br>
        <a href="/lobby" style="color:#d4af37; text-decoration:none; font-weight:bold;">⬅ Back to Lobby</a>
        {SBA_NOTICE_HTML}
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)
import os
import random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# تأكد من وجود مكتبة socketio، إذا لم تكن موجودة لن يعمل السيرفر
try:
    from flask_socketio import SocketIO, emit, join_room
    socketio = SocketIO(async_mode='eventlet', cors_allowed_origins='*', logger=False, engineio_logger=False)
    HAS_SOCKETIO = True
except ImportError:
    print("Error: flask-socketio is not installed. Please update requirements.txt")
    HAS_SOCKETIO = False

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "dz_connect_sovereign_2025"

# --- معالجة الصوت (Audio) ---
static_path = os.path.join(app.root_path, 'static')
audio_path = os.path.join(static_path, 'audio')
if not os.path.exists(static_path): os.makedirs(static_path)
if os.path.exists(audio_path) and not os.path.isdir(audio_path): os.remove(audio_path)
if not os.path.exists(audio_path): os.makedirs(audio_path)
app.config['UPLOAD_FOLDER'] = audio_path

# --- حالة الشات واللعبة (Global State) ---
chat_history = []

# حالة اللعبة المشتركة (إذا كان SocketIO موجود)
if HAS_SOCKETIO:
    game_state = {
        "board": [],
        "deck": [],
        "hands": {},
        "turn": None,
        "players": [],
        "spectators": []
    }
else:
    game_state = {}

# --- دوال مساعدة اللعبة ---
def generate_random_deck():
    deck = []
    for i in range(7):
        for j in range(i, 7):
            deck.append({'t': i, 'b': j})
    random.shuffle(deck)
    return deck

# --- الصفحات (Routes) ---
@app.route('/')
def index(): return render_template('register.html')

@app.route('/join')
def join(): return render_template('register.html')

@app.route('/verify')
def verify(): return render_template('verify.html')

@app.route('/settings')
def settings():
    if 'temp_nick' not in session: return redirect(url_for('join'))
    return render_template('settings.html')

@app.route('/hub')
def hub():
    if 'nickname' not in session: return redirect(url_for('join'))
    return render_template('hub.html')

@app.route('/arena')
def arena():
    if 'nickname' not in session: return redirect(url_for('join'))
    return render_template('arena.html')

# --- API Auth (نفس السابق) ---
@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.get_json(silent=True)
    if not data: return jsonify({"status": "error", "message": "Bad Request"}), 400
    nick = data.get('nickname', '').strip()
    phone = data.get('phone', '').strip()
    
    clean_phone = phone.replace('+213', '').replace(' ', '')
    if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
    is_valid = len(clean_phone) == 9 and clean_phone[0] in ['5', '6', '7']
    
    if not is_valid: return jsonify({"status": "error", "message": "Invalid Algerian Number!"}), 403
    if nick.lower() == "misterai" and clean_phone != "554014890": 
        return jsonify({"status": "error", "message": "Admin Reserved!"}), 403
    
    session['temp_nick'] = nick
    session['temp_phone'] = "+213" + clean_phone
    session['v_code'] = "1234"
    return jsonify({"status": "success", "url": "/verify"})

@app.route('/api/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json(silent=True)
    if data and str(data.get('code')) == str(session.get('v_code')):
        return jsonify({"status": "success", "url": "/settings"})
    return jsonify({"status": "error", "message": "Wrong Code!"}), 400

@app.route('/api/finalize', methods=['POST'])
def finalize():
    data = request.get_json(silent=True)
    if data:
        session['nickname'] = session.get('temp_nick')
        return jsonify({"status": "success", "url": "/hub"})
    return jsonify({"status": "error", "message": "Invalid Request"}), 400

# --- API Chat (نفس السابق) ---
@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user = session.get('nickname', 'Guest')
        is_admin = (user.lower() == "misterai")
        data = request.get_json(silent=True)
        if data:
            msg = data.get('msg')
            if msg: chat_history.append({"user": user, "text": msg, "admin": is_admin, "type": "text"})
        elif 'audio' in request.files:
            audio_file = request.files['audio']
            if audio_file:
                ext = os.path.splitext(audio_file.filename)[1]
                if not ext: ext = '.webm'
                safe_user = "".join(c for c in user if c.isalnum() or c in ('_', '-'))
                filename = f"{safe_user}_{random.randint(1000, 9999)}{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                audio_file.save(save_path)
                chat_history.append({"user": user, "audio_url": f"/static/audio/{filename}", "admin": is_admin, "type": "audio"})
        if len(chat_history) > 30: chat_history.pop(0)
        return jsonify({"status": "ok"})
    return jsonify(chat_history)

# --- Socket.IO Events (Multiplayer) ---
if HAS_SOCKETIO:

    @socketio.on('connect')
    def on_connect():
        print(f"Client connected: {request.sid}")
        emit('game_state_update', game_state, to=request.sid)

    @socketio.on('join_arena')
    def on_join(data):
        username = data.get('username', 'Guest')
        join_room('arena')
        
        # Logic: First = Blue, Second = Red, Rest = Spectators
        if len(game_state['players']) < 2:
            role = "Blue" if len(game_state['players']) == 0 else "Red"
            game_state['players'].append(request.sid)
            game_state['hands'][request.sid] = []
            
            # Start game if 2 players
            if len(game_state['players']) == 2:
                game_state['deck'] = generate_random_deck()
                for p_sid in game_state['players']:
                    game_state['hands'][p_sid] = game_state['deck'][:7]
                    game_state['deck'] = game_state['deck'][7:]
                game_state['turn'] = game_state['players'][0]
                game_state['board'] = []
                
            emit('player_role', {'sid': request.sid, 'role': role})
        else:
            game_state['spectators'].append(request.sid)
            emit('player_role', {'sid': request.sid, 'role': 'Spectator'})

        emit('game_state_update', game_state, room='arena', skip_sid=request.sid)
        emit('game_state_update', game_state, to=request.sid)

    @socketio.on('play_tile')
    def on_play(data):
        if game_state['turn'] != request.sid: return

        tile_id = data.get('id') 
        # Find tile in hand
        hand = game_state['hands'][request.sid]
        
        # Simple parsing of tile_id "1-5"
        try:
            t_val = int(tile_id.split('-')[0])
            b_val = int(tile_id.split('-')[1])
            played_tile = next((t for t in hand if t['t'] == t_val and t['b'] == b_val), None)
        except:
            return

        if not played_tile: return
        
        l_val = game_state['board'][0]['tile']['t'] if game_state['board'] else None
        r_val = game_state['board'][-1]['tile']['b'] if game_state['board'] else None
        
        played = False
        if not game_state['board']:
            game_state['board'].append({'tile': played_tile, 'flipped': False})
            played = True
        elif played_tile['t'] == r_val:
            game_state['board'].append({'tile': played_tile, 'flipped': False})
            played = True
        elif played_tile['b'] == r_val:
            game_state['board'].append({'tile': played_tile, 'flipped': True})
            played = True
        elif played_tile['b'] == l_val:
            game_state['board'].insert(0, {'tile': played_tile, 'flipped': False})
            played = True
        elif played_tile['t'] == l_val:
            game_state['board'].insert(0, {'tile': played_tile, 'flipped': True})
            played = True

        if played:
            hand.remove(played_tile)
            game_state['hands'][request.sid] = hand
            
            # Switch turn
            current_idx = game_state['players'].index(request.sid)
            next_idx = (current_idx + 1) % 2
            game_state['turn'] = game_state['players'][next_idx]
            
            emit('game_state_update', game_state, room='arena')
            
            if len(hand) == 0:
                winner_role = "Blue" if current_idx == 0 else "Red"
                emit('game_over', {'winner': winner_role}, room='arena')

    @socketio.on('draw_tile')
    def on_draw():
        if game_state['turn'] != request.sid or len(game_state['deck']) == 0: return
        tile = game_state['deck'].pop()
        game_state['hands'][request.sid].append(tile)
        
        current_idx = game_state['players'].index(request.sid)
        next_idx = (current_idx + 1) % 2
        game_state['turn'] = game_state['players'][next_idx]
        
        emit('game_state_update', game_state, room='arena')

# --- Run Server ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if HAS_SOCKETIO:
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
    else:
        app.run(host='0.0.0.0', port=port, debug=True)

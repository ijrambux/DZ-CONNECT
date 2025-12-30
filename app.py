from flask import Flask, render_template, request, jsonify, session, redirect

app = Flask(__name__)
app.secret_key = "dz_connect_sovereign_2025"

chat_history = [] 

@app.route('/')
def index(): return render_template('index.html')

@app.route('/join')
def join(): return render_template('register.html')

@app.route('/verify')
def verify(): return render_template('verify.html')

@app.route('/settings')
def settings():
    if 'temp_nick' not in session: return redirect('/join')
    return render_template('settings.html')

@app.route('/hub')
def hub():
    if 'nickname' not in session: return redirect('/join')
    return render_template('hub.html')

# --- APIs ---

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    nick = data.get('nickname', '').strip()
    phone = data.get('phone', '').strip()
    
    # تنظيف وتوحيد الرقم الجزائري
    clean_phone = phone.replace('+213', '').replace(' ', '')
    if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
    
    # شرط الرقم الجزائري (9 أرقام تبدأ بـ 5، 6، أو 7)
    is_valid = len(clean_phone) == 9 and clean_phone[0] in ['5', '6', '7']
    
    if not is_valid:
        return jsonify({"status": "error", "message": "Invalid Algerian Number! Use (5/6/7)XXXXXXXX"}), 403

    # حماية اسم MisterAI (ضع رقمك الحقيقي هنا ليسمح لك وحدك بالدخول)
    if nick.lower() == "misterai" and clean_phone != "554014890": 
        return jsonify({"status": "error", "message": "Nickname 'MisterAI' is reserved for Admin!"}), 403
    
    session['temp_nick'] = nick
    session['temp_phone'] = "+213" + clean_phone
    session['v_code'] = "1234" # كود تجريبي
    return jsonify({"status": "success", "url": "/verify"})

@app.route('/api/verify_code', methods=['POST'])
def verify_code():
    if request.json.get('code') == session.get('v_code'):
        return jsonify({"status": "success", "url": "/settings"})
    return jsonify({"status": "error", "message": "Wrong Code! Use 1234"}), 400

@app.route('/api/finalize', methods=['POST'])
def finalize():
    session['nickname'] = session.get('temp_nick')
    session['bio'] = request.json.get('bio', 'Proud Algerian User')
    return jsonify({"status": "success", "url": "/hub"})

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        msg = request.json.get('msg')
        user = session.get('nickname', 'Guest')
        if msg:
            is_admin = (user.lower() == "misterai")
            chat_history.append({"user": user, "text": msg, "admin": is_admin})
            if len(chat_history) > 30: chat_history.pop(0)
            return jsonify({"status": "ok"})
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)

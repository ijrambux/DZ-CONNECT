from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "dz_sovereign_2025" # مفتاح أمان الجلسات

# مخزن مؤقت للدردشة (يُحذف عند إعادة التشغيل لضمان الخصوصية)
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join')
def join():
    return render_template('register.html')

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/settings')
def settings():
    if 'temp_nick' not in session: return redirect('/join')
    return render_template('settings.html')

@app.route('/hub')
def hub():
    if 'nickname' not in session: return redirect('/join')
    return render_template('hub.html')

# --- محركات الـ API ---

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    nick = data.get('nickname', '')
    phone = data.get('phone', '')
    
    # حماية اسمك MisterAI - لا يدخل إلا برقمك (مثال: 055...)
    if nick.lower() == "misterai" and phone != "0554014890":
        return jsonify({"status": "error", "message": "Nickname RESERVED for Admin!"}), 403
    
    session['temp_nick'] = nick
    session['temp_phone'] = phone
    session['v_code'] = "1234" # كود التحقق الافتراضي حالياً
    return jsonify({"status": "success", "url": "/verify"})

@app.route('/api/verify_code', methods=['POST'])
def verify_code():
    code = request.json.get('code')
    if code == session.get('v_code'):
        return jsonify({"status": "success", "url": "/settings"})
    return jsonify({"status": "error", "message": "Wrong Code! Try 1234"}), 400

@app.route('/api/finalize', methods=['POST'])
def finalize():
    session['nickname'] = session.get('temp_nick')
    session['bio'] = request.json.get('bio', 'Proud Algerian')
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

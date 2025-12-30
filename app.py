from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import random

app = Flask(__name__)
app.secret_key = "dz_connect_sovereign_2025"

# --- إعدادات مجلدات الصوت (تُنشأ تلقائياً لمنع خطأ 404) ---
UPLOAD_FOLDER = 'static/audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# مخزن مؤقت للدردشة
chat_history = []

# --- مسارات الصفحات (Routes) ---

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

# --- محركات الـ API والتحقق ---

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    nick = data.get('nickname', '').strip()
    phone = data.get('phone', '').strip()
    
    # تنظيف وتوحيد الرقم الجزائري (إزالة +213 والصفر الأول)
    clean_phone = phone.replace('+213', '').replace(' ', '')
    if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
    
    # شرط الرقم الجزائري (9 أرقام تبدأ بـ 5، 6، أو 7)
    is_valid = len(clean_phone) == 9 and clean_phone[0] in ['5', '6', '7']
    
    if not is_valid:
        return jsonify({"status": "error", "message": "Access Denied: Use a valid Algerian number (5/6/7)XXXXXXXX"}), 403

    # حماية اسم MisterAI (لا يدخل إلا برقمك المبرمج هنا)
    if nick.lower() == "misterai" and clean_phone != "554014890": 
        return jsonify({"status": "error", "message": "Nickname 'MisterAI' is reserved for Admin!"}), 403
    
    session['temp_nick'] = nick
    session['temp_phone'] = "+213" + clean_phone
    session['v_code'] = "1234" # كود التحقق الافتراضي حالياً
    return jsonify({"status": "success", "url": "/verify"})

@app.route('/api/verify_code', methods=['POST'])
def verify_code():
    code = request.json.get('code')
    if code == session.get('v_code'):
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
        user = session.get('nickname', 'Guest')
        is_admin = (user.lower() == "misterai")

        # معالجة الرسائل النصية
        if request.is_json:
            msg = request.json.get('msg')
            if msg:
                chat_history.append({"user": user, "text": msg, "admin": is_admin, "type": "text"})

        # معالجة الرسائل الصوتية (رفع الملفات)
        elif 'audio' in request.files:
            audio_file = request.files['audio']
            filename = f"{user}_{random.randint(1000, 9999)}.webm"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(filepath)
            chat_history.append({
                "user": user, 
                "audio_url": url_for('static', filename=f'audio/{filename}'), 
                "admin": is_admin, 
                "type": "audio"
            })

        if len(chat_history) > 30: chat_history.pop(0)
        return jsonify({"status": "ok"})
    
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)

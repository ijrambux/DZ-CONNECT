import os
import random
import shutil
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "dz_connect_sovereign_2025"

# --- إصلاح ذكي للمجلدات لمنع خطأ Not Found ---
static_path = os.path.join(app.root_path, 'static')
audio_path = os.path.join(static_path, 'audio')

# التأكد من وجود مجلد static
if not os.path.exists(static_path):
    os.makedirs(static_path)

# إذا وجد ملفاً باسم audio (كما في الصورة) بدلاً من مجلد، سيحذفه وينشئ مجلداً
if os.path.exists(audio_path) and not os.path.isdir(audio_path):
    os.remove(audio_path)

if not os.path.exists(audio_path):
    os.makedirs(audio_path)

app.config['UPLOAD_FOLDER'] = audio_path

chat_history = []

# --- مسارات الصفحات ---
@app.route('/')
def index(): return render_template('index.html')

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

# --- محرك الدردشة والصوت ---
@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user = session.get('nickname', 'Guest')
        is_admin = (user.lower() == "misterai")
        
        if 'audio' in request.files:
            audio_file = request.files['audio']
            filename = f"{user}_{random.randint(1000, 9999)}.webm"
            audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            chat_history.append({"user": user, "audio_url": f"/static/audio/{filename}", "admin": is_admin, "type": "audio"})
        
        elif request.is_json:
            msg = request.json.get('msg')
            if msg: chat_history.append({"user": user, "text": msg, "admin": is_admin, "type": "text"})
        
        if len(chat_history) > 50: chat_history.pop(0)
        return jsonify({"status": "ok"})
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)

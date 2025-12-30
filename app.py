from flask import Flask, render_template, request, jsonify, session, redirect
import random
import os # لإدارة الملفات الصوتية

app = Flask(__name__)
app.secret_key = "dz_connect_sovereign_2025"

chat_history = []
# مجلد لحفظ التسجيلات الصوتية مؤقتاً
UPLOAD_FOLDER = 'static/audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- (بقية المسارات كما هي: index, join, verify, settings, hub) ---

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user = session.get('nickname', 'Guest')
        is_admin = (user.lower() == "misterai")

        if 'msg' in request.json: # رسالة نصية عادية
            msg = request.json.get('msg')
            if msg: chat_history.append({"user": user, "text": msg, "admin": is_admin, "type": "text"})

        elif 'audio' in request.files: # رسالة صوتية
            audio_file = request.files['audio']
            filename = f"{user}_{random.randint(1000,9999)}.webm" # اسم فريد للملف
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(filepath)
            chat_history.append({"user": user, "audio_url": url_for('static', filename=f'audio/{filename}'), "admin": is_admin, "type": "audio"})

        if len(chat_history) > 30: chat_history.pop(0)
        return jsonify({"status": "ok"})
        
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)

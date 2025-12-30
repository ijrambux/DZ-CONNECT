from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "misterai_secure_v1" # مفتاح الأمان للجلسات

# بيانات تجريبية (سيتم حذف الرسائل عند إعادة التشغيل ليبقى السيرفر خفيفاً)
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join')
def join():
    return render_template('register.html')

@app.route('/hub')
def hub():
    if 'user_phone' not in session:
        return redirect(url_for('join'))
    return render_template('hub.html')

@app.route('/api/auth', methods=['POST'])
def authenticate():
    data = request.json
    phone = data.get('phone')
    if phone and len(phone) >= 10:
        session['user_phone'] = phone
        return jsonify({"status": "success", "url": "/hub"})
    return jsonify({"status": "failed", "message": "Invalid Phone"}), 400

@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        msg = request.json.get('text')
        if msg and 'user_phone' in session:
            chat_history.append({"sender": session['user_phone'], "body": msg})
            if len(chat_history) > 30: chat_history.pop(0) # حذف الرسائل القديمة تلقائياً
            return jsonify({"status": "sent"})
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)

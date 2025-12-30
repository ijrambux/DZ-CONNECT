from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "dz_connect_secret_key" # مفتاح الأمان للجلسات

# قواعد بيانات مؤقتة في الذاكرة
users = {} # تخزين المستخدمين: {phone: password}
chat_messages = [] # تخزين رسائل الدردشة الجماعية

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join')
def join():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    if phone and password:
        users[phone] = password
        session['user'] = phone
        return jsonify({"status": "success", "redirect": "/forum"})
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/forum')
def forum():
    if 'user' not in session:
        return redirect(url_for('join'))
    return render_template('forum.html')

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        msg = request.json.get('message')
        if msg and 'user' in session:
            chat_messages.append({"user": session['user'], "text": msg})
            return jsonify({"status": "success"})
    return jsonify(chat_messages)

if __name__ == '__main__':
    app.run(debug=True)

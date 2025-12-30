from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "dz_connect_sovereign_key"

# Database for English Forum & Chat
users_db = {} 
global_chat = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join')
def join():
    return render_template('register.html')

@app.route('/api/auth', methods=['POST'])
def authenticate():
    data = request.json
    phone = data.get('phone')
    if phone:
        session['user_phone'] = phone
        users_db[phone] = True
        return jsonify({"status": "success", "url": "/hub"})
    return jsonify({"status": "failed"}), 400

@app.route('/hub')
def hub():
    if 'user_phone' not in session:
        return redirect(url_for('join'))
    return render_template('hub.html')

@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        msg = request.json.get('text')
        if msg and 'user_phone' in session:
            global_chat.append({"sender": session['user_phone'], "body": msg})
            if len(global_chat) > 50: global_chat.pop(0) # Keep chat fresh
            return jsonify({"status": "sent"})
    return jsonify(global_chat)

if __name__ == '__main__':
    app.run(debug=True)

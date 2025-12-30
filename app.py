from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html') # الصفحة الرئيسية الجديدة

@app.route('/join')
def join():
    return render_template('register.html') # صفحة التسجيل

@app.route('/community')
def community():
    return render_template('community.html') # منصة المجتمع

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    phone = data.get('phone')
    if phone and phone.startswith(('05', '06', '07')) and len(phone) == 10:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "الرقم غير صحيح"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

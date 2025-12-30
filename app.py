from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

app = Flask(__name__)

# قاعدة بيانات وهمية (لأغراض التجربة)
users = {}

@app.route('/')
def home_page():
    # الصفحة الرئيسية (Landing Page) التي ترحب بالزوار
    return render_template('index.html')

@app.route('/register')
def register_page():
    # صفحة التسجيل التي صممناها
    return render_template('register.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    phone = data.get('phone')
    password = data.get('password') # الآن نستقبل كلمة السر أيضاً

    if not phone or not phone.startswith(('05', '06', '07')) or len(phone) != 10:
        return jsonify({"status": "error", "message": "عذراً! يجب إدخال رقم هاتف جزائري صحيح (05/06/07)."})
    
    if len(password) < 6:
        return jsonify({"status": "error", "message": "كلمة السر يجب أن تكون 6 أحرف على الأقل."})

    if phone in users:
        return jsonify({"status": "error", "message": "هذا الرقم مسجل بالفعل!"})

    users[phone] = {"password": password, "status": "active"}
    print(f"User {phone} registered.")
    
    # بعد التسجيل الناجح، نرسل إشارة للتحويل
    return jsonify({"status": "success", "message": "تم تسجيلك بنجاح!"})

@app.route('/community')
def community_page():
    # صفحة المجتمع التي سيدخلها الأعضاء المسجلون
    return render_template('community.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    # فتح واجهة DZ-CONNECT الاحترافية
    return render_template('register.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    phone = data.get('phone')
    
    # التحقق من أن الرقم جزائري (05/06/07) ويتكون من 10 أرقام
    if not phone or not phone.startswith(('05', '06', '07')) or len(phone) != 10:
        return jsonify({"status": "error", "message": "عذراً! يجب إدخال رقم هاتف جزائري صحيح"}), 400
    
    return jsonify({"status": "success", "message": "تم تسجيلك بنجاح في مجتمع DZ-CONNECT!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

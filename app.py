from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# قاعدة بيانات مؤقتة لتخزين منشورات الساحة (تختفي عند إعادة تشغيل السيرفر)
# أضفنا منشورك الأول كترحيب رسمي
posts_db = [
    {
        "user": "MisterAI", 
        "content": "مرحباً بكم في 🅓🅩-🅒🅞🅝🅝🅔🅒🅣.. هذه هي بذرة مشروعنا السيادي للجزائر 🇩🇿.", 
        "likes": 10
    }
]

# 1. الصفحة الرئيسية (Landing Page)
@app.route('/')
def index():
    return render_template('index.html')

# 2. صفحة الانضمام / التسجيل (التي كانت تظهر Not Found)
@app.route('/join')
def join():
    return render_template('register.html')

# 3. صفحة ساحة المجتمع (Feed)
@app.route('/community')
def community():
    return render_template('community.html')

# 4. محرك الـ API لإدارة المنشورات (الإرسال والاستقبال)
@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.json
        if data and data.get('content'):
            new_post = {
                "user": "عضو جديد", # يمكنك تطويرها لاحقاً لتأخذ اسم المستخدم الحقيقي
                "content": data.get('content'),
                "likes": 0
            }
            # إضافة المنشور الجديد في بداية القائمة ليظهر في الأعلى
            posts_db.insert(0, new_post)
            return jsonify({"status": "success", "message": "تم النشر بنجاح"}), 201
        return jsonify({"status": "error", "message": "المحتوى فارغ"}), 400
    
    # عند طلب GET يتم إرسال كل المنشورات المخزنة
    return jsonify(posts_db)

# تشغيل التطبيق
if __name__ == '__main__':
    # ملاحظة: عند الرفع على Render، السيرفر يستخدم Gunicorn تلقائياً
    app.run(debug=True)

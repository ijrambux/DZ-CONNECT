from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# تخزين المنشورات في الذاكرة (للتجربة الحقيقية)
posts_db = [
    {"user": "MisterAI", "content": "مرحباً بكم في فضاء السيادة الرقمية 🇩🇿. نحن نبني المستقبل معاً.", "likes": 12}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.json
        if data.get('content'):
            new_post = {
                "user": "عضو مؤسس",
                "content": data.get('content'),
                "likes": 0
            }
            posts_db.insert(0, new_post)
            return jsonify({"status": "success"})
    return jsonify(posts_db)

if __name__ == '__main__':
    app.run(debug=True)

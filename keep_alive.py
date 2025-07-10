from flask import Flask, request, render_template_string
from threading import Thread
import json
import os

app = Flask('')

# HTML-шаблон для веб-интерфейса
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Управление промокодами</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        form { margin-bottom: 20px; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        ul { list-style: none; padding: 0; }
        li { padding: 10px; border: 1px solid #ddd; margin-bottom: 10px; }
        .delete-btn { background: #dc3545; }
        .delete-btn:hover { background: #c82333; }
        .note { color: #555; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Управление промокодами</h1>
    <form method="POST" action="/admin">
        <input type="text" name="keyword" placeholder="Ключевое слово" required>
        <input type="text" name="path" placeholder="Путь к файлу или URL (например, https://example.com/image.png)">
        <p class="note">Оставьте путь пустым для ответа только текстом. Используйте URL для изображений или файлов.</p>
        <textarea name="caption" placeholder="Текст ответа" required></textarea>
        <button type="submit">Добавить промокод</button>
    </form>
    <h2>Текущие промокоды</h2>
    <ul>
        {% for keyword, data in keywords.items() %}
        <li>
            <strong>{{ keyword }}</strong>: {{ data.caption }} (Файл/URL: {{ data.path or 'Нет' }})
            <form method="POST" action="/admin/delete" style="display:inline;">
                <input type="hidden" name="keyword" value="{{ keyword }}">
                <button class="delete-btn" type="submit">Удалить</button>
            </form>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
'''

@app.route('/')
def home():
    return "Я жив!"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    keywords = load_keywords()
    if request.method == 'POST':
        keyword = request.form['keyword'].lower().strip()
        path = request.form['path'].strip() or None
        caption = request.form['caption'].strip()
        keywords[keyword] = {'path': path, 'caption': caption}
        save_keywords(keywords)
    return render_template_string(ADMIN_TEMPLATE, keywords=keywords)

@app.route('/admin/delete', methods=['POST'])
def delete_keyword():
    keywords = load_keywords()
    keyword = request.form['keyword']
    if keyword in keywords:
        del keywords[keyword]
        save_keywords(keywords)
    return render_template_string(ADMIN_TEMPLATE, keywords=keywords)

def load_keywords():
    try:
        with open('keywords.json', 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_keywords(keywords):
    with open('keywords.json', 'w') as f:
        json.dump(keywords, f, ensure_ascii=False, indent=2)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

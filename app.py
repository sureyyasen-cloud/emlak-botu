import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Gelen ilanları hafızada tutacak liste
ilanlar = []

HTML_LAYOUT = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Emlak İlan Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        h1 { color: #1a252f; margin: 0 0 10px 0; text-align: center; }
        .status-container { text-align: center; margin-bottom: 20px; }
        .status { background: #27ae60; color: white; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: bold; }
        .ilan-card { border-left: 5px solid #25d366; background: #fff; padding: 15px; margin-top: 15px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
        .ilan-text { white-space: pre-wrap; word-break: break-word; font-size: 14px; color: #334155; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🏢 WhatsApp Emlak İlan Paneli</h1>
            <div class="status-container"><span class="status">● Canlı Akış Aktif</span></div>
        </div>

        <div class="card">
            <h3>🔍 Gelen Emlak İlanları</h3>
            {% if ilanlar %}
                {% for ilan in ilanlar[::-1] %}
                    <div class="ilan-card">
                        <div class="ilan-text">{{ ilan }}</div>
                    </div>
                {% endfor %}
            {% else %}
                <p style="color: #64748b; text-align: center;"><i>Henüz filtreye uygun ilan düşmedi. Mesajlar geldikçe burada otomatik listelenecektir.</i></p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT, ilanlar=ilanlar)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if data and 'message' in data:
            ilanlar.append(data['message'])
            return jsonify({"status": "success"}), 200
    except Exception as e:
        print("Hata:", e)
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

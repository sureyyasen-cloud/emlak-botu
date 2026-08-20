from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emlak İlan Filtreleme Paneli</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; text-align: center; }
        .card { background: white; max-width: 600px; margin: 20px auto; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .filter-box { background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>🏢 WhatsApp Emlak İlan Paneli</h1>
    
    <div class="card">
        <h3>📲 WhatsApp Bağlantı Durumu</h3>
        <p>WhatsApp grubundaki gelen ilanları otomatik filtrelemek için oturum açın.</p>
        <div style="background: #e9ecef; padding: 40px; border-radius: 8px; border: 2px dashed #ccc; margin: 15px 0;">
            <p><strong>QR KOD HAZIRLANIYOR...</strong></p>
            <small>Canlı WhatsApp köprüsü entegre ediliyor.</small>
        </div>
    </div>

    <div class="card filter-box">
        <h3>🔍 İlan Filtreleme</h3>
        <p>Gelen ilanlar Sahibinden formatında buraya düşecektir.</p>
        <p><i>Henüz kaydedilmiş ilan bulunmuyor.</i></p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

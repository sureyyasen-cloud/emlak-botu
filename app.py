from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

ilanlar = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emlak Portföy Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #27ae60; word-break: break-word; }
        .card.opsiyon { border-left-color: #e67e22; }
        .price { font-size: 1.2em; font-weight: bold; color: #2c3e50; margin: 8px 0; }
        .badge { background: #27ae60; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; float: right; }
        .badge.opsiyon { background: #e67e22; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 Emlak Portföy Paneli <span style="font-size:0.5em; background:#27ae60; padding:4px 8px; border-radius:12px;">● CANLI YAYIN</span></h1>
    </div>
    <div class="grid" id="ilan-container">
        {% for ilan in ilanlar %}
        <div class="card {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}">
            <span class="badge {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}">{{ ilan.durum }}</span>
            <h3 style="margin:0;">{{ ilan.baslik }}</h3>
            <p class="price">{{ ilan.fiyat }}</p>
            <p style="color: #555;">💬 {{ ilan.detay }}</p>
            <small style="color: #888;">🕒 {{ ilan.tarih }}</small>
        </div>
        {% else %}
        <p style="text-align:center; width:100%; color:#7f8c8d;">Henüz kaydedilmiş ilan bulunmuyor. WhatsApp'tan mesaj geldikçe burası güncellenecektir.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, ilanlar=ilanlar)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    data = request.get_json(force=True, silent=True)
    if data:
        ilanlar.insert(0, {
            "baslik": str(data.get('baslik', 'Emlak Grubu')),
            "fiyat": str(data.get('fiyat', 'Fiyat Belirtilmedi')),
            "detay": str(data.get('detay', '')),
            "durum": str(data.get('durum', 'Satışta')),
            "tarih": str(data.get('tarih', ''))
        })
        # Son 50 ilanı hafızada tut
        if len(ilanlar) > 50:
            ilanlar.pop()
        return jsonify({"status": "success", "count": len(ilanlar)}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

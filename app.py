import os
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

ilanlar = []

def ilan_ayristir(metin):
    oda = re.search(r'\b\d\+\d\b', metin)
    oda_str = oda.group(0) if oda else "Oda Belirtilmedi"
    
    fiyat = re.search(r'(\d[\d\.\,\s]*)\s*(TL|tl|bin|milyon|Bin|Milyon)', metin)
    fiyat_str = fiyat.group(0) if fiyat else "Fiyat Belirtilmedi"
    
    return {
        "id": len(ilanlar) + 1,
        "ham_metin": metin,
        "oda": oda_str,
        "fiyat": fiyat_str
    }

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emlak Portföy Paneli</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #f4f6f9; margin: 0; padding: 20px; }
        .header { background: #ffe800; color: #111; padding: 18px 25px; border-radius: 10px; font-weight: bold; font-size: 22px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; margin-top: 25px; }
        .card { background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); padding: 20px; border-top: 5px solid #27ae60; position: relative; display: flex; flex-direction: column; justify-content: space-between; }
        .badges { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .badge-oda { background: #e74c3c; color: white; padding: 5px 10px; border-radius: 6px; font-size: 13px; font-weight: bold; }
        .badge-fiyat { background: #27ae60; color: white; padding: 5px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; }
        .metin { font-size: 14px; color: #2c3e50; line-height: 1.6; white-space: pre-wrap; word-break: break-word; background: #f8f9fa; padding: 12px; border-radius: 6px; border: 1px solid #edf2f7; }
        .empty { text-align: center; color: #7f8c8d; font-size: 16px; margin-top: 50px; font-weight: 500; }
    </style>
</head>
<body>
    <div class="header">
        <span>🏠 Emlak Portföy Paneli</span>
        <span style="font-size:13px; background:#fff; color:#27ae60; padding:6px 12px; border-radius:20px; font-weight:bold;">● CANLI YAYIN</span>
    </div>

    {% if ilanlar %}
    <div class="grid">
        {% for item in ilanlar[::-1] %}
        <div class="card">
            <div class="badges">
                <span class="badge-oda">{{ item.oda }}</span>
                <span class="badge-fiyat">{{ item.fiyat }}</span>
            </div>
            <div class="metin">{{ item.ham_metin }}</div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="empty">Henüz aktif ilan bulunmuyor. WhatsApp'tan gelen mesajlar burada ilan kartına dönüşecektir.</div>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, ilanlar=ilanlar)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    islem = data.get('islem', 'ekle')
    metin = data.get('message', '')

    if islem == 'ekle' and metin:
        ilanlar.append(ilan_ayristir(metin))
        return jsonify({"status": "eklendi"}), 200
    
    elif islem == 'sil' and metin:
        global ilanlar
        ilanlar = [i for i in ilanlar if metin.lower() not in i['ham_metin'].lower()]
        return jsonify({"status": "silindi"}), 200

    return jsonify({"status": "gecersiz"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

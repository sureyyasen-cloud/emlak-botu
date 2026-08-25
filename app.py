from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Sınırsız İlan Veritabanı (Hafızada tutulur)
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
        .header { background: #1e293b; color: white; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .controls { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; gap: 10px; flex-wrap: wrap; }
        .controls input, .controls select { padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; flex: 1; min-width: 180px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #10b981; word-break: break-word; position: relative; display: flex; flex-direction: column; justify-content: space-between; }
        .card.opsiyon { border-left-color: #f59e0b; }
        .card-header { font-size: 0.85em; color: #64748b; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
        .price { font-size: 1.25em; font-weight: bold; color: #0f172a; margin: 5px 0 10px 0; }
        .sender-info { background: #f8fafc; padding: 8px; border-radius: 6px; font-size: 0.85em; color: #334155; margin-bottom: 10px; line-height: 1.5; }
        .badge { background: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75em; position: absolute; top: 15px; right: 15px; }
        .badge.opsiyon { background: #f59e0b; }
        .video-btn { background: #2563eb; color: white; text-align: center; padding: 8px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 10px; display: block; font-size: 0.9em; }
        .video-btn:hover { background: #1d4ed8; }
        .footer-info { display: flex; justify-content: space-between; font-size: 0.75em; color: #94a3b8; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">🏠 Canlı Emlak Portföy & Filtreleme Paneli</h2>
    </div>

    <!-- GELİŞMİŞ FİLTRELEME ALANI -->
    <div class="controls">
        <input type="text" id="searchInput" onkeyup="filterCards()" placeholder="İlan detayında ara (örn: 2+1, Daire, Esenyurt)...">
        <input type="text" id="phoneInput" onkeyup="filterCards()" placeholder="Telefon veya Kişi ismi ara...">
        <select id="statusFilter" onchange="filterCards()">
            <option value="">Tüm Durumlar</option>
            <option value="Satışta">Satışta</option>
            <option value="Opsiyonlandı">Opsiyonlandı</option>
            <option value="Kiralık">Kiralık</option>
        </select>
    </div>

    <div class="grid" id="ilan-container">
        {% for ilan in ilanlar %}
        <div class="card {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}" 
             data-detay="{{ ilan.detay.lower() }}" 
             data-gonderen="{{ ilan.gonderen_tel.lower() }} {{ ilan.gonderen_adi.lower() }}" 
             data-durum="{{ ilan.durum }}">
            <div>
                <span class="badge {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}">{{ ilan.durum }}</span>
                <div class="card-header">📌 {{ ilan.grup_adi }}</div>
                <div class="price">{{ ilan.fiyat }}</div>
                
                <div class="sender-info">
                    👤 <b>Gönderen:</b> {{ ilan.gonderen_adi }}<br>
                    📞 <b>Tel:</b> <a href="https://wa.me/{{ ilan.gonderen_tel }}" target="_blank" style="color:#2563eb;">+{{ ilan.gonderen_tel }}</a>
                </div>

                <p style="color: #475569; font-size: 0.9em; line-height: 1.4;">{{ ilan.detay }}</p>
            </div>

            <div>
                {% if ilan.has_media %}
                <a href="https://web.whatsapp.com" target="_blank" class="video-btn">🎥 İlan Medyasını / Videosunu Gör</a>
                {% endif %}
                <div class="footer-info">
                    <span>🕒 {{ ilan.tarih }}</span>
                    <span>ID: #{{ loop.index }}</span>
                </div>
            </div>
        </div>
        {% else %}
        <p style="text-align:center; width:100%; color:#64748b;">Henüz kaydedilmiş ilan bulunmuyor. Bot çalıştıkça tüm ilanlar buraya akacaktır.</p>
        {% endfor %}
    </div>

    <script>
        function filterCards() {
            let search = document.getElementById('searchInput').value.toLowerCase();
            let phone = document.getElementById('phoneInput').value.toLowerCase();
            let status = document.getElementById('statusFilter').value;
            let cards = document.getElementsByClassName('card');

            for (let card of cards) {
                let cardDetay = card.getAttribute('data-detay') || '';
                let cardGonderen = card.getAttribute('data-gonderen') || '';
                let cardDurum = card.getAttribute('data-durum') || '';

                let matchesSearch = cardDetay.includes(search);
                let matchesPhone = cardGonderen.includes(phone);
                let matchesStatus = status === "" || cardDurum === status;

                if (matchesSearch && matchesPhone && matchesStatus) {
                    card.style.display = "flex";
                } else {
                    card.style.display = "none";
                }
            }
        }
    </script>
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
            "grup_adi": str(data.get('grup_adi', 'Emlak Grubu')),
            "gonderen_adi": str(data.get('gonderen_adi', 'Bilinmiyor')),
            "gonderen_tel": str(data.get('gonderen_tel', '')),
            "fiyat": str(data.get('fiyat', 'Fiyat Belirtilmedi')),
            "detay": str(data.get('detay', '')),
            "durum": str(data.get('durum', 'Satışta')),
            "has_media": bool(data.get('has_media', False)),
            "tarih": str(data.get('tarih', ''))
        })
        # Herhangi bir limit bulunmuyor, tüm ilanlar sınırsız eklenir.
        return jsonify({"status": "success", "count": len(ilanlar)}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

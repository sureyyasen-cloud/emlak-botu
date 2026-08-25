from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

ilanlar = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emlak Portföy & Filtre Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }
        .header { background: #1e293b; color: white; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .controls { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
        .controls input, .controls select { padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; flex: 1; min-width: 140px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #10b981; word-break: break-word; display: flex; flex-direction: column; justify-content: space-between; }
        .card.opsiyon { border-left-color: #f59e0b; }
        .card-header { font-size: 0.85em; color: #0284c7; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; background: #e0f2fe; padding: 4px 8px; border-radius: 4px; display: inline-block; }
        .price { font-size: 1.3em; font-weight: bold; color: #0f172a; margin: 8px 0; }
        .sender-info { background: #f8fafc; padding: 8px; border-radius: 6px; font-size: 0.85em; color: #334155; margin-bottom: 10px; line-height: 1.5; border: 1px solid #e2e8f0; }
        .badge { background: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75em; float: right; }
        .badge.opsiyon { background: #f59e0b; }
        .media-container { margin-top: 10px; text-align: center; background: #000; border-radius: 6px; overflow: hidden; }
        .media-container img, .media-container video { max-width: 100%; max-height: 250px; display: block; margin: 0 auto; }
        .footer-info { display: flex; justify-content: space-between; font-size: 0.75em; color: #94a3b8; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">🏠 Gelişmiş Emlak Portföy Paneli</h2>
    </div>

    <!-- GELİŞMİŞ SEÇENEKLİ FİLTRE ALANI -->
    <div class="controls">
        <input type="text" id="searchInput" onkeyup="filterCards()" placeholder="Kelime / Konum Ara (örn: Bahçe Katı, Esenyurt)...">
        <input type="text" id="phoneInput" onkeyup="filterCards()" placeholder="Telefon / İsim...">
        
        <select id="odaFilter" onchange="filterCards()">
            <option value="">Tüm Oda Sayıları</option>
            <option value="1+1">1+1</option>
            <option value="2+1">2+1</option>
            <option value="3+1">3+1</option>
            <option value="4+1">4+1</option>
            <option value="4+2">4+2</option>
        </select>

        <select id="statusFilter" onchange="filterCards()">
            <option value="">Tüm Durumlar</option>
            <option value="Satışta">Satışta</option>
            <option value="Opsiyonlandı">Opsiyonlandı</option>
            <option value="Kiralık">Kiralık</option>
        </select>

        <input type="number" id="minPrice" onkeyup="filterCards()" placeholder="Min TL">
        <input type="number" id="maxPrice" onkeyup="filterCards()" placeholder="Max TL">
    </div>

    <div class="grid" id="ilan-container">
        {% for ilan in ilanlar %}
        <div class="card {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}" 
             data-detay="{{ ilan.detay.lower() }}" 
             data-gonderen="{{ ilan.gonderen_tel }} {{ ilan.gonderen_adi.lower() }}" 
             data-durum="{{ ilan.durum }}"
             data-fiyat="{{ ilan.fiyat_raw }}">
            <div>
                <span class="badge {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}">{{ ilan.durum }}</span>
                <div class="card-header">👥 {{ ilan.grup_adi }}</div>
                <div class="price">{{ ilan.fiyat }}</div>
                
                <div class="sender-info">
                    👤 <b>Gönderen:</b> {{ ilan.gonderen_adi }}<br>
                    📞 <b>Tel:</b> <a href="https://wa.me/{{ ilan.gonderen_tel }}" target="_blank" style="color:#2563eb; font-weight:bold;">{{ ilan.gonderen_tel_formatlı }}</a>
                </div>

                <p style="color: #475569; font-size: 0.9em; line-height: 1.4; white-space: pre-line;">{{ ilan.detay }}</p>
            </div>

            <div>
                {% if ilan.media_data %}
                <div class="media-container">
                    {% if 'video' in ilan.media_mimetype %}
                    <video controls src="data:{{ ilan.media_mimetype }};base64,{{ ilan.media_data }}"></video>
                    {% else %}
                    <img src="data:{{ ilan.media_mimetype }};base64,{{ ilan.media_data }}" alt="İlan Görseli">
                    {% endif %}
                </div>
                {% endif %}
                <div class="footer-info">
                    <span>🕒 {{ ilan.tarih }}</span>
                    <span>ID: #{{ loop.index }}</span>
                </div>
            </div>
        </div>
        {% else %}
        <p style="text-align:center; width:100%; color:#64748b;">Henüz ilan bulunmuyor. Bot çalıştıkça ilanlar görselleriyle buraya akacaktır.</p>
        {% endfor %}
    </div>

    <script>
        function filterCards() {
            let search = document.getElementById('searchInput').value.toLowerCase();
            let phone = document.getElementById('phoneInput').value.toLowerCase();
            let oda = document.getElementById('odaFilter').value.toLowerCase();
            let status = document.getElementById('statusFilter').value;
            let minP = parseFloat(document.getElementById('minPrice').value) || 0;
            let maxP = parseFloat(document.getElementById('maxPrice').value) || Infinity;

            let cards = document.getElementsByClassName('card');

            for (let card of cards) {
                let cardDetay = card.getAttribute('data-detay') || '';
                let cardGonderen = card.getAttribute('data-gonderen') || '';
                let cardDurum = card.getAttribute('data-durum') || '';
                let cardFiyat = parseFloat(card.getAttribute('data-fiyat')) || 0;

                let matchesSearch = cardDetay.includes(search);
                let matchesPhone = cardGonderen.includes(phone);
                let matchesOda = oda === "" || cardDetay.includes(oda);
                let matchesStatus = status === "" || cardDurum === status;
                let matchesPrice = (cardFiyat === 0) || (cardFiyat >= minP && cardFiyat <= maxP);

                if (matchesSearch && matchesPhone && matchesOda && matchesStatus && matchesPrice) {
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
            "gonderen_adi": str(data.get('gonderen_adi', 'Emlak Danışmanı')),
            "gonderen_tel": str(data.get('gonderen_tel', '')),
            "gonderen_tel_formatlı": str(data.get('gonderen_tel_formatlı', '')),
            "fiyat": str(data.get('fiyat', 'Fiyat Belirtilmedi')),
            "fiyat_raw": data.get('fiyat_raw', 0),
            "detay": str(data.get('detay', '')),
            "durum": str(data.get('durum', 'Satışta')),
            "media_data": data.get('media_data', None),
            "media_mimetype": data.get('media_mimetype', ''),
            "tarih": str(data.get('tarih', ''))
        })
        return jsonify({"status": "success", "count": len(ilanlar)}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

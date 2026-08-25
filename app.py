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
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }
        .header { background: #0f172a; color: white; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .controls { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
        .controls input, .controls select { padding: 9px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9em; width: 100%; box-sizing: border-box; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #10b981; word-break: break-word; display: flex; flex-direction: column; justify-content: space-between; }
        .card.opsiyon { border-left-color: #f59e0b; }
        .card-header { font-size: 0.85em; color: #0369a1; font-weight: bold; margin-bottom: 8px; background: #e0f2fe; padding: 4px 8px; border-radius: 4px; display: inline-block; }
        .price { font-size: 1.3em; font-weight: bold; color: #0f172a; margin: 5px 0; }
        .sender-info { background: #f8fafc; padding: 8px; border-radius: 6px; font-size: 0.85em; color: #334155; margin-bottom: 10px; border: 1px solid #e2e8f0; }
        .badge { background: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75em; float: right; }
        .badge.opsiyon { background: #f59e0b; }
        .media-container { margin-top: 10px; text-align: center; background: #000; border-radius: 6px; overflow: hidden; }
        .media-container img, .media-container video { width: 100%; max-height: 250px; display: block; object-fit: contain; }
        .footer-info { display: flex; justify-content: space-between; font-size: 0.75em; color: #94a3b8; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">🏠 Emlak Portföyü ve Detaylı Filtreleme Paneli</h2>
    </div>

    <div class="controls">
        <input type="text" id="searchInput" onkeyup="filterCards()" placeholder="Genel Arama...">
        <input type="text" id="konumInput" onkeyup="filterCards()" placeholder="İl / İlçe / Mahalle / Sokak...">
        <input type="text" id="phoneInput" onkeyup="filterCards()" placeholder="Telefon / Danışman Adı...">
        
        <select id="odaFilter" onchange="filterCards()">
            <option value="">Tüm Oda Sayıları</option>
            <option value="1+1">1+1</option>
            <option value="2+1">2+1</option>
            <option value="3+1">3+1</option>
            <option value="4+1">4+1</option>
            <option value="4+2">4+2</option>
            <option value="dublex">Dublex</option>
        </select>

        <select id="tapuFilter" onchange="filterCards()">
            <option value="">Tapu / İskan Durumu</option>
            <option value="kat mülkiyeti">Kat Mülkiyeti</option>
            <option value="kat irtifakı">Kat İrtifakı</option>
            <option value="iskanli">İskanlı</option>
            <option value="iskan">İskan</option>
        </select>

        <select id="rayicFilter" onchange="filterCards()">
            <option value="">Rayiç Durumu</option>
            <option value="sınırsız">Rayiç Sınırsız</option>
            <option value="rayiç">Rayiç Limitli</option>
        </select>

        <select id="statusFilter" onchange="filterCards()">
            <option value="">Tüm Durumlar</option>
            <option value="Satışta">Satışta</option>
            <option value="Opsiyonlandı">Opsiyonlandı</option>
            <option value="Kiralık">Kiralık</option>
        </select>

        <input type="number" id="minPrice" onkeyup="filterCards()" placeholder="Min Fiyat (TL)">
        <input type="number" id="maxPrice" onkeyup="filterCards()" placeholder="Max Fiyat (TL)">
    </div>

    <div class="grid" id="ilan-container">
        {% for ilan in ilanlar %}
        <div class="card {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}" 
             data-detay="{{ ilan.detay_normalized }}" 
             data-gonderen="{{ ilan.gonderen_tel }} {{ ilan.gonderen_adi_normalized }}" 
             data-durum="{{ ilan.durum }}"
             data-fiyat="{{ ilan.fiyat_raw }}">
            <div>
                <span class="badge {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}">{{ ilan.durum }}</span>
                <div class="card-header">📢 {{ ilan.grup_adi }}</div>
                <div class="price">{{ ilan.fiyat }}</div>
                
                <div class="sender-info">
                    👤 <b>Gönderen:</b> {{ ilan.gonderen_adi }}<br>
                    📞 <b>Tel:</b> <a href="https://wa.me/{{ ilan.gonderen_tel }}" target="_blank" style="color:#2563eb; font-weight:bold;">{{ ilan.gonderen_tel_formatli }}</a>
                </div>

                <p style="color: #334155; font-size: 0.9em; line-height: 1.45; white-space: pre-line;">{{ ilan.detay }}</p>
            </div>

            <div>
                {% if ilan.media_data %}
                <div class="media-container">
                    {% if 'video' in ilan.media_mimetype %}
                    <video controls src="data:{{ ilan.media_mimetype }};base64,{{ ilan.media_data }}"></video>
                    {% else %}
                    <img src="data:{{ ilan.media_mimetype }};base64,{{ ilan.media_data }}" alt="İlan Medyası">
                    {% endif %}
                </div>
                {% endif %}
                <div class="footer-info">
                    <span>🕒 {{ ilan.tarih }}</span>
                    <span>İlan ID: #{{ loop.index }}</span>
                </div>
            </div>
        </div>
        {% else %}
        <p style="text-align:center; width:100%; color:#64748b;">Henüz ilan yok.</p>
        {% endfor %}
    </div>

    <script>
        // Türkçe Karakterleri Normalleştirme Fonksiyonu
        function normalizeTR(text) {
            if (!text) return "";
            return text.toString().toLowerCase()
                .replace(/ğ/g, "g")
                .replace(/ü/g, "u")
                .replace(/ş/g, "s")
                .replace(/ı/g, "i")
                .replace(/ö/g, "o")
                .replace(/ç/g, "c")
                .replace(/İ/g, "i")
                .replace(/I/g, "i");
        }

        function filterCards() {
            let search = normalizeTR(document.getElementById('searchInput').value);
            let konum = normalizeTR(document.getElementById('konumInput').value);
            let phone = normalizeTR(document.getElementById('phoneInput').value);
            let oda = normalizeTR(document.getElementById('odaFilter').value);
            let tapu = normalizeTR(document.getElementById('tapuFilter').value);
            let rayic = normalizeTR(document.getElementById('rayicFilter').value);
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
                let matchesKonum = cardDetay.includes(konum);
                let matchesPhone = cardGonderen.includes(phone);
                let matchesOda = oda === "" || cardDetay.includes(oda);
                let matchesTapu = tapu === "" || cardDetay.includes(tapu);
                let matchesRayic = rayic === "" || cardDetay.includes(rayic);
                let matchesStatus = status === "" || cardDurum === status;
                let matchesPrice = (cardFiyat === 0) || (cardFiyat >= minP && cardFiyat <= maxP);

                if (matchesSearch && matchesKonum && matchesPhone && matchesOda && matchesTapu && matchesRayic && matchesStatus && matchesPrice) {
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

def tr_normalize(text):
    if not text:
        return ""
    mapping = str.maketrans("ÇĞIİÖŞÜçğıöşü", "cgiosucgiosu")
    return text.translate(mapping).lower()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, ilanlar=ilanlar)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    data = request.get_json(force=True, silent=True)
    if data:
        detay_text = str(data.get('detay', ''))
        gonderen_adi = str(data.get('gonderen_adi', 'Emlak Danışmanı'))
        
        ilanlar.insert(0, {
            "grup_adi": str(data.get('grup_adi', 'Emlak Grubu')),
            "gonderen_adi": gonderenAdi if 'gonderenAdi' in locals() else gonderen_adi,
            "gonderen_adi_normalized": tr_normalize(gonderen_adi),
            "gonderen_tel": str(data.get('gonderen_tel', '')),
            "gonderen_tel_formatli": str(data.get('gonderen_tel_formatli', '')),
            "fiyat": str(data.get('fiyat', 'Fiyat Belirtilmedi')),
            "fiyat_raw": data.get('fiyat_raw', 0),
            "detay": detay_text,
            "detay_normalized": tr_normalize(detay_text),
            "durum": str(data.get('durum', 'Satışta')),
            "media_data": data.get('media_data', None),
            "media_mimetype": data.get('media_mimetype', ''),
            "tarih": str(data.get('tarih', ''))
        })
        return jsonify({"status": "success", "count": len(ilanlar)}), 200
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

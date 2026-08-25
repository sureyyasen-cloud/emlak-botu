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
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
        
        /* Kompakt Kart Yapısı */
        .card { background: white; border-radius: 8px; padding: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #10b981; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; display: flex; flex-direction: column; justify-content: space-between; height: 180px; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.1); }
        .card.opsiyon { border-left-color: #f59e0b; }
        
        .card-header { font-size: 0.8em; color: #0369a1; font-weight: bold; background: #e0f2fe; padding: 3px 6px; border-radius: 4px; display: inline-block; margin-bottom: 6px; }
        .price { font-size: 1.2em; font-weight: bold; color: #0f172a; margin: 4px 0; }
        .sender-preview { font-size: 0.8em; color: #475569; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .text-preview { font-size: 0.82em; color: #64748b; margin-top: 8px; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .badge { background: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; float: right; }
        .badge.opsiyon { background: #f59e0b; }
        .media-badge { background: #6366f1; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; float: right; margin-right: 4px; }

        /* Modal (Açılır Pencere) Stilleri */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); backdrop-filter: blur(2px); align-items: center; justify-content: center; }
        .modal-content { background-color: #fff; border-radius: 10px; width: 90%; max-width: 650px; max-height: 85vh; overflow-y: auto; padding: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); position: relative; animation: fadeIn 0.2s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
        .close-btn { position: absolute; top: 15px; right: 20px; font-size: 24px; font-weight: bold; color: #64748b; cursor: pointer; }
        .close-btn:hover { color: #0f172a; }
        .modal-media { margin-top: 15px; text-align: center; background: #000; border-radius: 8px; overflow: hidden; }
        .modal-media img, .modal-media video { width: 100%; max-height: 380px; display: block; object-fit: contain; }
        .sender-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; margin: 10px 0; font-size: 0.9em; }
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
             onclick="openModal({{ loop.index0 }})"
             data-detay="{{ ilan.detay_normalized }}" 
             data-gonderen="{{ ilan.gonderen_tel }} {{ ilan.gonderen_adi_normalized }}" 
             data-durum="{{ ilan.durum }}"
             data-fiyat="{{ ilan.fiyat_raw }}">
            <div>
                <span class="badge {% if 'opsiyon' in ilan.durum.lower() %}opsiyon{% endif %}">{{ ilan.durum }}</span>
                {% if ilan.media_data %}
                <span class="media-badge">🎥 Medya Var</span>
                {% endif %}
                <div class="card-header">📢 {{ ilan.grup_adi }}</div>
                <div class="price">{{ ilan.fiyat }}</div>
                <div class="sender-preview">👤 {{ ilan.gonderen_adi }} | 📞 {{ ilan.gonderen_tel_formatli }}</div>
                <div class="text-preview">{{ ilan.detay }}</div>
            </div>
            <div style="font-size:0.7em; color:#94a3b8; margin-top:6px; display:flex; justify-content:space-between;">
                <span>🕒 {{ ilan.tarih }}</span>
                <span style="color:#2563eb; font-weight:bold;">Tıkla Detay Gör &rarr;</span>
            </div>
        </div>
        {% else %}
        <p style="text-align:center; width:100%; color:#64748b;">Henüz kaydedilmiş ilan bulunmuyor.</p>
        {% endfor %}
    </div>

    <!-- Modal Yapısı -->
    <div id="detailModal" class="modal" onclick="closeModalOnOuterClick(event)">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <span id="mBadge" class="badge"></span>
            <div id="mGrup" class="card-header"></div>
            <div id="mFiyat" class="price" style="margin-top:10px;"></div>
            
            <div class="sender-box">
                👤 <b>Gönderen Danışman:</b> <span id="mGonderen"></span><br>
                📞 <b>Telefon:</b> <a id="mTelLink" href="" target="_blank" style="color:#2563eb; font-weight:bold;"></a>
            </div>

            <p id="mDetay" style="color: #334155; font-size: 0.95em; line-height: 1.5; white-space: pre-line; background:#f1f5f9; padding:12px; border-radius:6px;"></p>

            <div id="mMediaContainer" class="modal-media" style="display:none;"></div>
            
            <div style="margin-top:15px; font-size:0.8em; color:#94a3b8; text-align:right;">
                🕒 İlan Tarihi: <span id="mTarih"></span>
            </div>
        </div>
    </div>

    <script>
        const ilanlarData = {{ ilanlar | tojson }};

        function openModal(index) {
            const ilan = ilanlarData[index];
            if (!ilan) return;

            document.getElementById('mGrup').innerText = '📢 ' + ilan.grup_adi;
            document.getElementById('mFiyat').innerText = ilan.fiyat;
            document.getElementById('mBadge').innerText = ilan.durum;
            document.getElementById('mBadge').className = 'badge ' + (ilan.durum.toLowerCase().includes('opsiyon') ? 'opsiyon' : '');
            document.getElementById('mGonderen').innerText = ilan.gonderen_adi;
            
            const telLink = document.getElementById('mTelLink');
            telLink.innerText = ilan.gonderen_tel_formatli;
            telLink.href = 'https://wa.me/' + ilan.gonderen_tel;

            document.getElementById('mDetay').innerText = ilan.detay;
            document.getElementById('mTarih').innerText = ilan.tarih;

            const mediaBox = document.getElementById('mMediaContainer');
            if (ilan.media_data) {
                mediaBox.style.display = 'block';
                if (ilan.media_mimetype.includes('video')) {
                    mediaBox.innerHTML = `<video controls src="data:${ilan.media_mimetype};base64,${ilan.media_data}"></video>`;
                } else {
                    mediaBox.innerHTML = `<img src="data:${ilan.media_mimetype};base64,${ilan.media_data}" alt="İlan Medyası">`;
                }
            } else {
                mediaBox.style.display = 'none';
                mediaBox.innerHTML = '';
            }

            document.getElementById('detailModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('detailModal').style.display = 'none';
            const mediaBox = document.getElementById('mMediaContainer');
            mediaBox.innerHTML = ''; // Videoyu durdurmak için temizle
        }

        function closeModalOnOuterClick(e) {
            if (e.target.id === 'detailModal') {
                closeModal();
            }
        }

        function normalizeTR(text) {
            if (!text) return "";
            return text.toString().toLowerCase()
                .replace(/ğ/g, "g").replace(/ü/g, "u").replace(/ş/g, "s")
                .replace(/ı/g, "i").replace(/ö/g, "o").replace(/ç/g, "c")
                .replace(/İ/g, "i").replace(/I/g, "i");
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
            "gonderen_adi": gonderen_adi,
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

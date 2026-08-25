from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

ilanlar = []

# Metin içinden fiyat ayıklama fonksiyonu
def fiyat_bul(metin):
    if not metin:
        return "Belirtilmedi"
    # 2.875.000 TL, 2875000 TL, 2.875.000₺ gibi kalıpları arar
    match = re.search(r'(\d{1,3}(?:\.\d{3})+|\d+)\s*(?:TL|tl|₺)', metin)
    if match:
        return match.group(0)
    return "Belirtilmedi"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emlak Portföy & Filtre Paneli</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }
        .header { background: #ffc107; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 20px; }
        .main-layout { display: flex; gap: 20px; }
        .filter-panel { width: 280px; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); height: fit-content; }
        .filter-group { margin-bottom: 15px; }
        .filter-group label { display: block; font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #333; }
        .filter-group input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        .btn-search { width: 100%; background: #0056b3; color: white; border: none; padding: 10px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .btn-search:hover { background: #004085; }
        .content-panel { flex-grow: 1; }
        .card { background: #fff; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center; cursor: pointer; }
        .card:hover { transform: translateY(-2px); }
        .card img { width: 100px; height: 80px; object-fit: cover; border-radius: 6px; margin-right: 15px; }
        .no-img { width: 100px; height: 80px; background: #eee; border-radius: 6px; margin-right: 15px; display: flex; align-items: center; justify-content: center; color: #888; font-size: 12px; }
        .details { flex-grow: 1; }
        .title { font-size: 15px; font-weight: bold; color: #0056b3; margin-bottom: 5px; }
        .meta { font-size: 13px; color: #666; }
        .price { font-size: 15px; font-weight: bold; color: #d9534f; width: 130px; text-align: right; }

        /* Modal Stilleri */
        .modal-bg { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 9999; align-items: center; justify-content: center; }
        .modal-body { background: #fff; padding: 25px; border-radius: 12px; max-width: 650px; width: 90%; max-height: 85vh; overflow-y: auto; position: relative; }
        .modal-close { position: absolute; top: 15px; right: 20px; font-size: 24px; font-weight: bold; cursor: pointer; color: #888; }
        .modal-img { width: 100%; max-height: 350px; object-fit: contain; border-radius: 8px; margin: 15px 0; background: #000; }
        .modal-text { white-space: pre-wrap; word-break: break-all; line-height: 1.6; font-size: 14px; background: #f8f9fa; padding: 15px; border-radius: 6px; }
        .modal-text a { color: #0056b3; text-decoration: underline; font-weight: bold; }
    </style>
</head>
<body>

<div class="header">🏠 Emlak Filtreleme Sistemi</div>

<div class="main-layout">
    <!-- Sol Filtreleme Paneli -->
    <div class="filter-panel">
        <h3 style="margin-top:0;">Detaylı Arama</h3>
        <div class="filter-group">
            <label>Kelime ile Ara</label>
            <input type="text" id="filterKeyword" placeholder="Örn: 2+1, satılık, sokak...">
        </div>
        <button class="btn-search" onclick="filtrele()">Ara</button>
    </div>

    <!-- Sağ İlan Listesi -->
    <div class="content-panel">
        <div id="ilanListesi">İlanlar yükleniyor...</div>
    </div>
</div>

<!-- Modal Pop-up -->
<div id="ilanModal" class="modal-bg" onclick="if(event.target === this) modalKapat()">
    <div class="modal-body">
        <span class="modal-close" onclick="modalKapat()">&times;</span>
        <h3 id="modalBaslik" style="margin-top:0; color:#333;">İlan Detayı</h3>
        <div id="modalMeta" style="font-size:13px; color:#666; margin-bottom:10px;"></div>
        <img id="modalResim" class="modal-img" src="" style="display:none;" />
        <div id="modalMetin" class="modal-text"></div>
    </div>
</div>

<script>
    let tumIlanlar = [];

    // Metindeki URL'leri Otomatik Tıklanabilir Linke Dönüştürür
    function urlYap(metin) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return metin.replace(urlRegex, function(url) {
            return '<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + url + '</a>';
        });
    }

    async function ilanlariGetir() {
        try {
            const res = await fetch('/api/ilanlar');
            tumIlanlar = await res.json();
            filtrele();
        } catch (e) { console.error(e); }
    }

    function filtrele() {
        const keyword = document.getElementById('filterKeyword').value.toLowerCase();
        const container = document.getElementById('ilanListesi');
        container.innerHTML = '';

        const filtrelenmis = tumIlanlar.filter(item => {
            return !keyword || item.detay.toLowerCase().includes(keyword);
        });

        if (filtrelenmis.length === 0) {
            container.innerHTML = '<div style="background:#fff; padding:20px; border-radius:8px;">Eşleşen ilan bulunamadı.</div>';
            return;
        }

        filtrelenmis.forEach((item, index) => {
            const imgHTML = item.resim_url 
                ? `<img src="${item.resim_url}">` 
                : `<div class="no-img">Görsel Yok</div>`;

            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => detayAc(item);
            card.innerHTML = `
                ${imgHTML}
                <div class="details">
                    <div class="title">${item.detay.substring(0, 80)}...</div>
                    <div class="meta">Grup: ${item.grup_adi} | Danışman: ${item.gonderen_adi}</div>
                </div>
                <div class="price">${item.fiyat}</div>
            `;
            container.appendChild(card);
        });
    }

    function detayAc(item) {
        document.getElementById('modalBaslik').innerText = `İlan Detayı - ${item.gonderen_adi}`;
        document.getElementById('modalMeta').innerText = `Tarih: ${item.tarih} | İletişim: ${item.gonderen_tel_formatli} | Grup: ${item.grup_adi}`;
        
        // Linkleri Tıklanabilir Yaparak Aktar
        document.getElementById('modalMetin').innerHTML = urlYap(item.detay);

        const img = document.getElementById('modalResim');
        if (item.resim_url) {
            img.src = item.resim_url;
            img.style.display = 'block';
        } else {
            img.style.display = 'none';
        }

        document.getElementById('ilanModal').style.display = 'flex';
    }

    function modalKapat() {
        document.getElementById('ilanModal').style.display = 'none';
    }

    ilanlariGetir();
    setInterval(ilanlariGetir, 10000);
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    data = request.json
    if data:
        # Fiyat Otomatik Ayıklanıyor
        data['fiyat'] = fiyat_bul(data.get('detay', ''))
        ilanlar.insert(0, data)
    return jsonify({"status": "success"}), 200

@app.route('/api/ilanlar', methods=['GET'])
def ilanlar_getir():
    return jsonify(ilanlar), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

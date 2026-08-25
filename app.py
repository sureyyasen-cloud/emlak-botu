from flask import Flask, request, jsonify, render_template_string

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
        body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #ffc107; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 20px; }
        .card { background: #fff; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; align-items: center; cursor: pointer; transition: transform 0.1s; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .card img { width: 110px; height: 85px; object-fit: cover; border-radius: 6px; margin-right: 15px; }
        .no-img { width: 110px; height: 85px; background: #eee; border-radius: 6px; margin-right: 15px; display: flex; align-items: center; justify-content: center; color: #888; font-size: 12px; font-weight: bold; }
        .details { flex-grow: 1; }
        .title { font-size: 15px; font-weight: bold; color: #0056b3; margin-bottom: 5px; line-height: 1.3; }
        .meta { font-size: 13px; color: #666; }
        .price { font-size: 16px; font-weight: bold; color: #d9534f; width: 150px; text-align: right; }

        /* Modal (Açılır Pencere) Stili */
        .modal-bg { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.65); z-index: 9999; align-items: center; justify-content: center; }
        .modal-body { background: #fff; padding: 25px; border-radius: 12px; max-width: 650px; width: 90%; max-height: 85vh; overflow-y: auto; position: relative; box-shadow: 0 5px 20px rgba(0,0,0,0.3); }
        .modal-close { position: absolute; top: 15px; right: 20px; font-size: 26px; font-weight: bold; cursor: pointer; color: #888; }
        .modal-close:hover { color: #000; }
        .modal-img { width: 100%; max-height: 380px; object-fit: contain; border-radius: 8px; margin: 15px 0; background: #111; }
        .modal-text { white-space: pre-wrap; word-break: break-word; line-height: 1.6; font-size: 14px; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">🏠 Emlak Filtreleme Sistemi</div>
    <div id="ilanListesi">İlanlar yükleniyor...</div>
</div>

<!-- İlan Detay Pop-Up (Modal) -->
<div id="ilanModal" class="modal-bg" onclick="if(event.target === this) modalKapat()">
    <div class="modal-body">
        <span class="modal-close" onclick="modalKapat()">&times;</span>
        <h3 id="modalBaslik" style="margin-top:0; color:#0056b3;">İlan Detayı</h3>
        <div id="modalMeta" style="font-size:13px; color:#666; margin-bottom:12px; border-bottom: 1px solid #eee; padding-bottom: 8px;"></div>
        <img id="modalResim" class="modal-img" src="" style="display:none;" />
        <div id="modalMetin" class="modal-text"></div>
    </div>
</div>

<script>
    let tumIlanlar = [];

    async function ilanlariGetir() {
        try {
            const res = await fetch('/api/ilanlar');
            tumIlanlar = await res.json();
            
            const container = document.getElementById('ilanListesi');
            container.innerHTML = '';

            if (tumIlanlar.length === 0) {
                container.innerHTML = '<div style="padding:20px; background:#fff; border-radius:8px;">Henüz aktif ilan bulunmuyor...</div>';
                return;
            }

            tumIlanlar.forEach((item, index) => {
                const imgHTML = item.resim_url 
                    ? `<img src="${item.resim_url}" alt="İlan Görseli">` 
                    : `<div class="no-img">Görsel Yok</div>`;

                const card = document.createElement('div');
                card.className = 'card';
                card.onclick = () => detayAc(index);
                card.innerHTML = `
                    ${imgHTML}
                    <div class="details">
                        <div class="title">${item.detay.substring(0, 85)}...</div>
                        <div class="meta">Grup: ${item.grup_adi} | Danışman: ${item.gonderen_adi}</div>
                    </div>
                    <div class="price">${item.fiyat || 'Belirtilmedi'}</div>
                `;
                container.appendChild(card);
            });
        } catch (e) {
            console.error("İlanlar çekilemedi:", e);
        }
    }

    function detayAc(index) {
        const item = tumIlanlar[index];
        document.getElementById('modalBaslik').innerText = `İlan Detayı - ${item.gonderen_adi}`;
        document.getElementById('modalMeta').innerText = `Tarih: ${item.tarih} | İletişim: ${item.gonderen_tel_formatli || item.gonderen_tel} | Grup: ${item.grup_adi}`;
        
        // Linkleri (Sahibinden, Hepsiemlak vb.) tıklanabilir yap
        let formatliMetin = item.detay;
        document.getElementById('modalMetin').innerText = formatliMetin;

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
    setInterval(ilanlariGetir, 8000);
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
        ilanlar.insert(0, data)
        if len(ilanlar) > 150: # Bellek şişmesini önlemek için son 150 ilanı tutar
            ilanlar.pop()
    return jsonify({"status": "success"}), 200

@app.route('/api/ilanlar', methods=['GET'])
def ilanlar_getir():
    return jsonify(ilanlar), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

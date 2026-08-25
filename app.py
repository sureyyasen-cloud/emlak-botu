import os
import re
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

ilanlar = []

def fiyat_bul(metin):
    if not metin or not isinstance(metin, str):
        return "Belirtilmedi", 0
    match = re.search(r'(\d{1,3}(?:\.\d{3})+|\d+)\s*(?:TL|tl|₺)', metin)
    if match:
        try:
            raw_price = int(re.sub(r'[^\d]', '', match.group(1)))
            return match.group(0), raw_price
        except ValueError:
            return "Belirtilmedi", 0
    return "Belirtilmedi", 0

def metin_ozeti(metin):
    if not metin or not isinstance(metin, str):
        return ""
    temiz = re.sub(r'[^\w\s]', '', metin.lower()).strip()
    return temiz[:60]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emlak Portföy & Filtre Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f5; margin: 0; padding: 15px; }
        .header { background: #ffc107; padding: 12px 20px; border-radius: 6px; font-weight: bold; font-size: 22px; margin-bottom: 15px; color: #222; }
        
        .filter-bar { background: #fdfdfd; padding: 15px; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #ddd; }
        .filter-row { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 10px; }
        .filter-row select, .filter-row input { padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; background: #fff; }
        .filter-row input[type="number"] { width: 110px; }
        .btn-search { background: #4285f4; color: white; border: none; padding: 9px 25px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 14px; }
        .btn-search:hover { background: #2b6cb0; }
        .btn-clear { background: #e2e8f0; color: #4a5568; border: 1px solid #cbd5e0; padding: 9px 15px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 14px; }
        .btn-map { background: #fff; color: #4285f4; border: 1px solid #4285f4; padding: 9px 15px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 14px; }
        .more-options { color: #0056b3; font-size: 13px; cursor: pointer; text-decoration: underline; margin-top: 5px; display: inline-block; }

        .card { background: #fff; border-radius: 6px; padding: 12px 15px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); display: flex; align-items: center; cursor: pointer; border-left: 4px solid #4285f4; position: relative; }
        .card:hover { background: #f8fafc; }
        .card img, .card video { width: 110px; height: 85px; object-fit: cover; border-radius: 4px; margin-right: 15px; background: #000; }
        .no-img { width: 110px; height: 85px; background: #edf2f7; border-radius: 4px; margin-right: 15px; display: flex; align-items: center; justify-content: center; color: #a0aec0; font-size: 12px; font-weight: bold; }
        .details { flex-grow: 1; }
        .title { font-size: 15px; font-weight: bold; color: #1a365d; margin-bottom: 5px; line-height: 1.3; }
        .meta { font-size: 12px; color: #718096; }
        .price-box { min-width: 140px; text-align: right; }
        .price { font-size: 16px; font-weight: bold; color: #c53030; }
        .badge-tekil { background: #ebf8ff; color: #2b6cb0; font-size: 11px; font-weight: bold; padding: 2px 6px; border-radius: 4px; border: 1px solid #bee3f8; display: inline-block; margin-top: 3px; }

        .modal-bg { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 9999; align-items: center; justify-content: center; }
        .modal-body { background: #fff; padding: 25px; border-radius: 10px; max-width: 750px; width: 90%; max-height: 85vh; overflow-y: auto; position: relative; }
        .modal-close { position: absolute; top: 15px; right: 20px; font-size: 26px; font-weight: bold; cursor: pointer; color: #a0aec0; }
        .modal-media { width: 100%; max-height: 420px; object-fit: contain; border-radius: 6px; margin: 15px 0; background: #000; }
        .modal-text { white-space: pre-wrap; word-break: break-all; line-height: 1.6; font-size: 14px; background: #f7fafc; padding: 15px; border-radius: 6px; border: 1px solid #e2e8f0; }
        .modal-text a { color: #3182ce; font-weight: bold; text-decoration: underline; }
        .paylasanlar-box { background: #fffaf0; border: 1px solid #feebc8; border-radius: 6px; padding: 12px; margin-top: 15px; }
        .paylasan-item { font-size: 13px; color: #744210; padding: 4px 0; border-bottom: 1px dashed #fbd38d; }
        .paylasan-item:last-child { border-bottom: none; }
    </style>
</head>
<body>

<div class="header">🏠 Emlak Filtreleme Sistemi</div>

<div class="filter-bar">
    <div class="filter-row">
        <select id="fDurum">
            <option value="">Satılık / Kiralık (Tümü)</option>
            <option value="satılık">Satılık</option>
            <option value="kiralık">Kiralık</option>
            <option value="devren">Devren</option>
        </select>
        <select id="fTuru">
            <option value="">Tüm Konut Türleri</option>
            <option value="daire">Daire</option>
            <option value="villa">Villa</option>
            <option value="dubleks">Dubleks</option>
            <option value="müstakil">Müstakil</option>
            <option value="arsa">Arsa / Tarla</option>
            <option value="dükkan">Dükkan / İşyeri</option>
        </select>
        <input type="text" id="fIl" placeholder="İl (Örn: İstanbul)">
        <input type="text" id="fIlce" placeholder="İlçe (Örn: Esenyurt)">
        <input type="text" id="fMahalle" placeholder="Mahalle">
    </div>
    <div class="filter-row">
        <input type="number" id="fMinFiyat" placeholder="Min TL">
        <span>-</span>
        <input type="number" id="fMaxFiyat" placeholder="Max TL">
        <select id="fOda">
            <option value="">Oda Sayısı</option>
            <option value="1+1">1+1</option>
            <option value="2+1">2+1</option>
            <option value="3+1">3+1</option>
            <option value="4+1">4+1</option>
            <option value="5+1">5+1</option>
        </select>
        <input type="text" id="fKelime" placeholder="Kelime ile ara (örn: site, deniz)..." style="flex-grow:1;">
        <button class="btn-search" onclick="filtrele()">Ara</button>
        <button class="btn-clear" onclick="sifirla()">Temizle</button>
        <button class="btn-map">Haritada Ara</button>
    </div>
    <span class="more-options">Daha fazla seçenek göster</span>
</div>

<div id="ilanListesi">İlanlar yükleniyor...</div>

<div id="ilanModal" class="modal-bg" onclick="if(event.target === this) modalKapat()">
    <div class="modal-body">
        <span class="modal-close" onclick="modalKapat()">&times;</span>
        <h3 id="modalBaslik" style="margin-top:0;">İlan Detayı</h3>
        <div id="modalMeta" style="font-size:13px; color:#4a5568; margin-bottom:10px;"></div>
        <div id="modalMediaContainer"></div>
        <div id="modalPaylasanlar" class="paylasanlar-box"></div>
        <div id="modalMetin" class="modal-text" style="margin-top:15px;"></div>
    </div>
</div>

<script>
    let tumIlanlar = [];

    function normalizeText(text) {
        if (!text) return '';
        return text.toLowerCase()
            .replace(/i/g, 'i').replace(/ı/g, 'i')
            .replace(/ş/g, 's').replace(/ğ/g, 'g')
            .replace(/ü/g, 'u').replace(/ö/g, 'o')
            .replace(/ç/g, 'c');
    }

    function urlYap(metin) {
        if (!metin) return '';
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
        const durum = normalizeText(document.getElementById('fDurum').value);
        const tur = normalizeText(document.getElementById('fTuru').value);
        const il = normalizeText(document.getElementById('fIl').value);
        const ilce = normalizeText(document.getElementById('fIlce').value);
        const mahalle = normalizeText(document.getElementById('fMahalle').value);
        const minFiyat = parseFloat(document.getElementById('fMinFiyat').value) || 0;
        const maxFiyat = parseFloat(document.getElementById('fMaxFiyat').value) || Infinity;
        const oda = normalizeText(document.getElementById('fOda').value);
        const kelime = normalizeText(document.getElementById('fKelime').value);

        const container = document.getElementById('ilanListesi');
        container.innerHTML = '';

        const filtrelenmis = tumIlanlar.filter(item => {
            const text = normalizeText(item.detay || '');
            
            if (durum && !text.includes(durum)) return false;
            if (tur && !text.includes(tur)) return false;
            if (il && !text.includes(il)) return false;
            if (ilce && !text.includes(ilce)) return false;
            if (mahalle && !text.includes(mahalle)) return false;
            if (oda && !text.includes(oda)) return false;
            if (kelime && !text.includes(kelime)) return false;
            
            if (minFiyat > 0 && item.fiyat_raw > 0 && item.fiyat_raw < minFiyat) return false;
            if (maxFiyat < Infinity && item.fiyat_raw > 0 && item.fiyat_raw > maxFiyat) return false;
            
            return true;
        });

        if (filtrelenmis.length === 0) {
            container.innerHTML = '<div style="background:#fff; padding:20px; border-radius:6px; color:#c53030; font-weight:bold;">Aramanıza uygun ilan bulunamadı. Filtreleri temizleyip tekrar deneyebilirsiniz.</div>';
            return;
        }

        filtrelenmis.forEach((item) => {
            let mediaHTML = `<div class="no-img">Görsel Yok</div>`;
            if (item.resim_url) {
                if (item.is_video) {
                    mediaHTML = `<video src="${item.resim_url}" muted></video>`;
                } else {
                    mediaHTML = `<img src="${item.resim_url}">`;
                }
            }

            const paylasanSayisi = item.paylasanlar ? item.paylasanlar.length : 1;
            const badgeHTML = paylasanSayisi > 1 ? `<div class="badge-tekil">🔥 ${paylasanSayisi} Farklı Kişi Paylaştı (En Uygun Fiyat)</div>` : '';
            const baslikMetni = (item.detay || '').substring(0, 100);

            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => detayAc(item);
            card.innerHTML = `
                ${mediaHTML}
                <div class="details">
                    <div class="title">${baslikMetni}...</div>
                    <div class="meta">Grup: ${item.grup_adi || ''} | İlan Sahibi: ${item.gonderen_adi || ''} | Tarih: ${item.tarih || ''}</div>
                    ${badgeHTML}
                </div>
                <div class="price-box">
                    <div class="price">${item.fiyat || 'Belirtilmedi'}</div>
                </div>
            `;
            container.appendChild(card);
        });
    }

    function sifirla() {
        document.getElementById('fDurum').value = "";
        document.getElementById('fTuru').value = "";
        document.getElementById('fIl').value = "";
        document.getElementById('fIlce').value = "";
        document.getElementById('fMahalle').value = "";
        document.getElementById('fMinFiyat').value = "";
        document.getElementById('fMaxFiyat').value = "";
        document.getElementById('fOda').value = "";
        document.getElementById('fKelime').value = "";
        filtrele();
    }

    function detayAc(item) {
        document.getElementById('modalBaslik').innerText = `İlan Detayı - ${item.gonderen_adi || ''}`;
        document.getElementById('modalMeta').innerText = `En Uygun Fiyat: ${item.fiyat || ''} | İletişim: ${item.gonderen_tel_formatli || ''}`;
        document.getElementById('modalMetin').innerHTML = urlYap(item.detay || '');

        const paylasanlarBox = document.getElementById('modalPaylasanlar');
        paylasanlarBox.innerHTML = '<strong>👥 Bu İlanı Paylaşan Danışmanlar / Teklifler:</strong><br><br>';
        
        if (item.paylasanlar && item.paylasanlar.length > 0) {
            item.paylasanlar.forEach(p => {
                paylasanlarBox.innerHTML += `
                    <div class="paylasan-item">
                        👤 <strong>${p.gonderen_adi || ''}</strong> (${p.gonderen_tel_formatli || ''}) 
                        — <span style="color:#c53030; font-weight:bold;">${p.fiyat || ''}</span> 
                        <span style="font-size:11px; color:#718096;">[${p.tarih || ''}]</span>
                    </div>`;
            });
        } else {
            paylasanlarBox.innerHTML += `
                <div class="paylasan-item">
                    👤 <strong>${item.gonderen_adi || ''}</strong> (${item.gonderen_tel_formatli || ''}) 
                    — <span style="color:#c53030; font-weight:bold;">${item.fiyat || ''}</span>
                </div>`;
        }

        const mediaBox = document.getElementById('modalMediaContainer');
        mediaBox.innerHTML = '';
        if (item.resim_url) {
            if (item.is_video) {
                mediaBox.innerHTML = `<video class="modal-media" src="${item.resim_url}" controls autoplay></video>`;
            } else {
                mediaBox.innerHTML = `<img class="modal-media" src="${item.resim_url}">`;
            }
        }

        document.getElementById('ilanModal').style.display = 'flex';
    }

    function modalKapat() {
        document.getElementById('ilanModal').style.display = 'none';
    }

    ilanlariGetir();
    setInterval(ilanlariGetir, 6000);
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    try:
        data = request.get_json(silent=True) or {}
        detay_metni = data.get('detay', '')
        
        fiyat_str, fiyat_raw = fiyat_bul(detay_metni)
        data['fiyat'] = fiyat_str
        data['fiyat_raw'] = fiyat_raw

        yeni_ozet = metin_ozeti(detay_metni)
        bulundu = False

        if yeni_ozet:
            for mevcut in ilanlar:
                mevcut_ozet = metin_ozeti(mevcut.get('detay', ''))
                if mevcut_ozet and (yeni_ozet in mevcut_ozet or mevcut_ozet in yeni_ozet):
                    bulundu = True
                    
                    if 'paylasanlar' not in mevcut or not isinstance(mevcut['paylasanlar'], list):
                        mevcut['paylasanlar'] = [{
                            'gonderen_adi': mevcut.get('gonderen_adi', ''),
                            'gonderen_tel_formatli': mevcut.get('gonderen_tel_formatli', ''),
                            'fiyat': mevcut.get('fiyat', ''),
                            'fiyat_raw': mevcut.get('fiyat_raw', 0),
                            'tarih': mevcut.get('tarih', '')
                        }]

                    mevcut['paylasanlar'].append({
                        'gonderen_adi': data.get('gonderen_adi', ''),
                        'gonderen_tel_formatli': data.get('gonderen_tel_formatli', ''),
                        'fiyat': data.get('fiyat', ''),
                        'fiyat_raw': data.get('fiyat_raw', 0),
                        'tarih': data.get('tarih', '')
                    })

                    if data['fiyat_raw'] > 0 and (mevcut.get('fiyat_raw', 0) == 0 or data['fiyat_raw'] < mevcut['fiyat_raw']):
                        mevcut['fiyat'] = data['fiyat']
                        mevcut['fiyat_raw'] = data['fiyat_raw']
                        mevcut['gonderen_adi'] = data.get('gonderen_adi', '')
                        mevcut['gonderen_tel_formatli'] = data.get('gonderen_tel_formatli', '')
                    
                    break

        if not bulundu:
            data['paylasanlar'] = [{
                'gonderen_adi': data.get('gonderen_adi', ''),
                'gonderen_tel_formatli': data.get('gonderen_tel_formatli', ''),
                'fiyat': data.get('fiyat', ''),
                'fiyat_raw': data.get('fiyat_raw', 0),
                'tarih': data.get('tarih', '')
            }]
            ilanlar.insert(0, data)

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ilanlar', methods=['GET'])
def ilanlar_getir():
    return jsonify(ilanlar), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

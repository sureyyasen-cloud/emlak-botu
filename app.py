from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

DB_FILE = "ilanlar.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ilanlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grup_adi TEXT, gonderen_adi TEXT, gonderen_tel TEXT, gonderen_tel_formatli TEXT,
            fiyat TEXT, fiyat_raw REAL, detay TEXT, durum TEXT, tarih TEXT, resim_url TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE ilanlar ADD COLUMN resim_url TEXT DEFAULT ''")
    except:
        pass
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Emlak Portföy & Filtre Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; margin: 0; }
        .header { background: #ffcc00; padding: 15px 30px; font-weight: bold; font-size: 24px; color: #333; border-bottom: 3px solid #e5b800; }
        .container { display: flex; max-width: 1400px; margin: 20px auto; padding: 0 15px; }
        .sidebar { width: 280px; background: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-right: 20px; height: fit-content; }
        .sidebar input, .sidebar select, .sidebar button { width: 100%; margin-bottom: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        .sidebar button { background: #337ab7; color: white; border: none; font-weight: bold; cursor: pointer; }
        .sidebar button:hover { background: #286090; }
        .content { flex: 1; background: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f5f5f5; padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 14px; color: #666; }
        td { padding: 15px 12px; border-bottom: 1px solid #eee; vertical-align: middle; font-size: 14px; }
        tr:hover { background: #fdfdfd; }
        .resim-kutusu { width: 120px; height: 90px; background: #eaebec; border-radius: 4px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .resim-kutusu img { width: 100%; height: 100%; object-fit: cover; }
        .ilan-baslik { font-weight: bold; color: #337ab7; cursor: pointer; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .fiyat { font-weight: bold; color: #d9534f; font-size: 16px; }
        .no-data { text-align: center; padding: 30px; color: #999; }
    </style>
</head>
<body>
    <div class="header">🏠 Emlak Filtreleme Sistemi</div>
    <div class="container">
        <div class="sidebar">
            <h4 style="margin-top:0;">Detaylı Arama</h4>
            <label>Kelime ile Ara</label>
            <input type="text" id="arama" placeholder="Örn: 2+1, deniz manzaralı...">
            <label>Minimum Fiyat</label>
            <input type="number" id="minFiyat" placeholder="TL">
            <label>Maksimum Fiyat</label>
            <input type="number" id="maxFiyat" placeholder="TL">
            <button onclick="ilanlariGetir()">Ara</button>
        </div>
        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th width="140">Görsel</th>
                        <th>İlan Detayı</th>
                        <th width="120">Fiyat</th>
                        <th width="120">Tarih</th>
                        <th width="150">Danışman</th>
                    </tr>
                </thead>
                <tbody id="ilanlar-container">
                    <tr><td colspan="5" class="no-data">Yükleniyor...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function ilanlariGetir() {
            try {
                const res = await fetch('/api/ilanlar');
                let data = await res.json();
                
                // Frontend Filtreleme Mantığı
                const arama = document.getElementById('arama').value.toLowerCase();
                const minFiyat = parseFloat(document.getElementById('minFiyat').value) || 0;
                const maxFiyat = parseFloat(document.getElementById('maxFiyat').value) || Infinity;

                data = data.filter(item => {
                    const icerikUygun = item.detay.toLowerCase().includes(arama) || item.grup_adi.toLowerCase().includes(arama);
                    const fiyatUygun = item.fiyat_raw >= minFiyat && item.fiyat_raw <= maxFiyat;
                    return icerikUygun && fiyatUygun;
                });

                const container = document.getElementById('ilanlar-container');
                if (data.length === 0) {
                    container.innerHTML = '<tr><td colspan="5" class="no-data">Kriterlere uygun ilan bulunamadı.</td></tr>';
                    return;
                }
                
                container.innerHTML = data.map(item => {
                    const resimHtml = item.resim_url 
                        ? `<img src="${item.resim_url}" alt="İlan Resmi">` 
                        : `<span style="color:#aaa; font-size:12px;">Görsel Yok</span>`;
                        
                    return `
                    <tr>
                        <td><div class="resim-kutusu">${resimHtml}</div></td>
                        <td>
                            <div class="ilan-baslik">${item.detay.substring(0, 150)}...</div>
                            <div style="font-size: 12px; color: #888; margin-top: 5px;">Grup: ${item.grup_adi}</div>
                        </td>
                        <td class="fiyat">${item.fiyat}</td>
                        <td>${item.tarih}</td>
                        <td>
                            <strong>${item.gonderen_adi}</strong><br>
                            <span style="font-size:12px; color:#666;">${item.gonderen_tel_formatli}</span>
                        </td>
                    </tr>
                `}).join('');
            } catch (e) {
                document.getElementById('ilanlar-container').innerHTML = '<tr><td colspan="5" class="no-data">Bağlantı hatası.</td></tr>';
            }
        }
        ilanlariGetir();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ilan-ekle', methods=['POST', 'OPTIONS'])
def ilan_ekle():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(force=True) or {}
        detay = str(data.get('detay', ''))
        
        # SPAM VE KELİME FİLTRESİ (Sadece gerçek ilanları kabul et)
        detay_kucuk = detay.lower()
        if "chat.whatsapp.com" in detay_kucuk or "katılmak için" in detay_kucuk:
            return jsonify({"success": False, "message": "Grup daveti reddedildi"}), 400
            
        grup_adi = str(data.get('grup_adi', 'Emlak Grubu'))
        gonderen_adi = str(data.get('gonderen_adi', 'Danışman'))
        gonderen_tel = str(data.get('gonderen_tel', ''))
        gonderen_tel_formatli = str(data.get('gonderen_tel_formatli', ''))
        fiyat = str(data.get('fiyat', 'Belirtilmedi'))
        fiyat_raw = float(data.get('fiyat_raw', 0) or 0)
        durum = str(data.get('durum', 'Satışta'))
        tarih = str(data.get('tarih', ''))
        resim_url = str(data.get('resim_url', ''))

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ilanlar (grup_adi, gonderen_adi, gonderen_tel, gonderen_tel_formatli, fiyat, fiyat_raw, detay, durum, tarih, resim_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (grup_adi, gonderen_adi, gonderen_tel, gonderen_tel_formatli, fiyat, fiyat_raw, detay, durum, tarih, resim_url))
        
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "İlan kaydedildi"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ilanlar', methods=['GET'])
def ilanlari_getir():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT grup_adi, gonderen_adi, gonderen_tel, gonderen_tel_formatli, fiyat, fiyat_raw, detay, durum, tarih, resim_url FROM ilanlar ORDER BY id DESC LIMIT 200')
        rows = cursor.fetchall()
        conn.close()

        liste = []
        for row in rows:
            liste.append({
                "grup_adi": row[0], "gonderen_adi": row[1], "gonderen_tel": row[2],
                "gonderen_tel_formatli": row[3], "fiyat": row[4], "fiyat_raw": row[5],
                "detay": row[6], "durum": row[7], "tarih": row[8], "resim_url": row[9]
            })
        return jsonify(liste), 200
    except Exception as e:
        return jsonify([]), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

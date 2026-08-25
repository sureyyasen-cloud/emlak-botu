from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)

# CORS ayarları
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
            grup_adi TEXT,
            gonderen_adi TEXT,
            gonderen_tel TEXT,
            gonderen_tel_formatli TEXT,
            fiyat TEXT,
            fiyat_raw REAL,
            detay TEXT,
            durum TEXT,
            tarih TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 404 Hatasını Önleyen Ana Sayfa Rota Tanımı
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Emlak Portföy & Filtre Paneli</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }
        .header { background: #1a252f; color: white; text-align: center; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; padding: 15px; margin-bottom: 12px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .grup { font-weight: bold; color: #2c3e50; }
        .fiyat { color: #e74c3c; font-weight: bold; font-size: 1.1em; }
        .detay { white-space: pre-wrap; margin-top: 10px; color: #333; }
        .meta { color: #7f8c8d; font-size: 0.85em; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🏠 Emlak Portföyü ve Filtre Paneli</h2>
    </div>
    <div id="ilanlar-container">İlanlar yükleniyor...</div>

    <script>
        async function ilanlariGetir() {
            try {
                const res = await fetch('/api/ilanlar');
                const data = await res.json();
                const container = document.getElementById('ilanlar-container');
                if (data.length === 0) {
                    container.innerHTML = '<p>Henüz kaydedilmiş ilan bulunmuyor.</p>';
                    return;
                }
                container.innerHTML = data.map(item => `
                    <div class="card">
                        <div class="grup">${item.grup_adi} - <span class="fiyat">${item.fiyat}</span></div>
                        <div class="detay">${item.detay}</div>
                        <div class="meta">Danışman: ${item.gonderen_adi} (${item.gonderen_tel_formatli}) | Tarih: ${item.tarih}</div>
                    </div>
                `).join('');
            } catch (e) {
                document.getElementById('ilanlar-container').innerHTML = '<p>İlanlar yüklenirken hata oluştu.</p>';
            }
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

@app.route('/api/ilan-ekle', methods=['POST', 'OPTIONS'])
def ilan_ekle():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(force=True) or {}
        
        grup_adi = str(data.get('grup_adi', 'Emlak Grubu'))
        gonderen_adi = str(data.get('gonderen_adi', 'Danışman'))
        gonderen_tel = str(data.get('gonderen_tel', ''))
        gonderen_tel_formatli = str(data.get('gonderen_tel_formatli', ''))
        fiyat = str(data.get('fiyat', 'Belirtilmedi'))
        fiyat_raw = float(data.get('fiyat_raw', 0) or 0)
        detay = str(data.get('detay', ''))
        durum = str(data.get('durum', 'Satışta'))
        tarih = str(data.get('tarih', ''))

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ilanlar (grup_adi, gonderen_adi, gonderen_tel, gonderen_tel_formatli, fiyat, fiyat_raw, detay, durum, tarih)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (grup_adi, gonderen_adi, gonderen_tel, gonderen_tel_formatli, fiyat, fiyat_raw, detay, durum, tarih))
        
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
        cursor.execute('SELECT grup_adi, gonderen_adi, gonderen_tel, gonderen_tel_formatli, fiyat, fiyat_raw, detay, durum, tarih FROM ilanlar ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()

        liste = []
        for row in rows:
            liste.append({
                "grup_adi": row[0],
                "gonderen_adi": row[1],
                "gonderen_tel": row[2],
                "gonderen_tel_formatli": row[3],
                "fiyat": row[4],
                "fiyat_raw": row[5],
                "detay": row[6],
                "durum": row[7],
                "tarih": row[8]
            })

        return jsonify(liste), 200
    except Exception as e:
        return jsonify([]), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

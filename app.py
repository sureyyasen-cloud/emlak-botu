from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'ilanlar.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("Veri okuma hatası:", e)
        return []

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Veri kaydetme hatası:", e)

@app.route('/')
def index():
    ilanlar = load_data()
    return render_template('index.html', ilanlar=ilanlar)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    try:
        data = request.get_json() or {}
        
        # Eksik veri gelse bile sunucunun 500 hatası vermesini engeller
        grup_adi = data.get('grup_adi', 'Bilinmeyen Grup')
        gonderen_adi = data.get('gonderen_adi', 'Bilinmiyor')
        gonderen_tel = data.get('gonderen_tel', '')
        gonderen_tel_formatli = data.get('gonderen_tel_formatli', '')
        detay = data.get('detay', '')
        resim_url = data.get('resim_url', '')
        is_video = data.get('is_video', False)
        tarih = data.get('tarih', '')

        ilanlar = load_data()
        
        yeni_ilan = {
            "id": len(ilanlar) + 1,
            "grup_adi": grupAdi if 'grupAdi' in locals() else grup_adi,
            "gonderen_adi": gonderen_adi,
            "gonderen_tel": gonderen_tel,
            "gonderen_tel_formatli": gonderen_tel_formatli,
            "detay": detay,
            "resim_url": resim_url,
            "is_video": is_video,
            "tarih": tarih
        }
        
        # Yeni ilanı listenin en başına ekler
        ilanlar.insert(0, yeni_ilan)
        save_data(ilanlar)
        
        return jsonify({"status": "success", "message": "İlan başarıyla eklendi"}), 200

    except Exception as e:
        print("API Hatası:", str(e))
        # Sunucunun dökülmesini engelleyen güvenli dönüş
        return jsonify({"status": "error", "message": str(e)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

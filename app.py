import os
import re
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Render 502 hatasını ve boyut sınırını aşmak için 50 MB limit tanımlıyoruz
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Veritabanı Yapılandırması (SQLite / PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///emlak.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Veritabanı Modeli
class Ilan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grup_adi = db.Column(db.String(250))
    gonderen_adi = db.Column(db.String(250))
    gonderen_tel = db.Column(db.String(100))
    gonderen_tel_formatli = db.Column(db.String(100))
    detay = db.Column(db.Text)
    resim_url = db.Column(db.Text)  # Base64 medya verisi (Resim / Video)
    is_video = db.Column(db.Boolean, default=False)
    tarih = db.Column(db.String(100))
    eklenme_tarihi = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # En son eklenen ilanları listele
    ilanlar = Ilan.query.order_by(Ilan.id.desc()).all()
    return render_template('index.html', ilanlar=ilanlar)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Veri bulunamadı'}), 400

        detay = data.get('detay', '')
        resim_url = data.get('resim_url', '')
        is_video = data.get('is_video', False)

        # Temel Emlak Anahtar Kelime Filtresi (Opsiyonel: İlan dışı mesajları elemek için)
        emlak_kelimeleri = [
            'satılık', 'kiralık', 'daire', 'arsa', 'villa', 'dükkan', 
            'm2', 'oda', 'fiyat', 'devren', 'kat', 'bina', 'portföy',
            'tl', 'usd', 'eur', 'konut', 'hisse', 'tarla', 'müşteri'
        ]
        
        # Metin veya medya içeriyorsa işleme al
        is_emlak_ilani = any(kelime in detay.lower() for kelime in emlak_kelimeleri)

        if is_emlak_ilani or resim_url:
            yeni_ilan = Ilan(
                grup_adi=data.get('grup_adi', 'Bilinmeyen Grup'),
                gonderen_adi=data.get('gonderen_adi', 'Bilinmeyen Gönderen'),
                gonderen_tel=data.get('gonderen_tel', ''),
                gonderen_tel_formatli=data.get('gonderen_tel_formatli', ''),
                detay=detay,
                resim_url=resim_url,
                is_video=is_video,
                tarih=data.get('tarih', '')
            )
            db.session.add(yeni_ilan)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'İlan ve medya başarıyla kaydedildi'}), 200
        else:
            return jsonify({'status': 'ignored', 'message': 'Mesaj ilan kriterlerine uymuyor'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

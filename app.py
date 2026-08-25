from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Base64 ile gelen büyük görseller ve videolar için limit (50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Veritabanı bağlantısı (PostgreSQL / SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///ilanlar.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Veritabanı Modeli
class Ilan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grup_adi = db.Column(db.String(255))
    gonderen_adi = db.Column(db.String(255))
    gonderen_tel = db.Column(db.String(100))
    gonderen_tel_formatli = db.Column(db.String(100))
    detay = db.Column(db.Text)
    resim_url = db.Column(db.Text)  # Base64 verisi veya URL buraya kaydolur
    is_video = db.Column(db.Boolean, default=False)
    tarih = db.Column(db.String(100))

# Veritabanı tablolarını oluştur
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    ilanlar = Ilan.query.order_by(Ilan.id.desc()).all()
    return render_template('index.html', ilanlar=ilanlar)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Veri alınamadı'}), 400

        yeni_ilan = Ilan(
            grup_adi=data.get('grup_adi', ''),
            gonderen_adi=data.get('gonderen_adi', ''),
            gonderen_tel=data.get('gonderen_tel', ''),
            gonderen_tel_formatli=data.get('gonderen_tel_formatli', ''),
            detay=data.get('detay', ''),
            resim_url=data.get('resim_url', ''),
            is_video=data.get('is_video', False),
            tarih=data.get('tarih', '')
        )

        db.session.add(yeni_ilan)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'İlan başarıyla eklendi'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

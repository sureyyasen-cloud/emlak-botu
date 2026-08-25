from flask import Flask, render_template_string, request, jsonify
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
    except Exception:
        return []

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

# HTML Şablonu (Tek dosya mimarisi)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emlak Portföy Paneli</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding: 20px; }
        .card { margin-bottom: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .media-box { max-width: 100%; max-height: 300px; object-fit: cover; border-radius: 8px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="mb-4 text-primary">Gelen Emlak İlanları</h2>
        <div class="row">
            {% for ilan in ilanlar %}
            <div class="col-md-6 col-lg-4">
                <div class="card p-3">
                    <div class="d-flex justify-content-between text-muted small">
                        <span><strong>{{ ilan.grup_adi }}</strong></span>
                        <span>{{ ilan.tarih }}</span>
                    </div>
                    <hr class="my-2">
                    <p class="mb-1"><strong>Gönderen:</strong> {{ ilan.gonderen_adi }} ({{ ilan.gonderen_tel_formatli }})</p>
                    <p class="card-text">{{ ilan.detay }}</p>
                    {% if ilan.resim_url %}
                        {% if ilan.is_video %}
                            <video src="{{ ilan.resim_url }}" controls class="media-box"></video>
                        {% else %}
                            <img src="{{ ilan.resim_url }}" class="media-box" alt="İlan Görseli">
                        {% endif %}
                    {% endif %}
                </div>
            </div>
            {% else %}
            <div class="col-12"><div class="alert alert-info">Henüz gelen ilan yok.</div></div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    ilanlar = load_data()
    return render_template_string(HTML_TEMPLATE, ilanlar=ilanlar)

@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    try:
        data = request.get_json() or {}
        
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
            "grup_adi": grup_adi,
            "gonderen_adi": gonderen_adi,
            "gonderen_tel": gonderen_tel,
            "gonderen_tel_formatli": gonderen_tel_formatli,
            "detay": detay,
            "resim_url": resim_url,
            "is_video": is_video,
            "tarih": tarih
        }
        
        ilanlar.insert(0, yeni_ilan)
        save_data(ilanlar)
        
        return jsonify({"status": "success", "message": "İlan başarıyla eklendi"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

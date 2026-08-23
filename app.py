import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>WhatsApp Emlak İlan Paneli</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 40px; text-align: center; }
            .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .badge { background: #27ae60; color: white; padding: 6px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
            .card { border: 1px solid #e0e0e0; padding: 20px; margin-top: 20px; border-radius: 8px; background: #fafafa; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 WhatsApp Emlak İlan Paneli</h1>
            <p><span class="badge">Sistem Aktif</span></p>
            <div class="card">
                <h3>🔍 İlan Filtreleme Akışı</h3>
                <p>WhatsApp grubundaki gelen emlak ilanları filtreye uygun olarak burada listelenecektir.</p>
                <p><i>Henüz kaydedilmiş ilan bulunmuyor.</i></p>
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const app = express();
const port = process.env.PORT || 3000;

let qrCodeData = '';

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', (qr) => {
    qrCodeData = qr;
    console.log('QR KOD OLUŞTURULDU');
});

client.on('ready', () => {
    console.log('WhatsApp Bağlantısı Hazır!');
});

client.initialize();

app.get('/', (req, res) => {
    res.send(`
        <html>
            <head><title>Emlak İlan Paneli</title></head>
            <body style="font-family:Arial; text-align:center; padding:50px;">
                <h1>🏢 WhatsApp Emlak İlan Paneli</h1>
                <h3>WhatsApp Bağlantı Durumu</h3>
                ${qrCodeData 
                    ? `<img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(qrCodeData)}" />`
                    : '<p>QR KOD HAZIRLANIYOR... Lütfen 10-15 saniye bekleyip sayfayı yenileyin.</p>'
                }
            </body>
        </html>
    `);
});

app.listen(port, () => console.log(`Sunucu ${port} portunda aktif.`));

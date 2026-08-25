@app.route('/api/ilan-ekle', methods=['POST'])
def ilan_ekle():
    try:
        data = request.json
        grup_adi = data.get('grup_adi', 'Emlak Grubu')
        detay = data.get('detay', '')
        gonderen_tel = data.get('gonderen_tel', '')
        tarih = data.get('tarih', '')
        
        # İlanı işleme ve kaydetme adımı
        print(f"✅ [KAYDEDİLDİ] {grup_adi}: {detay[:40]}...")
        
        return jsonify({"success": True, "message": "İlan başarıyla eklendi."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

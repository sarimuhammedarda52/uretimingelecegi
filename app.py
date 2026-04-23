import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Fotoğrafların kaydedileceği klasör ayarı
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

duyurular = []
sayac = 0

# Fotoğrafları web sitesine (ana sayfaya) servis eden kapı
@app.route('/uploads/<isim>')
def dosya_indir(isim):
    return send_from_directory(app.config["UPLOAD_FOLDER"], isim)

@app.route('/api/duyurular', methods=['GET'])
def duyurulari_getir():
    return jsonify(duyurular)

# YENİ DUYURU EKLEME (FOTOĞRAF YÜKLEME DESTEKLİ)
@app.route('/api/duyuru-ekle', methods=['POST'])
def duyuru_ekle():
    global sayac
    sayac += 1
    
    etiket = request.form.get('etiket', 'Genel')
    baslik = request.form.get('baslik', '')
    metin = request.form.get('metin', '')
    
    gorsel_url = ""
    # Eğer forma dosya eklendiyse onu kaydet
    if 'gorsel' in request.files:
        dosya = request.files['gorsel']
        if dosya.filename != '':
            dosya_adi = secure_filename(dosya.filename)
            dosya_adi = f"{sayac}_{dosya_adi}" # Çakışmayı önlemek için ID ekliyoruz
            dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosya_adi))
            gorsel_url = f"http://127.0.0.1:5000/uploads/{dosya_adi}"
            
    yeni_duyuru = {
        "id": sayac,
        "etiket": etiket,
        "baslik": baslik,
        "metin": metin,
        "gorsel": gorsel_url
    }
    duyurular.insert(0, yeni_duyuru)
    return jsonify({"mesaj": "Duyuru jilet gibi eklendi!"}), 201

# DUYURU DÜZENLEME (GÜNCELLEME) KAPISI
@app.route('/api/duyuru-duzenle/<int:duyuru_id>', methods=['POST'])
def duyuru_duzenle(duyuru_id):
    global duyurular
    for d in duyurular:
        if d['id'] == duyuru_id:
            d['etiket'] = request.form.get('etiket', d['etiket'])
            d['baslik'] = request.form.get('baslik', d['baslik'])
            d['metin'] = request.form.get('metin', d['metin'])
            
            # Eğer düzenlerken yeni bir fotoğraf yüklendiyse eskisinin üstüne yaz
            if 'gorsel' in request.files:
                dosya = request.files['gorsel']
                if dosya.filename != '':
                    dosya_adi = secure_filename(dosya.filename)
                    dosya_adi = f"{duyuru_id}_{dosya_adi}"
                    dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosya_adi))
                    d['gorsel'] = f"http://127.0.0.1:5000/uploads/{dosya_adi}"
                    
            return jsonify({"mesaj": "Duyuru başarıyla güncellendi!"}), 200
    return jsonify({"hata": "Duyuru bulunamadı!"}), 404

@app.route('/api/duyuru-sil/<int:duyuru_id>', methods=['DELETE'])
def duyuru_sil(duyuru_id):
    global duyurular
    duyurular = [d for d in duyurular if d.get('id') != duyuru_id]
    return jsonify({"mesaj": "Duyuru silindi!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
# 🧥 Outfit AI Web Uygulaması

Bu proje, Python Flask kullanılarak geliştirilmiş modern bir kıyafet öneri sistemidir. Visual Studio veya VS Code ile kolayca çalıştırılabilir.

## 🚀 Visual Studio Code (VS Code) ile Çalıştırma

1. **Klasörü Açın**: VS Code'da `Outfit Recommendation AI` klasörünü açın.
2. **Terminali Açın**: `Terminal > New Terminal` menüsünden yeni terminal açın.
3. **Web App Klasörüne Gidin**:
   ```powershell
   cd web-app
   ```
4. **Uygulamayı Başlatın**:
   ```powershell
   python app.py
   ```
5. **Tarayıcıda Açın**: Terminalde çıkan `http://127.0.0.1:5000` linkine tıklayın veya tarayıcınızda açın.

### Alternatif (Run Butonu ile)
VS Code'da `web-app/app.py` dosyasını açıp sağ üstteki **▷ (Play)** butonuna basarak da çalıştırabilirsiniz.

---

## 💜 Visual Studio 2022 ile Çalıştırma

1. **Projeyi Açın**: Visual Studio'da "Open a local folder" seçeneği ile proje klasörünü açın.
2. **Başlangıç Öğesi**: `web-app/app.py` dosyasına sağ tıklayıp "Set as Startup Item" (Başlangıç Öğesi Yap) diyebilirsiniz.
3. **Çalıştır**: Yukarıdaki yeşil "Start" butonuna basın.

---

## 📦 Kurulum (İlk Kez Çalıştırıyorsanız)

Gerekli kütüphaneleri yüklemek için terminalde şunu çalıştırın:
```powershell
pip install -r web-app/requirements.txt
```

# 🧥 Outfit AI Web Uygulaması

Bu proje, Python Flask kullanılarak geliştirilmiş modern bir kıyafet öneri sistemidir. Visual Studio veya VS Code ile kolayca çalıştırılabilir.

## ✅ Yeni (MVP v1) Kişiselleştirme Alanları

Arayüzde "Profile" bölümünden aşağıdaki alanları gönderebilirsin:

- **gender**: `male | female | unisex`
- **age_range**: örn. `18_24 | 25_34 | 35_44 | 45_54 | 55_plus`
- **height_cm**: sayı (cm)
- **weight_kg**: sayı (kg)
- **style**: örn. `casual | sporty | street | classic | formal | minimalist`
- **color_palette**: `neutral | dark | pastel | vibrant`
- **cold_sensitivity**: `cold | normal | warm`
- **event_type**: örn. `daily | work | meeting | sport | special`

Bu alanlar opsiyoneldir. Gönderildiğinde backend 5-8 adet kombin üretir ve `outfits` alanında döndürür.

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

---

## 🔌 API: `/api/predict` (JSON)

### İstek (örnek)

```json
{
  "sicaklik": 20,
  "yagmur": "yok",
  "ruzgar": "zayıf",
  "ortam": "günlük",
  "mevsim": "ilkbahar",

  "gender": "male",
  "age_range": "25_34",
  "height_cm": 180,
  "weight_kg": 80,
  "style": "casual",
  "color_palette": "neutral",
  "cold_sensitivity": "normal",
  "event_type": "daily"
}
```

### Yanıt (özet)

`ml_prediction` ve `rule_prediction` mevcut davranış için korunur.
Kişiselleştirme gönderildiğinde ayrıca `outfits` (liste) döner.

```json
{
  "success": true,
  "ml_prediction": { "outfit": "tişört", "emoji": "👕", "description": "...", "model_name": "..." },
  "rule_prediction": { "outfit": "tişört", "emoji": "👕", "description": "..." },
  "match": false,
  "outfits": [
    {
      "title": "Casual Daily Kombin #1",
      "reasons": ["..."],
      "pieces": [
        {
          "category": "top",
          "key": "top_tshirt",
          "label": "Tişört",
          "image": "/static/images/outfits/tisort.png",
          "shop_link": "https://www.boyner.com.tr/search?q=erkek%20daily%20bej%20ti%C5%9F%C3%B6rt",
          "link": "https://www.boyner.com.tr/search?q=erkek%20daily%20bej%20ti%C5%9F%C3%B6rt"
        }
      ],
      "meta": { "base_outfit": "tişört", "mevsim": "ilkbahar", "ortam": "günlük", "bmi": 24.7 }
    }
  ]
}
```

---

## 🧪 Testler

Testler `outfit-ai/tests` altında bulunur.

```powershell
pytest -q
```

# 🧥 Outfit AI - Akıllı Kıyafet Öneri Sistemi

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.2+-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Makine Öğrenimi ve Kural Tabanlı Hibrit Kıyafet Öneri Sistemi**

</div>

---

## 📋 Proje Hakkında

Bu proje, hava durumu koşullarına göre akıllı kıyafet önerisi yapan bir yapay zeka sistemidir. Hem **Makine Öğrenimi** hem de **Kural Tabanlı** yaklaşımları kullanarak kullanıcıya en uygun kıyafeti önerir.

### ✨ Özellikler

- 🤖 **3 Farklı ML Modeli**: Decision Tree, Random Forest, Gradient Boosting
- 📊 **Cross-Validation**: 5-fold CV ile model değerlendirme
- 🎯 **Hibrit Öneri**: ML + Kural tabanlı karşılaştırmalı sonuç
- 🌐 **Web Arayüzü**: Modern Streamlit dashboard
- 📝 **Kapsamlı Logging**: Tüm işlemler loglanır
- ✅ **Unit Testler**: Pytest ile test coverage

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)

### Adımlar

```bash
# 1. Proje klasörüne git
cd outfit-ai

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Modeli eğit (ilk kullanımda)
python model_comparison.py
```

---

## 💻 Kullanım

### Web Arayüzü (Önerilen)

```bash
streamlit run app.py
```

Tarayıcınızda otomatik olarak `http://localhost:8501` açılacaktır.

### Komut Satırı

```bash
# Tahmin yap
python predict_outfit.py

# Sadece kural tabanlı sistem
python rules_baseline.py
```

---

## 📁 Proje Yapısı

```
outfit-ai/
├── 📊 data/
│   └── weather_outfit.csv    # Eğitim veri seti (200+ örnek)
├── 🤖 models/
│   ├── outfit_model.pkl      # Decision Tree modeli
│   └── best_model.pkl        # En iyi model (otomatik seçim)
├── 🛠️ utils/
│   └── logger.py             # Logging sistemi
├── 🧪 tests/
│   └── test_outfit.py        # Unit testler
├── 📄 logs/                   # Log dosyaları
├── app.py                     # Streamlit web arayüzü
├── config.py                  # Merkezi konfigürasyon
├── model_comparison.py        # Multi-model karşılaştırma
├── train_model.py             # Model eğitimi
├── predict_outfit.py          # Tahmin scripti
├── rules_baseline.py          # Kural tabanlı sistem
├── requirements.txt           # Bağımlılıklar
└── README.md                  # Bu dosya
```

---

## 🎯 Model Performansı

| Model | Cross-Val Accuracy | Test Accuracy |
|-------|-------------------|---------------|
| Decision Tree | ~85% | ~83% |
| Random Forest | ~88% | ~86% |
| Gradient Boosting | ~87% | ~85% |

> *Performans değerleri veri setine göre değişebilir.*

---

## 🧪 Testleri Çalıştırma

```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# Belirli bir test sınıfını çalıştır
python -m pytest tests/test_outfit.py::TestRuleBasedOutfit -v
```

---

## 📊 Veri Seti Özellikleri

| Özellik | Değerler |
|---------|----------|
| `sicaklik` | -20 ile 45 arası (°C) |
| `yagmur` | var, yok |
| `ruzgar` | zayıf, orta, kuvvetli |
| `ortam` | günlük, okul, özel |
| `mevsim` | kış, ilkbahar, yaz, sonbahar |
| `kiyafet` | 13 farklı kıyafet kombinasyonu |

---

## 🔧 Konfigürasyon

Tüm ayarlar `config.py` dosyasında bulunur:

- Sıcaklık eşikleri
- Model parametreleri
- Dosya yolları
- Streamlit ayarları

---

## 📸 Ekran Görüntüleri

### Web Arayüzü
- Modern gradient tasarım
- Emoji destekli kıyafet gösterimi
- ML ve Kural tabanlı yan yana karşılaştırma

---

## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/yenilik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yenilik`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

<div align="center">

**🎓 Makine Öğrenimi Projesi**

Made with ❤️ for Education

</div>

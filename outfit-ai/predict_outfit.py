"""
predict_outfit.py
ML modeli ve kural tabanlı sistem ile kıyafet tahmini yapar.
Her iki yöntemin sonuçlarını karşılaştırmalı olarak gösterir.
"""

import pandas as pd
import joblib
import os
import sys

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    MODEL_FILE, BEST_MODEL_FILE, 
    OUTFIT_EMOJIS, OUTFIT_DESCRIPTIONS,
    YAGMUR_OPTIONS, RUZGAR_OPTIONS, ORTAM_OPTIONS, MEVSIM_OPTIONS
)
from rules_baseline import rule_based_outfit, get_outfit_emoji, get_outfit_description
from utils.logger import get_prediction_logger


def load_model():
    """
    Eğitilmiş modeli yükler. Önce best_model.pkl, yoksa outfit_model.pkl dener.
    """
    logger = get_prediction_logger()
    
    # Önce en iyi modeli dene
    if os.path.exists(BEST_MODEL_FILE):
        logger.info(f"En iyi model yükleniyor: {BEST_MODEL_FILE}")
        return joblib.load(BEST_MODEL_FILE), "En İyi Model"
    
    # Fallback: Standart model
    if os.path.exists(MODEL_FILE):
        logger.info(f"Standart model yükleniyor: {MODEL_FILE}")
        return joblib.load(MODEL_FILE), "Decision Tree"
    
    print("❌ Hata: Model dosyası bulunamadı!")
    print("   Önce 'python model_comparison.py' veya 'python train_model.py' çalıştırın.")
    return None, None


def predict_with_model(model, sicaklik: int, yagmur: str, ruzgar: str, ortam: str, mevsim: str) -> str:
    """
    ML modeli ile tahmin yapar.
    """
    # Girdiyi DataFrame formatına çevir
    input_data = pd.DataFrame({
        'sicaklik': [sicaklik],
        'yagmur': [yagmur],
        'ruzgar': [ruzgar],
        'ortam': [ortam],
        'mevsim': [mevsim]
    })
    
    # Tahmin yap
    prediction = model.predict(input_data)
    return prediction[0]


def get_season_from_temp(sicaklik: int) -> str:
    """Sıcaklığa göre tahmini mevsim döndürür."""
    if sicaklik < 5:
        return "kış"
    elif sicaklik < 15:
        return "sonbahar"
    elif sicaklik < 25:
        return "ilkbahar"
    else:
        return "yaz"


def display_result(outfit: str, method: str):
    """Sonucu güzel formatta gösterir."""
    emoji = get_outfit_emoji(outfit)
    desc = get_outfit_description(outfit)
    print(f"   {method}: {emoji} {outfit}")
    print(f"      └─ {desc}")


def main():
    """
    Ana fonksiyon: Kullanıcıdan girdi alır ve tahminleri gösterir.
    """
    logger = get_prediction_logger()
    
    print("\n" + "="*70)
    print("🧥 AKILLI KIYaFET ÖNERİ SİSTEMİ")
    print("   ML Model & Kural Tabanlı Karşılaştırma")
    print("="*70)
    
    # Modeli yükle
    model, model_name = load_model()
    if model is None:
        return
    
    print(f"\n✓ Model yüklendi: {model_name}")
    
    try:
        # Kullanıcıdan girdi al
        print("\n" + "-"*70)
        print("📝 Lütfen hava durumu bilgilerini girin:")
        print("-"*70)
        
        sicaklik = int(input("🌡️  Sıcaklık (°C): "))
        yagmur = input("🌧️  Yağmur (var/yok): ").strip().lower()
        ruzgar = input("💨 Rüzgar (zayıf/orta/kuvvetli): ").strip().lower()
        ortam = input("📍 Ortam (günlük/okul/özel): ").strip().lower()
        
        # Mevsim otomatik veya manuel
        mevsim_input = input("🗓️  Mevsim (kış/ilkbahar/yaz/sonbahar) [Enter=otomatik]: ").strip().lower()
        if mevsim_input in MEVSIM_OPTIONS:
            mevsim = mevsim_input
        else:
            mevsim = get_season_from_temp(sicaklik)
            print(f"   → Otomatik mevsim: {mevsim}")
        
        # Girdi doğrulama
        errors = []
        if yagmur not in YAGMUR_OPTIONS:
            errors.append("Yağmur 'var' veya 'yok' olmalıdır.")
        if ruzgar not in RUZGAR_OPTIONS:
            errors.append("Rüzgar 'zayıf', 'orta' veya 'kuvvetli' olmalıdır.")
        if ortam not in ORTAM_OPTIONS:
            errors.append("Ortam 'günlük', 'okul' veya 'özel' olmalıdır.")
        
        if errors:
            for err in errors:
                print(f"❌ Hata: {err}")
            return
        
        # Log the prediction request
        logger.info(f"Tahmin isteği: sicaklik={sicaklik}, yagmur={yagmur}, ruzgar={ruzgar}, ortam={ortam}, mevsim={mevsim}")
        
        # ML modeli ile tahmin
        ml_tahmin = predict_with_model(model, sicaklik, yagmur, ruzgar, ortam, mevsim)
        
        # Kural tabanlı tahmin
        kural_tahmin = rule_based_outfit(sicaklik, yagmur, ruzgar, ortam)
        
        # Log predictions
        logger.info(f"ML Tahmin: {ml_tahmin}, Kural Tahmin: {kural_tahmin}")
        
        # Sonuçları göster
        print("\n" + "="*70)
        print("🎯 TAHMİN SONUÇLARI")
        print("="*70)
        
        print(f"\n📊 Girdi: {sicaklik}°C, Yağmur: {yagmur}, Rüzgar: {ruzgar}, Ortam: {ortam}, Mevsim: {mevsim}")
        print()
        
        display_result(ml_tahmin, f"🤖 {model_name}")
        print()
        display_result(kural_tahmin, "📋 Kural Tabanlı")
        
        print("\n" + "-"*70)
        
        # Eşleşme durumunu göster
        if ml_tahmin == kural_tahmin:
            print("✅ Mükemmel! Her iki yöntem de aynı sonuca ulaştı!")
        else:
            print("ℹ️  Yöntemler farklı öneriler sunuyor.")
            print("   ML modeli, veri setindeki kalıpları öğrenirken,")
            print("   kural tabanlı sistem sabit kurallar uygular.")
        
        print("="*70)
    
    except ValueError:
        print("❌ Hata: Geçerli bir sıcaklık değeri giriniz.")
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {e}")
        print(f"❌ Beklenmeyen hata: {e}")


if __name__ == "__main__":
    main()

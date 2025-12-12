"""
rules_baseline.py
Kural tabanlı kıyafet öneri sistemi.
Sıcaklık, yağmur, rüzgar ve ortam durumuna göre kıyafet önerisi yapar.
"""

import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TEMP_THRESHOLDS, OUTFIT_EMOJIS, OUTFIT_DESCRIPTIONS


def rule_based_outfit(sicaklik: int, yagmur: str, ruzgar: str, ortam: str = "günlük") -> str:
    """
    Kural tabanlı kıyafet önerisi yapar.
    
    Args:
        sicaklik: Hava sıcaklığı (Celsius)
        yagmur: "var" veya "yok"
        ruzgar: "zayıf", "orta" veya "kuvvetli"
        ortam: "günlük", "okul" veya "özel"
    
    Returns:
        Önerilen kıyafet
    """
    # Özel ortam için farklı öneri
    if ortam == "özel":
        base_outfit = "gömlek_pantolon"
        if yagmur == "var":
            return base_outfit + "_şemsiye"
        return base_outfit
    
    # Sıcaklığa göre temel kıyafet seç
    if sicaklik < TEMP_THRESHOLDS['çok_soğuk']:
        kiyafet = "kalın_mont"
    elif sicaklik < TEMP_THRESHOLDS['soğuk']:
        kiyafet = "mont"
    elif sicaklik < TEMP_THRESHOLDS['serin']:
        kiyafet = "sweatshirt"
    elif sicaklik < TEMP_THRESHOLDS['ılık']:
        kiyafet = "tişört"
    else:
        kiyafet = "tişört_şort"
    
    # Rüzgar kuvvetliyse ve hafif giysilerdeyse → daha kalın giysi
    if ruzgar == "kuvvetli":
        if kiyafet == "tişört" or kiyafet == "tişört_şort":
            kiyafet = "sweatshirt"
        elif kiyafet == "sweatshirt":
            kiyafet = "mont"
    
    # Yağmur varsa ve serin hava + yağmur → yağmurluk
    if yagmur == "var":
        if kiyafet == "sweatshirt" and 12 <= sicaklik < 18:
            kiyafet = "yağmurluk"
        else:
            kiyafet = kiyafet + "_şemsiye"
    
    return kiyafet


def get_outfit_emoji(outfit: str) -> str:
    """Kıyafet için emoji döndürür."""
    return OUTFIT_EMOJIS.get(outfit, "👔")


def get_outfit_description(outfit: str) -> str:
    """Kıyafet için açıklama döndürür."""
    return OUTFIT_DESCRIPTIONS.get(outfit, "Önerilen kıyafet")


if __name__ == "__main__":
    print("="*60)
    print("🧥 Kural Tabanlı Kıyafet Öneri Sistemi")
    print("="*60)
    
    try:
        sicaklik = int(input("\n🌡️  Sıcaklık (°C): "))
        yagmur = input("🌧️  Yağmur (var/yok): ").strip().lower()
        ruzgar = input("💨 Rüzgar (zayıf/orta/kuvvetli): ").strip().lower()
        ortam = input("📍 Ortam (günlük/okul/özel): ").strip().lower()
        
        # Girdi doğrulama
        if yagmur not in ["var", "yok"]:
            print("❌ Hata: Yağmur 'var' veya 'yok' olmalıdır.")
        elif ruzgar not in ["zayıf", "orta", "kuvvetli"]:
            print("❌ Hata: Rüzgar 'zayıf', 'orta' veya 'kuvvetli' olmalıdır.")
        elif ortam not in ["günlük", "okul", "özel"]:
            print("❌ Hata: Ortam 'günlük', 'okul' veya 'özel' olmalıdır.")
        else:
            sonuc = rule_based_outfit(sicaklik, yagmur, ruzgar, ortam)
            emoji = get_outfit_emoji(sonuc)
            aciklama = get_outfit_description(sonuc)
            
            print("\n" + "="*60)
            print(f"🎯 Önerilen Kıyafet: {sonuc}")
            print(f"   {emoji} {aciklama}")
            print("="*60)
    
    except ValueError:
        print("❌ Hata: Geçerli bir sıcaklık değeri giriniz.")

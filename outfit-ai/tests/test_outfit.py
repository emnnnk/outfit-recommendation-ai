"""
test_outfit.py
Kıyafet Öneri Sistemi için Unit Testler
"""

import pytest
import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules_baseline import rule_based_outfit, get_outfit_emoji, get_outfit_description
from config import OUTFIT_EMOJIS, TEMP_THRESHOLDS


class TestRuleBasedOutfit:
    """Kural tabanlı sistem testleri."""
    
    def test_very_cold_weather(self):
        """Çok soğuk havada kalın mont önerilmeli."""
        result = rule_based_outfit(-10, "yok", "zayıf", "günlük")
        assert result == "kalın_mont"
    
    def test_very_cold_with_rain(self):
        """Çok soğuk ve yağmurlu havada kalın mont + şemsiye."""
        result = rule_based_outfit(-5, "var", "zayıf", "günlük")
        assert result == "kalın_mont_şemsiye"
    
    def test_cold_weather(self):
        """Soğuk havada mont önerilmeli."""
        result = rule_based_outfit(8, "yok", "zayıf", "günlük")
        assert result == "mont"
    
    def test_mild_weather(self):
        """Ilık havada sweatshirt önerilmeli."""
        result = rule_based_outfit(15, "yok", "zayıf", "günlük")
        assert result == "sweatshirt"
    
    def test_warm_weather(self):
        """Sıcak havada tişört önerilmeli."""
        result = rule_based_outfit(22, "yok", "zayıf", "günlük")
        assert result == "tişört"
    
    def test_hot_weather(self):
        """Çok sıcak havada tişört + şort önerilmeli."""
        result = rule_based_outfit(35, "yok", "zayıf", "günlük")
        assert result == "tişört_şort"
    
    def test_rain_adds_umbrella(self):
        """Yağmur varken şemsiye eklenmeli."""
        result = rule_based_outfit(20, "var", "zayıf", "günlük")
        assert "_şemsiye" in result
    
    def test_strong_wind_upgrades_outfit(self):
        """Kuvvetli rüzgarda daha kalın kıyafet önerilmeli."""
        # Tişört → sweatshirt olmalı
        result = rule_based_outfit(23, "yok", "kuvvetli", "günlük")
        assert result == "sweatshirt"
    
    def test_special_occasion(self):
        """Özel günde gömlek pantolon önerilmeli."""
        result = rule_based_outfit(20, "yok", "zayıf", "özel")
        assert result == "gömlek_pantolon"
    
    def test_special_occasion_with_rain(self):
        """Özel gün + yağmur → gömlek pantolon + şemsiye."""
        result = rule_based_outfit(20, "var", "zayıf", "özel")
        assert result == "gömlek_pantolon_şemsiye"
    
    def test_raincoat_specific_condition(self):
        """Yağmurluk belirli koşullarda önerilmeli."""
        result = rule_based_outfit(14, "var", "zayıf", "günlük")
        assert result == "yağmurluk"


class TestOutfitEmojis:
    """Emoji fonksiyonu testleri."""
    
    def test_emoji_for_known_outfit(self):
        """Bilinen kıyafetler için emoji döndürmeli."""
        emoji = get_outfit_emoji("kalın_mont")
        assert emoji == OUTFIT_EMOJIS["kalın_mont"]
    
    def test_emoji_for_unknown_outfit(self):
        """Bilinmeyen kıyafetler için varsayılan emoji."""
        emoji = get_outfit_emoji("bilinmeyen_kiyafet")
        assert emoji == "👔"


class TestOutfitDescriptions:
    """Açıklama fonksiyonu testleri."""
    
    def test_description_for_known_outfit(self):
        """Bilinen kıyafetler için açıklama döndürmeli."""
        desc = get_outfit_description("kalın_mont")
        assert "soğuk" in desc.lower() or "kış" in desc.lower()
    
    def test_description_for_unknown_outfit(self):
        """Bilinmeyen kıyafetler için varsayılan açıklama."""
        desc = get_outfit_description("bilinmeyen_kiyafet")
        assert desc == "Önerilen kıyafet"


class TestTemperatureThresholds:
    """Sıcaklık eşikleri testleri."""
    
    def test_thresholds_are_ordered(self):
        """Sıcaklık eşikleri sıralı olmalı."""
        thresholds = list(TEMP_THRESHOLDS.values())
        assert thresholds == sorted(thresholds)
    
    def test_all_thresholds_exist(self):
        """Tüm gerekli eşikler tanımlı olmalı."""
        required = ['çok_soğuk', 'soğuk', 'serin', 'ılık', 'sıcak']
        for key in required:
            assert key in TEMP_THRESHOLDS


class TestEdgeCases:
    """Sınır değerler testleri."""
    
    def test_zero_temperature(self):
        """0°C'de sistem çalışmalı."""
        result = rule_based_outfit(0, "yok", "zayıf", "günlük")
        assert result in ["kalın_mont", "mont"]
    
    def test_extreme_cold(self):
        """-20°C gibi aşırı soğukta sistem çalışmalı."""
        result = rule_based_outfit(-20, "yok", "kuvvetli", "günlük")
        assert result == "kalın_mont"
    
    def test_extreme_hot(self):
        """45°C gibi aşırı sıcakta sistem çalışmalı."""
        result = rule_based_outfit(45, "yok", "zayıf", "günlük")
        assert result == "tişört_şort"
    
    def test_boundary_temperature_5(self):
        """5°C sınır değerinde doğru kıyafet."""
        result = rule_based_outfit(5, "yok", "zayıf", "günlük")
        assert result == "mont"  # 5°C >= çok_soğuk threshold
    
    def test_boundary_temperature_12(self):
        """12°C sınır değerinde doğru kıyafet."""
        result = rule_based_outfit(12, "yok", "zayıf", "günlük")
        assert result == "sweatshirt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

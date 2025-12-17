"""
test_outfit.py
Kıyafet Öneri Sistemi için Unit Testler
"""

import pytest
import sys
import os
import importlib.util

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules_baseline import rule_based_outfit, get_outfit_emoji, get_outfit_description
from config import OUTFIT_EMOJIS, TEMP_THRESHOLDS
from personalized_recommendations import UserProfile, compute_bmi, generate_outfit_recommendations


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


class TestPersonalizedRecommendations:
    def test_compute_bmi_valid(self):
        bmi = compute_bmi(180, 81)
        assert bmi is not None
        assert 24.0 < bmi < 26.0

    def test_compute_bmi_invalid(self):
        assert compute_bmi(None, 70) is None
        assert compute_bmi(0, 70) is None
        assert compute_bmi(170, None) is None
        assert compute_bmi(170, 0) is None

    def test_generate_outfits_schema_minimal(self):
        profile = UserProfile(
            gender="male",
            age_range="25_34",
            height_cm=180,
            weight_kg=80,
            style="casual",
            color_palette="neutral",
            cold_sensitivity="normal",
            event_type="daily",
        )

        outfits = generate_outfit_recommendations(
            base_outfit="tişört",
            sicaklik=22,
            yagmur="yok",
            ruzgar="zayıf",
            mevsim="ilkbahar",
            ortam="günlük",
            profile=profile,
            count=6,
        )

        assert isinstance(outfits, list)
        assert 3 <= len(outfits) <= 8

        first = outfits[0]
        assert isinstance(first.get("title"), str)
        assert isinstance(first.get("reasons"), list)
        assert isinstance(first.get("pieces"), list)
        assert len(first.get("pieces")) >= 3

        for piece in first["pieces"]:
            assert "category" in piece
            assert "key" in piece
            assert "label" in piece
            assert "image" in piece
            assert "link" in piece

            assert piece["image"].startswith("/static/images/outfits/")
            assert piece["link"].startswith("https://www.trendyol.com/sr?q=")

    def test_generate_outfits_rain_includes_umbrella_piece(self):
        profile = UserProfile(style="street", color_palette="dark")
        outfits = generate_outfit_recommendations(
            base_outfit="yağmurluk",
            sicaklik=15,
            yagmur="var",
            ruzgar="zayıf",
            mevsim="sonbahar",
            ortam="günlük",
            profile=profile,
            count=5,
        )

        assert len(outfits) >= 3
        has_umbrella = any(
            any((p.get("key") or "").find("umbrella") >= 0 for p in o.get("pieces", []))
            for o in outfits
        )
        assert has_umbrella


class TestWebAppPredictEndpoint:
    def test_api_predict_returns_outfits_and_backward_compat_fields(self):
        pytest.importorskip("flask")

        tests_dir = os.path.dirname(os.path.abspath(__file__))
        outfit_ai_dir = os.path.dirname(tests_dir)
        project_root = os.path.dirname(outfit_ai_dir)
        web_app_path = os.path.join(project_root, "web-app", "app.py")

        spec = importlib.util.spec_from_file_location("web_app_app", web_app_path)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        client = module.app.test_client()

        payload = {
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
            "event_type": "daily",
        }

        resp = client.post("/api/predict", json=payload)
        assert resp.status_code == 200

        data = resp.get_json()
        assert data["success"] is True

        assert "ml_prediction" in data
        assert "rule_prediction" in data
        assert "match" in data

        assert isinstance(data.get("outfits"), list)
        assert len(data["outfits"]) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
config.py
Kıyafet Öneri Sistemi - Merkezi Konfigürasyon Dosyası
Tüm sabitler, eşikler ve model parametreleri burada tanımlanır.
"""

import os

# ============================================
# DOSYA YOLLARI
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

DATA_FILE = os.path.join(DATA_DIR, 'weather_outfit.csv')
MODEL_FILE = os.path.join(MODELS_DIR, 'outfit_model.pkl')
BEST_MODEL_FILE = os.path.join(MODELS_DIR, 'best_model.pkl')

# ============================================
# SICAKLIK EŞİKLERİ (°C)
# ============================================
TEMP_THRESHOLDS = {
    'çok_soğuk': 5,      # < 5°C → kalın_mont
    'soğuk': 12,         # 5-12°C → mont
    'serin': 20,         # 12-20°C → sweatshirt
    'ılık': 28,          # 20-28°C → tişört
    'sıcak': 100         # >= 28°C → tişört_şort
}

# ============================================
# KATEGORİK DEĞİŞKENLER
# ============================================
YAGMUR_OPTIONS = ['var', 'yok']
RUZGAR_OPTIONS = ['zayıf', 'orta', 'kuvvetli']
ORTAM_OPTIONS = ['günlük', 'okul', 'özel']
MEVSIM_OPTIONS = ['kış', 'ilkbahar', 'yaz', 'sonbahar']

# ============================================
# KIYAFET KARŞILIKLARI (Görsel için)
# ============================================
OUTFIT_EMOJIS = {
    'kalın_mont': '🧥❄️',
    'kalın_mont_şemsiye': '🧥❄️☂️',
    'mont': '🧥',
    'mont_şemsiye': '🧥☂️',
    'sweatshirt': '👕',
    'sweatshirt_şemsiye': '👕☂️',
    'tişört': '👔',
    'tişört_şemsiye': '👔☂️',
    'tişört_şort': '👔🩳',
    'tişört_şort_şemsiye': '👔🩳☂️',
    'yağmurluk': '🧥🌧️',
    'gömlek_pantolon': '👔👖',
    'gömlek_pantolon_şemsiye': '👔👖☂️'
}

# ============================================
# KIYAFET AÇIKLAMALARI
# ============================================
OUTFIT_DESCRIPTIONS = {
    'kalın_mont': 'Kalın kışlık mont - Çok soğuk havalar için',
    'kalın_mont_şemsiye': 'Kalın mont + Şemsiye - Soğuk ve yağmurlu',
    'mont': 'Orta kalınlıkta mont - Serin havalar için',
    'mont_şemsiye': 'Mont + Şemsiye - Serin ve yağmurlu',
    'sweatshirt': 'Sweatshirt/Kazak - Hafif serin havalar',
    'sweatshirt_şemsiye': 'Sweatshirt + Şemsiye - Ilık ama yağmurlu',
    'tişört': 'Tişört - Güzel ve ılık havalar',
    'tişört_şemsiye': 'Tişört + Şemsiye - Sıcak ama yağmurlu',
    'tişört_şort': 'Tişört ve Şort - Sıcak yaz günleri',
    'tişört_şort_şemsiye': 'Tişört, Şort + Şemsiye - Sıcak ve yağmurlu',
    'yağmurluk': 'Yağmurluk - Ilık ve yağmurlu havalar',
    'gömlek_pantolon': 'Gömlek ve Pantolon - Özel günler için',
    'gömlek_pantolon_şemsiye': 'Gömlek, Pantolon + Şemsiye - Özel gün, yağmurlu'
}

# ============================================
# MODEL PARAMETRELERİ
# ============================================
MODEL_PARAMS = {
    'decision_tree': {
        'max_depth': 8,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42
    },
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42,
        'n_jobs': -1
    },
    'gradient_boosting': {
        'n_estimators': 100,
        'max_depth': 5,
        'learning_rate': 0.1,
        'random_state': 42
    }
}

# ============================================
# EĞİTİM AYARLARI
# ============================================
TRAINING_CONFIG = {
    'test_size': 0.2,
    'cv_folds': 5,
    'random_state': 42
}

# ============================================
# ÖZELLİK SÜTUNLARI
# ============================================
FEATURE_COLUMNS = ['sicaklik', 'yagmur', 'ruzgar', 'ortam', 'mevsim']
CATEGORICAL_FEATURES = ['yagmur', 'ruzgar', 'ortam', 'mevsim']
NUMERIC_FEATURES = ['sicaklik']
TARGET_COLUMN = 'kiyafet'

# ============================================
# STREAMLIT AYARLARI
# ============================================
STREAMLIT_CONFIG = {
    'page_title': '🧥 Akıllı Kıyafet Öneri Sistemi',
    'page_icon': '👔',
    'layout': 'wide',
    'temp_min': -20,
    'temp_max': 45,
    'temp_default': 20
}

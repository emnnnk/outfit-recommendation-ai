"""
app.py
Modern Flask Backend - Akıllı Kıyafet Öneri Sistemi
Animasyonlu hava durumu ve premium UI için API sunucusu.
"""

from flask import Flask, render_template, jsonify, request
import sys
import os

# Outfit-ai modüllerini import et
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outfit-ai'))

try:
    from config import (
        OUTFIT_EMOJIS, OUTFIT_DESCRIPTIONS,
        YAGMUR_OPTIONS, RUZGAR_OPTIONS, ORTAM_OPTIONS, MEVSIM_OPTIONS
    )
    from rules_baseline import rule_based_outfit
    from utils.weather_api import get_weather_wttr, get_weather_emoji, TURKEY_CITIES
    import joblib
    import pandas as pd
    
    # Model dosyaları
    MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outfit-ai', 'models')
    BEST_MODEL_FILE = os.path.join(MODELS_DIR, 'best_model.pkl')
    MODEL_FILE = os.path.join(MODELS_DIR, 'outfit_model.pkl')
except ImportError as e:
    print(f"Import hatası: {e}")
    OUTFIT_EMOJIS = {}
    OUTFIT_DESCRIPTIONS = {}

app = Flask(__name__)

# Model cache
_model = None
_model_name = None


def load_model():
    """Modeli yükle ve cache'le."""
    global _model, _model_name
    
    if _model is not None:
        return _model, _model_name
    
    if os.path.exists(BEST_MODEL_FILE):
        _model = joblib.load(BEST_MODEL_FILE)
        _model_name = "En İyi Model (Multi-Model)"
    elif os.path.exists(MODEL_FILE):
        _model = joblib.load(MODEL_FILE)
        _model_name = "Decision Tree"
    else:
        _model = None
        _model_name = None
    
    return _model, _model_name


@app.route('/')
def index():
    """Ana sayfa."""
    return render_template('index.html', cities=TURKEY_CITIES)


@app.route('/api/weather/<city>')
def get_weather(city):
    """Hava durumu API endpoint."""
    try:
        weather_data = get_weather_wttr(city)
        if weather_data:
            weather_data['emoji'] = get_weather_emoji(weather_data.get('weather_main', ''))
            return jsonify({"success": True, "data": weather_data})
        else:
            return jsonify({"success": False, "error": "Hava durumu alınamadı"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """Kıyafet tahmini endpoint."""
    try:
        data = request.get_json()
        
        sicaklik = int(data.get('sicaklik', 20))
        yagmur = data.get('yagmur', 'yok')
        ruzgar = data.get('ruzgar', 'zayıf')
        ortam = data.get('ortam', 'günlük')
        mevsim = data.get('mevsim', 'ilkbahar')
        
        # ML Tahmini
        model, model_name = load_model()
        ml_prediction = None
        
        if model is not None:
            input_data = pd.DataFrame({
                'sicaklik': [sicaklik],
                'yagmur': [yagmur],
                'ruzgar': [ruzgar],
                'ortam': [ortam],
                'mevsim': [mevsim]
            })
            ml_prediction = model.predict(input_data)[0]
        
        # Kural tabanlı tahmin
        rule_prediction = rule_based_outfit(sicaklik, yagmur, ruzgar, ortam)
        
        # Sonuç
        result = {
            "success": True,
            "ml_prediction": {
                "outfit": ml_prediction,
                "emoji": OUTFIT_EMOJIS.get(ml_prediction, "👔"),
                "description": OUTFIT_DESCRIPTIONS.get(ml_prediction, "Önerilen kıyafet"),
                "model_name": model_name
            } if ml_prediction else None,
            "rule_prediction": {
                "outfit": rule_prediction,
                "emoji": OUTFIT_EMOJIS.get(rule_prediction, "👔"),
                "description": OUTFIT_DESCRIPTIONS.get(rule_prediction, "Önerilen kıyafet")
            },
            "match": ml_prediction == rule_prediction if ml_prediction else False
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/cities')
def get_cities():
    """Şehir listesi."""
    return jsonify({"success": True, "cities": TURKEY_CITIES})


if __name__ == '__main__':
    print("Akilli Kiyafet Oneri Sistemi - Modern Web App")
    print("http://localhost:5000 adresinde baslatiliyor...")
    app.run(debug=True, port=5000)

"""
app.py
Modern Flask Backend - Akıllı Kıyafet Öneri Sistemi
Animasyonlu hava durumu ve premium UI için API sunucusu.
"""

from flask import Flask, render_template, jsonify, request
import json
import sys
import os
from typing import Any, Dict, Optional, Tuple

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
    import numpy as np
    import pandas as pd
    from personalized_recommendations import UserProfile, generate_outfit_recommendations
    
    # Model dosyaları
    MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'outfit-ai', 'models')
    BEST_MODEL_FILE = os.path.join(MODELS_DIR, 'best_model.pkl')
    MODEL_FILE = os.path.join(MODELS_DIR, 'outfit_model.pkl')
    XGB_MODEL_FILE = os.path.join(MODELS_DIR, 'xgb_model.pkl')
    MLP_MODEL_FILE = os.path.join(MODELS_DIR, 'mlp_model.pkl')
    METRICS_FILE = os.path.join(MODELS_DIR, 'metrics.json')
except ImportError as e:
    print(f"Import hatası: {e}")
    OUTFIT_EMOJIS = {}
    OUTFIT_DESCRIPTIONS = {}
    UserProfile = None
    generate_outfit_recommendations = None

app = Flask(__name__)

# Model cache
_model = None
_model_name = None

_model_cache: Dict[str, Any] = {}
_metrics_cache: Optional[Dict[str, Any]] = None


def load_model():
    """Modeli yükle ve cache'le."""
    global _model, _model_name
    
    if _model is not None:
        return _model, _model_name

    if os.path.exists(BEST_MODEL_FILE):
        _model = joblib.load(BEST_MODEL_FILE)
        _model_name = "En İyi Model"
    elif os.path.exists(MODEL_FILE):
        _model = joblib.load(MODEL_FILE)
        _model_name = "Decision Tree"
    else:
        _model = None
        _model_name = None

    return _model, _model_name


def load_metrics() -> Optional[Dict[str, Any]]:
    global _metrics_cache

    if _metrics_cache is not None:
        return _metrics_cache

    try:
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, 'r', encoding='utf-8') as f:
                _metrics_cache = json.load(f)
            return _metrics_cache
    except Exception:
        return None

    return None


def load_model_by_key(model_key: str) -> Tuple[Optional[Any], Optional[str]]:
    """Load a specific model pipeline by key.

    model_key: best | xgboost | mlp
    """
    key = (model_key or '').lower().strip()
    if key in _model_cache:
        return _model_cache[key], key

    path = None
    if key == 'xgboost':
        path = XGB_MODEL_FILE
    elif key == 'mlp':
        path = MLP_MODEL_FILE
    else:
        path = BEST_MODEL_FILE if os.path.exists(BEST_MODEL_FILE) else MODEL_FILE
        key = 'best'

    if path and os.path.exists(path):
        try:
            model = joblib.load(path)
            _model_cache[key] = model
            return model, key
        except Exception:
            return None, None

    return None, None


def _predict_with_model(model: Any, input_data: 'pd.DataFrame') -> Tuple[Optional[str], Optional[float], Optional[list]]:
    try:
        pred = model.predict(input_data)[0]
    except Exception:
        return None, None, None

    proba = None
    top2 = None
    try:
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(input_data)[0]
            classes = list(getattr(model, 'classes_', []))
            if classes and len(classes) == len(probs):
                idx = int(np.argmax(probs))
                proba = float(probs[idx])
                pairs = sorted(zip(classes, probs), key=lambda x: float(x[1]), reverse=True)[:2]
                top2 = [{"outfit": str(c), "confidence": float(p)} for c, p in pairs]
    except Exception:
        proba = None
        top2 = None

    return str(pred) if pred is not None else None, proba, top2


def _rules_explanation(*, sicaklik: int, yagmur: str, ruzgar: str, ortam: str) -> str:
    parts = []
    if ortam == 'özel':
        parts.append('Özel ortam için gömlek/pantolon temelli kural uygulanır.')
    if sicaklik < 5:
        parts.append('Sıcaklık çok düşük olduğu için kalın katman önerilir.')
    elif sicaklik < 12:
        parts.append('Soğuk hava için mont önerisi.')
    elif sicaklik < 20:
        parts.append('Serin hava için sweatshirt önerisi.')
    elif sicaklik < 28:
        parts.append('Ilık hava için tişört önerisi.')
    else:
        parts.append('Sıcak hava için tişört/şort önerisi.')

    if ruzgar == 'kuvvetli':
        parts.append('Kuvvetli rüzgâr nedeniyle daha kalın katman tercih edilir.')
    if yagmur == 'var':
        parts.append('Yağış ihtimali nedeniyle şemsiye/yağmurluk eklenir.')

    return ' '.join(parts)[:240]


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


@app.route('/api/model-metrics')
def get_model_metrics():
    try:
        metrics = load_metrics()
        if metrics is None:
            return jsonify({"success": False, "error": "metrics.json bulunamadı"}), 404
        return jsonify({"success": True, "metrics": metrics})
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

        model_choice: str = (data.get('model') or data.get('model_choice') or 'best')

        gender: Optional[str] = data.get('gender')
        age_range: Optional[str] = data.get('age_range')
        height_cm = data.get('height_cm')
        weight_kg = data.get('weight_kg')
        style: Optional[str] = data.get('style')
        color_palette: Optional[str] = data.get('color_palette')
        cold_sensitivity: Optional[str] = data.get('cold_sensitivity')
        event_type: Optional[str] = data.get('event_type')

        try:
            height_cm = float(height_cm) if height_cm not in (None, "") else None
        except Exception:
            height_cm = None

        try:
            weight_kg = float(weight_kg) if weight_kg not in (None, "") else None
        except Exception:
            weight_kg = None
        
        input_data = pd.DataFrame({
            'sicaklik': [sicaklik],
            'yagmur': [yagmur],
            'ruzgar': [ruzgar],
            'ortam': [ortam],
            'mevsim': [mevsim]
        })

        selected_model_key = (model_choice or 'best').lower().strip()

        ml_prediction = None
        ml_confidence = None
        ml_top2 = None
        ml_model_name = None

        if selected_model_key not in ('rules', 'rule', 'rules_baseline'):
            model, loaded_key = load_model_by_key('xgboost' if selected_model_key == 'xgboost' else selected_model_key)
            if model is None:
                model, _ = load_model()
                loaded_key = 'best'

            if model is not None:
                ml_prediction, ml_confidence, ml_top2 = _predict_with_model(model, input_data)
                if loaded_key == 'mlp':
                    ml_model_name = 'MLP'
                elif loaded_key == 'xgboost':
                    metrics = load_metrics() or {}
                    ml_model_name = (
                        ((metrics.get('models') or {}).get('xgboost') or {}).get('display_name')
                        or 'XGBoost'
                    )
                else:
                    ml_model_name = 'En İyi Model'
        
        # Kural tabanlı tahmin
        rule_prediction = rule_based_outfit(sicaklik, yagmur, ruzgar, ortam)
        rule_explanation = _rules_explanation(sicaklik=sicaklik, yagmur=yagmur, ruzgar=ruzgar, ortam=ortam)

        selected_prediction = None
        if selected_model_key in ('rules', 'rule', 'rules_baseline'):
            selected_prediction = {
                "model": "rules",
                "outfit": rule_prediction,
                "emoji": OUTFIT_EMOJIS.get(rule_prediction, "👔"),
                "description": OUTFIT_DESCRIPTIONS.get(rule_prediction, "Önerilen kıyafet"),
                "model_name": "Rules Baseline",
                "confidence": None,
                "explanation": rule_explanation,
                "top2": None,
            }
        else:
            selected_prediction = {
                "model": "ml",
                "outfit": ml_prediction,
                "emoji": OUTFIT_EMOJIS.get(ml_prediction, "👔"),
                "description": OUTFIT_DESCRIPTIONS.get(ml_prediction, "Önerilen kıyafet"),
                "model_name": ml_model_name,
                "confidence": ml_confidence,
                "explanation": (
                    f"{ml_model_name} tahmini. Güven: {round(ml_confidence * 100, 1)}%" if ml_confidence is not None else f"{ml_model_name} tahmini."
                ),
                "top2": ml_top2,
            }

        outfits = None
        profile = None
        if generate_outfit_recommendations is not None and UserProfile is not None:
            try:
                profile = UserProfile(
                    gender=gender,
                    age_range=age_range,
                    height_cm=height_cm,
                    weight_kg=weight_kg,
                    style=style,
                    color_palette=color_palette,
                    cold_sensitivity=cold_sensitivity,
                    event_type=event_type,
                )
                base_outfit_key = ml_prediction or rule_prediction
                outfits = generate_outfit_recommendations(
                    base_outfit=base_outfit_key,
                    sicaklik=sicaklik,
                    yagmur=yagmur,
                    ruzgar=ruzgar,
                    mevsim=mevsim,
                    ortam=ortam,
                    profile=profile,
                    count=6,
                )
            except Exception:
                outfits = None
        
        # Sonuç
        result = {
            "success": True,
            "ml_prediction": {
                "outfit": ml_prediction,
                "emoji": OUTFIT_EMOJIS.get(ml_prediction, "👔"),
                "description": OUTFIT_DESCRIPTIONS.get(ml_prediction, "Önerilen kıyafet"),
                "model_name": ml_model_name,
                "confidence": ml_confidence,
                "explanation": (
                    f"{ml_model_name} tahmini. Güven: {round(ml_confidence * 100, 1)}%" if ml_confidence is not None else (f"{ml_model_name} tahmini." if ml_model_name else None)
                ),
                "top2": ml_top2,
            } if ml_prediction else None,
            "rule_prediction": {
                "outfit": rule_prediction,
                "emoji": OUTFIT_EMOJIS.get(rule_prediction, "👔"),
                "description": OUTFIT_DESCRIPTIONS.get(rule_prediction, "Önerilen kıyafet"),
                "confidence": None,
                "explanation": rule_explanation,
            },
            "match": ml_prediction == rule_prediction if ml_prediction else False,
            "selected_prediction": selected_prediction,
            "model_choice": model_choice,
            "outfits": outfits,
            "profile": {
                "gender": gender,
                "age_range": age_range,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "style": style,
                "color_palette": color_palette,
                "cold_sensitivity": cold_sensitivity,
                "event_type": event_type,
            } if any(
                v is not None and v != "" for v in [
                    gender,
                    age_range,
                    height_cm,
                    weight_kg,
                    style,
                    color_palette,
                    cold_sensitivity,
                    event_type,
                ]
            ) else None,
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

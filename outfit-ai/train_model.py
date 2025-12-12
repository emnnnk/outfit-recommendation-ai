"""
train_model.py
Kıyafet öneri modeli eğitimi için gelişmiş script.
DecisionTreeClassifier kullanarak weather_outfit.csv verisini eğitir.
Logging ve metrik raporlama içerir.
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import sys

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATA_FILE, MODELS_DIR, MODEL_FILE,
    CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET_COLUMN, FEATURE_COLUMNS,
    MODEL_PARAMS, TRAINING_CONFIG
)
from utils.logger import get_training_logger


def train_and_save_model():
    """
    CSV verisini okuyup modeli eğitir, değerlendirir ve kaydeder.
    """
    logger = get_training_logger()
    logger.info("Model eğitimi başlatıldı")
    
    print("\n" + "="*60)
    print("🎓 MODEL EĞİTİMİ")
    print("="*60)
    
    # Veriyi oku
    logger.info(f"Veri yükleniyor: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)
    print(f"\n📁 Veri yüklendi: {len(df)} satır")
    
    # Özellikler ve hedef değişkeni ayır
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TRAINING_CONFIG['test_size'],
        random_state=TRAINING_CONFIG['random_state'],
        stratify=y
    )
    
    print(f"   Eğitim seti: {len(X_train)} örnek")
    print(f"   Test seti: {len(X_test)} örnek")
    
    # One-hot encoding için ColumnTransformer oluştur
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', NUMERIC_FEATURES),
            ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)
        ]
    )
    
    # Pipeline oluştur: Preprocessing + DecisionTree
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', DecisionTreeClassifier(**MODEL_PARAMS['decision_tree']))
    ])
    
    # Modeli eğit
    print("\n🔄 Model eğitiliyor...")
    logger.info("Model eğitiliyor...")
    pipeline.fit(X_train, y_train)
    
    # Eğitim ve test doğruluğu
    train_accuracy = accuracy_score(y_train, pipeline.predict(X_train))
    test_accuracy = accuracy_score(y_test, pipeline.predict(X_test))
    
    print(f"\n📊 Performans Metrikleri:")
    print(f"   Eğitim Doğruluğu: {train_accuracy:.4f}")
    print(f"   Test Doğruluğu: {test_accuracy:.4f}")
    
    logger.info(f"Eğitim Accuracy: {train_accuracy:.4f}")
    logger.info(f"Test Accuracy: {test_accuracy:.4f}")
    
    # Classification report
    y_pred = pipeline.predict(X_test)
    print("\n" + "-"*60)
    print("Classification Report:")
    print("-"*60)
    print(classification_report(y_test, y_pred))
    
    # Modeli kaydet
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_FILE)
    
    print("="*60)
    print(f"✅ Model kaydedildi: {MODEL_FILE}")
    print("="*60)
    
    logger.info(f"Model kaydedildi: {MODEL_FILE}")
    
    return pipeline


if __name__ == "__main__":
    train_and_save_model()

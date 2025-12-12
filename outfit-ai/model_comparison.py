"""
model_comparison.py
Birden fazla ML modelini karşılaştırır ve en iyi modeli seçer.
Decision Tree, Random Forest ve Gradient Boosting modellerini değerlendirir.
"""

import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import sys

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    DATA_FILE, MODELS_DIR, BEST_MODEL_FILE,
    CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET_COLUMN, FEATURE_COLUMNS,
    MODEL_PARAMS, TRAINING_CONFIG
)
from utils.logger import get_training_logger


def load_data():
    """Veri setini yükler."""
    logger = get_training_logger()
    logger.info(f"Veri yükleniyor: {DATA_FILE}")
    
    df = pd.read_csv(DATA_FILE)
    logger.info(f"Toplam {len(df)} satır veri yüklendi")
    logger.info(f"Özellikler: {list(df.columns)}")
    
    return df


def create_preprocessor():
    """Veri önişleme pipeline'ı oluşturur."""
    return ColumnTransformer(
        transformers=[
            ('num', 'passthrough', NUMERIC_FEATURES),
            ('cat', OneHotEncoder(handle_unknown='ignore'), CATEGORICAL_FEATURES)
        ]
    )


def get_models():
    """Karşılaştırılacak modelleri döndürür."""
    return {
        'Decision Tree': DecisionTreeClassifier(**MODEL_PARAMS['decision_tree']),
        'Random Forest': RandomForestClassifier(**MODEL_PARAMS['random_forest']),
        'Gradient Boosting': GradientBoostingClassifier(**MODEL_PARAMS['gradient_boosting'])
    }


def evaluate_models(X_train, X_test, y_train, y_test):
    """
    Tüm modelleri eğitir ve değerlendirir.
    
    Returns:
        dict: Model adı -> (pipeline, accuracy, cv_scores)
    """
    logger = get_training_logger()
    preprocessor = create_preprocessor()
    models = get_models()
    results = {}
    
    print("\n" + "="*70)
    print("📊 MODEL KARŞILAŞTIRMA RAPORU")
    print("="*70)
    
    for name, model in models.items():
        logger.info(f"{name} modeli eğitiliyor...")
        print(f"\n🔄 {name} eğitiliyor...")
        
        # Pipeline oluştur
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        # Cross-validation
        cv_scores = cross_val_score(
            pipeline, X_train, y_train, 
            cv=TRAINING_CONFIG['cv_folds'], 
            scoring='accuracy'
        )
        
        # Modeli eğit
        pipeline.fit(X_train, y_train)
        
        # Test seti üzerinde tahmin
        y_pred = pipeline.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_pred)
        
        results[name] = {
            'pipeline': pipeline,
            'test_accuracy': test_accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'y_pred': y_pred
        }
        
        # Sonuçları yazdır
        print(f"   ✓ Cross-Validation Accuracy: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        print(f"   ✓ Test Accuracy: {test_accuracy:.4f}")
        
        logger.info(f"{name} - CV: {cv_scores.mean():.4f}, Test: {test_accuracy:.4f}")
    
    return results


def print_detailed_report(results, y_test):
    """Detaylı rapor yazdırır."""
    print("\n" + "="*70)
    print("📈 DETAYLI PERFORMANS RAPORU")
    print("="*70)
    
    # En iyi modeli bul
    best_model_name = max(results, key=lambda x: results[x]['cv_mean'])
    best_result = results[best_model_name]
    
    print(f"\n🏆 EN İYİ MODEL: {best_model_name}")
    print(f"   Cross-Validation Accuracy: {best_result['cv_mean']:.4f}")
    print(f"   Test Accuracy: {best_result['test_accuracy']:.4f}")
    
    print("\n" + "-"*70)
    print("Classification Report (En İyi Model):")
    print("-"*70)
    print(classification_report(y_test, best_result['y_pred']))
    
    return best_model_name, best_result['pipeline']


def save_best_model(pipeline, model_name):
    """En iyi modeli kaydeder."""
    logger = get_training_logger()
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(pipeline, BEST_MODEL_FILE)
    
    # Metadata kaydet
    metadata = {
        'model_name': model_name,
        'features': FEATURE_COLUMNS,
        'categorical_features': CATEGORICAL_FEATURES,
        'numeric_features': NUMERIC_FEATURES
    }
    metadata_file = os.path.join(MODELS_DIR, 'model_metadata.pkl')
    joblib.dump(metadata, metadata_file)
    
    print(f"\n✅ En iyi model kaydedildi: {BEST_MODEL_FILE}")
    logger.info(f"Model kaydedildi: {BEST_MODEL_FILE}")


def compare_models():
    """Ana model karşılaştırma fonksiyonu."""
    logger = get_training_logger()
    logger.info("Model karşılaştırma başlatıldı")
    
    # Veriyi yükle
    df = load_data()
    
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=TRAINING_CONFIG['test_size'],
        random_state=TRAINING_CONFIG['random_state'],
        stratify=y
    )
    
    print(f"\n📁 Veri Seti Bilgileri:")
    print(f"   Toplam örnek: {len(df)}")
    print(f"   Eğitim seti: {len(X_train)}")
    print(f"   Test seti: {len(X_test)}")
    print(f"   Benzersiz sınıf sayısı: {y.nunique()}")
    
    # Modelleri değerlendir
    results = evaluate_models(X_train, X_test, y_train, y_test)
    
    # Detaylı rapor ve en iyi model
    best_name, best_pipeline = print_detailed_report(results, y_test)
    
    # En iyi modeli kaydet
    save_best_model(best_pipeline, best_name)
    
    print("\n" + "="*70)
    print("✅ Model karşılaştırma tamamlandı!")
    print("="*70)
    
    logger.info("Model karşılaştırma tamamlandı")
    
    return results


if __name__ == "__main__":
    compare_models()

"""
app.py
Streamlit Web Arayüzü - Akıllı Kıyafet Öneri Sistemi
Modern ve görsel açıdan çekici UI ile ML ve kural tabanlı tahminleri gösterir.
Gerçek zamanlı hava durumu API entegrasyonu içerir.
"""

import streamlit as st
import pandas as pd
import joblib
import os
import sys
import base64
from pathlib import Path

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    MODEL_FILE, BEST_MODEL_FILE, DATA_FILE,
    OUTFIT_EMOJIS, OUTFIT_DESCRIPTIONS,
    YAGMUR_OPTIONS, RUZGAR_OPTIONS, ORTAM_OPTIONS, MEVSIM_OPTIONS,
    STREAMLIT_CONFIG
)
from rules_baseline import rule_based_outfit
from utils.weather_api import get_weather_data, get_weather_wttr, get_weather_emoji, TURKEY_CITIES

# Sayfa konfigürasyonu
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout']
)

# Kıyafet görselleri mapping
OUTFIT_IMAGES = {
    "mont": "mont.png",
    "kaban": "mont.png",
    "mont_semsiye": "mont.png",
    "polar": "kazak.png",
    "kazak": "kazak.png",
    "hirka": "kazak.png",
    "yagmurluk": "yagmurluk.png",
    "yagmurluk_ceket": "yagmurluk.png",
    "ceket": "ceket.png",
    "ince_ceket": "ceket.png",
    "gomlek": "tisort.png",
    "tisort": "tisort.png",
    "sort_tisort": "tisort.png",
    "takim_elbise": "takim_elbise.png",
    "resmi_giyim": "takim_elbise.png",
    "elbise": "takim_elbise.png"
}


def get_image_base64(image_name: str) -> str:
    """Görsel dosyasını base64 formatına çevirir."""
    image_path = Path(__file__).parent / "static" / "images" / image_name
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def get_outfit_image_html(outfit: str, size: int = 150) -> str:
    """Kıyafet için görsel HTML döndürür."""
    image_file = OUTFIT_IMAGES.get(outfit.lower(), "tisort.png")
    base64_img = get_image_base64(image_file)
    
    if base64_img:
        return f'<img src="data:image/png;base64,{base64_img}" style="width:{size}px; height:{size}px; object-fit:contain; border-radius:15px; margin:10px 0;">'
    else:
        # Fallback: emoji göster
        emoji = OUTFIT_EMOJIS.get(outfit, "👔")
        return f'<div style="font-size:{size//2}px; margin:10px 0;">{emoji}</div>'


# Custom CSS - Daha modern ve gelişmiş tasarım
st.markdown("""
<style>
    /* Dark theme override */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Weather Card - Glassmorphism */
    .weather-live-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        color: white;
        margin-bottom: 1.5rem;
    }
    
    .weather-city {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .weather-temp {
        font-size: 4rem;
        font-weight: bold;
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .weather-desc {
        font-size: 1.2rem;
        color: #c0c0c0;
        margin-top: 0.5rem;
    }
    
    .weather-details {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .weather-detail-item {
        text-align: center;
    }
    
    .weather-detail-label {
        font-size: 0.8rem;
        color: #888;
    }
    
    .weather-detail-value {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    /* Result Cards */
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px;
        padding: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.5);
    }
    
    .result-card-rule {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 15px 50px rgba(240, 147, 251, 0.4);
    }
    
    .result-card-rule:hover {
        box-shadow: 0 20px 60px rgba(240, 147, 251, 0.5);
    }
    
    .outfit-title {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }
    
    .outfit-emoji {
        font-size: 4rem;
        margin: 1rem 0;
    }
    
    .outfit-name {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-transform: capitalize;
    }
    
    .outfit-desc {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Match/Diff Banner */
    .comparison-match {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 1.5rem;
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.4);
    }
    
    .comparison-diff {
        background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 1.5rem;
        box-shadow: 0 10px 30px rgba(252, 74, 26, 0.4);
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Input Section */
    .input-section {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* API Key Input */
    .api-key-section {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 2rem;
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    """Modeli yükle ve cache'le."""
    if os.path.exists(BEST_MODEL_FILE):
        return joblib.load(BEST_MODEL_FILE), "En İyi Model (Multi-Model)"
    elif os.path.exists(MODEL_FILE):
        return joblib.load(MODEL_FILE), "Decision Tree"
    return None, None


@st.cache_data
def load_stats():
    """Veri seti istatistiklerini yükle."""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        return {
            'total_samples': len(df),
            'unique_outfits': df['kiyafet'].nunique(),
            'temp_range': f"{df['sicaklik'].min()}°C - {df['sicaklik'].max()}°C"
        }
    return None


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


def predict_outfit(model, sicaklik, yagmur, ruzgar, ortam, mevsim):
    """ML modeli ile tahmin."""
    input_data = pd.DataFrame({
        'sicaklik': [sicaklik],
        'yagmur': [yagmur],
        'ruzgar': [ruzgar],
        'ortam': [ortam],
        'mevsim': [mevsim]
    })
    return model.predict(input_data)[0]


def main():
    # Header
    st.markdown('<h1 class="main-header">🧥 Akıllı Kıyafet Öneri Sistemi</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">ML & Kural Tabanlı Hibrit Öneri Motoru | Gerçek Zamanlı Hava Durumu</p>', unsafe_allow_html=True)
    
    # Model yükle
    model, model_name = load_model()
    
    if model is None:
        st.error("⚠️ Model bulunamadı! Lütfen önce `python model_comparison.py` çalıştırın.")
        return
    
    st.success(f"✅ Model yüklendi: **{model_name}**")
    
    # İstatistikler
    stats = load_stats()
    if stats:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['total_samples']}</div>
                <div class="stat-label">Eğitim Örneği</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <div class="stat-number">{stats['unique_outfits']}</div>
                <div class="stat-label">Farklı Kıyafet</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="stat-number">{stats['temp_range']}</div>
                <div class="stat-label">Sıcaklık Aralığı</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== HAVA DURUMU API BÖLÜMÜ ====================
    st.subheader("🌤️ Canlı Hava Durumu")
    
    # Şehir Seçimi
    col_api1, col_api2 = st.columns([2, 1])
    
    with col_api1:
        city = st.selectbox(
            "📍 Şehir Seçin",
            options=TURKEY_CITIES,
            index=0,
            help="Hava durumu bilgisi alınacak şehri seçin"
        )
    
    with col_api2:
        # Hava durumu getir butonu
        fetch_weather = st.button("🔄 Hava Durumunu Getir", use_container_width=True)
    
    # Session state ile hava durumu verisi sakla
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'last_city' not in st.session_state:
        st.session_state.last_city = None
    
    # Hava durumu verisi
    weather_data = None
    use_live_weather = False
    
    # Butona basıldığında veya şehir değiştiğinde hava durumunu getir
    if fetch_weather or (st.session_state.last_city != city):
        with st.spinner("Hava durumu alınıyor..."):
            # Önce wttr.in dene (API key gerektirmez)
            weather_data = get_weather_wttr(city)
            
            if weather_data:
                st.session_state.weather_data = weather_data
                st.session_state.last_city = city
            else:
                st.warning("⚠️ Hava durumu verisi alınamadı. İnternet bağlantınızı kontrol edin.")
    
    # Önceki veriyi kullan
    if st.session_state.weather_data and st.session_state.last_city == city:
        weather_data = st.session_state.weather_data
    
    if weather_data:
        use_live_weather = True
        weather_emoji = get_weather_emoji(weather_data.get('weather_main', ''))
        source = weather_data.get('source', 'API')
        
        st.markdown(f"""
        <div class="weather-live-card">
            <div class="weather-city">{weather_emoji} {weather_data['city']}, {weather_data['country']}</div>
            <div class="weather-temp">{weather_data['temperature']}°C</div>
            <div class="weather-desc">{weather_data['description']}</div>
            <div class="weather-details">
                <div class="weather-detail-item">
                    <div class="weather-detail-value">🌡️ {weather_data['feels_like']}°C</div>
                    <div class="weather-detail-label">Hissedilen</div>
                </div>
                <div class="weather-detail-item">
                    <div class="weather-detail-value">💧 %{weather_data['humidity']}</div>
                    <div class="weather-detail-label">Nem</div>
                </div>
                <div class="weather-detail-item">
                    <div class="weather-detail-value">💨 {weather_data['wind_speed']} m/s</div>
                    <div class="weather-detail-label">Rüzgar</div>
                </div>
                <div class="weather-detail-item">
                    <div class="weather-detail-value">🌧️ {weather_data['rain'].capitalize()}</div>
                    <div class="weather-detail-label">Yağış</div>
                </div>
            </div>
            <div style="font-size: 0.7rem; opacity: 0.6; margin-top: 1rem;">Kaynak: {source}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 **Hava Durumunu Getir** butonuna tıklayarak canlı hava durumunu alabilirsiniz.")
    
    st.markdown("---")
    
    # ==================== GİRİŞ FORMU ====================
    st.subheader("📝 Hava Durumu Bilgileri")
    
    # Eğer canlı veri varsa, değerleri otomatik doldur
    default_temp = weather_data['temperature'] if weather_data else STREAMLIT_CONFIG['temp_default']
    default_rain = weather_data['rain'] if weather_data else "yok"
    default_wind = weather_data['wind'] if weather_data else "zayıf"
    default_season = weather_data['season'] if weather_data else "ilkbahar"
    
    col1, col2 = st.columns(2)
    
    with col1:
        sicaklik = st.slider(
            "🌡️ Sıcaklık (°C)",
            min_value=STREAMLIT_CONFIG['temp_min'],
            max_value=STREAMLIT_CONFIG['temp_max'],
            value=max(STREAMLIT_CONFIG['temp_min'], min(default_temp, STREAMLIT_CONFIG['temp_max'])),
            help="Hava sıcaklığını seçin"
        )
        
        yagmur = st.selectbox(
            "🌧️ Yağmur Durumu",
            options=YAGMUR_OPTIONS,
            index=YAGMUR_OPTIONS.index(default_rain) if default_rain in YAGMUR_OPTIONS else 0,
            format_func=lambda x: "Yağmur Var 🌧️" if x == "var" else "Yağmur Yok ☀️"
        )
    
    with col2:
        ruzgar = st.selectbox(
            "💨 Rüzgar Şiddeti",
            options=RUZGAR_OPTIONS,
            index=RUZGAR_OPTIONS.index(default_wind) if default_wind in RUZGAR_OPTIONS else 0,
            format_func=lambda x: {"zayıf": "Zayıf 🍃", "orta": "Orta 💨", "kuvvetli": "Kuvvetli 🌪️"}[x]
        )
        
        ortam = st.selectbox(
            "📍 Ortam",
            options=ORTAM_OPTIONS,
            format_func=lambda x: {"günlük": "Günlük 🏠", "okul": "Okul 🎒", "özel": "Özel Gün 👔"}[x]
        )
    
    # Mevsim seçimi
    auto_season = get_season_from_temp(sicaklik)
    mevsim = st.selectbox(
        "🗓️ Mevsim",
        options=MEVSIM_OPTIONS,
        index=MEVSIM_OPTIONS.index(default_season) if default_season in MEVSIM_OPTIONS else MEVSIM_OPTIONS.index(auto_season),
        format_func=lambda x: {"kış": "Kış ❄️", "ilkbahar": "İlkbahar 🌸", "yaz": "Yaz ☀️", "sonbahar": "Sonbahar 🍂"}[x]
    )
    
    st.markdown("---")
    
    # Tahmin butonu
    if st.button("🎯 Kıyafet Öner", type="primary", use_container_width=True):
        # Tahminleri yap
        ml_prediction = predict_outfit(model, sicaklik, yagmur, ruzgar, ortam, mevsim)
        rule_prediction = rule_based_outfit(sicaklik, yagmur, ruzgar, ortam)
        
        st.markdown("---")
        st.subheader("🎯 Öneri Sonuçları")
        
        # Sonuç kartları
        col1, col2 = st.columns(2)
        
        with col1:
            emoji = OUTFIT_EMOJIS.get(ml_prediction, "👔")
            desc = OUTFIT_DESCRIPTIONS.get(ml_prediction, "Önerilen kıyafet")
            image_html = get_outfit_image_html(ml_prediction, 120)
            
            st.markdown(f"""
            <div class="result-card">
                <div class="outfit-title">🤖 ML Model Tahmini</div>
                {image_html}
                <div class="outfit-name">{ml_prediction.replace('_', ' ').title()}</div>
                <div class="outfit-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            emoji = OUTFIT_EMOJIS.get(rule_prediction, "👔")
            desc = OUTFIT_DESCRIPTIONS.get(rule_prediction, "Önerilen kıyafet")
            image_html = get_outfit_image_html(rule_prediction, 120)
            
            st.markdown(f"""
            <div class="result-card result-card-rule">
                <div class="outfit-title">📋 Kural Tabanlı</div>
                {image_html}
                <div class="outfit-name">{rule_prediction.replace('_', ' ').title()}</div>
                <div class="outfit-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Karşılaştırma
        if ml_prediction == rule_prediction:
            st.markdown("""
            <div class="comparison-match">
                ✅ Mükemmel Uyum! Her iki yöntem de aynı kıyafeti önerdi.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="comparison-diff">
                ℹ️ Farklı Öneriler - ML modeli veri kalıplarını, kural sistemi sabit kuralları kullanır.
            </div>
            """, unsafe_allow_html=True)
        
        # Girdi özeti
        st.markdown("---")
        source_text = f"(🌐 Canlı: {weather_data['city']})" if use_live_weather else "(📝 Manuel giriş)"
        st.markdown(f"""
        **📊 Girdi Özeti** {source_text}
        - 🌡️ Sıcaklık: **{sicaklik}°C**
        - 🌧️ Yağmur: **{yagmur}**
        - 💨 Rüzgar: **{ruzgar}**
        - 📍 Ortam: **{ortam}**
        - 🗓️ Mevsim: **{mevsim}**
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>🎓 <strong>Outfit AI</strong> - Makine Öğrenimi Projesi</p>
        <p>Decision Tree, Random Forest & Gradient Boosting ile Hibrit Öneri Sistemi</p>
        <p style="font-size: 0.8rem; margin-top: 1rem;">
            💡 API Key almak için: <a href="https://openweathermap.org/api" target="_blank">openweathermap.org</a>
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

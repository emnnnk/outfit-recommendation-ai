"""
weather_api.py
Hava durumu API entegrasyonu - Gerçek zamanlı hava durumu verisi çekme.
OpenWeatherMap ve wttr.in desteği.
"""

import requests
from typing import Optional, Dict, Any
import os
import json
from datetime import datetime


# OpenWeatherMap Free API
OPENWEATHERMAP_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# wttr.in - Ücretsiz, API key gerektirmez
WTTR_API_URL = "https://wttr.in"


def get_weather_wttr(city: str) -> Optional[Dict[str, Any]]:
    """
    wttr.in API'den hava durumu verisini çeker.
    API key gerektirmez!
    
    Args:
        city: Şehir adı (örn: "Istanbul", "Ankara")
    
    Returns:
        Hava durumu verisi dict veya None
    """
    try:
        # wttr.in JSON formatı
        url = f"{WTTR_API_URL}/{city}?format=j1"
        headers = {"User-Agent": "OutfitAI/1.0"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return parse_wttr_response(data, city)
        else:
            return None
            
    except Exception as e:
        print(f"wttr.in API hatası: {e}")
        return None


def parse_wttr_response(data: Dict[str, Any], city: str) -> Dict[str, Any]:
    """
    wttr.in yanıtını uygulama formatına dönüştürür.
    """
    try:
        current = data.get("current_condition", [{}])[0]
        
        # Sıcaklık
        temp = int(current.get("temp_C", 20))
        feels_like = int(current.get("FeelsLikeC", temp))
        
        # Hava durumu açıklaması
        weather_desc_list = current.get("lang_tr", current.get("weatherDesc", [{}]))
        if isinstance(weather_desc_list, list) and len(weather_desc_list) > 0:
            weather_desc = weather_desc_list[0].get("value", "Bilinmiyor")
        else:
            weather_desc = "Bilinmiyor"
        
        # Yağmur durumu
        precip = float(current.get("precipMM", 0))
        weather_code = int(current.get("weatherCode", 0))
        # Yağmur kodları: 200-299 (gök gürültülü), 300-399 (çisenti), 500-599 (yağmur), 600-699 (kar)
        rain = "var" if precip > 0.1 or weather_code in range(200, 700) else "yok"
        
        # Rüzgar hızı (km/h -> kategori)
        wind_speed_kmh = float(current.get("windspeedKmph", 0))
        wind_speed_ms = wind_speed_kmh / 3.6  # m/s'ye çevir
        if wind_speed_kmh < 10:
            ruzgar = "zayıf"
        elif wind_speed_kmh < 30:
            ruzgar = "orta"
        else:
            ruzgar = "kuvvetli"
        
        # Nem
        humidity = int(current.get("humidity", 0))
        
        # Mevsim tahmini (gerçek tarihe göre)
        month = datetime.now().month
        if month in [12, 1, 2]:
            mevsim = "kış"
        elif month in [3, 4, 5]:
            mevsim = "ilkbahar"
        elif month in [6, 7, 8]:
            mevsim = "yaz"
        else:
            mevsim = "sonbahar"
        
        # Hava durumu tipi
        weather_main = "clear"
        if weather_code >= 200 and weather_code < 300:
            weather_main = "thunderstorm"
        elif weather_code >= 300 and weather_code < 600:
            weather_main = "rain"
        elif weather_code >= 600 and weather_code < 700:
            weather_main = "snow"
        elif weather_code >= 700 and weather_code < 800:
            weather_main = "mist"
        elif weather_code >= 800:
            weather_main = "clouds" if weather_code > 800 else "clear"
        
        return {
            "city": city.capitalize(),
            "country": "TR",
            "temperature": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "description": weather_desc,
            "icon_url": "",
            "rain": rain,
            "wind": ruzgar,
            "wind_speed": round(wind_speed_ms, 1),
            "season": mevsim,
            "weather_main": weather_main,
            "source": "wttr.in"
        }
    except Exception as e:
        print(f"wttr.in parse hatası: {e}")
        return None


def get_weather_data(city: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    OpenWeatherMap API'den hava durumu verisini çeker.
    
    Args:
        city: Şehir adı (örn: "Istanbul", "Ankara")
        api_key: OpenWeatherMap API anahtarı (opsiyonel, env'den de alınabilir)
    
    Returns:
        Hava durumu verisi dict veya None
    """
    # API key kontrolü
    api_key = api_key or os.environ.get("OPENWEATHERMAP_API_KEY")
    
    if not api_key:
        return None
    
    try:
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",  # Celsius
            "lang": "tr"  # Türkçe açıklamalar
        }
        
        response = requests.get(OPENWEATHERMAP_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return parse_weather_response(data)
        else:
            return None
            
    except Exception as e:
        print(f"Hava durumu API hatası: {e}")
        return None


def parse_weather_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    API yanıtını uygulama formatına dönüştürür.
    """
    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})
    
    # Sıcaklık
    temp = round(main.get("temp", 20))
    
    # Yağmur durumu
    weather_main = weather.get("main", "").lower()
    weather_desc = weather.get("description", "")
    rain = "var" if weather_main in ["rain", "drizzle", "thunderstorm", "snow"] else "yok"
    
    # Rüzgar hızı (m/s -> kategori)
    wind_speed = wind.get("speed", 0)
    if wind_speed < 3:
        ruzgar = "zayıf"
    elif wind_speed < 8:
        ruzgar = "orta"
    else:
        ruzgar = "kuvvetli"
    
    # Mevsim tahmini (sıcaklığa göre)
    if temp < 5:
        mevsim = "kış"
    elif temp < 15:
        mevsim = "sonbahar"
    elif temp < 25:
        mevsim = "ilkbahar"
    else:
        mevsim = "yaz"
    
    # Hava durumu ikonu
    icon_code = weather.get("icon", "01d")
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    
    return {
        "city": data.get("name", "Bilinmeyen"),
        "country": data.get("sys", {}).get("country", ""),
        "temperature": temp,
        "feels_like": round(main.get("feels_like", temp)),
        "humidity": main.get("humidity", 0),
        "description": weather_desc.capitalize(),
        "icon_url": icon_url,
        "rain": rain,
        "wind": ruzgar,
        "wind_speed": wind_speed,
        "season": mevsim,
        "weather_main": weather_main
    }


def get_weather_emoji(weather_main: str) -> str:
    """Hava durumu için emoji döndürür."""
    emoji_map = {
        "clear": "☀️",
        "clouds": "☁️",
        "rain": "🌧️",
        "drizzle": "🌦️",
        "thunderstorm": "⛈️",
        "snow": "❄️",
        "mist": "🌫️",
        "fog": "🌫️",
        "haze": "🌫️"
    }
    return emoji_map.get(weather_main.lower(), "🌤️")


# Şehir listesi (Türkiye + Dünya Başkentleri)
TURKEY_CITIES = [
    # Türkiye
    "Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", 
    "Adana", "Konya", "Gaziantep", "Mersin", "Diyarbakir",
    "Kayseri", "Eskisehir", "Samsun", "Denizli", "Trabzon",
    "Malatya", "Erzurum", "Van", "Batman", "Elazig",
    "Sanliurfa", "Manisa", "Balikesir", "Sakarya", "Kocaeli",
    "Rize", "Artvin", "Giresun", "Ordu", "Osmaniye",
    
    # Dünya Başkentleri & Önemli Şehirler
    "Baku", "London", "New York", "Paris", "Berlin", 
    "Tokyo", "Moscow", "Rome", "Dubai", "Amsterdam",
    "Madrid", "Vienna", "Seoul", "Beijing", "Sydney"
]


if __name__ == "__main__":
    # Test
    print("Hava durumu API test...")
    # API key olmadan çalışmaz, sadece yapıyı test et
    result = get_weather_data("Istanbul")
    if result:
        print(f"Şehir: {result['city']}")
        print(f"Sıcaklık: {result['temperature']}°C")
        print(f"Durum: {result['description']}")
    else:
        print("API key gerekli veya bağlantı hatası")

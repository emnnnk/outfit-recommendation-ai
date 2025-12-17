/**
 * Main Application Logic
 * Handles UI interactions, API calls, and state management
 */

class OutfitApp {
    constructor() {
        // Elements
        this.citySelect = document.getElementById('city-select');
        this.fetchWeatherBtn = document.getElementById('fetch-weather-btn');
        this.weatherDisplay = document.getElementById('weather-display');
        this.weatherLoading = document.getElementById('weather-loading');
        this.weatherPlaceholder = document.getElementById('weather-placeholder');

        this.tempSlider = document.getElementById('temp-slider');
        this.tempValue = document.getElementById('temp-value');
        this.rainSelect = document.getElementById('rain-select');
        this.windSelect = document.getElementById('wind-select');
        this.occasionSelect = document.getElementById('occasion-select');
        this.seasonSelect = document.getElementById('season-select');

        this.predictBtn = document.getElementById('predict-btn');
        this.mlResult = document.getElementById('ml-result');
        this.ruleResult = document.getElementById('rule-result');
        this.matchStatus = document.getElementById('match-status');

        this.modelSelect = document.getElementById('model-select');
        this.selectedResult = document.getElementById('selected-result');

        this.modelMetricsLoading = document.getElementById('model-metrics-loading');
        this.modelMetricsError = document.getElementById('model-metrics-error');
        this.modelMetricsGrid = document.getElementById('model-metrics-grid');

        this.genderSelect = document.getElementById('gender-select');
        this.ageRangeSelect = document.getElementById('age-range-select');
        this.heightCmInput = document.getElementById('height-cm');
        this.weightKgInput = document.getElementById('weight-kg');
        this.styleSelect = document.getElementById('style-select');
        this.paletteSelect = document.getElementById('palette-select');
        this.coldSensitivitySelect = document.getElementById('cold-sensitivity-select');
        this.eventTypeSelect = document.getElementById('event-type-select');

        this.outfitsLoading = document.getElementById('outfits-loading');
        this.outfitsError = document.getElementById('outfits-error');
        this.outfitsPlaceholder = document.getElementById('outfits-placeholder');
        this.outfitsGrid = document.getElementById('outfits-grid');

        // State
        this.weatherData = null;
        this.isLoading = false;
        this.seasonManuallyChanged = false;

        // Initialize
        this.bindEvents();
        this.hideLoading();
        this.hideOutfitsLoading();

        this.fetchModelMetrics();
    }

    bindEvents() {
        // Fetch weather button
        this.fetchWeatherBtn.addEventListener('click', () => this.fetchWeather());

        // City select change
        this.citySelect.addEventListener('change', () => {
            // Auto-fetch when city changes
            this.fetchWeather();
        });

        // Temperature slider
        this.tempSlider.addEventListener('input', (e) => {
            this.tempValue.textContent = e.target.value;
            // Removed automatic season update from temperature to respect calendar date
        });

        // Manual season change
        this.seasonSelect.addEventListener('change', () => {
            this.seasonManuallyChanged = true;
        });

        // Predict button
        this.predictBtn.addEventListener('click', () => this.predict());

        if (this.modelSelect) {
            this.modelSelect.addEventListener('change', () => {
                const label = this.modelSelect.options[this.modelSelect.selectedIndex]?.textContent || 'Model';
                this.showToast(`Model: ${label}`, 'info');
            });
        }

        // Add ripple effect to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.createRipple(e));
        });

        // Start live clock
        this.updateDateTime();
        setInterval(() => this.updateDateTime(), 1000);
    }

    // Update live date, time and season
    updateDateTime() {
        const now = new Date();

        // Date
        const dateOptions = { day: 'numeric', month: 'long', year: 'numeric', weekday: 'long' };
        const dateStr = now.toLocaleDateString('tr-TR', dateOptions);
        document.getElementById('live-date').textContent = dateStr;

        // Time
        const timeStr = now.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('live-time').textContent = timeStr;

        // Season (Calendar based)
        const month = now.getMonth() + 1; // 1-12
        let season = 'İlkbahar';
        let seasonKey = 'ilkbahar';

        if (month === 12 || month === 1 || month === 2) {
            season = 'Kış';
            seasonKey = 'kış';
        } else if (month >= 3 && month <= 5) {
            season = 'İlkbahar';
            seasonKey = 'ilkbahar';
        } else if (month >= 6 && month <= 8) {
            season = 'Yaz';
            seasonKey = 'yaz';
        } else {
            season = 'Sonbahar';
            seasonKey = 'sonbahar';
        }

        document.getElementById('live-season').textContent = season;

        // Only update select if not manually changed recently (optional, or just enforce it)
        // For this request, we force update the season select to match real season initially
        if (!this.seasonManuallyChanged) {
            this.seasonSelect.value = seasonKey;
        }
    }

    // Fetch weather from API
    async fetchWeather() {
        const city = this.citySelect.value;

        this.showLoading();

        try {
            const response = await fetch(`/api/weather/${encodeURIComponent(city)}`);
            const data = await response.json();

            if (data.success) {
                this.weatherData = data.data;
                this.displayWeather(data.data);
                this.updateFormFromWeather(data.data);

                // Update weather background
                if (window.setWeatherBackground) {
                    window.setWeatherBackground(data.data.weather_main);
                }

                // Update city background image
                this.updateCityBackground(data.data.city, data.data.weather_main, data.data.description);

                // Automatically predict outfit
                setTimeout(() => this.predict(), 500); // Small delay for visual effect

            } else {
                this.showError('Hava durumu alınamadı: ' + data.error);
            }
        } catch (error) {
            console.error('Weather fetch error:', error);
            this.showError('Bağlantı hatası. Lütfen tekrar deneyin.');
        } finally {
            this.hideLoading();
        }
    }

    // Update city background image
    updateCityBackground(city, weatherMain, description) {
        const bgElement = document.getElementById('city-background');
        if (!bgElement) return;

        // Construct query for image
        let query = `${city} city landmark`;

        // Add weather context for mood
        if (weatherMain.toLowerCase().includes('rain')) query += ' rainy';
        else if (weatherMain.toLowerCase().includes('snow')) query += ' winter snow';
        else if (weatherMain.toLowerCase().includes('cloud')) query += ' cloudy sky';
        else if (weatherMain.toLowerCase().includes('clear')) query += ' sunny bright';

        // Add random seed to avoid caching same image if weather barely changes, but keep it consistent for same request
        const seed = Date.now();

        // Use Pollinations AI for reliable generation/search
        // const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(query)}?width=1920&height=1080&nologo=true`;

        // OR Use Unsplash Source (sometimes unreliable/deprecated but high quality)
        // const imageUrl = `https://source.unsplash.com/1920x1080/?${encodeURIComponent(query)}`;

        // Pollinations is safer as it generates or retrieves
        const imageUrl = `https://image.pollinations.ai/prompt/cinematic shot of ${encodeURIComponent(city)} city landmark, ${encodeURIComponent(weatherMain)} weather, high quality, 8k, photorealistic?width=1600&height=900&nologo=true&seed=${seed}`;

        // Improve transition
        bgElement.style.opacity = '0';

        const img = new Image();
        img.onload = () => {
            bgElement.style.backgroundImage = `url('${imageUrl}')`;
            bgElement.style.opacity = '1';
        };
        img.src = imageUrl;
    }

    // Display weather data
    displayWeather(data) {
        this.weatherPlaceholder.classList.add('hidden');
        this.weatherDisplay.classList.remove('hidden');

        document.getElementById('weather-emoji').textContent = data.emoji || '🌤️';
        document.getElementById('weather-temp').textContent = data.temperature;
        document.getElementById('weather-desc').textContent = data.description;
        document.getElementById('feels-like').textContent = `${data.feels_like}°C`;
        document.getElementById('humidity').textContent = `${data.humidity}%`;
        document.getElementById('wind-speed').textContent = `${data.wind_speed} m/s`;
        document.getElementById('rain-status').textContent = data.rain === 'var' ? 'Var' : 'Yok';

        // Animate weather card
        const weatherCard = document.getElementById('weather-card');
        weatherCard.style.animation = 'none';
        weatherCard.offsetHeight; // Trigger reflow
        weatherCard.style.animation = 'fadeInUp 0.5s ease';
    }

    // Update form from weather data
    updateFormFromWeather(data) {
        // Temperature
        const temp = Math.max(-20, Math.min(45, data.temperature));
        this.tempSlider.value = temp;
        this.tempValue.textContent = temp;

        // Rain
        this.rainSelect.value = data.rain;

        // Wind
        this.windSelect.value = data.wind;

        // Season
        this.seasonSelect.value = data.season;
    }

    // Update season from temperature
    updateSeasonFromTemp(temp) {
        let season;
        if (temp < 5) season = 'kış';
        else if (temp < 15) season = 'sonbahar';
        else if (temp < 25) season = 'ilkbahar';
        else season = 'yaz';

        this.seasonSelect.value = season;
    }

    // Make prediction
    async predict() {
        // Get form values
        const data = {
            sicaklik: parseInt(this.tempSlider.value),
            yagmur: this.rainSelect.value,
            ruzgar: this.windSelect.value,
            ortam: this.occasionSelect.value,
            mevsim: this.seasonSelect.value,

            model: this.modelSelect ? this.modelSelect.value : 'best',

            gender: this.genderSelect ? this.genderSelect.value : null,
            age_range: this.ageRangeSelect ? this.ageRangeSelect.value : null,
            height_cm: this.heightCmInput ? this.heightCmInput.value : null,
            weight_kg: this.weightKgInput ? this.weightKgInput.value : null,
            style: this.styleSelect ? this.styleSelect.value : null,
            color_palette: this.paletteSelect ? this.paletteSelect.value : null,
            cold_sensitivity: this.coldSensitivitySelect ? this.coldSensitivitySelect.value : null,
            event_type: this.eventTypeSelect ? this.eventTypeSelect.value : null,
        };

        this.showOutfitsLoading();
        this.showSelectedLoading();

        // Add loading state to button
        this.predictBtn.disabled = true;
        this.predictBtn.innerHTML = `
            <div class="spinner" style="width: 20px; height: 20px; margin-right: 8px;"></div>
            <span class="btn-text">Hesaplanıyor...</span>
        `;

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.displayResults(result);
                this.displayOutfits(result.outfits);
                this.displaySelectedPrediction(result.selected_prediction, result);
            } else {
                this.showError('Tahmin yapılamadı: ' + result.error);
                this.showOutfitsError('Tahmin yapılamadı: ' + result.error);
                this.showToast('Tahmin yapılamadı', 'error');
            }
        } catch (error) {
            console.error('Prediction error:', error);
            this.showError('Bağlantı hatası. Lütfen tekrar deneyin.');
            this.showOutfitsError('Bağlantı hatası. Lütfen tekrar deneyin.');
            this.showToast('Bağlantı hatası', 'error');
        } finally {
            this.hideOutfitsLoading();
            // Reset button
            this.predictBtn.disabled = false;
            this.predictBtn.innerHTML = `
                <span class="btn-icon">🎯</span>
                <span class="btn-text">Kıyafet Öner</span>
                <div class="btn-shine"></div>
            `;
        }
    }

    // Display prediction results
    displayResults(result) {
        // Update outfit display with image
        const outfitToShow = result.selected_prediction || result.ml_prediction || result.rule_prediction;
        if (outfitToShow && window.setOutfitDisplay) {
            window.setOutfitDisplay(
                outfitToShow.outfit,
                outfitToShow.description,
                outfitToShow.emoji
            );
        }

        // Update weather bar
        if (window.updateWeatherBar) {
            window.updateWeatherBar(
                this.tempSlider.value,
                this.rainSelect.value,
                this.windSelect.value,
                this.seasonSelect.value
            );
        }

        // ML Result
        if (result.ml_prediction) {
            const confidence = (typeof result.ml_prediction.confidence === 'number')
                ? `${Math.round(result.ml_prediction.confidence * 100)}%`
                : null;
            const explanation = result.ml_prediction.explanation ? this.escapeHtml(result.ml_prediction.explanation) : null;
            this.mlResult.innerHTML = `
                <div class="result-outfit">
                    <span class="result-emoji">${result.ml_prediction.emoji}</span>
                    <div class="result-name">${this.formatOutfitName(result.ml_prediction.outfit)}</div>
                    <div class="result-desc">${result.ml_prediction.description}</div>
                    ${confidence ? `<div class="result-confidence">Confidence: <strong>${confidence}</strong></div>` : ''}
                    ${explanation ? `<div class="result-explanation">${explanation}</div>` : ''}
                    <div class="result-model" style="font-size: 0.75rem; opacity: 0.6; margin-top: 8px;">
                        Model: ${result.ml_prediction.model_name}
                    </div>
                </div>
            `;
        } else {
            this.mlResult.innerHTML = `
                <div class="result-placeholder">
                    <span class="placeholder-icon">⚠️</span>
                    <p>ML model bulunamadı</p>
                </div>
            `;
        }

        // Rule Result
        const ruleExplanation = result.rule_prediction.explanation ? this.escapeHtml(result.rule_prediction.explanation) : null;
        this.ruleResult.innerHTML = `
            <div class="result-outfit">
                <span class="result-emoji">${result.rule_prediction.emoji}</span>
                <div class="result-name">${this.formatOutfitName(result.rule_prediction.outfit)}</div>
                <div class="result-desc">${result.rule_prediction.description}</div>
                ${ruleExplanation ? `<div class="result-explanation">${ruleExplanation}</div>` : ''}
            </div>
        `;

        // Match Status
        if (result.match) {
            this.matchStatus.className = 'match-status match';
            this.matchStatus.innerHTML = `
                <span class="match-icon">✅</span>
                <span class="match-text">Mükemmel Uyum! Her iki yöntem de aynı öneriyi verdi.</span>
            `;
        } else {
            this.matchStatus.className = 'match-status diff';
            this.matchStatus.innerHTML = `
                <span class="match-icon">ℹ️</span>
                <span class="match-text">Farklı Öneriler - ML ve kural sistemi farklı sonuçlar verdi.</span>
            `;
        }

        // Animate result cards
        document.querySelectorAll('.result-card').forEach((card, index) => {
            card.style.animation = 'none';
            card.offsetHeight;
            card.style.animation = `fadeInUp 0.5s ease ${index * 0.1}s`;
        });
    }

    // Render multi-outfit recommendations
    displayOutfits(outfits) {
        if (!this.outfitsGrid || !this.outfitsPlaceholder || !this.outfitsError) return;

        this.outfitsError.classList.add('hidden');

        if (!Array.isArray(outfits) || outfits.length === 0) {
            this.outfitsGrid.classList.add('hidden');
            this.outfitsGrid.innerHTML = '';
            this.outfitsPlaceholder.classList.remove('hidden');
            return;
        }

        this.outfitsPlaceholder.classList.add('hidden');
        this.outfitsGrid.classList.remove('hidden');

        const cardsHtml = outfits
            .map((o) => {
                const title = this.escapeHtml(o.title || 'Outfit');
                const reasons = Array.isArray(o.reasons) ? o.reasons : [];
                const pieces = Array.isArray(o.pieces) ? o.pieces : [];

                const reasonsHtml = reasons
                    .slice(0, 5)
                    .map((r) => `<li>${this.escapeHtml(r)}</li>`)
                    .join('');

                const piecesHtml = pieces
                    .map((p) => {
                        const label = this.escapeHtml(p.label || p.category || 'Parça');
                        const img = this.escapeHtml(p.image || '');
                        const link = this.escapeHtml(p.link || '#');
                        return `
                            <div class="piece-item">
                                <div class="piece-image">
                                    <img src="${img}" alt="${label}" loading="lazy" />
                                </div>
                                <div class="piece-meta">
                                    <div class="piece-label">${label}</div>
                                    <a class="piece-link" href="${link}" target="_blank" rel="noopener noreferrer">Shop</a>
                                </div>
                            </div>
                        `;
                    })
                    .join('');

                return `
                    <div class="outfit-card">
                        <div class="outfit-card-header">
                            <div class="outfit-card-title">${title}</div>
                        </div>
                        <ul class="outfit-reasons">${reasonsHtml}</ul>
                        <div class="pieces-grid">${piecesHtml}</div>
                    </div>
                `;
            })
            .join('');

        this.outfitsGrid.innerHTML = cardsHtml;
    }

    // Format outfit name for display
    formatOutfitName(name) {
        return name
            .replace(/_/g, ' ')
            .replace(/şemsiye/g, '+ Şemsiye')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Show loading state
    showLoading() {
        this.isLoading = true;
        this.weatherLoading.classList.remove('hidden');
        this.weatherPlaceholder.classList.add('hidden');
        this.weatherDisplay.classList.add('hidden');
    }

    // Hide loading state
    hideLoading() {
        this.isLoading = false;
        this.weatherLoading.classList.add('hidden');
    }

    // Show error message
    showError(message) {
        this.weatherPlaceholder.innerHTML = `
            <span class="placeholder-icon">⚠️</span>
            <p style="color: #f5576c;">${message}</p>
        `;
        this.weatherPlaceholder.classList.remove('hidden');
        this.weatherDisplay.classList.add('hidden');
    }

    showSelectedLoading() {
        if (!this.selectedResult) return;
        this.selectedResult.innerHTML = `
            <div class="metrics-skeleton">
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
                <div class="skeleton-line"></div>
            </div>
        `;
    }

    displaySelectedPrediction(selected) {
        if (!this.selectedResult) return;

        if (!selected || !selected.outfit) {
            this.selectedResult.innerHTML = `
                <div class="result-placeholder">
                    <span class="placeholder-icon">⚠️</span>
                    <p>Selected model çıktısı alınamadı.</p>
                </div>
            `;
            return;
        }

        const modelName = this.escapeHtml(selected.model_name || 'Selected');
        const outfit = this.escapeHtml(this.formatOutfitName(selected.outfit));
        const emoji = this.escapeHtml(selected.emoji || '✨');
        const desc = this.escapeHtml(selected.description || '');
        const explanation = selected.explanation ? this.escapeHtml(selected.explanation) : '';
        const confidence = (typeof selected.confidence === 'number')
            ? `${Math.round(selected.confidence * 100)}%`
            : null;

        this.selectedResult.innerHTML = `
            <div class="result-outfit">
                <span class="result-emoji">${emoji}</span>
                <div class="result-name">${outfit}</div>
                <div class="result-desc">${desc}</div>
                ${confidence ? `<div class="result-confidence">Confidence: <strong>${confidence}</strong></div>` : ''}
                ${explanation ? `<div class="result-explanation">${explanation}</div>` : ''}
                <div class="result-model" style="font-size: 0.75rem; opacity: 0.6; margin-top: 8px;">Model: ${modelName}</div>
            </div>
        `;

        const picked = this.modelSelect ? this.modelSelect.value : null;
        if (picked && picked !== 'best') {
            this.showToast(`Selected: ${modelName}`, 'success');
        }
    }

    async fetchModelMetrics() {
        if (!this.modelMetricsLoading || !this.modelMetricsGrid || !this.modelMetricsError) return;

        this.modelMetricsError.classList.add('hidden');
        this.modelMetricsGrid.classList.add('hidden');
        this.modelMetricsLoading.classList.remove('hidden');

        try {
            const resp = await fetch('/api/model-metrics');
            const payload = await resp.json();
            if (!payload.success) {
                throw new Error(payload.error || 'metrics error');
            }
            this.renderModelMetrics(payload.metrics);
        } catch (e) {
            this.modelMetricsError.textContent = 'Model metrikleri yüklenemedi.';
            this.modelMetricsError.classList.remove('hidden');
        } finally {
            this.modelMetricsLoading.classList.add('hidden');
        }
    }

    renderModelMetrics(metrics) {
        if (!this.modelMetricsGrid || !this.modelMetricsError) return;
        if (!metrics || !metrics.models) {
            this.modelMetricsError.textContent = 'Model metrikleri bulunamadı.';
            this.modelMetricsError.classList.remove('hidden');
            return;
        }

        const models = metrics.models;
        const order = ['rules', 'xgboost', 'random_forest', 'mlp'];

        const entries = Object.keys(models)
            .sort((a, b) => {
                const ia = order.indexOf(a);
                const ib = order.indexOf(b);
                return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib);
            })
            .map((k) => ({ key: k, v: models[k] }));

        const best = metrics.best_model ? String(metrics.best_model) : null;

        const cards = entries
            .map(({ key, v }) => {
                const name = this.escapeHtml(v.display_name || key);
                const acc = (typeof v.accuracy === 'number') ? `${(v.accuracy * 100).toFixed(1)}%` : '--';
                const f1 = (typeof v.macro_f1 === 'number') ? `${(v.macro_f1 * 100).toFixed(1)}%` : '--';
                const isBest = best && (best === key);

                return `
                    <div class="metric-card ${isBest ? 'is-best' : ''}">
                        <div class="metric-title">${name}${isBest ? ' <span class="best-badge">Best</span>' : ''}</div>
                        <div class="metric-row"><span>Accuracy</span><strong>${acc}</strong></div>
                        <div class="metric-row"><span>Macro F1</span><strong>${f1}</strong></div>
                    </div>
                `;
            })
            .join('');

        this.modelMetricsGrid.innerHTML = cards;
        this.modelMetricsGrid.classList.remove('hidden');
    }

    showToast(message, type) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type || 'info'}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('toast-hide');
            setTimeout(() => toast.remove(), 250);
        }, 2200);
    }

    showOutfitsLoading() {
        if (this.outfitsLoading) this.outfitsLoading.classList.remove('hidden');
        if (this.outfitsError) this.outfitsError.classList.add('hidden');
        if (this.outfitsPlaceholder) this.outfitsPlaceholder.classList.add('hidden');
        if (this.outfitsGrid) this.outfitsGrid.classList.add('hidden');
    }

    hideOutfitsLoading() {
        if (this.outfitsLoading) this.outfitsLoading.classList.add('hidden');
    }

    showOutfitsError(message) {
        if (!this.outfitsError) return;

        this.outfitsError.textContent = message;
        this.outfitsError.classList.remove('hidden');
        if (this.outfitsGrid) this.outfitsGrid.classList.add('hidden');
        if (this.outfitsPlaceholder) this.outfitsPlaceholder.classList.remove('hidden');
    }

    // Create ripple effect on buttons
    createRipple(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();

        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }
}

// Add ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize app when DOM is ready
let app = null;

document.addEventListener('DOMContentLoaded', () => {
    app = new OutfitApp();

    // Auto-fetch weather for first city after short delay
    setTimeout(() => {
        app.fetchWeather();
    }, 1000);
});

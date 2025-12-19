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

        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.drawerBackdrop = document.getElementById('drawer-backdrop');
        this.topbarGenerate = document.getElementById('topbar-generate');

        this.avatarPieces = document.getElementById('avatar-pieces');
        this.avatarShadow = document.getElementById('avatar-shadow');
        this.avatarBody = document.getElementById('avatar-body');
        this.avatarTop = document.getElementById('avatar-top');
        this.avatarBottom = document.getElementById('avatar-bottom');
        this.avatarShoes = document.getElementById('avatar-shoes');
        this.avatarOuterwear = document.getElementById('avatar-outerwear');
        this.avatarAccessory = document.getElementById('avatar-accessory');
        this.avatarHighlight = document.getElementById('avatar-highlight');

        // State
        this.weatherData = null;
        this.isLoading = false;
        this.seasonManuallyChanged = false;
        this.currentOutfits = [];
        this.selectedOutfitIndex = 0;
        this.activeCity = null;

        // Initialize
        this.bindEvents();
        this.hideLoading();
        this.hideOutfitsLoading();

        this.fetchModelMetrics();

        this.applyInitialSidebarState();

        // Init Avatar Creator
        this.initAvatarCreator();
    }

    getCurrentThemeKey() {
        const season = this.seasonSelect?.value || '';
        const temp = parseFloat(this.tempSlider?.value || '20');
        const rain = this.rainSelect?.value || 'yok';
        const eventType = this.eventTypeSelect?.value || '';
        const style = this.styleSelect?.value || '';

        if (season === 'kış' || temp <= 8) return 'winter';
        if (season === 'yaz' || temp >= 24) return 'summer';
        if (rain === 'var') return 'rainy';
        if (eventType === 'work' || eventType === 'meeting') return 'work';
        if (style === 'formal' || eventType === 'special' || eventType === 'date') return 'formal';
        return 'casual';
    }

    themedOutfitSlots() {
        return [
            { key: 'winter', title: 'Winter', board: 'winter.svg', accent: '#38ef7d' },
            { key: 'summer', title: 'Summer', board: 'summer.svg', accent: '#f59e0b' },
            { key: 'rainy', title: 'Rainy', board: 'rainy.svg', accent: '#4facfe' },
            { key: 'work', title: 'Work', board: 'business.svg', accent: '#667eea' },
            { key: 'casual', title: 'Casual', board: 'street.svg', accent: '#ec4899' },
            { key: 'formal', title: 'Formal', board: 'formal.svg', accent: '#a855f7' },
        ];
    }

    scoreOutfitForTheme(outfit, themeKey) {
        const reasons = Array.isArray(outfit?.reasons) ? outfit.reasons.join(' ').toLowerCase() : '';
        const title = String(outfit?.title || '').toLowerCase();
        const pieces = Array.isArray(outfit?.pieces) ? outfit.pieces : [];

        const hasOuterwear = Boolean(outfit?.avatar_layers?.outerwear);
        const hasAccessory = Boolean(outfit?.avatar_layers?.accessory);

        const hasKeyword = (kw) => (title.includes(kw) || reasons.includes(kw));
        const hasPieceCategory = (cat) => pieces.some((p) => String(p?.category || '').toLowerCase() === cat);

        let s = 0;
        if (themeKey === 'winter') {
            if (hasOuterwear) s += 4;
            if (hasKeyword('kış') || hasKeyword('winter') || hasKeyword('soğuk') || hasKeyword('mont') || hasKeyword('ceket')) s += 3;
        }
        if (themeKey === 'summer') {
            if (!hasOuterwear) s += 2;
            if (hasKeyword('yaz') || hasKeyword('summer') || hasKeyword('serin') || hasKeyword('tişört') || hasKeyword('şort')) s += 3;
        }
        if (themeKey === 'rainy') {
            if (hasAccessory) s += 4;
            if (hasKeyword('yağmur') || hasKeyword('rain') || hasKeyword('umbrella') || hasKeyword('şemsiye')) s += 3;
        }
        if (themeKey === 'work') {
            if (hasKeyword('work') || hasKeyword('iş') || hasKeyword('meeting') || hasKeyword('office') || hasKeyword('gömlek')) s += 3;
        }
        if (themeKey === 'formal') {
            if (hasKeyword('formal') || hasKeyword('özel') || hasKeyword('special') || hasKeyword('date') || hasKeyword('klasik')) s += 3;
        }
        if (themeKey === 'casual') {
            if (hasKeyword('casual') || hasKeyword('günlük') || hasKeyword('street') || hasKeyword('rahat')) s += 3;
        }

        // Prefer full outfits with at least top/bottom/shoes
        if (hasPieceCategory('top')) s += 1;
        if (hasPieceCategory('bottom')) s += 1;
        if (hasPieceCategory('shoes')) s += 1;

        return s;
    }

    buildThemedOutfits(outfits) {
        const list = Array.isArray(outfits) ? outfits : [];
        const slots = this.themedOutfitSlots();

        const used = new Set();
        const picked = slots.map((slot) => {
            const ranked = list
                .map((o, idx) => ({ o, idx, s: this.scoreOutfitForTheme(o, slot.key) }))
                .sort((a, b) => b.s - a.s);

            let chosen = ranked.find((x) => !used.has(x.idx)) || ranked[0] || null;
            if (chosen) used.add(chosen.idx);

            return {
                ...slot,
                outfit: chosen ? chosen.o : null,
                sourceIndex: chosen ? chosen.idx : -1,
            };
        });

        // If backend returns fewer than slots, fill deterministically
        for (let i = 0; i < picked.length; i++) {
            if (picked[i].outfit) continue;
            const fallback = list[i % Math.max(1, list.length)] || null;
            picked[i].outfit = fallback;
            picked[i].sourceIndex = i % Math.max(1, list.length);
        }

        return picked;
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

        if (this.topbarGenerate) {
            this.topbarGenerate.addEventListener('click', () => this.predict());
        }

        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.drawerBackdrop) {
            this.drawerBackdrop.addEventListener('click', () => this.closeSidebar());
        }

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSidebar();
            }
        });

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

        if (this.outfitsGrid) {
            this.outfitsGrid.addEventListener('click', (e) => {
                const card = e.target && e.target.closest ? e.target.closest('.pin-card[data-outfit-index]') : null;
                if (!card) return;
                const idx = parseInt(card.getAttribute('data-outfit-index') || '0', 10);
                if (!Number.isFinite(idx)) return;
                this.selectOutfitIndex(idx);
            });
        }

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
                this.activeCity = data.data.city || city;
                this.displayWeather(data.data);
                this.updateFormFromWeather(data.data);
                this.updateActiveCityChip();

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
                this.setOutfits(result.outfits);
                this.updateActiveCityChip();
                this.showToast('Öneriler hazır', 'success');
            } else {
                this.showError('Tahmin yapılamadı: ' + result.error);
                this.showOutfitsError('Tahmin yapılamadı: ' + result.error);
                this.setOutfits([]);
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
        // Single academic summary: fill the existing summary blocks (selected/ml/rules/match)

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

        const themed = this.buildThemedOutfits(outfits);
        const currentTheme = this.getCurrentThemeKey();
        const heroOnError = this.imgOnErrorTo(this.defaultBoardImage());

        const cardsHtml = themed
            .map((slot, visualIdx) => {
                const o = slot.outfit || {};
                const reasons = Array.isArray(o.reasons) ? o.reasons : [];
                const pieces = Array.isArray(o.pieces) ? o.pieces : [];

                const title = this.escapeHtml(slot.title);
                const subtitle = this.escapeHtml(this.generateOutfitSubtitle(pieces) || '');
                const accent = slot.accent;
                const hero = `/static/images/boards/${slot.board}`;

                const isBest = slot.key === currentTheme;
                const bestBadge = isBest ? `<div class="best-city-badge">Best for Current City</div>` : '';

                const chipsHtml = reasons
                    .slice(0, 4)
                    .map((r) => `<span class="chip">${this.escapeHtml(r)}</span>`)
                    .join('');

                const piecesHtml = pieces
                    .slice(0, 6)
                    .map((p) => {
                        const labelRaw = p.label || p.category || 'Parça';
                        const label = this.escapeHtml(labelRaw);
                        const categoryRaw = p.category || '';
                        const category = this.escapeHtml(categoryRaw);
                        const img = this.escapeHtml(this.resolvePieceImage(p));
                        const onError = this.imgOnErrorTo(this.categoryFallbackImage(categoryRaw));

                        return `
                            <div class="piece-mini">
                                <img src="${img}" alt="${label}" loading="lazy" ${onError} />
                                <div>
                                    <div class="piece-mini-title">${label}</div>
                                    <div class="piece-mini-meta">
                                        <span class="piece-mini-cat">${category}</span>
                                    </div>
                                    ${p.shop_link ? `<a href="${p.shop_link}" target="_blank" rel="noopener" class="btn-shop">Boyner'de Gör</a>` : ''}
                                </div>
                            </div>
                        `;
                    })
                    .join('');

                return `
                    <article class="pin-card ${isBest ? 'is-best-for-city' : ''}" data-outfit-index="${slot.sourceIndex}" data-theme="${slot.key}" style="--accent: ${accent}">
                        <div class="pin-hero">
                            <img src="${hero}" alt="${title}" loading="lazy" ${heroOnError} />
                            ${bestBadge}
                        </div>
                        <div class="pin-body">
                            <div class="pin-title">${title}</div>
                            <div class="pin-subtitle">${subtitle}</div>
                            <div class="chip-row">${chipsHtml}</div>
                            <div class="pieces-row">${piecesHtml}</div>
                        </div>
                    </article>
                `;
            })
            .join('');

        this.outfitsGrid.innerHTML = cardsHtml;

        this.setOutfits(outfits);

        // Auto-select the best-for-current-city theme so the avatar and highlight match the current weather.
        const bestSlot = themed.find((s) => s && s.key === currentTheme);
        const bestIdx = bestSlot ? bestSlot.sourceIndex : -1;
        if (Number.isFinite(bestIdx) && bestIdx >= 0) {
            this.selectOutfitIndex(bestIdx);
        }
    }

    avatarAsset(name) {
        return `/static/images/avatar/${name}.svg`;
    }

    setOutfits(outfits) {
        this.currentOutfits = Array.isArray(outfits) ? outfits : [];
        this.selectedOutfitIndex = 0;
        this.applySelectedOutfitStyles();
        this.updateAvatarFromOutfit(this.currentOutfits[0]);
    }

    selectOutfitIndex(idx) {
        if (!Array.isArray(this.currentOutfits) || this.currentOutfits.length === 0) return;
        const safe = Math.max(0, Math.min(this.currentOutfits.length - 1, idx));
        this.selectedOutfitIndex = safe;
        this.applySelectedOutfitStyles();
        this.updateAvatarFromOutfit(this.currentOutfits[safe]);
    }

    applySelectedOutfitStyles() {
        if (!this.outfitsGrid) return;
        const cards = this.outfitsGrid.querySelectorAll('.pin-card[data-outfit-index]');
        cards.forEach((card) => {
            const idx = parseInt(card.getAttribute('data-outfit-index') || '0', 10);
            const isSelected = idx === this.selectedOutfitIndex;
            card.classList.toggle('is-selected', isSelected);
        });
    }

    updateAvatarFromOutfit(outfit) {
        if (!outfit) {
            if (this.avatarPieces) {
                this.avatarPieces.innerHTML = '<div class="avatar-pieces-placeholder">Bir kombin seçildiğinde parçalar burada görünecek.</div>';
            }
            return;
        }

        const layers = outfit.avatar_layers || {};
        const safeLayer = (key, fallback) => {
            const v = layers && typeof layers[key] === 'string' ? layers[key].trim() : '';
            return v || fallback;
        };

        if (this.avatarBody) this.avatarBody.src = safeLayer('body', this.avatarAsset('body'));
        if (this.avatarTop) this.avatarTop.src = safeLayer('top', this.avatarAsset('top'));
        if (this.avatarBottom) this.avatarBottom.src = safeLayer('bottom', this.avatarAsset('bottom'));
        if (this.avatarShoes) this.avatarShoes.src = safeLayer('shoes', this.avatarAsset('shoes'));

        const outer = layers && typeof layers.outerwear === 'string' ? layers.outerwear.trim() : '';
        if (this.avatarOuterwear) {
            this.avatarOuterwear.src = outer || this.avatarAsset('outerwear');
            this.avatarOuterwear.classList.toggle('hidden', !outer);
        }

        const acc = layers && typeof layers.accessory === 'string' ? layers.accessory.trim() : '';
        if (this.avatarAccessory) {
            this.avatarAccessory.src = acc || this.avatarAsset('accessory');
            this.avatarAccessory.classList.toggle('hidden', !acc);
        }

        this.renderAvatarPieces(outfit.pieces);
    }

    renderAvatarPieces(pieces) {
        if (!this.avatarPieces) return;

        const list = Array.isArray(pieces) ? pieces : [];
        if (list.length === 0) {
            this.avatarPieces.innerHTML = '<div class="avatar-pieces-placeholder">Bir kombin seçildiğinde parçalar burada görünecek.</div>';
            return;
        }

        const rows = list.map((p) => {
            const label = this.escapeHtml(p.label || p.category || 'Parça');
            const category = this.escapeHtml(p.category || '');
            const img = this.escapeHtml(this.resolvePieceImage(p));
            const onError = this.imgOnErrorTo(this.categoryFallbackImage(p.category || 'top'));

            return `
                <div class="avatar-piece-row">
                    <img src="${img}" alt="${label}" loading="lazy" ${onError} />
                    <div>
                        <div class="avatar-piece-title">${label}</div>
                        <div class="avatar-piece-sub">${category}</div>
                    </div>
                </div>
            `;
        });

        this.avatarPieces.innerHTML = rows.join('');
    }

    updateActiveCityChip() {
        const chipContainer = document.getElementById('active-city-chip-container');
        if (!chipContainer) return;

        if (this.activeCity) {
            chipContainer.innerHTML = `<div class="active-city-chip">Active: ${this.escapeHtml(this.activeCity)}</div>`;
            chipContainer.classList.remove('hidden');
        } else {
            chipContainer.innerHTML = '';
            chipContainer.classList.add('hidden');
        }
    }

    applyInitialSidebarState() {
        const isMobile = window.matchMedia && window.matchMedia('(max-width: 768px)').matches;
        if (isMobile) {
            document.body.classList.remove('sidebar-open');
        }
    }

    toggleSidebar() {
        document.body.classList.toggle('sidebar-open');
    }

    closeSidebar() {
        const isMobile = window.matchMedia && window.matchMedia('(max-width: 768px)').matches;
        if (isMobile) {
            document.body.classList.remove('sidebar-open');
        }
    }

    defaultBoardImage() {
        return '/static/images/boards/default.svg';
    }

    defaultPieceImage() {
        return '/static/images/boards/piece.svg';
    }

    categoryFallbackImage(category) {
        const safe = ['top', 'bottom', 'shoes', 'outerwear', 'accessory'].includes(category)
            ? category
            : 'top';
        return `/static/images/pieces_fallback/${safe}.svg`;
    }

    resolvePieceImage(piece) {
        const category = piece?.category || 'top';
        const label = piece?.label || piece?.category || 'piece';
        const base = piece?.image || '';

        if (typeof base === 'string' && base.trim().length > 0) {
            return base;
        }

        // deterministic generated placeholder, mirrors backend filename scheme
        const palette = (this.paletteSelect?.value || 'default');
        const slugify = (t) => {
            const map = { 'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u' };
            return String(t)
                .toLowerCase()
                .replace(/[çğıöşü]/g, (m) => map[m] || m)
                .replace(/[^a-z0-9]+/g, '-')
                .replace(/-+/g, '-')
                .replace(/^-|-$/g, '') || 'item';
        };

        const gen = `/static/images/generated/${category}__${slugify(label)}__${slugify(palette)}.svg`;
        return gen;
    }

    imgOnErrorTo(url) {
        const safe = this.escapeHtml(url);
        return `onerror="this.onerror=null;this.src='${safe}';"`;
    }

    generateOutfitSubtitle(pieces) {
        if (!Array.isArray(pieces) || pieces.length === 0) {
            return 'Complete outfit';
        }

        const labels = pieces.slice(0, 3).map(p => p.label || p.category).filter(Boolean);
        if (labels.length === 0) return 'Stylish combination';

        return labels.join(' + ');
    }

    getVariedBoardImageUrl(outfit, idx) {
        if (outfit && outfit.board_image) {
            return String(outfit.board_image);
        }

        const boardKeys = ['winter', 'summer', 'classic', 'minimalist', 'business', 'street', 'outdoors', 'rainy', 'date', 'sporty', 'default'];
        const key = boardKeys[idx % boardKeys.length];
        return `/static/images/boards/${key}.svg`;
    }

    getBoardImageUrl(outfit, idx) {
        if (outfit && outfit.board_image) {
            return String(outfit.board_image);
        }

        const temp = parseInt(this.tempSlider?.value || '20', 10);
        const rain = this.rainSelect?.value || 'yok';
        const style = this.styleSelect?.value || '';
        const eventType = this.eventTypeSelect?.value || '';

        let key = 'default';
        if (rain === 'var') key = 'rainy';
        else if (temp <= 8) key = 'winter';
        else if (temp >= 28) key = 'summer';
        else if (eventType === 'work' || eventType === 'meeting') key = 'business';
        else if (eventType === 'date') key = 'date';
        else if (eventType === 'outdoors') key = 'outdoors';
        else if (eventType === 'class') key = 'class';
        else if (eventType === 'sport') key = 'sporty';
        else if (style === 'street') key = 'street';
        else if (style === 'classic') key = 'classic';
        else if (style === 'minimalist') key = 'minimalist';
        else if (style === 'formal') key = 'formal';

        const variants = [key];
        const pick = variants[idx % variants.length] || key;
        return `/static/images/boards/${pick}.svg`;
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
        const canonical = [
            { key: 'rules', display_name: 'Rules (Baseline)', group: 'rule' },
            { key: 'xgboost', display_name: 'RandomForest / XGBoost', group: 'ml' },
            { key: 'random_forest', display_name: 'Random Forest', group: 'ml' },
            { key: 'mlp', display_name: 'sklearn MLP', group: 'ml' },
            { key: 'ann', display_name: 'ANN (PyTorch)', group: 'deep' },
            { key: 'cnn1d', display_name: 'CNN1D (PyTorch)', group: 'deep' },
            { key: 'lstm', display_name: 'LSTM (PyTorch)', group: 'deep' },
        ];

        const entries = canonical.map((c) => {
            const v = models[c.key] || { display_name: c.display_name };
            return { key: c.key, v, group: c.group, fallbackName: c.display_name };
        });

        const best = metrics.best_model ? String(metrics.best_model) : null;

        const cards = entries
            .map(({ key, v, group, fallbackName }) => {
                const name = this.escapeHtml(v.display_name || fallbackName || key);
                const acc = (typeof v.accuracy === 'number') ? `${(v.accuracy * 100).toFixed(1)}%` : '--';
                const f1 = (typeof v.macro_f1 === 'number') ? `${(v.macro_f1 * 100).toFixed(1)}%` : '--';
                const isBest = best && (best === key);

                // Determine model type badge
                let typeBadge = '';
                if (group === 'rule' || key === 'rules') {
                    typeBadge = '<span class="model-type-badge badge-rule">Rule</span>';
                } else if (group === 'ml' || ['xgboost', 'random_forest', 'mlp'].includes(key)) {
                    typeBadge = '<span class="model-type-badge badge-ml">ML</span>';
                } else if (group === 'deep' || ['ann', 'cnn1d', 'lstm'].includes(key)) {
                    typeBadge = '<span class="model-type-badge badge-deep">Deep Learning</span>';
                }

                // Experimental badge for CNN1D and LSTM
                const isExperimental = ['cnn1d', 'lstm'].includes(key);
                const expBadge = isExperimental ? '<span class="model-type-badge badge-experimental">Experimental</span>' : '';

                return `
                    <div class="metric-card ${isBest ? 'is-best' : ''}">
                        <div class="metric-title">
                            ${name}
                            ${isBest ? ' <span class="best-badge">Best</span>' : ''}
                        </div>
                        <div class="metric-badges">
                            ${typeBadge}
                            ${expBadge}
                        </div>
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
        if (this.outfitsGrid) {
            this.outfitsGrid.classList.remove('hidden');
            this.outfitsGrid.innerHTML = this.renderOutfitSkeletons(6);
        }
    }

    renderOutfitSkeletons(n) {
        const cards = Array.from({ length: n }).map(() => {
            return `
                <article class="pin-card pin-skeleton">
                    <div class="pin-hero"></div>
                    <div class="pin-body">
                        <div class="skeleton-line" style="width: 70%"></div>
                        <div class="skeleton-line" style="width: 95%"></div>
                        <div class="skeleton-line" style="width: 80%"></div>
                    </div>
                </article>
            `;
        });
        return cards.join('');
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

    /* =========================================
       READY PLAYER ME INTEGRATION
       ========================================= */
    initAvatarCreator() {
        const modal = document.getElementById('rpm-modal');
        const iframe = document.getElementById('rpm-iframe');
        const closeBtn = document.getElementById('rpm-close');
        const customBtn = document.getElementById('avatar-custom-btn');
        const stage = document.getElementById('avatar-stage');

        if (!modal || !iframe || !customBtn) return;

        // Load saved avatar on startup
        const savedAvatar = localStorage.getItem('user_avatar_url');
        if (savedAvatar && stage) {
            console.log('[App] Loading saved avatar:', savedAvatar);
            stage.setAttribute('data-model-url', savedAvatar);
        }

        const openModal = () => {
            modal.classList.add('active');
            // Use 'frameApi' to enable postMessage communication
            iframe.src = 'https://demo.readyplayer.me/avatar?frameApi';
        };

        const closeModal = () => {
            modal.classList.remove('active');
            iframe.src = ''; // Clear src to stop it running
        };

        customBtn.addEventListener('click', openModal);

        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        // Listen for RPM events
        window.addEventListener('message', (event) => {
            // Verify origin for security
            if (!event.origin.includes('readyplayer.me')) return;

            const url = event.data;

            try {
                if (typeof url === 'string' && url.startsWith('http')) {
                    // This is likely the avatar URL
                    console.log('[RPM] Avatar URL received:', url);

                    // Save and use
                    localStorage.setItem('user_avatar_url', url);

                    if (stage) {
                        stage.setAttribute('data-model-url', url);
                        this.showToast('Avatar güncellendi! Sayfa yenileniyor...', 'success');
                        setTimeout(() => window.location.reload(), 1500);
                    }

                    closeModal();
                }
            } catch (e) {
                console.error('[RPM] Error processing message:', e);
            }
        });
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

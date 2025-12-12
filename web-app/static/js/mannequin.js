/**
 * Outfit Display System
 * Shows outfit images with animations
 */

class OutfitDisplay {
    constructor() {
        this.outfitImage = document.getElementById('outfit-image');
        this.outfitEmoji = document.getElementById('outfit-emoji');
        this.outfitName = document.getElementById('outfit-name');
        this.outfitDesc = document.getElementById('outfit-desc');
        this.accessoryBadge = document.getElementById('accessory-badge');

        // Image mappings
        this.outfitImages = {
            'kalın_mont': 'mont.png',
            'kalın_mont_şemsiye': 'mont.png',
            'mont': 'mont.png',
            'mont_şemsiye': 'mont.png',
            'kaban': 'mont.png',
            'polar': 'kazak.png',
            'kazak': 'kazak.png',
            'hirka': 'kazak.png',
            'sweatshirt': 'kazak.png',
            'sweatshirt_şemsiye': 'kazak.png',
            'yağmurluk': 'yagmurluk.png',
            'yagmurluk': 'yagmurluk.png',
            'ceket': 'ceket.png',
            'ince_ceket': 'ceket.png',
            'gömlek': 'tisort.png',
            'gomlek': 'tisort.png',
            'tişört': 'tisort.png',
            'tisort': 'tisort.png',
            'tişört_şemsiye': 'tisort.png',
            'tişört_şort': 'tisort.png',
            'tişört_şort_şemsiye': 'tisort.png',
            'takim_elbise': 'takim_elbise.png',
            'resmi_giyim': 'takim_elbise.png',
            'elbise': 'takim_elbise.png',
            'gömlek_pantolon': 'takim_elbise.png',
            'gömlek_pantolon_şemsiye': 'takim_elbise.png'
        };

        // Emoji mappings
        this.outfitEmojis = {
            'kalın_mont': '🧥❄️',
            'kalın_mont_şemsiye': '🧥☂️',
            'mont': '🧥',
            'mont_şemsiye': '🧥☂️',
            'sweatshirt': '👕',
            'sweatshirt_şemsiye': '👕☂️',
            'kazak': '🧶',
            'polar': '🧥',
            'yağmurluk': '🧥🌧️',
            'yagmurluk': '🧥🌧️',
            'ceket': '🧥',
            'tişört': '👕',
            'tisort': '👕',
            'tişört_şemsiye': '👕☂️',
            'tişört_şort': '👕🩳',
            'tişört_şort_şemsiye': '👕🩳☂️',
            'gömlek_pantolon': '👔👖',
            'gömlek_pantolon_şemsiye': '👔👖☂️',
            'takim_elbise': '👔'
        };

        this.currentOutfit = null;
    }

    // Set outfit with animation
    setOutfit(outfitName, description = '', emoji = '') {
        const imageFile = this.outfitImages[outfitName] || this.outfitImages[outfitName.toLowerCase()] || 'tisort.png';
        const outfitEmoji = emoji || this.outfitEmojis[outfitName] || '👔';

        // Check if has umbrella
        const hasUmbrella = outfitName.includes('şemsiye') || outfitName.includes('semsiye');

        // Animate out
        if (this.outfitImage) {
            this.outfitImage.style.opacity = '0';
            this.outfitImage.style.transform = 'scale(0.8)';
        }

        setTimeout(() => {
            // Update image
            if (this.outfitImage) {
                this.outfitImage.src = `/static/images/outfits/${imageFile}`;
                this.outfitImage.style.opacity = '1';
                this.outfitImage.style.transform = 'scale(1)';
            }

            // Update emoji
            if (this.outfitEmoji) {
                this.outfitEmoji.textContent = outfitEmoji;
            }

            // Update name
            if (this.outfitName) {
                this.outfitName.textContent = this.formatName(outfitName);
            }

            // Update description
            if (this.outfitDesc) {
                this.outfitDesc.textContent = description || 'Önerilen kıyafet';
            }

            // Update accessory
            if (this.accessoryBadge) {
                this.accessoryBadge.textContent = hasUmbrella ? '☂️' : '';
            }

            this.currentOutfit = outfitName;

        }, 200);
    }

    // Format outfit name for display
    formatName(name) {
        return name
            .replace(/_/g, ' ')
            .replace(/şemsiye/g, '+ Şemsiye')
            .replace(/semsiye/g, '+ Şemsiye')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    // Update weather summary bar
    updateWeatherBar(temp, rain, wind, season) {
        const barTemp = document.getElementById('bar-temp');
        const barRain = document.getElementById('bar-rain');
        const barWind = document.getElementById('bar-wind');
        const barSeason = document.getElementById('bar-season');

        if (barTemp) barTemp.textContent = `${temp}°C`;
        if (barRain) barRain.textContent = rain === 'var' ? 'Yağmurlu' : 'Yok';
        if (barWind) barWind.textContent = this.formatWind(wind);
        if (barSeason) barSeason.textContent = this.formatSeason(season);
    }

    formatWind(wind) {
        const map = { 'zayıf': 'Hafif', 'orta': 'Orta', 'kuvvetli': 'Güçlü' };
        return map[wind] || wind;
    }

    formatSeason(season) {
        const map = { 'kış': 'Kış', 'ilkbahar': 'İlkbahar', 'yaz': 'Yaz', 'sonbahar': 'Sonbahar' };
        return map[season] || season;
    }

    // Reset to default
    reset() {
        this.setOutfit('tişört', 'Kıyafet önermek için butona tıklayın');
    }
}

// Global instance
let outfitDisplay = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    outfitDisplay = new OutfitDisplay();
});

// Export for use in main.js
window.OutfitDisplay = OutfitDisplay;
window.setOutfitDisplay = (outfit, description, emoji) => {
    if (outfitDisplay) {
        outfitDisplay.setOutfit(outfit, description, emoji);
    }
};
window.updateWeatherBar = (temp, rain, wind, season) => {
    if (outfitDisplay) {
        outfitDisplay.updateWeatherBar(temp, rain, wind, season);
    }
};

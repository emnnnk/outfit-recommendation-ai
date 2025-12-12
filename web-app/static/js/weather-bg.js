/**
 * Weather Background Animation
 * Canvas-based animated weather effects
 */

class WeatherBackground {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.currentWeather = 'clear';
        this.animationId = null;

        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    // Set weather type and create particles
    setWeather(weatherType) {
        this.currentWeather = weatherType.toLowerCase();
        this.particles = [];

        // Update body class for background gradient
        document.body.className = '';

        switch (this.currentWeather) {
            case 'rain':
            case 'drizzle':
                document.body.classList.add('weather-rainy');
                this.createRainParticles();
                break;
            case 'snow':
                document.body.classList.add('weather-snowy');
                this.createSnowParticles();
                break;
            case 'thunderstorm':
                document.body.classList.add('weather-stormy');
                this.createStormParticles();
                break;
            case 'clouds':
            case 'mist':
            case 'fog':
                document.body.classList.add('weather-cloudy');
                this.createCloudParticles();
                break;
            case 'clear':
            default:
                document.body.classList.add('weather-sunny');
                this.createSunParticles();
                break;
        }

        this.startAnimation();
    }

    // Rain particles
    createRainParticles() {
        const count = Math.floor(this.canvas.width / 8);
        for (let i = 0; i < count; i++) {
            this.particles.push({
                type: 'rain',
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                length: Math.random() * 20 + 10,
                speed: Math.random() * 15 + 10,
                opacity: Math.random() * 0.3 + 0.1
            });
        }
    }

    // Snow particles
    createSnowParticles() {
        const count = Math.floor(this.canvas.width / 15);
        for (let i = 0; i < count; i++) {
            this.particles.push({
                type: 'snow',
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                radius: Math.random() * 4 + 2,
                speed: Math.random() * 2 + 1,
                wobble: Math.random() * 2 - 1,
                wobbleSpeed: Math.random() * 0.02 + 0.01,
                wobblePhase: Math.random() * Math.PI * 2,
                opacity: Math.random() * 0.6 + 0.4
            });
        }
    }

    // Sun particles (light rays)
    createSunParticles() {
        const count = 50;
        for (let i = 0; i < count; i++) {
            this.particles.push({
                type: 'sun',
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                radius: Math.random() * 3 + 1,
                speed: Math.random() * 0.5 + 0.2,
                opacity: Math.random() * 0.3 + 0.1,
                pulse: Math.random() * Math.PI * 2,
                pulseSpeed: Math.random() * 0.02 + 0.01
            });
        }
    }

    // Cloud particles
    createCloudParticles() {
        const count = 20;
        for (let i = 0; i < count; i++) {
            this.particles.push({
                type: 'cloud',
                x: Math.random() * this.canvas.width,
                y: Math.random() * (this.canvas.height / 2),
                width: Math.random() * 200 + 100,
                height: Math.random() * 50 + 30,
                speed: Math.random() * 0.5 + 0.1,
                opacity: Math.random() * 0.1 + 0.05
            });
        }
    }

    // Storm particles (rain + lightning)
    createStormParticles() {
        this.createRainParticles();
        // Add extra rain
        const count = Math.floor(this.canvas.width / 5);
        for (let i = 0; i < count; i++) {
            this.particles.push({
                type: 'rain',
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                length: Math.random() * 30 + 15,
                speed: Math.random() * 20 + 15,
                opacity: Math.random() * 0.4 + 0.2
            });
        }
        // Lightning effect timing
        this.lightningTimer = 0;
        this.lightningActive = false;
    }

    // Animation loop
    startAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.animate();
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw and update particles
        this.particles.forEach(particle => {
            switch (particle.type) {
                case 'rain':
                    this.drawRain(particle);
                    break;
                case 'snow':
                    this.drawSnow(particle);
                    break;
                case 'sun':
                    this.drawSun(particle);
                    break;
                case 'cloud':
                    this.drawCloud(particle);
                    break;
            }
        });

        // Lightning effect for storm
        if (this.currentWeather === 'thunderstorm') {
            this.drawLightning();
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    // Draw rain drop
    drawRain(particle) {
        this.ctx.beginPath();
        this.ctx.moveTo(particle.x, particle.y);
        this.ctx.lineTo(particle.x + 1, particle.y + particle.length);
        this.ctx.strokeStyle = `rgba(174, 194, 224, ${particle.opacity})`;
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();

        // Update position
        particle.y += particle.speed;
        particle.x += 1; // Slight angle

        // Reset if out of screen
        if (particle.y > this.canvas.height) {
            particle.y = -particle.length;
            particle.x = Math.random() * this.canvas.width;
        }
    }

    // Draw snow flake
    drawSnow(particle) {
        // Update wobble
        particle.wobblePhase += particle.wobbleSpeed;
        const wobbleX = Math.sin(particle.wobblePhase) * particle.wobble;

        // Draw snowflake
        this.ctx.beginPath();
        this.ctx.arc(particle.x + wobbleX, particle.y, particle.radius, 0, Math.PI * 2);
        this.ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
        this.ctx.fill();

        // Add sparkle
        if (Math.random() > 0.95) {
            this.ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity + 0.2})`;
            this.ctx.fill();
        }

        // Update position
        particle.y += particle.speed;
        particle.x += wobbleX * 0.1;

        // Reset if out of screen
        if (particle.y > this.canvas.height) {
            particle.y = -10;
            particle.x = Math.random() * this.canvas.width;
        }
    }

    // Draw sun particle (glowing dots)
    drawSun(particle) {
        // Update pulse
        particle.pulse += particle.pulseSpeed;
        const pulseFactor = 1 + Math.sin(particle.pulse) * 0.3;

        // Draw glowing particle
        const gradient = this.ctx.createRadialGradient(
            particle.x, particle.y, 0,
            particle.x, particle.y, particle.radius * pulseFactor * 2
        );
        gradient.addColorStop(0, `rgba(255, 223, 128, ${particle.opacity * pulseFactor})`);
        gradient.addColorStop(1, 'rgba(255, 223, 128, 0)');

        this.ctx.beginPath();
        this.ctx.arc(particle.x, particle.y, particle.radius * pulseFactor * 2, 0, Math.PI * 2);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();

        // Slow upward drift
        particle.y -= particle.speed * 0.5;
        particle.x += Math.sin(particle.pulse) * 0.2;

        // Reset if out of screen
        if (particle.y < -10) {
            particle.y = this.canvas.height + 10;
            particle.x = Math.random() * this.canvas.width;
        }
    }

    // Draw cloud
    drawCloud(particle) {
        this.ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;

        // Draw cloud shape (multiple circles)
        const cx = particle.x;
        const cy = particle.y;
        const w = particle.width;
        const h = particle.height;

        this.ctx.beginPath();
        this.ctx.arc(cx, cy, h * 0.6, 0, Math.PI * 2);
        this.ctx.arc(cx + w * 0.2, cy - h * 0.2, h * 0.5, 0, Math.PI * 2);
        this.ctx.arc(cx + w * 0.4, cy, h * 0.7, 0, Math.PI * 2);
        this.ctx.arc(cx + w * 0.6, cy - h * 0.1, h * 0.5, 0, Math.PI * 2);
        this.ctx.arc(cx + w * 0.8, cy, h * 0.6, 0, Math.PI * 2);
        this.ctx.fill();

        // Move cloud
        particle.x += particle.speed;

        // Reset if out of screen
        if (particle.x > this.canvas.width + particle.width) {
            particle.x = -particle.width;
        }
    }

    // Draw lightning effect
    drawLightning() {
        this.lightningTimer++;

        // Random lightning flash
        if (this.lightningTimer > 100 && Math.random() > 0.995) {
            this.lightningActive = true;
            this.lightningTimer = 0;

            // Flash effect
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

            // Draw lightning bolt
            this.drawLightningBolt();
        }

        if (this.lightningActive && this.lightningTimer < 5) {
            this.ctx.fillStyle = `rgba(255, 255, 255, ${0.2 - this.lightningTimer * 0.04})`;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        } else {
            this.lightningActive = false;
        }
    }

    // Draw lightning bolt
    drawLightningBolt() {
        const startX = Math.random() * this.canvas.width;
        let x = startX;
        let y = 0;

        this.ctx.beginPath();
        this.ctx.moveTo(x, y);

        while (y < this.canvas.height * 0.7) {
            x += (Math.random() - 0.5) * 50;
            y += Math.random() * 30 + 20;
            this.ctx.lineTo(x, y);
        }

        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();

        // Glow effect
        this.ctx.strokeStyle = 'rgba(200, 200, 255, 0.5)';
        this.ctx.lineWidth = 8;
        this.ctx.stroke();
    }

    // Stop animation
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
}

// Global instance
let weatherBg = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    weatherBg = new WeatherBackground('weather-canvas');
    weatherBg.setWeather('clear'); // Default
});

// Export for use in main.js
window.WeatherBackground = WeatherBackground;
window.setWeatherBackground = (weatherType) => {
    if (weatherBg) {
        weatherBg.setWeather(weatherType);
    }
};

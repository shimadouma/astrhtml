/**
 * Theme management for dark/light mode
 */

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.toggleButton = null;
        this.init();
    }

    init() {
        // Apply saved theme
        this.applyTheme(this.currentTheme);
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupToggle());
        } else {
            this.setupToggle();
        }
    }

    setupToggle() {
        this.toggleButton = document.querySelector('.theme-toggle');
        if (this.toggleButton) {
            this.updateToggleText();
            this.toggleButton.addEventListener('click', () => this.toggleTheme());
        }
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        
        if (this.toggleButton) {
            this.updateToggleText();
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    updateToggleText() {
        if (this.toggleButton) {
            this.toggleButton.textContent = this.currentTheme === 'light' ? '🌙 ダークモード' : '☀️ ライトモード';
            this.toggleButton.setAttribute('aria-label', 
                this.currentTheme === 'light' ? 'ダークモードに切り替え' : 'ライトモードに切り替え'
            );
        }
    }
}

// Initialize theme manager
const themeManager = new ThemeManager();
/**
 * Font management for sans-serif/serif switching
 */

class FontManager {
    constructor() {
        this.currentFont = localStorage.getItem('font') || 'sans-serif';
        this.toggleButton = null;
        this.init();
    }

    init() {
        // Apply saved font
        this.applyFont(this.currentFont);
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupToggle());
        } else {
            this.setupToggle();
        }
    }

    setupToggle() {
        this.toggleButton = document.querySelector('.font-toggle');
        if (this.toggleButton) {
            this.updateToggleText();
            this.toggleButton.addEventListener('click', () => this.toggleFont());
        }
    }

    applyFont(font) {
        document.documentElement.setAttribute('data-font', font);
        this.currentFont = font;
        localStorage.setItem('font', font);
        
        if (this.toggleButton) {
            this.updateToggleText();
        }
    }

    toggleFont() {
        const newFont = this.currentFont === 'sans-serif' ? 'serif' : 'sans-serif';
        this.applyFont(newFont);
    }

    updateToggleText() {
        if (this.toggleButton) {
            const isSerif = this.currentFont === 'serif';
            this.toggleButton.textContent = isSerif ? 'あ ゴシック体' : 'あ 明朝体';
            this.toggleButton.setAttribute('aria-label', 
                isSerif ? 'ゴシック体フォントに切り替え' : '明朝体フォントに切り替え'
            );
        }
    }
}

// Initialize font manager
const fontManager = new FontManager();
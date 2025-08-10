/**
 * Card filtering functionality for unified event and main story layout
 */

class FilterManager {
    constructor() {
        this.allCards = [];
        this.activeFilters = {
            type: '',
            sort: 'default',
            search: ''
        };
        this.init();
    }

    init() {
        this.collectCardData();
        this.setupFilterUI();
        this.bindEvents();
        this.applyFilters();
    }

    collectCardData() {
        // Use data passed from template if available
        if (window.cardData) {
            this.allCards = window.cardData.map(card => ({
                ...card,
                element: null // Will be set when rendering
            }));
        } else {
            // Fallback: collect from DOM
            const cards = document.querySelectorAll('.card');
            this.allCards = Array.from(cards).map(card => {
                const titleElement = card.querySelector('.card-title a');
                const typeElement = card.querySelector('.event-type, .chapter-indicator');
                const dateElement = card.querySelector('.event-date');
                
                return {
                    element: card,
                    title: titleElement ? titleElement.textContent.trim() : '',
                    type: this.determineCardType(card),
                    subtitle: this.getCardSubtitle(card),
                    link: titleElement ? titleElement.getAttribute('href') : '',
                    can_access: !titleElement || !titleElement.closest('.btn-disabled'),
                    start_date: dateElement ? this.extractDate(dateElement.textContent) : '',
                    story_count: this.getStoryCount(card)
                };
            });
        }
        
        console.log('Collected cards:', this.allCards.length);
    }

    determineCardType(card) {
        if (card.classList.contains('main-story-card')) {
            return 'main_story';
        }
        const typeElement = card.querySelector('.event-type');
        return typeElement ? typeElement.textContent.trim() : '';
    }

    getCardSubtitle(card) {
        const subtitleElement = card.querySelector('.card-subtitle, .event-type');
        return subtitleElement ? subtitleElement.textContent.trim() : '';
    }

    getStoryCount(card) {
        const storyElement = card.querySelector('.event-stories');
        if (storyElement) {
            const match = storyElement.textContent.match(/(\d+)/);
            return match ? parseInt(match[1]) : 0;
        }
        return 0;
    }

    extractDate(dateText) {
        const match = dateText.match(/(\d{4}年\d{2}月\d{2}日)/);
        return match ? match[1] : '';
    }

    extractYear(dateText) {
        // Extract year from date text like "開催期間: 2025-07-17 ~ 2025-08-07"
        const match = dateText.match(/(\d{4})/);
        return match ? match[1] : '';
    }

    setupFilterUI() {
        // Filter UI is already in the template, just get references
        this.typeFilter = document.getElementById('type-filter');
        this.sortFilter = document.getElementById('sort-filter');
        this.clearButton = document.querySelector('.filter-clear');
        this.resultsCount = document.querySelector('.results-count');
    }

    bindEvents() {
        if (this.typeFilter) {
            this.typeFilter.addEventListener('change', () => {
                this.activeFilters.type = this.typeFilter.value;
                this.applyFilters();
            });
        }

        if (this.sortFilter) {
            this.sortFilter.addEventListener('change', () => {
                this.activeFilters.sort = this.sortFilter.value;
                this.applyFilters();
            });
        }

        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => {
                this.clearFilters();
            });
        }

        // Listen to search events (if search is implemented)
        document.addEventListener('searchUpdated', (e) => {
            this.activeFilters.search = e.detail.query;
            this.applyFilters();
        });
    }

    applyFilters() {
        let filteredCards = [...this.allCards];

        // Apply type filter
        if (this.activeFilters.type) {
            if (this.activeFilters.type === 'main_story') {
                filteredCards = filteredCards.filter(card => card.type === 'main_story');
            } else {
                filteredCards = filteredCards.filter(card => 
                    card.type !== 'main_story' && card.subtitle === this.activeFilters.type
                );
            }
        }

        // Apply search filter
        if (this.activeFilters.search) {
            const query = this.activeFilters.search.toLowerCase();
            filteredCards = filteredCards.filter(card => 
                card.title.toLowerCase().includes(query) ||
                card.subtitle.toLowerCase().includes(query)
            );
        }

        // Apply sorting
        this.sortCards(filteredCards);

        this.renderCards(filteredCards);
        this.updateResultsCount(filteredCards.length);
    }

    sortCards(cards) {
        switch (this.activeFilters.sort) {
            case 'date-desc':
                cards.sort((a, b) => {
                    if (a.type === 'main_story' && b.type !== 'main_story') return -1;
                    if (a.type !== 'main_story' && b.type === 'main_story') return 1;
                    if (a.type === 'main_story' && b.type === 'main_story') {
                        return (a.chapter_number || 0) - (b.chapter_number || 0);
                    }
                    return b.sort_key.localeCompare(a.sort_key);
                });
                break;
            case 'date-asc':
                cards.sort((a, b) => {
                    if (a.type === 'main_story' && b.type !== 'main_story') return -1;
                    if (a.type !== 'main_story' && b.type === 'main_story') return 1;
                    if (a.type === 'main_story' && b.type === 'main_story') {
                        return (a.chapter_number || 0) - (b.chapter_number || 0);
                    }
                    return a.sort_key.localeCompare(b.sort_key);
                });
                break;
            case 'name-asc':
                cards.sort((a, b) => a.title.localeCompare(b.title));
                break;
            default: // 'default'
                // Keep original order (main story first, then events by date)
                break;
        }
    }

    renderCards(cards) {
        const container = document.getElementById('cards-container');
        if (!container) return;

        // Clear existing cards
        container.innerHTML = '';

        // Render filtered cards
        cards.forEach(card => {
            const cardElement = this.createCardElement(card);
            container.appendChild(cardElement);
        });

        // Show/hide "no results" message
        this.toggleNoResults(cards.length === 0, container);
    }

    createCardElement(card) {
        const article = document.createElement('article');
        article.className = `card ${card.type === 'main_story' ? 'main-story-card' : 'event-card'}`;

        let headerContent = '';
        if (card.type === 'main_story') {
            headerContent = `
                <div class="chapter-indicator">
                    第${String(card.chapter_number).padStart(2, '0')}章
                </div>
            `;
        } else {
            headerContent = `
                <span class="event-type">${card.subtitle}</span>
            `;
        }

        let bodyContent = '';
        if (card.type === 'main_story') {
            bodyContent = `
                <p class="card-subtitle">${card.subtitle}</p>
            `;
        } else {
            bodyContent = `
                <p class="event-date">
                    開催期間: ${card.start_date} ~ ${card.end_date}
                </p>
                <p class="event-stories">
                    ストーリー数: ${card.story_count}
                </p>
            `;
        }

        article.innerHTML = `
            <div class="card-header">
                ${headerContent}
                <h3 class="card-title">
                    <a href="${card.link}">${card.title}</a>
                </h3>
            </div>
            
            <div class="card-body">
                ${bodyContent}
            </div>
            
            <div class="card-footer">
                <a href="${card.link}" 
                   class="btn btn-primary${!card.can_access ? ' btn-disabled' : ''}">
                    ${card.can_access ? 'ストーリーを読む' : '準備中'}
                </a>
            </div>
        `;

        return article;
    }

    toggleNoResults(show, container) {
        const existingMessage = document.querySelector('.no-cards-message');
        
        if (show && !existingMessage) {
            const message = document.createElement('div');
            message.className = 'no-cards-message';
            message.innerHTML = '<p>条件に一致するストーリーが見つかりませんでした。</p>';
            container.after(message);
        } else if (!show && existingMessage) {
            existingMessage.remove();
        }
    }

    updateResultsCount(count) {
        if (this.resultsCount) {
            const total = this.allCards.length;
            if (count === total) {
                this.resultsCount.textContent = `${total}件のストーリー`;
            } else {
                this.resultsCount.textContent = `${count}/${total}件のストーリーを表示`;
            }
        }
    }

    clearFilters() {
        // Reset filter values
        this.activeFilters = {
            type: '',
            sort: 'default',
            search: ''
        };

        // Reset UI
        if (this.typeFilter) this.typeFilter.value = '';
        if (this.sortFilter) this.sortFilter.value = 'default';

        // Clear search if it exists
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.value = '';
            // Trigger search clear
            const event = new CustomEvent('searchCleared');
            document.dispatchEvent(event);
        }

        this.applyFilters();
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new FilterManager());
} else {
    new FilterManager();
}
/**
 * Event filtering functionality
 */

class FilterManager {
    constructor() {
        this.events = [];
        this.allEvents = [];
        this.activeFilters = {
            type: '',
            year: '',
            search: ''
        };
        this.init();
    }

    init() {
        this.collectEventData();
        this.setupFilterUI();
        this.bindEvents();
        this.applyFilters();
    }

    collectEventData() {
        // Collect all event cards from DOM
        const eventCards = document.querySelectorAll('.event-card');
        this.allEvents = Array.from(eventCards).map(card => {
            const titleElement = card.querySelector('.event-title a');
            const typeElement = card.querySelector('.event-type');
            const dateElement = card.querySelector('.event-date');
            
            return {
                element: card,
                title: titleElement ? titleElement.textContent.trim() : '',
                type: typeElement ? typeElement.textContent.trim() : '',
                dateText: dateElement ? dateElement.textContent.trim() : '',
                year: this.extractYear(dateElement ? dateElement.textContent.trim() : '')
            };
        });
        
        this.events = [...this.allEvents];
        console.log('Collected events:', this.events.length);
    }

    extractYear(dateText) {
        // Extract year from date text like "開催期間: 2025-07-17 ~ 2025-08-07"
        const match = dateText.match(/(\d{4})/);
        return match ? match[1] : '';
    }

    setupFilterUI() {
        const eventsSection = document.querySelector('#events');
        if (!eventsSection) return;

        // Create filter container
        const filterContainer = document.createElement('div');
        filterContainer.className = 'filter-container';
        
        // Get unique types and years
        const types = [...new Set(this.allEvents.map(e => e.type).filter(t => t))].sort();
        const years = [...new Set(this.allEvents.map(e => e.year).filter(y => y))].sort().reverse();

        filterContainer.innerHTML = `
            <div class="filter-controls">
                <div class="filter-group">
                    <label for="type-filter">イベント種別:</label>
                    <select id="type-filter" class="filter-select">
                        <option value="">すべて</option>
                        ${types.map(type => `<option value="${type}">${type}</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="year-filter">開催年:</label>
                    <select id="year-filter" class="filter-select">
                        <option value="">すべて</option>
                        ${years.map(year => `<option value="${year}">${year}年</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <button id="clear-filters" class="filter-clear">フィルターをクリア</button>
                </div>
            </div>
            
            <div class="filter-results">
                <span class="results-count"></span>
            </div>
        `;

        // Insert after events header
        const eventsHeader = eventsSection.querySelector('h2');
        if (eventsHeader) {
            eventsHeader.after(filterContainer);
        }

        // Get references
        this.typeFilter = document.getElementById('type-filter');
        this.yearFilter = document.getElementById('year-filter');
        this.clearButton = document.getElementById('clear-filters');
        this.resultsCount = document.querySelector('.results-count');
    }

    bindEvents() {
        if (this.typeFilter) {
            this.typeFilter.addEventListener('change', () => {
                this.activeFilters.type = this.typeFilter.value;
                this.applyFilters();
            });
        }

        if (this.yearFilter) {
            this.yearFilter.addEventListener('change', () => {
                this.activeFilters.year = this.yearFilter.value;
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
        let filteredEvents = [...this.allEvents];

        // Apply type filter
        if (this.activeFilters.type) {
            filteredEvents = filteredEvents.filter(event => 
                event.type === this.activeFilters.type
            );
        }

        // Apply year filter
        if (this.activeFilters.year) {
            filteredEvents = filteredEvents.filter(event => 
                event.year === this.activeFilters.year
            );
        }

        // Apply search filter
        if (this.activeFilters.search) {
            const query = this.activeFilters.search.toLowerCase();
            filteredEvents = filteredEvents.filter(event => 
                event.title.toLowerCase().includes(query) ||
                event.type.toLowerCase().includes(query)
            );
        }

        this.showFilteredEvents(filteredEvents);
        this.updateResultsCount(filteredEvents.length);
    }

    showFilteredEvents(filteredEvents) {
        // Hide all events first
        this.allEvents.forEach(event => {
            event.element.style.display = 'none';
        });

        // Show filtered events
        filteredEvents.forEach(event => {
            event.element.style.display = 'block';
        });

        // Show/hide "no results" message
        this.toggleNoResults(filteredEvents.length === 0);
    }

    toggleNoResults(show) {
        const existingMessage = document.querySelector('.no-events-message');
        
        if (show && !existingMessage) {
            const eventsGrid = document.querySelector('.events-grid');
            if (eventsGrid) {
                const message = document.createElement('div');
                message.className = 'no-events-message';
                message.innerHTML = '<p>条件に一致するイベントが見つかりませんでした。</p>';
                eventsGrid.after(message);
            }
        } else if (!show && existingMessage) {
            existingMessage.remove();
        }
    }

    updateResultsCount(count) {
        if (this.resultsCount) {
            const total = this.allEvents.length;
            if (count === total) {
                this.resultsCount.textContent = `${total}件のイベント`;
            } else {
                this.resultsCount.textContent = `${count}/${total}件のイベントを表示`;
            }
        }
    }

    clearFilters() {
        // Reset filter values
        this.activeFilters = {
            type: '',
            year: '',
            search: ''
        };

        // Reset UI
        if (this.typeFilter) this.typeFilter.value = '';
        if (this.yearFilter) this.yearFilter.value = '';

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
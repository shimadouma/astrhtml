/**
 * Client-side search functionality
 */

class SearchManager {
    constructor() {
        this.searchData = null;
        this.searchInput = null;
        this.searchResults = null;
        this.isLoading = false;
        this.init();
    }

    async init() {
        await this.loadSearchData();
        this.setupSearchUI();
        this.bindEvents();
    }

    async loadSearchData() {
        try {
            this.isLoading = true;
            const response = await fetch('/static/data/search.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.searchData = await response.json();
            console.log('Search data loaded:', this.searchData);
        } catch (error) {
            console.error('Failed to load search data:', error);
        } finally {
            this.isLoading = false;
        }
    }

    setupSearchUI() {
        // Create search container
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.innerHTML = `
            <div class="search-input-container">
                <input type="text" 
                       class="search-input" 
                       placeholder="イベント名、ストーリー名、内容で検索..." 
                       autocomplete="off">
                <button class="search-clear" style="display: none;">×</button>
            </div>
            <div class="search-results" style="display: none;"></div>
        `;

        // Insert after events section header
        const eventsSection = document.querySelector('#events');
        if (eventsSection) {
            const eventsHeader = eventsSection.querySelector('h2');
            if (eventsHeader) {
                eventsHeader.after(searchContainer);
            }
        }

        // Get references
        this.searchInput = document.querySelector('.search-input');
        this.searchResults = document.querySelector('.search-results');
        this.searchClear = document.querySelector('.search-clear');
    }

    bindEvents() {
        if (!this.searchInput) return;

        // Search input
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Clear button
        if (this.searchClear) {
            this.searchClear.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // ESC key to clear search
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.searchInput === document.activeElement) {
                this.clearSearch();
            }
        });
    }

    handleSearch(query) {
        query = query.trim();

        // Show/hide clear button
        if (this.searchClear) {
            this.searchClear.style.display = query ? 'block' : 'none';
        }

        if (query.length < 2) {
            this.hideResults();
            return;
        }

        if (!this.searchData) {
            this.showResults([{ 
                type: 'message', 
                content: this.isLoading ? '検索データを読み込み中...' : '検索データの読み込みに失敗しました' 
            }]);
            return;
        }

        const results = this.performSearch(query);
        this.showResults(results);
    }

    performSearch(query) {
        const normalizedQuery = query.toLowerCase();
        const results = [];

        // Search events
        for (const event of this.searchData.events) {
            if (event.searchable_text.toLowerCase().includes(normalizedQuery)) {
                results.push({
                    type: 'event',
                    ...event,
                    relevance: this.calculateRelevance(event.searchable_text, normalizedQuery)
                });
            }
        }

        // Search stories
        for (const story of this.searchData.stories) {
            if (story.searchable_text.toLowerCase().includes(normalizedQuery)) {
                results.push({
                    type: 'story',
                    ...story,
                    relevance: this.calculateRelevance(story.searchable_text, normalizedQuery)
                });
            }
        }

        // Sort by relevance (higher is better)
        results.sort((a, b) => b.relevance - a.relevance);

        return results.slice(0, 10); // Limit to 10 results
    }

    calculateRelevance(text, query) {
        const lowerText = text.toLowerCase();
        const lowerQuery = query.toLowerCase();
        
        let score = 0;
        
        // Exact match in name gets highest score
        if (lowerText.includes(lowerQuery)) {
            score += 10;
        }
        
        // Count occurrences
        const occurrences = (lowerText.match(new RegExp(lowerQuery, 'g')) || []).length;
        score += occurrences;
        
        // Boost if query appears at the beginning
        if (lowerText.startsWith(lowerQuery)) {
            score += 5;
        }
        
        return score;
    }

    showResults(results) {
        if (!this.searchResults) return;

        if (results.length === 0) {
            this.searchResults.innerHTML = '<div class="search-no-results">検索結果が見つかりませんでした</div>';
        } else {
            const html = results.map(result => {
                if (result.type === 'message') {
                    return `<div class="search-message">${result.content}</div>`;
                } else if (result.type === 'event') {
                    return `
                        <div class="search-result search-event">
                            <a href="${result.url}">
                                <div class="search-title">${this.highlightMatch(result.name, this.searchInput.value)}</div>
                                <div class="search-meta">イベント • ${result.type}</div>
                                <div class="search-date">${result.start_date} ~ ${result.end_date}</div>
                            </a>
                        </div>
                    `;
                } else if (result.type === 'story') {
                    return `
                        <div class="search-result search-story">
                            <a href="${result.url}">
                                <div class="search-title">${this.highlightMatch(result.name, this.searchInput.value)}</div>
                                <div class="search-meta">ストーリー • ${result.event_name}</div>
                                ${result.info ? `<div class="search-snippet">${this.highlightMatch(result.info, this.searchInput.value)}</div>` : ''}
                            </a>
                        </div>
                    `;
                }
                return '';
            }).join('');

            this.searchResults.innerHTML = html;
        }

        this.searchResults.style.display = 'block';
    }

    hideResults() {
        if (this.searchResults) {
            this.searchResults.style.display = 'none';
        }
    }

    clearSearch() {
        if (this.searchInput) {
            this.searchInput.value = '';
            this.searchInput.focus();
        }
        if (this.searchClear) {
            this.searchClear.style.display = 'none';
        }
        this.hideResults();
    }

    highlightMatch(text, query) {
        if (!query.trim()) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
}

// Initialize search when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new SearchManager());
} else {
    new SearchManager();
}
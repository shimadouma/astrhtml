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
            // Use base path from window.basePath or fallback to relative path
            const basePath = window.basePath || './';
            const searchUrl = `${basePath}static/data/search.json`;
            const response = await fetch(searchUrl);
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
                       placeholder="イベント名、メインストーリー、内容で検索..." 
                       autocomplete="off">
                <button class="search-clear" style="display: none;">×</button>
            </div>
            <div class="search-query-display" style="display: none;">
                <span class="query-label">検索条件:</span>
                <span class="query-content"></span>
            </div>
            <div class="search-results" style="display: none;"></div>
        `;

        // Insert after content section header or filter container
        const contentSection = document.querySelector('#content');
        if (contentSection) {
            const filterContainer = contentSection.querySelector('.filter-container');
            if (filterContainer) {
                // Insert search after filter container
                filterContainer.after(searchContainer);
            } else {
                // Fallback: insert after section header
                const contentHeader = contentSection.querySelector('h2');
                if (contentHeader) {
                    contentHeader.after(searchContainer);
                }
            }
        }

        // Get references
        this.searchInput = document.querySelector('.search-input');
        this.searchResults = document.querySelector('.search-results');
        this.searchClear = document.querySelector('.search-clear');
        this.queryDisplay = document.querySelector('.search-query-display');
        this.queryContent = document.querySelector('.query-content');
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
            this.hideQueryDisplay();
            return;
        }

        // Parse query into keywords for AND search
        const keywords = this.parseQuery(query);
        this.showQueryDisplay(keywords);

        if (!this.searchData) {
            this.showResults([{ 
                type: 'message', 
                content: this.isLoading ? '検索データを読み込み中...' : '検索データの読み込みに失敗しました' 
            }]);
            return;
        }

        const results = this.performSearch(keywords);
        this.showResults(results);
    }

    parseQuery(queryString) {
        // Split by both half-width and full-width spaces, filter out empty strings
        return queryString.split(/[\s　]+/).filter(keyword => keyword.trim().length > 0);
    }

    performSearch(keywords) {
        const results = [];

        // Search events
        for (const event of this.searchData.events) {
            if (this.matchesAllKeywords(event.searchable_text, keywords)) {
                results.push({
                    type: 'event',
                    ...event,
                    relevance: this.calculateRelevanceForKeywords(event.searchable_text, keywords)
                });
            }
        }

        // Search stories
        for (const story of this.searchData.stories) {
            if (this.matchesAllKeywords(story.searchable_text, keywords)) {
                results.push({
                    type: 'story',
                    ...story,
                    relevance: this.calculateRelevanceForKeywords(story.searchable_text, keywords)
                });
            }
        }

        // Sort by relevance (higher is better)
        results.sort((a, b) => b.relevance - a.relevance);

        return results.slice(0, 10); // Limit to 10 results
    }

    matchesAllKeywords(text, keywords) {
        const lowerText = text.toLowerCase();
        return keywords.every(keyword => lowerText.includes(keyword.toLowerCase()));
    }

    calculateRelevanceForKeywords(text, keywords) {
        const lowerText = text.toLowerCase();
        let score = 0;
        
        keywords.forEach(keyword => {
            const lowerKeyword = keyword.toLowerCase();
            
            // Exact match gets highest score
            if (lowerText.includes(lowerKeyword)) {
                score += 10;
            }
            
            // Count occurrences
            const occurrences = (lowerText.match(new RegExp(lowerKeyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
            score += occurrences;
            
            // Boost if keyword appears at the beginning
            if (lowerText.startsWith(lowerKeyword)) {
                score += 5;
            }
        });
        
        return score;
    }

    calculateRelevance(text, query) {
        // Legacy method for backward compatibility
        return this.calculateRelevanceForKeywords(text, [query]);
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
                    const keywords = this.parseQuery(this.searchInput.value);
                    return `
                        <div class="search-result search-event">
                            <a href="${result.url}">
                                <div class="search-title">${this.highlightMatches(result.name, keywords)}</div>
                                <div class="search-meta">イベント • ${result.type}</div>
                                <div class="search-date">${result.start_date} ~ ${result.end_date}</div>
                            </a>
                        </div>
                    `;
                } else if (result.type === 'story') {
                    const keywords = this.parseQuery(this.searchInput.value);
                    return `
                        <div class="search-result search-story">
                            <a href="${result.url}">
                                <div class="search-title">${this.highlightMatches(result.name, keywords)}</div>
                                <div class="search-meta">ストーリー • ${result.event_name}</div>
                                ${result.info ? `<div class="search-snippet">${this.highlightMatches(result.info, keywords)}</div>` : ''}
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

    showQueryDisplay(keywords) {
        if (!this.queryDisplay || !this.queryContent || keywords.length === 0) return;
        
        // Build query display with CSS-styled keywords and operators
        const queryHtml = keywords.map(keyword => 
            `<span class="search-keyword">${this.escapeHtml(keyword)}</span>`
        ).join(' <span class="search-operator">AND</span> ');
        
        this.queryContent.innerHTML = queryHtml;
        this.queryDisplay.style.display = 'block';
    }

    hideQueryDisplay() {
        if (this.queryDisplay) {
            this.queryDisplay.style.display = 'none';
        }
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
        this.hideQueryDisplay();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    highlightMatches(text, keywords) {
        if (!keywords || keywords.length === 0) return text;
        
        let highlightedText = text;
        keywords.forEach(keyword => {
            if (keyword.trim()) {
                const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
            }
        });
        
        return highlightedText;
    }

    highlightMatch(text, query) {
        // Legacy method for backward compatibility
        return this.highlightMatches(text, [query]);
    }
}

// Initialize search when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new SearchManager());
} else {
    new SearchManager();
}
/**
 * N-gram based search functionality with chunked data loading
 */

class NGramSearchManager {
    constructor() {
        this.searchIndex = null;
        this.loadedChunks = new Map();
        this.searchInput = null;
        this.searchResults = null;
        this.isLoading = false;
        this.debounceTimer = null;
        this.debounceDelay = 300; // ms
        this.init();
    }

    async init() {
        await this.loadSearchIndex();
        this.setupSearchUI();
        this.bindEvents();
    }

    async loadSearchIndex() {
        try {
            this.isLoading = true;
            const basePath = window.basePath || './';
            const indexUrl = `${basePath}static/data/search/index.json`;
            const response = await fetch(indexUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.searchIndex = await response.json();
            console.log('N-gram search index loaded:', this.searchIndex.metadata);
        } catch (error) {
            console.error('Failed to load N-gram search index:', error);
        } finally {
            this.isLoading = false;
        }
    }

    async loadChunk(chunkId) {
        if (this.loadedChunks.has(chunkId)) {
            return this.loadedChunks.get(chunkId);
        }

        try {
            const basePath = window.basePath || './';
            const chunkUrl = `${basePath}static/data/search/chunks/chunk_${chunkId}.json`;
            const response = await fetch(chunkUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const chunkData = await response.json();
            this.loadedChunks.set(chunkId, chunkData);
            console.log(`Loaded chunk ${chunkId}: ${chunkData.stages.length} stages`);
            return chunkData;
        } catch (error) {
            console.error(`Failed to load chunk ${chunkId}:`, error);
            return null;
        }
    }

    setupSearchUI() {
        // Check if search container already exists
        const existingContainer = document.querySelector('.search-container');
        if (existingContainer) {
            console.log('Search container already exists, skipping setup');
            return;
        }

        // Create search container
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.innerHTML = `
            <div class="search-input-container">
                <input type="text" 
                       class="search-input" 
                       placeholder="ストーリー内容で全文検索..." 
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
                filterContainer.after(searchContainer);
            } else {
                const contentHeader = contentSection.querySelector('h2');
                if (contentHeader) {
                    contentHeader.after(searchContainer);
                }
            }
        }

        // Get references (check if they already exist)
        this.searchInput = document.querySelector('.search-input');
        this.searchResults = document.querySelector('.search-results');
        this.searchClear = document.querySelector('.search-clear');
        this.queryDisplay = document.querySelector('.search-query-display');
        this.queryContent = document.querySelector('.query-content');

        // If setupSearchUI was skipped, elements might not be available
        if (!this.searchInput) {
            console.warn('Search input not found, search functionality may not work');
        }
    }

    bindEvents() {
        if (!this.searchInput) return;

        // Debounced search input
        this.searchInput.addEventListener('input', (e) => {
            this.debouncedSearch(e.target.value);
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

    debouncedSearch(query) {
        // Clear existing timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Set new timer
        this.debounceTimer = setTimeout(() => {
            this.handleSearch(query);
        }, this.debounceDelay);
    }

    async handleSearch(query) {
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

        if (!this.searchIndex) {
            this.showResults([{ 
                type: 'message', 
                content: this.isLoading ? '検索インデックスを読み込み中...' : '検索インデックスの読み込みに失敗しました' 
            }]);
            return;
        }

        try {
            const results = await this.performNGramSearch(keywords);
            this.showResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.showResults([{ 
                type: 'message', 
                content: '検索中にエラーが発生しました' 
            }]);
        }
    }

    parseQuery(queryString) {
        return queryString.split(/[\s　]+/).filter(keyword => keyword.trim().length > 0);
    }

    generateNGrams(text, sizes = [2, 3]) {
        const ngrams = new Set();
        
        for (const size of sizes) {
            for (let i = 0; i <= text.length - size; i++) {
                ngrams.add(text.substring(i, i + size));
            }
        }
        
        return Array.from(ngrams);
    }

    async performNGramSearch(keywords) {
        const candidateChunks = new Set();
        const candidateStages = new Set();

        // Generate N-grams for each keyword and find candidate chunks
        for (const keyword of keywords) {
            const ngrams = this.generateNGrams(keyword, this.searchIndex.metadata.ngram_config.sizes);
            
            for (const ngram of ngrams) {
                const entries = this.searchIndex.inverted_index[ngram];
                if (entries) {
                    for (const entry of entries) {
                        candidateChunks.add(entry.chunk);
                        for (const stage of entry.stages) {
                            candidateStages.add(stage);
                        }
                    }
                }
            }
        }

        console.log(`Found ${candidateChunks.size} candidate chunks, ${candidateStages.size} candidate stages`);

        if (candidateChunks.size === 0) {
            return [];
        }

        // Load necessary chunks
        const loadPromises = Array.from(candidateChunks).map(chunkId => this.loadChunk(chunkId));
        const chunks = await Promise.all(loadPromises);

        // Search within loaded chunks
        const results = [];
        
        for (let i = 0; i < chunks.length; i++) {
            const chunk = chunks[i];
            if (!chunk) continue;

            for (const stage of chunk.stages) {
                if (!candidateStages.has(stage.stage_code)) continue;

                // Check if all keywords match in the stage content
                if (this.matchesAllKeywords(stage.content, keywords)) {
                    // Calculate relevance score
                    const relevance = this.calculateRelevanceForKeywords(stage.content, keywords);
                    
                    results.push({
                        type: 'story',
                        stage_code: stage.stage_code,
                        name: stage.title || stage.stage_code,
                        event_name: stage.event_name,
                        url: stage.url,
                        content: stage.content,
                        relevance: relevance,
                        chunk_id: Array.from(candidateChunks)[i]
                    });
                }
            }
        }

        // Sort by relevance (higher is better)
        results.sort((a, b) => b.relevance - a.relevance);

        return results.slice(0, 20); // Limit to 20 results
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
            score += occurrences * 2;
            
            // Boost if keyword appears at the beginning
            if (lowerText.startsWith(lowerKeyword)) {
                score += 5;
            }

            // N-gram matching bonus for partial matches
            const textNgrams = this.generateNGrams(lowerText);
            const keywordNgrams = this.generateNGrams(lowerKeyword);
            const matchingNgrams = keywordNgrams.filter(ngram => textNgrams.includes(ngram));
            score += matchingNgrams.length * 0.5;
        });
        
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
                } else if (result.type === 'story') {
                    const keywords = this.parseQuery(this.searchInput.value);
                    const snippet = this.extractSnippet(result.content, keywords, 150);
                    
                    return `
                        <div class="search-result search-story">
                            <a href="${result.url}">
                                <div class="search-title">${this.highlightMatches(result.name, keywords)}</div>
                                <div class="search-meta">ストーリー • ${result.event_name} • ${result.stage_code}</div>
                                <div class="search-snippet">${this.highlightMatches(snippet, keywords)}</div>
                                <div class="search-relevance">関連度: ${Math.round(result.relevance)}</div>
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

    extractSnippet(text, keywords, maxLength = 150) {
        // Find the best snippet containing the most keywords
        let bestSnippet = '';
        let bestScore = 0;
        
        // Try different starting positions around keyword matches
        for (const keyword of keywords) {
            const lowerText = text.toLowerCase();
            const lowerKeyword = keyword.toLowerCase();
            const index = lowerText.indexOf(lowerKeyword);
            
            if (index !== -1) {
                // Extract snippet around the keyword
                const start = Math.max(0, index - Math.floor(maxLength / 2));
                const end = Math.min(text.length, start + maxLength);
                const snippet = text.substring(start, end);
                
                // Score this snippet based on keyword occurrences
                const score = keywords.reduce((acc, kw) => {
                    return acc + (snippet.toLowerCase().match(new RegExp(kw.toLowerCase(), 'g')) || []).length;
                }, 0);
                
                if (score > bestScore) {
                    bestScore = score;
                    bestSnippet = snippet;
                }
            }
        }
        
        // Fallback to beginning of text if no keywords found
        if (!bestSnippet) {
            bestSnippet = text.substring(0, maxLength);
        }
        
        // Add ellipsis if truncated
        if (bestSnippet.length === maxLength && text.length > maxLength) {
            bestSnippet += '...';
        }
        
        return bestSnippet;
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
        
        // Clear debounce timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
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
}

// Initialize N-gram search when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new NGramSearchManager());
} else {
    new NGramSearchManager();
}
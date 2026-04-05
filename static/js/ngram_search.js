/**
 * Bi-gram based full-text search with two-stage architecture:
 *   Stage 1: Bi-gram inverted index lookup for candidate filtering
 *   Stage 2: Full-text verification via String.includes()
 */

class NGramSearchManager {
    constructor() {
        this.searchIndex = null;
        this.loadedChunks = new Map();
        this.chunkAccessOrder = []; // LRU tracking
        this.maxCachedChunks = 10;
        this.searchInput = null;
        this.searchResults = null;
        this.isLoading = false;
        this.debounceTimer = null;
        this.debounceDelay = 300;
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
            const response = await fetch(`${basePath}static/data/search/index.json`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            this.searchIndex = await response.json();

            // Validate required fields
            if (!this.searchIndex.inverted_index || !this.searchIndex.stage_chunk_map) {
                throw new Error('Invalid index structure');
            }

            console.log('Search index loaded:', this.searchIndex.metadata);
        } catch (error) {
            console.error('Failed to load search index:', error);
        } finally {
            this.isLoading = false;
        }
    }

    async loadChunk(chunkId) {
        if (this.loadedChunks.has(chunkId)) {
            // Update LRU order
            this.chunkAccessOrder = this.chunkAccessOrder.filter(id => id !== chunkId);
            this.chunkAccessOrder.push(chunkId);
            return this.loadedChunks.get(chunkId);
        }

        try {
            const basePath = window.basePath || './';
            const response = await fetch(`${basePath}static/data/search/chunks/chunk_${chunkId}.json`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const chunkData = await response.json();

            // Evict oldest if cache is full
            while (this.loadedChunks.size >= this.maxCachedChunks && this.chunkAccessOrder.length > 0) {
                const evictId = this.chunkAccessOrder.shift();
                this.loadedChunks.delete(evictId);
            }

            this.loadedChunks.set(chunkId, chunkData);
            this.chunkAccessOrder.push(chunkId);
            return chunkData;
        } catch (error) {
            console.error(`Failed to load chunk ${chunkId}:`, error);
            return null;
        }
    }

    setupSearchUI() {
        const existingContainer = document.querySelector('.search-container');
        if (existingContainer) return;

        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.innerHTML = `
            <div class="search-input-container">
                <input type="text"
                       class="search-input"
                       placeholder="ストーリー内容で全文検索..."
                       autocomplete="off">
                <button class="search-clear" style="display: none;">×</button>
                <button class="search-help-btn" title="検索ヒント">?</button>
            </div>
            <div class="search-help-panel" style="display: none;">
                <div class="search-help-content">
                    <div class="search-help-title">検索の使い方</div>
                    <dl class="search-help-list">
                        <dt>基本検索</dt>
                        <dd>キーワードを入力すると、ストーリー本文から全文検索します（2文字以上）</dd>
                        <dt>AND検索</dt>
                        <dd>スペース区切りで複数キーワードを入力すると、すべてを含むストーリーを検索します<br><span class="search-help-example">例: ドクター ケルシー</span></dd>
                        <dt>検索対象</dt>
                        <dd>イベントストーリー・メインストーリーの台詞テキストが対象です</dd>
                    </dl>
                </div>
            </div>
            <div class="search-query-display" style="display: none;">
                <span class="query-label">検索条件:</span>
                <span class="query-content"></span>
            </div>
            <div class="search-loading" style="display: none;">検索中...</div>
            <div class="search-results" style="display: none;"></div>
        `;

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

        this.searchInput = document.querySelector('.search-input');
        this.searchResults = document.querySelector('.search-results');
        this.searchClear = document.querySelector('.search-clear');
        this.searchHelpBtn = document.querySelector('.search-help-btn');
        this.searchHelpPanel = document.querySelector('.search-help-panel');
        this.queryDisplay = document.querySelector('.search-query-display');
        this.queryContent = document.querySelector('.query-content');
        this.searchLoading = document.querySelector('.search-loading');
    }

    bindEvents() {
        if (!this.searchInput) return;

        this.searchInput.addEventListener('input', (e) => {
            this.debouncedSearch(e.target.value);
        });

        if (this.searchHelpBtn && this.searchHelpPanel) {
            this.searchHelpBtn.addEventListener('click', () => {
                const visible = this.searchHelpPanel.style.display !== 'none';
                this.searchHelpPanel.style.display = visible ? 'none' : 'block';
                this.searchHelpBtn.classList.toggle('active', !visible);
            });
        }

        if (this.searchClear) {
            this.searchClear.addEventListener('click', () => this.clearSearch());
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.searchInput === document.activeElement) {
                this.clearSearch();
            }
        });
    }

    debouncedSearch(query) {
        if (this.debounceTimer) clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.handleSearch(query), this.debounceDelay);
    }

    async handleSearch(query) {
        query = query.trim();

        if (this.searchClear) {
            this.searchClear.style.display = query ? 'block' : 'none';
        }

        if (query.length < 2) {
            this.hideResults();
            this.hideQueryDisplay();
            this.hideLoading();
            return;
        }

        const keywords = this.parseQuery(query);
        this.showQueryDisplay(keywords);

        if (!this.searchIndex) {
            this.showResults([{
                type: 'message',
                content: this.isLoading ? '検索インデックスを読み込み中...' : '検索インデックスの読み込みに失敗しました'
            }]);
            return;
        }

        this.showLoading();

        try {
            const results = await this.performSearch(keywords);
            this.hideLoading();
            this.showResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.hideLoading();
            this.showResults([{ type: 'message', content: '検索中にエラーが発生しました' }]);
        }
    }

    parseQuery(queryString) {
        return queryString.split(/[\s\u3000]+/).filter(kw => kw.length > 0);
    }

    /**
     * Generate bi-grams from text.
     */
    generateBigrams(text) {
        const lower = text.toLowerCase();
        const bigrams = new Set();
        for (let i = 0; i < lower.length - 1; i++) {
            const bg = lower.substring(i, i + 2);
            if (bg.trim()) bigrams.add(bg);
        }
        return bigrams;
    }

    /**
     * Two-stage search:
     *  1. Bi-gram index lookup → candidate chunk IDs (intersection for AND)
     *  2. Load chunks → full-text verify with String.includes()
     */
    async performSearch(keywords) {
        const index = this.searchIndex;

        // Stage 1: For each keyword, find candidate chunk IDs via bi-gram index.
        // Index format: bigram -> [chunk_id, chunk_id, ...]
        let chunkSets = [];

        for (const keyword of keywords) {
            const bigrams = this.generateBigrams(keyword);
            if (bigrams.size === 0) continue;

            // A chunk must contain ALL bi-grams of this keyword
            let keywordChunks = null;

            for (const bg of bigrams) {
                const chunkIds = index.inverted_index[bg];
                if (!chunkIds) {
                    keywordChunks = new Set();
                    break;
                }

                const chunkSet = new Set(chunkIds);

                if (keywordChunks === null) {
                    keywordChunks = chunkSet;
                } else {
                    keywordChunks = new Set([...keywordChunks].filter(c => chunkSet.has(c)));
                }

                if (keywordChunks.size === 0) break;
            }

            chunkSets.push(keywordChunks || new Set());
        }

        if (chunkSets.length === 0) return [];

        // AND across keywords: intersect chunk sets
        let neededChunks = chunkSets[0];
        for (let i = 1; i < chunkSets.length; i++) {
            neededChunks = new Set([...neededChunks].filter(c => chunkSets[i].has(c)));
        }

        if (neededChunks.size === 0) return [];

        // Load candidate chunks in parallel
        const chunks = await Promise.all(
            [...neededChunks].map(cid => this.loadChunk(cid))
        );

        // Stage 2: Full-text verification on all stages in loaded chunks
        const results = [];

        for (const chunk of chunks) {
            if (!chunk) continue;
            for (const stage of chunk.stages) {
                const text = stage.full_content || '';
                const lowerText = text.toLowerCase();

                // Verify ALL keywords actually appear in full text
                const allMatch = keywords.every(kw => lowerText.includes(kw.toLowerCase()));
                if (!allMatch) continue;

                const relevance = this.calculateRelevance(stage, keywords);
                results.push({
                    type: 'story',
                    stage_id: stage.stage_id,
                    stage_name: stage.stage_name,
                    event_name: stage.event_name,
                    url: stage.url,
                    full_content: text,
                    relevance: relevance,
                });
            }
        }

        results.sort((a, b) => b.relevance - a.relevance);
        return results.slice(0, 20);
    }

    /**
     * Simple relevance scoring: occurrence count + title/meta bonuses,
     * normalized by text length.
     */
    calculateRelevance(stage, keywords) {
        let score = 0;
        const content = (stage.full_content || '').toLowerCase();
        const contentLen = content.length || 1;
        const title = (stage.stage_name || '').toLowerCase();
        const eventName = (stage.event_name || '').toLowerCase();

        for (const keyword of keywords) {
            const kw = keyword.toLowerCase();

            // Count occurrences in content
            let count = 0;
            let pos = 0;
            while ((pos = content.indexOf(kw, pos)) !== -1) {
                count++;
                pos += kw.length;
            }
            // Normalize by text length (per 1000 chars)
            score += (count / contentLen) * 1000 * 5;

            // Bonus for title match
            if (title.includes(kw)) score += 20;

            // Bonus for event name match
            if (eventName.includes(kw)) score += 10;
        }

        return score;
    }

    showResults(results) {
        if (!this.searchResults) return;

        if (results.length === 0) {
            this.searchResults.innerHTML = '<div class="search-no-results">検索結果が見つかりませんでした</div>';
        } else {
            const keywords = this.parseQuery(this.searchInput.value);
            const html = results.map(result => {
                if (result.type === 'message') {
                    return `<div class="search-message">${result.content}</div>`;
                }
                const snippet = this.extractSnippet(result.full_content, keywords, 150);
                return `
                    <div class="search-result search-story">
                        <a href="${result.url}">
                            <div class="search-title">${this.highlightMatches(result.stage_name || result.stage_id, keywords)}</div>
                            <div class="search-meta">ストーリー • ${this.escapeHtml(result.event_name)} • ${this.escapeHtml(result.stage_id)}</div>
                            <div class="search-snippet">${this.highlightMatches(snippet, keywords)}</div>
                        </a>
                    </div>
                `;
            }).join('');
            this.searchResults.innerHTML = html;
        }

        this.searchResults.style.display = 'block';
    }

    extractSnippet(text, keywords, maxLength) {
        if (!text) return '';

        let bestSnippet = '';
        let bestScore = -1;

        for (const keyword of keywords) {
            const idx = text.toLowerCase().indexOf(keyword.toLowerCase());
            if (idx === -1) continue;

            const start = Math.max(0, idx - Math.floor(maxLength / 3));
            const end = Math.min(text.length, start + maxLength);
            const snippet = text.substring(start, end);

            const score = keywords.reduce((acc, kw) => {
                return acc + (snippet.toLowerCase().includes(kw.toLowerCase()) ? 1 : 0);
            }, 0);

            if (score > bestScore) {
                bestScore = score;
                bestSnippet = snippet;
            }
        }

        if (!bestSnippet) bestSnippet = text.substring(0, maxLength);

        const prefix = bestSnippet !== text.substring(0, bestSnippet.length) ? '...' : '';
        const suffix = bestSnippet.length < text.length ? '...' : '';
        return prefix + bestSnippet + suffix;
    }

    showQueryDisplay(keywords) {
        if (!this.queryDisplay || !this.queryContent || keywords.length === 0) return;
        const html = keywords.map(kw =>
            `<span class="search-keyword">${this.escapeHtml(kw)}</span>`
        ).join(' <span class="search-operator">AND</span> ');
        this.queryContent.innerHTML = html;
        this.queryDisplay.style.display = 'block';
    }

    hideQueryDisplay() {
        if (this.queryDisplay) this.queryDisplay.style.display = 'none';
    }

    hideResults() {
        if (this.searchResults) this.searchResults.style.display = 'none';
    }

    showLoading() {
        if (this.searchLoading) this.searchLoading.style.display = 'block';
    }

    hideLoading() {
        if (this.searchLoading) this.searchLoading.style.display = 'none';
    }

    clearSearch() {
        if (this.searchInput) {
            this.searchInput.value = '';
            this.searchInput.focus();
        }
        if (this.searchClear) this.searchClear.style.display = 'none';
        this.hideResults();
        this.hideQueryDisplay();
        this.hideLoading();
        if (this.debounceTimer) clearTimeout(this.debounceTimer);
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    highlightMatches(text, keywords) {
        if (!keywords || keywords.length === 0 || !text) return text || '';
        let result = this.escapeHtml(text);
        for (const keyword of keywords) {
            if (!keyword.trim()) continue;
            const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(`(${escaped})`, 'gi');
            result = result.replace(regex, '<mark>$1</mark>');
        }
        return result;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new NGramSearchManager());
} else {
    new NGramSearchManager();
}

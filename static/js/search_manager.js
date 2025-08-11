/**
 * Auto-detecting search manager that chooses between N-gram and basic search
 */

class SearchManagerFactory {
    static async createSearchManager() {
        // Prevent multiple search managers
        if (window.searchManagerInitialized) {
            return;
        }
        window.searchManagerInitialized = true;

        try {
            // Try to detect N-gram search availability
            const basePath = window.basePath || './';
            const ngramIndexUrl = `${basePath}static/data/search/index.json`;
            
            const response = await fetch(ngramIndexUrl, { method: 'HEAD' });
            
            if (response.ok) {
                console.log('N-gram search index detected, using N-gram search');
                // Dynamically load N-gram search script
                await this.loadScript('static/js/ngram_search.js');
                return new NGramSearchManager();
            } else {
                console.log('N-gram search index not found, using basic search');
                // Fallback to basic search
                await this.loadScript('static/js/search.js');
                return new SearchManager();
            }
        } catch (error) {
            console.log('Failed to detect N-gram search, using basic search:', error);
            // Fallback to basic search
            await this.loadScript('static/js/search.js');
            return new SearchManager();
        }
    }

    static loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if script is already loaded
            const existingScript = document.querySelector(`script[src="${src}"]`);
            if (existingScript) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
}

// Initialize appropriate search manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', async () => {
        await SearchManagerFactory.createSearchManager();
    });
} else {
    SearchManagerFactory.createSearchManager();
}
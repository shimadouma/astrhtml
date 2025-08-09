/**
 * Bookmark management system for Arknights Story Archive
 * Manages bookmark storage, UI, and navigation
 */

class BookmarkManager {
    constructor() {
        this.bookmarks = this.loadBookmarks();
        this.maxBookmarks = 100; // Limit bookmarks for performance
        this.init();
    }

    /**
     * Initialize bookmark system
     */
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupBookmarkUI());
        } else {
            this.setupBookmarkUI();
        }
    }

    /**
     * Load bookmarks from localStorage
     */
    loadBookmarks() {
        try {
            const stored = localStorage.getItem('arknights_bookmarks');
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('Error loading bookmarks:', error);
            return {};
        }
    }

    /**
     * Save bookmarks to localStorage
     */
    saveBookmarks() {
        try {
            localStorage.setItem('arknights_bookmarks', JSON.stringify(this.bookmarks));
            return true;
        } catch (error) {
            console.error('Error saving bookmarks:', error);
            return false;
        }
    }

    /**
     * Setup bookmark UI on story pages
     */
    setupBookmarkUI() {
        const dialogBlocks = document.querySelectorAll('.dialog-block');
        
        dialogBlocks.forEach((block, index) => {
            // Create unique ID for each dialog block
            const blockId = `dialog-${index}`;
            block.setAttribute('data-bookmark-id', blockId);
            
            // Make block clickable
            block.style.position = 'relative';
            block.style.cursor = 'pointer';
            block.setAttribute('title', 'クリックでブックマーク設定・解除');
            
            // Create bookmark indicator (initially hidden)
            const bookmarkIndicator = document.createElement('div');
            bookmarkIndicator.className = 'bookmark-indicator';
            bookmarkIndicator.setAttribute('aria-label', 'ブックマーク済み');
            
            // Check if already bookmarked
            const currentUrl = window.location.pathname;
            const bookmarkId = this.generateBookmarkId(currentUrl, blockId);
            if (this.bookmarks[bookmarkId]) {
                bookmarkIndicator.classList.add('visible');
                block.classList.add('bookmarked');
            } else {
                // Ensure indicator is hidden for non-bookmarked items
                bookmarkIndicator.classList.remove('visible');
                block.classList.remove('bookmarked');
            }
            
            // Add click handler to the block itself
            block.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleBookmark(block, blockId, bookmarkIndicator);
            });
            
            // Add bookmark indicator to dialog block
            block.appendChild(bookmarkIndicator);
        });
    }

    /**
     * Generate unique bookmark ID
     */
    generateBookmarkId(url, blockId) {
        return `${url}_${blockId}`.replace(/[^a-zA-Z0-9_-]/g, '_');
    }

    /**
     * Toggle bookmark for a dialog block
     */
    toggleBookmark(block, blockId, indicator) {
        const currentUrl = window.location.pathname;
        const bookmarkId = this.generateBookmarkId(currentUrl, blockId);
        
        if (this.bookmarks[bookmarkId]) {
            // Remove bookmark
            this.removeBookmark(bookmarkId);
            indicator.classList.remove('visible');
            block.classList.remove('bookmarked');
            block.setAttribute('title', 'クリックでブックマーク設定・解除');
            this.showNotification('ブックマークを削除しました');
        } else {
            // Add bookmark
            if (Object.keys(this.bookmarks).length >= this.maxBookmarks) {
                this.showNotification('ブックマーク数が上限に達しています');
                return;
            }
            
            const bookmarkData = this.extractBookmarkData(block, blockId);
            if (bookmarkData) {
                this.addBookmark(bookmarkId, bookmarkData);
                indicator.classList.add('visible');
                block.classList.add('bookmarked');
                block.setAttribute('title', 'クリックでブックマーク設定・解除');
                this.showNotification('ブックマークに追加しました');
            }
        }
    }

    /**
     * Extract bookmark data from dialog block
     */
    extractBookmarkData(block, blockId) {
        try {
            // Extract speaker name
            const speakerElement = block.querySelector('.speaker');
            const speaker = speakerElement ? speakerElement.textContent.trim() : '';
            
            // Extract dialog content
            const contentElement = block.querySelector('.dialog-text') || block.querySelector('.content') || block.querySelector('p');
            const content = contentElement ? contentElement.textContent.trim() : '';
            
            // Extract page information from URL and page title
            const currentUrl = window.location.pathname;
            const pageTitle = document.title;
            
            // Extract event and story information
            const breadcrumb = document.querySelector('.breadcrumb');
            let eventName = '';
            let storyName = '';
            
            if (breadcrumb) {
                const links = breadcrumb.querySelectorAll('a');
                if (links.length >= 3) {
                    eventName = links[2].textContent.trim(); // Third link is the event name
                }
            }
            
            const storyHeader = document.querySelector('.story-header h2');
            if (storyHeader) {
                storyName = storyHeader.textContent.trim();
            }
            
            return {
                id: this.generateBookmarkId(currentUrl, blockId),
                url: currentUrl,
                eventName: eventName,
                storyName: storyName,
                speaker: speaker,
                content: content,
                position: blockId,
                timestamp: Date.now(),
                pageTitle: pageTitle
            };
        } catch (error) {
            console.error('Error extracting bookmark data:', error);
            return null;
        }
    }

    /**
     * Add bookmark
     */
    addBookmark(bookmarkId, bookmarkData) {
        this.bookmarks[bookmarkId] = bookmarkData;
        return this.saveBookmarks();
    }

    /**
     * Remove bookmark
     */
    removeBookmark(bookmarkId) {
        delete this.bookmarks[bookmarkId];
        return this.saveBookmarks();
    }

    /**
     * Get all bookmarks sorted by timestamp
     */
    getAllBookmarks() {
        return Object.values(this.bookmarks)
            .sort((a, b) => b.timestamp - a.timestamp);
    }

    /**
     * Get bookmarks count
     */
    getBookmarkCount() {
        return Object.keys(this.bookmarks).length;
    }

    /**
     * Clear all bookmarks
     */
    clearAllBookmarks() {
        this.bookmarks = {};
        return this.saveBookmarks();
    }

    /**
     * Show notification to user
     */
    showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'bookmark-notification';
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Export bookmarks for backup
     */
    exportBookmarks() {
        const data = {
            version: '1.0',
            exportDate: new Date().toISOString(),
            bookmarks: this.bookmarks
        };
        return JSON.stringify(data, null, 2);
    }

    /**
     * Import bookmarks from backup
     */
    importBookmarks(jsonData) {
        try {
            const data = JSON.parse(jsonData);
            if (data.bookmarks && typeof data.bookmarks === 'object') {
                this.bookmarks = { ...this.bookmarks, ...data.bookmarks };
                return this.saveBookmarks();
            }
            return false;
        } catch (error) {
            console.error('Error importing bookmarks:', error);
            return false;
        }
    }
}

// Initialize bookmark manager
let bookmarkManager;

// Wait for DOM to be ready before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        bookmarkManager = new BookmarkManager();
        window.bookmarkManager = bookmarkManager;
    });
} else {
    bookmarkManager = new BookmarkManager();
    window.bookmarkManager = bookmarkManager;
}
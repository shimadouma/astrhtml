/**
 * Bookmarks page functionality
 * Handles bookmark display, search, and management
 */

class BookmarksPage {
    constructor() {
        this.filteredBookmarks = [];
        this.init();
    }

    /**
     * Initialize bookmarks page
     */
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    /**
     * Setup page elements and event listeners
     */
    setup() {
        // Wait for bookmarkManager to be available
        this.bookmarkManager = window.bookmarkManager;
        if (!this.bookmarkManager) {
            // Wait a bit more and try again
            setTimeout(() => this.setup(), 100);
            return;
        }
        
        this.loadBookmarks();
        this.setupEventListeners();
        this.updateStats();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('bookmark-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterBookmarks(e.target.value);
            });
        }

        // Export bookmarks
        const exportBtn = document.getElementById('export-bookmarks');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportBookmarks());
        }

        // Import bookmarks
        const importBtn = document.getElementById('import-bookmarks');
        const importFile = document.getElementById('import-file');
        if (importBtn && importFile) {
            importBtn.addEventListener('click', () => importFile.click());
            importFile.addEventListener('change', (e) => this.importBookmarks(e.target.files[0]));
        }

        // Clear all bookmarks
        const clearBtn = document.getElementById('clear-bookmarks');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.confirmClearBookmarks());
        }

        // Dialog controls
        this.setupDialogControls();
    }

    /**
     * Setup dialog controls
     */
    setupDialogControls() {
        const confirmDialog = document.getElementById('confirm-dialog');
        const confirmOk = document.getElementById('confirm-ok');
        const confirmCancel = document.getElementById('confirm-cancel');

        if (confirmCancel) {
            confirmCancel.addEventListener('click', () => this.hideDialog());
        }

        if (confirmOk) {
            confirmOk.addEventListener('click', () => {
                this.executeConfirmAction();
                this.hideDialog();
            });
        }

        // Close dialog on overlay click
        if (confirmDialog) {
            confirmDialog.addEventListener('click', (e) => {
                if (e.target === confirmDialog) {
                    this.hideDialog();
                }
            });
        }
    }

    /**
     * Load and display bookmarks
     */
    loadBookmarks() {
        if (!this.bookmarkManager) {
            console.error('BookmarkManager not available');
            return;
        }

        const bookmarks = this.bookmarkManager.getAllBookmarks();
        this.filteredBookmarks = bookmarks;
        this.displayBookmarks(bookmarks);
    }

    /**
     * Display bookmarks in the list
     */
    displayBookmarks(bookmarks) {
        const bookmarksList = document.getElementById('bookmarks-list');
        const noBookmarks = document.getElementById('no-bookmarks');

        if (!bookmarksList || !noBookmarks) return;

        if (bookmarks.length === 0) {
            bookmarksList.style.display = 'none';
            noBookmarks.classList.add('visible');
            return;
        }

        bookmarksList.style.display = 'grid';
        noBookmarks.classList.remove('visible');
        
        bookmarksList.innerHTML = bookmarks.map(bookmark => this.createBookmarkItem(bookmark)).join('');
        
        // Add delete event listeners
        bookmarksList.querySelectorAll('.bookmark-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const bookmarkId = btn.getAttribute('data-bookmark-id');
                this.confirmDeleteBookmark(bookmarkId);
            });
        });
    }

    /**
     * Create HTML for a bookmark item
     */
    createBookmarkItem(bookmark) {
        const date = new Date(bookmark.timestamp).toLocaleDateString('ja-JP');
        const eventPath = bookmark.eventName || 'イベント名不明';
        const storyPath = bookmark.storyName || 'ストーリー名不明';
        
        return `
            <div class="bookmark-item" data-bookmark-id="${bookmark.id}">
                <div class="bookmark-meta">
                    <span class="bookmark-date">${date}</span>
                    <button class="bookmark-delete" data-bookmark-id="${bookmark.id}" title="削除">
                        ❌
                    </button>
                </div>
                <div class="bookmark-path">
                    <a href="${bookmark.url}#${bookmark.position}">${eventPath} > ${storyPath}</a>
                </div>
                ${bookmark.speaker ? `<div class="bookmark-speaker">${this.escapeHtml(bookmark.speaker)}</div>` : ''}
                <div class="bookmark-content">${this.escapeHtml(bookmark.content)}</div>
            </div>
        `;
    }

    /**
     * Filter bookmarks by search term
     */
    filterBookmarks(searchTerm) {
        if (!searchTerm) {
            this.filteredBookmarks = this.bookmarkManager.getAllBookmarks();
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredBookmarks = this.bookmarkManager.getAllBookmarks().filter(bookmark => {
                return (
                    (bookmark.content && bookmark.content.toLowerCase().includes(term)) ||
                    (bookmark.speaker && bookmark.speaker.toLowerCase().includes(term)) ||
                    (bookmark.eventName && bookmark.eventName.toLowerCase().includes(term)) ||
                    (bookmark.storyName && bookmark.storyName.toLowerCase().includes(term))
                );
            });
        }
        
        this.displayBookmarks(this.filteredBookmarks);
    }

    /**
     * Update statistics display
     */
    updateStats() {
        const countElement = document.getElementById('bookmark-count');
        if (countElement && this.bookmarkManager) {
            countElement.textContent = this.bookmarkManager.getBookmarkCount();
        }
    }

    /**
     * Export bookmarks to JSON file
     */
    exportBookmarks() {
        if (!this.bookmarkManager) return;

        try {
            const data = this.bookmarkManager.exportBookmarks();
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `arknights-bookmarks-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showNotification('ブックマークをエクスポートしました');
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('エクスポートに失敗しました');
        }
    }

    /**
     * Import bookmarks from JSON file
     */
    importBookmarks(file) {
        if (!file || !this.bookmarkManager) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const success = this.bookmarkManager.importBookmarks(e.target.result);
                if (success) {
                    this.loadBookmarks();
                    this.updateStats();
                    this.showNotification('ブックマークをインポートしました');
                } else {
                    this.showNotification('インポートに失敗しました');
                }
            } catch (error) {
                console.error('Import error:', error);
                this.showNotification('ファイル形式が正しくありません');
            }
        };
        reader.readAsText(file);
    }

    /**
     * Show confirmation dialog for clearing all bookmarks
     */
    confirmClearBookmarks() {
        this.showDialog(
            'すべてのブックマークを削除',
            'すべてのブックマークを削除しますか？この操作は取り消すことができません。',
            () => this.clearAllBookmarks()
        );
    }

    /**
     * Show confirmation dialog for deleting a bookmark
     */
    confirmDeleteBookmark(bookmarkId) {
        this.showDialog(
            'ブックマークを削除',
            'このブックマークを削除しますか？',
            () => this.deleteBookmark(bookmarkId)
        );
    }

    /**
     * Clear all bookmarks
     */
    clearAllBookmarks() {
        if (!this.bookmarkManager) return;

        this.bookmarkManager.clearAllBookmarks();
        this.loadBookmarks();
        this.updateStats();
        this.showNotification('すべてのブックマークを削除しました');
    }

    /**
     * Delete a specific bookmark
     */
    deleteBookmark(bookmarkId) {
        if (!this.bookmarkManager) return;

        this.bookmarkManager.removeBookmark(bookmarkId);
        this.loadBookmarks();
        this.updateStats();
        this.showNotification('ブックマークを削除しました');
    }

    /**
     * Show confirmation dialog
     */
    showDialog(title, message, confirmCallback) {
        const dialog = document.getElementById('confirm-dialog');
        const titleEl = document.getElementById('confirm-title');
        const messageEl = document.getElementById('confirm-message');
        
        if (dialog && titleEl && messageEl) {
            titleEl.textContent = title;
            messageEl.textContent = message;
            this.confirmCallback = confirmCallback;
            dialog.style.display = 'flex';
        }
    }

    /**
     * Hide dialog
     */
    hideDialog() {
        const dialog = document.getElementById('confirm-dialog');
        if (dialog) {
            dialog.style.display = 'none';
        }
        this.confirmCallback = null;
    }

    /**
     * Execute confirmed action
     */
    executeConfirmAction() {
        if (this.confirmCallback) {
            this.confirmCallback();
        }
    }

    /**
     * Show notification
     */
    showNotification(message) {
        if (this.bookmarkManager && this.bookmarkManager.showNotification) {
            this.bookmarkManager.showNotification(message);
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize bookmarks page
new BookmarksPage();
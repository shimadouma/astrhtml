"""End-to-end tests for bi-gram full-text search using Playwright.

Prerequisites:
  - Build the site first: uv run python build.py --limit 3 --no-check-links
  - Install Playwright: npx playwright install chromium && npx playwright install-deps chromium

Run:
  uv run pytest tests/e2e/test_search.py -v
"""
import http.server
import subprocess
import sys
import threading
from pathlib import Path

import pytest

# Conditionally import playwright - skip tests if not available
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

DIST_DIR = Path(__file__).resolve().parents[2] / "dist"
SERVER_PORT = 8765


class StaticServer:
    """Simple HTTP server for serving the built site during tests."""

    def __init__(self, directory: Path, port: int):
        self.directory = directory
        self.port = port
        self.httpd = None
        self.thread = None

    def start(self):
        handler = http.server.SimpleHTTPRequestHandler
        self.httpd = http.server.HTTPServer(
            ("127.0.0.1", self.port),
            lambda *args, **kwargs: handler(*args, directory=str(self.directory), **kwargs),
        )
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()


@pytest.fixture(scope="module")
def built_site():
    """Ensure the site is built before tests run."""
    if not (DIST_DIR / "index.html").exists():
        result = subprocess.run(
            [sys.executable, "build.py", "--limit", "3", "--no-check-links"],
            capture_output=True, text=True,
            cwd=str(DIST_DIR.parent),
        )
        if result.returncode != 0:
            pytest.fail(f"Build failed:\n{result.stdout}\n{result.stderr}")
    return DIST_DIR


@pytest.fixture(scope="module")
def server(built_site):
    """Start a local HTTP server for the built site."""
    srv = StaticServer(built_site, SERVER_PORT)
    srv.start()
    yield srv
    srv.stop()


@pytest.fixture(scope="module")
def browser_page(server):
    """Create a Playwright browser page."""
    if not HAS_PLAYWRIGHT:
        pytest.skip("Playwright not installed")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


def base_url():
    return f"http://127.0.0.1:{SERVER_PORT}"


@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="Playwright not installed")
class TestSearchBasic:
    """Basic search functionality tests."""

    def test_search_index_loads(self, browser_page):
        """Search index should load without errors."""
        page = browser_page
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        # Check no critical errors
        critical_errors = [e for e in errors if "Failed to load search index" in e]
        assert len(critical_errors) == 0, f"Search index load errors: {critical_errors}"

    def test_search_ui_exists(self, browser_page):
        """Search UI elements should be present."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        assert page.query_selector(".search-input") is not None
        assert page.query_selector(".search-clear") is not None
        assert page.query_selector(".search-results") is not None

    def test_search_returns_results(self, browser_page):
        """Searching for a common word should return results."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        # Type a common Japanese word that should appear in story content
        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")

        # Wait for results to appear (debounce + search)
        page.wait_for_selector(".search-result", timeout=10000)

        results = page.query_selector_all(".search-result")
        assert len(results) > 0, "Expected at least one search result for 'ドクター'"

    def test_search_shows_query_display(self, browser_page):
        """Query display should show the search keywords."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")

        page.wait_for_selector(".search-query-display", state="visible", timeout=10000)
        query_display = page.query_selector(".search-query-display")
        assert query_display is not None
        assert query_display.is_visible()

    def test_search_result_has_link(self, browser_page):
        """Search results should contain clickable links."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")
        page.wait_for_selector(".search-result a", timeout=10000)

        link = page.query_selector(".search-result a")
        href = link.get_attribute("href")
        assert href is not None
        assert "stories/" in href

    def test_search_result_has_snippet(self, browser_page):
        """Search results should show text snippets."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")
        page.wait_for_selector(".search-snippet", timeout=10000)

        snippets = page.query_selector_all(".search-snippet")
        assert len(snippets) > 0
        # Snippet should have some text content
        assert len(snippets[0].inner_text()) > 0

    def test_search_highlight(self, browser_page):
        """Search results should highlight matching keywords."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")
        page.wait_for_selector(".search-result mark", timeout=10000)

        marks = page.query_selector_all(".search-result mark")
        assert len(marks) > 0


@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="Playwright not installed")
class TestSearchAndQuery:
    """AND search (multiple keywords) tests."""

    def test_and_search_narrows_results(self, browser_page):
        """Searching with two keywords should return fewer or equal results than one."""
        page = browser_page

        # Single keyword search
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")
        page.wait_for_selector(".search-result", timeout=10000)
        single_count = len(page.query_selector_all(".search-result"))

        # AND search with two keywords
        search_input.fill("")
        page.wait_for_timeout(500)
        search_input.fill("ドクター 博士")
        # Wait a bit for debounce + search
        page.wait_for_timeout(2000)

        and_results = page.query_selector_all(".search-result")
        and_count = len(and_results)

        assert and_count <= single_count, (
            f"AND search should return ≤ single keyword results: {and_count} > {single_count}"
        )

    def test_and_search_query_display(self, browser_page):
        """AND search should display keywords with AND operator."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("キーワード1 キーワード2")
        page.wait_for_selector(".search-operator", timeout=10000)

        operators = page.query_selector_all(".search-operator")
        assert len(operators) > 0
        assert "AND" in operators[0].inner_text()


@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="Playwright not installed")
class TestSearchEdgeCases:
    """Edge case tests."""

    def test_short_query_no_search(self, browser_page):
        """Queries shorter than 2 characters should not trigger search."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("あ")
        page.wait_for_timeout(500)

        results_div = page.query_selector(".search-results")
        assert results_div.is_hidden() or results_div.inner_text() == ""

    def test_clear_button(self, browser_page):
        """Clear button should reset search."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")
        page.wait_for_selector(".search-result", timeout=10000)

        # Click clear
        clear_btn = page.query_selector(".search-clear")
        clear_btn.click()

        assert search_input.input_value() == ""
        results_div = page.query_selector(".search-results")
        assert results_div.is_hidden()

    def test_no_results_message(self, browser_page):
        """Searching for nonsense should show no-results message."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("zzzzxxxxxqqqq")
        page.wait_for_timeout(2000)

        # Should show no-results or empty
        results = page.query_selector_all(".search-result")
        assert len(results) == 0

    def test_escape_clears_search(self, browser_page):
        """Pressing Escape should clear the search."""
        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)

        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")
        page.wait_for_selector(".search-result", timeout=10000)

        search_input.press("Escape")

        assert search_input.input_value() == ""

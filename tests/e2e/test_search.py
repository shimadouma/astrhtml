"""End-to-end tests for bi-gram full-text search using Playwright.

Prerequisites:
  - Build the site first: uv run python build.py --limit 10 --no-check-links
  - Install Playwright: uv run playwright install chromium

Run:
  uv run pytest tests/e2e/test_search.py -v
"""
import http.server
import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

DIST_DIR = Path(__file__).resolve().parents[2] / "dist"
SERVER_PORT = 8765
BUILD_LIMIT = 10


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


def _build_ground_truth():
    """Scan chunk files to build keyword -> expected stage_ids mapping."""
    search_dir = DIST_DIR / "static" / "data" / "search"
    chunks_dir = search_dir / "chunks"
    if not chunks_dir.exists():
        return {}

    # Load all stages from all chunks
    all_stages = []
    chunk_id = 0
    while True:
        chunk_file = chunks_dir / f"chunk_{chunk_id}.json"
        if not chunk_file.exists():
            break
        with open(chunk_file, encoding="utf-8") as f:
            chunk = json.load(f)
        all_stages.extend(chunk["stages"])
        chunk_id += 1

    # Build truth for each keyword
    keywords = ["アーミヤ", "ドクター", "星熊", "ケルシー", "アイリス", "ロドス", "龍門"]
    truth = {}
    for kw in keywords:
        matching = [s["stage_id"] for s in all_stages if kw in s["full_content"]]
        truth[kw] = set(matching)
    return truth


def _search_and_get_stage_ids(page, keyword, timeout=10000):
    """Perform a search and return list of stage_ids from results."""
    search_input = page.query_selector(".search-input")
    search_input.fill("")
    page.wait_for_timeout(400)
    search_input.fill(keyword)

    try:
        page.wait_for_selector(".search-result", timeout=timeout)
    except Exception:
        return []

    results = page.query_selector_all(".search-result")
    stage_ids = []
    for r in results:
        meta = r.query_selector(".search-meta")
        if meta:
            parts = meta.inner_text().split(" \u2022 ")
            if len(parts) >= 3:
                stage_ids.append(parts[2].strip())
    return stage_ids


@pytest.fixture(scope="module")
def built_site():
    """Ensure the site is built before tests run."""
    if not (DIST_DIR / "index.html").exists():
        result = subprocess.run(
            [sys.executable, "build.py", "--limit", str(BUILD_LIMIT), "--no-check-links"],
            capture_output=True, text=True,
            cwd=str(DIST_DIR.parent),
        )
        if result.returncode != 0:
            pytest.fail(f"Build failed:\n{result.stdout}\n{result.stderr}")
    return DIST_DIR


@pytest.fixture(scope="module")
def ground_truth(built_site):
    """Build ground truth from chunk data."""
    return _build_ground_truth()


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


# ---------------------------------------------------------------------------
# Basic functionality
# ---------------------------------------------------------------------------

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

        search_input = page.query_selector(".search-input")
        search_input.fill("ドクター")
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


# ---------------------------------------------------------------------------
# Ground truth: character names
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="Playwright not installed")
class TestSearchCharacterNames:
    """Verify search results match ground truth for character names."""

    def test_search_amiya(self, browser_page, ground_truth):
        """Search for アーミヤ should return all stages containing it."""
        expected = ground_truth.get("アーミヤ", set())
        if not expected:
            pytest.skip("アーミヤ not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "アーミヤ"))

        assert found == expected, (
            f"アーミヤ: missing={expected - found}, extra={found - expected}"
        )

    def test_search_doctor(self, browser_page, ground_truth):
        """Search for ドクター should return all stages containing it."""
        expected = ground_truth.get("ドクター", set())
        if not expected:
            pytest.skip("ドクター not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "ドクター"))

        assert found == expected, (
            f"ドクター: missing={expected - found}, extra={found - expected}"
        )

    def test_search_hoshiguma(self, browser_page, ground_truth):
        """Search for 星熊 should return all stages containing it."""
        expected = ground_truth.get("星熊", set())
        if not expected:
            pytest.skip("星熊 not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "星熊"))

        assert found == expected, (
            f"星熊: missing={expected - found}, extra={found - expected}"
        )

    def test_search_kal_tsit(self, browser_page, ground_truth):
        """Search for ケルシー should return all stages containing it."""
        expected = ground_truth.get("ケルシー", set())
        if not expected:
            pytest.skip("ケルシー not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "ケルシー"))

        assert found == expected, (
            f"ケルシー: missing={expected - found}, extra={found - expected}"
        )

    def test_search_iris(self, browser_page, ground_truth):
        """Search for アイリス should return all stages containing it."""
        expected = ground_truth.get("アイリス", set())
        if not expected:
            pytest.skip("アイリス not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "アイリス"))

        assert found == expected, (
            f"アイリス: missing={expected - found}, extra={found - expected}"
        )


# ---------------------------------------------------------------------------
# Ground truth: place names / keywords
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="Playwright not installed")
class TestSearchPlaceNames:
    """Verify search results match ground truth for place names."""

    def test_search_rhodes_island(self, browser_page, ground_truth):
        """Search for ロドス should return all stages containing it (capped at 20)."""
        expected = ground_truth.get("ロドス", set())
        if not expected:
            pytest.skip("ロドス not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "ロドス"))

        # Results are capped at 20, so found must be a subset of expected
        assert found.issubset(expected), (
            f"ロドス: unexpected results not in ground truth: {found - expected}"
        )
        # Should return the max (20) or all if fewer
        expected_count = min(20, len(expected))
        assert len(found) == expected_count, (
            f"ロドス: expected {expected_count} results, got {len(found)}"
        )

    def test_search_lungmen(self, browser_page, ground_truth):
        """Search for 龍門 should return all stages containing it (capped at 20)."""
        expected = ground_truth.get("龍門", set())
        if not expected:
            pytest.skip("龍門 not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "龍門"))

        assert found.issubset(expected), (
            f"龍門: unexpected results not in ground truth: {found - expected}"
        )
        expected_count = min(20, len(expected))
        assert len(found) == expected_count, (
            f"龍門: expected {expected_count} results, got {len(found)}"
        )


# ---------------------------------------------------------------------------
# AND search
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="Playwright not installed")
class TestSearchAndQuery:
    """AND search (multiple keywords) tests."""

    def test_and_search_narrows_results(self, browser_page, ground_truth):
        """AND search for ドクター ケルシー should match intersection."""
        expected_doctor = ground_truth.get("ドクター", set())
        expected_kaltsit = ground_truth.get("ケルシー", set())
        expected_and = expected_doctor & expected_kaltsit
        if not expected_and:
            pytest.skip("No stages with both ドクター and ケルシー")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "ドクター ケルシー"))

        assert found == expected_and, (
            f"ドクター ケルシー: missing={expected_and - found}, extra={found - expected_and}"
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


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

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

    def test_two_char_query_works(self, browser_page, ground_truth):
        """A 2-character query (minimum) should still work."""
        # 星熊 is exactly 2 characters
        expected = ground_truth.get("星熊", set())
        if not expected:
            pytest.skip("星熊 not in built data")

        page = browser_page
        page.goto(base_url())
        page.wait_for_selector(".search-input", timeout=10000)
        found = set(_search_and_get_stage_ids(page, "星熊"))

        assert found == expected, (
            f"星熊 (2-char): missing={expected - found}, extra={found - expected}"
        )

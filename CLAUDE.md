# Claude Code Project Settings

Claude Code specific settings and information for this project.

## Project Overview

**Arknights Story Archive**

A static site generator for viewing Arknights event stories in HTML format. Uses ArknightsStoryJson Japanese (ja_JP) data to process and generate stories in Japanese, published on GitHub Pages.

## Code Standards

**IMPORTANT**: All git commit messages and code comments must be written in English.
- Git commit messages: Use clear, concise English
- Code comments: Write all comments in English
- Variable names and function names: Use English naming conventions
- Documentation: Technical documentation should be in English

## Website Content Standards

**IMPORTANT**: The generated HTML website content should be in Japanese.
- HTML templates: Use Japanese text for UI elements and labels
- Story content: Display stories in Japanese (using ArknightsStoryJson ja_JP data)
- Navigation: Menu items and buttons should be in Japanese
- Error messages: User-facing error messages should be in Japanese
- Meta information: Page titles and descriptions should be in Japanese

Note: This applies only to the generated website content for end users. All source code, comments, and development documentation remain in English.

## Key Features

- **Automatic Story Ordering**: Display stories in game order by referencing stage_table.json
- **Battle Information Display**: Distinguish between pre-battle, post-battle, and interlude chapters with recommended level display
- **Responsive Design**: Compatible with both mobile and desktop
- **Automatic Deployment**: Daily automatic updates via GitHub Actions

## Build Commands

```bash
# Install dependencies
uv sync

# Build the Rust search index tool (first time only)
cd tools/bigram-index && cargo build --release && cd ../..

# Build all events
uv run python build.py

# Test build (limited events)
uv run python build.py --limit 5

# Clean build
uv run python build.py --clean

# Start local preview server
uv run python preview.py
```

## Local Preview

### Starting the Preview Server

```bash
# Basic usage (opens browser automatically on port 8000)
uv run python preview.py

# Custom port
uv run python preview.py --port 3000

# Don't open browser automatically
uv run python preview.py --no-browser

# Allow external connections
uv run python preview.py --host 0.0.0.0
```

### Development Workflow

1. **Build the site**: `uv run python build.py --limit 5`
2. **Start preview server**: `uv run python preview.py`
3. **Make code changes**
4. **Rebuild**: `uv run python build.py --limit 5`
5. **Refresh browser** to see changes

**Important**: You must run `uv run python build.py` first to generate the `dist/` directory before using the preview server.

## Test Commands

```bash
# Check if dependencies are correctly installed
uv run python -c "import jinja2, pathlib; print('Dependencies OK')"

# Verify build system functionality
uv run python build.py --limit 1

# Run Rust search indexer unit tests
cd tools/bigram-index && cargo test && cd ../..

# Update submodules
git submodule update --remote --merge
```

## End-to-End Tests (Playwright)

Integration tests verify the search functionality in a real browser (headless Chromium).

```bash
# Install test dependencies
uv sync --group dev

# Install Playwright browser (first time only)
uv run playwright install chromium

# Build the site, then run tests
uv run python build.py --limit 10 --no-check-links
uv run pytest tests/e2e/test_search.py -v
```

## Link Health Check

**IMPORTANT**: Always run link health checks during development and testing to ensure all internal links are working correctly.

### Automatic Link Checking

The build process now includes automatic link checking by default:

```bash
# Build with automatic link checking (default)
uv run python build.py

# Skip link checking if needed
uv run python build.py --no-check-links
```

### Manual Link Checking

You can also run the link checker manually:

```bash
# Check all links in the generated site
uv run python scripts/check_links.py

# Check links with detailed output
uv run python scripts/check_links.py --verbose

# Check links and fail with exit code if broken links found
uv run python scripts/check_links.py --fail-on-broken
```

### Development Workflow with Link Checking

**During development and testing, always ensure the link check passes:**

1. **Build the site**: `uv run python build.py --limit 5`
2. **Verify links are working**: The build will automatically check links and fail if any are broken
3. **Fix any broken links** if the build fails
4. **Rebuild and verify**: `uv run python build.py --limit 5`

**Before deploying or committing changes:**
- Always run a full build with link checking enabled
- Fix any broken links immediately
- Never deploy with broken links

## Event Story Validation

**IMPORTANT**: Always validate that all events have stories AND proper linking to ensure complete story generation.

### Enhanced Event Validation

Use the enhanced event validator to identify comprehensive story generation issues:

```bash
# Check for event story generation and linking issues
uv run python scripts/check_empty_events.py

# This script performs comprehensive validation:
# - Checks all event directories in dist/events/
# - Verifies story files exist in stories/ directories
# - Validates that all story files are properly linked in event index pages
# - Identifies broken links and missing story references
# - Categorizes issues: no files, unlinked files, partial linking, broken links
# - Provides detailed diagnostics and troubleshooting recommendations
# - Exits with error code if any issues are found
```

### Validation Categories

The script identifies several types of issues:

1. **Events with No Story Files**: No story files exist in the stories/ directory
2. **Events with Unlinked Stories**: Story files exist but are not linked in the event index page
3. **Events with Partial Linking**: Some stories are linked, but others are missing from the index
4. **Events with Broken Links**: Index page links to non-existent story files

### Development Workflow with Enhanced Event Validation

**During development and testing, always verify complete story generation:**

1. **Build the site**: `uv run python build.py --limit 5`
2. **Run enhanced validation**: `uv run python scripts/check_empty_events.py`
3. **Fix any issues found**:
   - **No files**: Check story data processing logic
   - **Unlinked files**: Verify event page generation and template rendering
   - **Partial linking**: Check story order determination logic
   - **Broken links**: Verify filename generation consistency
4. **Rebuild and verify**: `uv run python build.py --limit 5`

**Before deploying or committing changes:**
- Always run the enhanced validation after a full build
- Investigate and fix all categories of issues
- Ensure 100% success rate (all events properly linked)

### Common Issue Causes and Solutions

**Events with story files but no links (Critical)**:
- Event page generation logic not creating story list
- Template rendering issues in story section
- Story order determination returning empty results
- Event type detection affecting processing

**Events with some unlinked stories (Warning)**:
- Story order logic missing certain file types
- Filename pattern mismatches
- Special stage types not being processed
- Stage mapping inconsistencies

**Automated Validation**: The enhanced validator is integrated into GitHub Actions to prevent deployment of sites with story linking issues.

## Important Files

### Data Processing
- `src/lib/stage_parser.py` - Stage information and story order determination
- `src/lib/event_parser.py` - Event information processing
- `src/lib/story_parser.py` - Story data analysis

### HTML Generation
- `src/generators/` - HTML generation modules
- `templates/` - Jinja2 templates
- `static/css/` - Stylesheets

### Search
- `tools/bigram-index/` - Rust CLI tool for bi-gram inverted index generation
- `src/generators/ngram_search_index.py` - Python stage extraction + Rust integration
- `static/js/ngram_search.js` - Client-side two-stage search (bi-gram index + full-text verify)
- `static/js/search_manager.js` - Search manager factory (auto-detects index type)
- `tests/e2e/test_search.py` - Playwright integration tests for search

### Configuration & Build
- `build.py` - Main build script with integrated link checking
- `preview.py` - Local preview server with auto-browser opening
- `scripts/check_links.py` - Link health check script
- `scripts/check_empty_events.py` - Enhanced event story validation script
- `src/config.py` - Configuration file
- `.github/workflows/deploy.yml` - GitHub Actions configuration

## Development Notes

1. **Submodules**: ArknightsStoryJson data is an external submodule
   ```bash
   git submodule update --init --recursive
   ```
   - Data structure reference: `docs/arknights_story_json_data_structure.md`

2. **Python Requirements**: Use Python 3.8 or higher. Dependencies are managed by uv.
   - Supply chain protection: see "Dependency Update Policy" section below

3. **Rust Requirements**: The search index builder requires Rust (install via `rustup.rs`).
   ```bash
   cd tools/bigram-index && cargo build --release
   ```
   - The Python build will fall back to a pure-Python indexer if the Rust binary is not found
   - Rust tests: `cd tools/bigram-index && cargo test`

4. **Pre-build Verification**: 
   - Confirm `data/ArknightsStoryJson` directory exists
   - Run `uv sync` to install dependencies

5. **HTML File Names**: 
   - Event pages: `events/{event_id}/index.html`
   - Story pages: `events/{event_id}/stories/{stage_code}.html`
   - Stage codes (OR-1, OR-ST-1, etc.) are used as file names

6. **MINISTORY Event Special Handling**:
   - **Critical Design Rule**: MINISTORY events have separate gameplay and story stages
   - **Gameplay stages** (in stage_table.json): Used for battles, should NOT be processed for story generation
   - **Story stages** (level_*_st*.json files): Contain story content, ONLY these should be processed
   - Example for act15mini:
     - Gameplay stages (ignore): `act15mini_01` (FD-1), `act15mini_02` (FD-2), etc.
     - Story stages (process): `level_act15mini_st01.json`, `level_act15mini_st02.json`, etc.
   - This separation is unique to MINISTORY event type and does not apply to SIDESTORY or other event types

7. **Data Compatibility and Backward Compatibility**:
   - **localStorage Bookmark Data**: Maintain backward compatibility for user bookmark data stored in browser localStorage
   - When updating bookmark data structure, implement migration logic to preserve existing bookmarks
   - Version bookmark data format and include migration paths for older versions
   - Test bookmark functionality after any JavaScript/data structure changes
   - Consider user experience when changing data formats - users should not lose their bookmarks
   - Document bookmark data structure changes in commit messages
   - Use defensive programming to handle malformed or outdated bookmark data gracefully

## Troubleshooting

### Common Issues and Solutions

1. **ImportError**: 
   ```bash
   uv sync
   ```
   If uv is not installed, see https://docs.astral.sh/uv/getting-started/installation/

2. **Empty Submodule**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Build Error**:
   - Confirm using Python 3.8 or higher
   - Verify `data/ArknightsStoryJson` exists

4. **Preview Server Error**:
   - Run `uv run python build.py` first to generate the site
   - If port is in use, try: `uv run python preview.py --port 8001`

## Dependency Update Policy

Python dependencies are protected against supply chain attacks using `exclude-newer` in `pyproject.toml` (`[tool.uv]` section). This pins a cutoff date so that `uv lock` will not resolve any package version published after that date.

**Key points**:
- `exclude-newer` only affects `uv lock` (lockfile regeneration), not `uv sync` (which installs from the existing lockfile)
- Normal `uv sync` is safe even if the date is old — versions are pinned in `uv.lock`
- Dependencies are few (Jinja2, python-dateutil, watchdog, beautifulsoup4) and rarely need updating
- **Do not auto-update** `exclude-newer` in CI — that defeats the purpose of the protection

### Manual Update Procedure

When you need to update dependencies (e.g., every few months, or when a vulnerability is reported):

1. **Update the cutoff date** in `pyproject.toml`:
   ```toml
   [tool.uv]
   exclude-newer = "YYYY-MM-DDT00:00:00Z"  # Set to today's date
   ```

2. **Regenerate the lockfile**:
   ```bash
   uv lock
   ```

3. **Review changes** before committing:
   - `git diff uv.lock` — check what packages and versions changed
   - Verify no unexpected new packages were added
   - For major version bumps, review the package's changelog
   - Check that package maintainers haven't changed recently on PyPI (`https://pypi.org/project/<name>/`)

4. **Run the full test suite**:
   ```bash
   uv run python build.py --limit 5
   uv run pytest tests/e2e/test_search.py -v
   ```

5. **Commit the lockfile update as a separate commit** so it can be easily reverted if issues are found.

### Vulnerability Monitoring

- Enable GitHub Dependabot **security alerts** (Settings > Code security) for passive notification of known CVEs
- Do **not** enable Dependabot version update PRs — manual updates are preferred for this project
- When a vulnerability alert is received, follow the manual update procedure above

## Deployment

- **Automatic Deployment**: Triggered automatically on push to main branch
- **Manual Deployment**: Run `./scripts/deploy.sh`
- **GitHub Pages**: Automatically configured via Actions

## Task Management

**TODO and DONE Files Management**:
- When tasks in `TODO.md` are completed, move them to `DONE.md`
- Keep `TODO.md` clean by only containing pending or in-progress tasks
- `DONE.md` serves as a record of completed features and improvements
- When moving items, preserve the original formatting and add completion date if relevant
- Group related completed items together in `DONE.md` for better organization

## License and Disclaimer

- This is an unofficial fan project
- Story data uses the ArknightsStoryJson project

## Devcontainer

This project uses a devcontainer for a consistent development environment.

### Files

- `.devcontainer/Dockerfile` — Container image definition. Edit to change the base image, install additional packages, or add language runtimes.
- `.devcontainer/devcontainer.json` — Devcontainer configuration. Controls the container name, VS Code extensions, environment variables, bind mounts, and port forwarding.
- `.devcontainer/inside-container.settings.local.json` — Claude Code local permission overrides inside the container. Mounted as `.claude/settings.local.json` to override project-level settings.
- `.devcontainer/build.sh` — Builds the container image. Run this after modifying the Dockerfile.
- `.devcontainer/shell.sh` — Starts the container and opens an interactive bash shell inside it.

### Usage

```bash
# Build the container image
.devcontainer/build.sh

# Start the container and open a shell
.devcontainer/shell.sh
```

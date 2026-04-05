# Arknights Story Archive

A static site generator for viewing Arknights event stories in HTML format.

## Overview

This project converts Arknights in-game event stories into readable HTML format and publishes them on GitHub Pages. It uses story data from [ArknightsStoryJson](https://github.com/050644zf/ArknightsStoryJson) to process and generate the stories.

## Features

- **Automatic Updates**: Daily updates with latest story data via GitHub Actions
- **Readable Display**: Organized layout for conversation-style stories
- **Mobile Support**: Responsive design for comfortable viewing on smartphones
- **Event Classification**: Categorized display by event types
- **Navigation**: Previous/next story navigation and breadcrumb navigation
- **Dark Mode**: Eye-friendly dark theme option
- **Font Switching**: Toggle between sans-serif and serif fonts
- **Search & Filter**: Search stories and filter events by type/year

## Setup

### Requirements

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Rust](https://rustup.rs/) (for building the search index tool)
- Git

### Installation

1. Clone the repository with submodules:
   ```bash
   git clone --recurse-submodules https://github.com/[username]/astrhtml.git
   cd astrhtml
   ```

2. Install Python dependencies (creates a project-local `.venv`):
   ```bash
   uv sync
   ```

3. Build the search index tool (Rust):
   ```bash
   cd tools/bigram-index && cargo build --release && cd ../..
   ```

4. Update submodules:
   ```bash
   git submodule update --remote --merge
   ```

## Usage

### Local Development

#### Build the Site

Build all events:
```bash
uv run python build.py
```

Test build with limited events:
```bash
uv run python build.py --limit 5
```

Clean build (removes previous output):
```bash
uv run python build.py --clean
```

#### Preview the Site

Start local preview server:
```bash
uv run python preview.py
```

This will:
- Start a local HTTP server on port 8000
- Automatically open your browser to view the site
- Serve the built site from the `dist/` directory

Preview server options:
```bash
# Use custom port
uv run python preview.py --port 3000

# Don't automatically open browser
uv run python preview.py --no-browser

# Allow external connections
uv run python preview.py --host 0.0.0.0
```

**Note**: You must run `uv run python build.py` first to generate the site before using the preview server.

### Development Workflow

1. Build the site: `uv run python build.py --limit 5`
2. Start preview server: `uv run python preview.py`
3. Make changes to code/templates
4. Rebuild: `uv run python build.py --limit 5`
5. Refresh browser to see changes

### GitHub Pages Deployment

1. Push to GitHub repository
2. Go to repository Settings > Pages
3. Select "GitHub Actions" as the source
4. Push to `main` branch triggers automatic deployment

### Manual Deployment

```bash
./scripts/deploy.sh
```

## Project Structure

```
astrhtml/
├── src/                    # Python source code
│   ├── models/            # Data models
│   ├── lib/               # Data processing libraries
│   ├── generators/        # HTML generators
│   ├── utils/             # Utility functions
│   └── config.py          # Configuration file
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Index page
│   ├── event.html        # Event page
│   └── story.html        # Story page
├── static/               # Static files
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── data/                 # Data directory
│   └── ArknightsStoryJson/ # Story data (submodule)
├── dist/                 # Build output directory
├── build.py              # Main build script
├── preview.py            # Local preview server
└── requirements.txt      # Python dependencies
```

## Configuration

You can modify settings in `src/config.py`:

- `MAX_EVENTS_PER_PAGE`: Maximum events per page
- `INCLUDE_REPLICATE_EVENTS`: Whether to include rerun events
- `SORT_EVENTS_BY_DATE`: Whether to sort by date

## Development

### Adding New Features

1. Add data models in `src/models/`
2. Add data processing logic in `src/lib/`
3. Add HTML templates in `templates/`
4. Add HTML generators in `src/generators/`

### Testing

Test with limited build:
```bash
uv run python build.py --limit 1
```

Verify dependencies:
```bash
uv run python -c "import jinja2, pathlib; print('Dependencies OK')"
```

### End-to-End Tests (Playwright)

Run integration tests for the search functionality using headless Chromium:

```bash
# Install test dependencies
uv sync --group dev

# Install Playwright browser
uv run playwright install chromium

# Build the site first
uv run python build.py --limit 3 --no-check-links

# Run tests
uv run pytest tests/e2e/test_search.py -v
```

## Troubleshooting

### Common Issues

1. **Empty submodule**:
   ```bash
   git submodule update --init --recursive
   ```

2. **Python dependency errors**:
   ```bash
   uv sync
   ```

3. **Build errors**:
   - Ensure `data/ArknightsStoryJson` directory exists
   - Confirm using Python 3.8 or higher

4. **Preview server errors**:
   - Run `uv run python build.py` first to generate the site
   - Check if port is already in use: `uv run python preview.py --port 8001`

## Technology Stack

- **Language**: Python 3.8+, Rust (search index builder)
- **Package Manager**: [uv](https://docs.astral.sh/uv/), Cargo
- **Template Engine**: Jinja2
- **Static Site Generator**: Custom implementation
- **Search**: Bi-gram inverted index (Rust) + client-side two-stage search (JavaScript)
- **Testing**: Playwright (headless Chromium e2e tests)
- **Deployment**: GitHub Pages + GitHub Actions
- **Styling**: Pure CSS with CSS variables
- **Frontend**: Vanilla JavaScript

## License and Disclaimer

- This is an unofficial fan project
- Story data is sourced from the [ArknightsStoryJson](https://github.com/050644zf/ArknightsStoryJson) project
- Arknights copyright belongs to Hypergryph

## Contributing

Bug reports and feature requests are welcome via GitHub Issues.

## Related Links

- [Arknights Official Website](https://www.arknights.jp/)
- [ArknightsStoryJson](https://github.com/050644zf/ArknightsStoryJson)
- [GitHub Pages Documentation](https://docs.github.com/pages)
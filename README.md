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
- Git

### Installation

1. Clone the repository with submodules:
   ```bash
   git clone --recurse-submodules https://github.com/[username]/astrhtml.git
   cd astrhtml
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update submodules:
   ```bash
   git submodule update --remote --merge
   ```

## Usage

### Local Development

#### Build the Site

Build all events:
```bash
python build.py
```

Test build with limited events:
```bash
python build.py --limit 5
```

Clean build (removes previous output):
```bash
python build.py --clean
```

#### Preview the Site

Start local preview server:
```bash
python preview.py
```

This will:
- Start a local HTTP server on port 8000
- Automatically open your browser to view the site
- Serve the built site from the `dist/` directory

Preview server options:
```bash
# Use custom port
python preview.py --port 3000

# Don't automatically open browser
python preview.py --no-browser

# Allow external connections
python preview.py --host 0.0.0.0
```

**Note**: You must run `python build.py` first to generate the site before using the preview server.

### Development Workflow

1. Build the site: `python build.py --limit 5`
2. Start preview server: `python preview.py`
3. Make changes to code/templates
4. Rebuild: `python build.py --limit 5`
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
python build.py --limit 1
```

Verify dependencies:
```bash
python -c "import jinja2, pathlib; print('Dependencies OK')"
```

## Troubleshooting

### Common Issues

1. **Empty submodule**:
   ```bash
   git submodule update --init --recursive
   ```

2. **Python dependency errors**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Build errors**:
   - Ensure `data/ArknightsStoryJson` directory exists
   - Confirm using Python 3.8 or higher

4. **Preview server errors**:
   - Run `python build.py` first to generate the site
   - Check if port is already in use: `python preview.py --port 8001`

## Technology Stack

- **Language**: Python 3.8+
- **Template Engine**: Jinja2
- **Static Site Generator**: Custom implementation
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
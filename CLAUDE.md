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
pip install -r requirements.txt

# Build all events
python3 build.py

# Test build (limited events)
python3 build.py --limit 5

# Clean build
python3 build.py --clean

# Start local preview server
python3 preview.py
```

## Local Preview

### Starting the Preview Server

```bash
# Basic usage (opens browser automatically on port 8000)
python3 preview.py

# Custom port
python3 preview.py --port 3000

# Don't open browser automatically
python3 preview.py --no-browser

# Allow external connections
python3 preview.py --host 0.0.0.0
```

### Development Workflow

1. **Build the site**: `python3 build.py --limit 5`
2. **Start preview server**: `python3 preview.py`
3. **Make code changes**
4. **Rebuild**: `python3 build.py --limit 5`
5. **Refresh browser** to see changes

**Important**: You must run `python3 build.py` first to generate the `dist/` directory before using the preview server.

## Test Commands

```bash
# Check if dependencies are correctly installed
python3 -c "import jinja2, pathlib; print('Dependencies OK')"

# Verify build system functionality
python3 build.py --limit 1

# Update submodules
git submodule update --remote --merge
```

## Important Files

### Data Processing
- `src/lib/stage_parser.py` - Stage information and story order determination
- `src/lib/event_parser.py` - Event information processing
- `src/lib/story_parser.py` - Story data analysis

### HTML Generation
- `src/generators/` - HTML generation modules
- `templates/` - Jinja2 templates
- `static/css/` - Stylesheets

### Configuration & Build
- `build.py` - Main build script
- `preview.py` - Local preview server with auto-browser opening
- `src/config.py` - Configuration file
- `.github/workflows/deploy.yml` - GitHub Actions configuration

## Development Notes

1. **Submodules**: ArknightsStoryJson data is an external submodule
   ```bash
   git submodule update --init --recursive
   ```

2. **Python Requirements**: Use Python 3.8 or higher

3. **Pre-build Verification**: 
   - Confirm `data/ArknightsStoryJson` directory exists
   - Ensure requirements.txt dependencies are installed

4. **HTML File Names**: 
   - Event pages: `events/{event_id}/index.html`
   - Story pages: `events/{event_id}/stories/{stage_code}.html`
   - Stage codes (OR-1, OR-ST-1, etc.) are used as file names

5. **Data Compatibility and Backward Compatibility**:
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
   pip install -r requirements.txt
   ```

2. **Empty Submodule**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Build Error**:
   - Confirm using Python 3.8 or higher
   - Verify `data/ArknightsStoryJson` exists

4. **Preview Server Error**:
   - Run `python3 build.py` first to generate the site
   - If port is in use, try: `python3 preview.py --port 8001`

## Deployment

- **Automatic Deployment**: Triggered automatically on push to main branch
- **Manual Deployment**: Run `./scripts/deploy.sh`
- **GitHub Pages**: Automatically configured via Actions

## License and Disclaimer

- This is an unofficial fan project
- Story data uses the ArknightsStoryJson project
- Arknights copyright belongs to Hypergryph
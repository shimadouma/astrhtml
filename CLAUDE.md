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

## Link Health Check

**IMPORTANT**: Always run link health checks during development and testing to ensure all internal links are working correctly.

### Automatic Link Checking

The build process now includes automatic link checking by default:

```bash
# Build with automatic link checking (default)
python3 build.py

# Skip link checking if needed
python3 build.py --no-check-links
```

### Manual Link Checking

You can also run the link checker manually:

```bash
# Check all links in the generated site
python3 scripts/check_links.py

# Check links with detailed output
python3 scripts/check_links.py --verbose

# Check links and fail with exit code if broken links found
python3 scripts/check_links.py --fail-on-broken
```

### Development Workflow with Link Checking

**During development and testing, always ensure the link check passes:**

1. **Build the site**: `python3 build.py --limit 5`
2. **Verify links are working**: The build will automatically check links and fail if any are broken
3. **Fix any broken links** if the build fails
4. **Rebuild and verify**: `python3 build.py --limit 5`

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
python3 scripts/check_empty_events.py

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

1. **Build the site**: `python3 build.py --limit 5`
2. **Run enhanced validation**: `python3 scripts/check_empty_events.py`
3. **Fix any issues found**:
   - **No files**: Check story data processing logic
   - **Unlinked files**: Verify event page generation and template rendering
   - **Partial linking**: Check story order determination logic
   - **Broken links**: Verify filename generation consistency
4. **Rebuild and verify**: `python3 build.py --limit 5`

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

2. **Python Requirements**: Use Python 3.8 or higher

3. **Pre-build Verification**: 
   - Confirm `data/ArknightsStoryJson` directory exists
   - Ensure requirements.txt dependencies are installed

4. **HTML File Names**: 
   - Event pages: `events/{event_id}/index.html`
   - Story pages: `events/{event_id}/stories/{stage_code}.html`
   - Stage codes (OR-1, OR-ST-1, etc.) are used as file names

5. **MINISTORY Event Special Handling**:
   - **Critical Design Rule**: MINISTORY events have separate gameplay and story stages
   - **Gameplay stages** (in stage_table.json): Used for battles, should NOT be processed for story generation
   - **Story stages** (level_*_st*.json files): Contain story content, ONLY these should be processed
   - Example for act15mini:
     - Gameplay stages (ignore): `act15mini_01` (FD-1), `act15mini_02` (FD-2), etc.
     - Story stages (process): `level_act15mini_st01.json`, `level_act15mini_st02.json`, etc.
   - This separation is unique to MINISTORY event type and does not apply to SIDESTORY or other event types

6. **Data Compatibility and Backward Compatibility**:
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

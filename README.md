# API Explorer

A desktop application for exploring and searching public APIs. Browse hundreds of APIs across categories including finance, social, weather, maps, email, storage, AI, music, video, news, sports, health, crypto, ecommerce, and developer tools.

## Features

- **Dark Theme** — Modern dark UI with high-contrast colors for comfortable browsing
- **Search & Filter** — Search across API names, descriptions, and tags; filter by category
- **Recently Viewed** — Tracks your browsing history using localStorage
- **Favorites** — Star and save your favorite APIs for quick access
- **Live Data Proxy** — Fetches data from public APIs at runtime with cached fallback
- **Offline Mode** — Falls back to bundled static data when network is unavailable
- **Data Integrity** — Validates JSON schema and checksums on startup; alerts on corruption
- **Self-Sustaining** — Caches fetched data locally for resilience
- **Discover Section** — Visual category cards with color-coded icons and hover effects
- **Popular APIs** — Mini-section highlighting the top 5 APIs by endpoint count

## Changes Log

### Recent Updates
- **Expanded API dataset** from 328 to 441 APIs across 15 categories (finance, social, weather, maps, email, storage, AI, music, video, news, sports, health, crypto, ecommerce, developer tools)
- **Enhanced Discover section** with color-coded category cards, animated hover effects (scale, lift, icon zoom), and a new "Popular APIs" mini-section showing the top 5 APIs by endpoint count
- **Polished card layouts** — increased grid gap (16px → 20px), card padding (10px 12px → 14px 16px), and smooth hover transitions (0.25s ease)
- **Improved header** — better alignment, increased padding, focused search bar with glow effect, and smoother button interactions
- **Updated checksum** for data integrity verification

## Setup

### Dev Server

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask development server:
   ```
   python app.py
   ```

3. Open http://localhost:5000 in your browser.

### PyInstaller Build

1. Ensure dependencies are installed (see above).

2. Run the build script:
   ```
   build.bat
   ```

3. The output executable will be in `dist\api-explorer-<VERSION>\`.

## Data Sources

The application bundles a dataset of 441+ public APIs in `data/apis.json`. Data categories include:

- Finance, Crypto, AI, Developer, Ecommerce, Email, Maps, Music, News, Sports, Storage, Video, Weather, Social, Health

The app also supports fetching live data from public APIs via proxy endpoints (`/api/proxy/<api_name>`). Fetched data is cached in the `cache/` directory.

## Usage Notes

- **No API keys required** for the bundled dataset. Proxy endpoints may require API keys configured via environment variables.
- **Stale data indicator** appears when the app falls back to cached or bundled data.
- **Configuration** should be stored in `.env` files (excluded from version control).
- **Production mode** disables debug output and does not leak stack traces.

## Project Structure

```
api-explorer/
├── app.py                  # Flask backend with proxy and caching
├── build.bat               # PyInstaller build script
├── dependencies.bat        # Dependency installer
├── requirements.txt        # Python dependencies
├── VERSION                 # Version number
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── data/
│   ├── apis.json           # Bundled API dataset (441+ APIs)
│   └── apis.json.sha256    # Checksum for integrity verification
├── cache/                  # Runtime cache for fetched data
└── static/
    ├── index.html          # Main HTML page
    ├── css/
    │   └── style.css       # Stylesheet (dark theme)
    └── js/
        ├── explorer.js     # Main application logic
        ├── favorites.js    # Favorites and recently viewed management
        └── filters.js      # Search and filter logic
```

## License

This project is part of the Trendsetter product line.
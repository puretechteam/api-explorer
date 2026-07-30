# API Explorer

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange)](CHANGELOG.md)

A desktop application for exploring and searching public APIs. Browse hundreds of APIs across categories including finance, social, weather, maps, email, storage, AI, music, video, news, sports, health, crypto, ecommerce, and developer tools.

## Contents

- [Contributing](CONTRIBUTING.md)
- [License](LICENSE)
- [Security](SECURITY.md)

## Development

### Prerequisites

- Python 3.12+
- pip

### Setup

1. Install dependencies:
   ```
   make install
   ```
   Or manually:
   ```
   pip install -r requirements.txt
   ```

### Running the App

```
make run
```

### Building the Executable

```
make build
```

### Running Tests

```
make test
```

### Linting

```
make lint
```

### Formatting

```
make format
```

### Docker

```
make docker-run
```
Or:
```
docker-compose up
```

> **Note:** The Makefile is the preferred build tool and provides cross-platform support for all development workflows.

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

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full changelog.

## Setup

### Dev Server

1. Install dependencies:
   ```
   make install
   ```

2. Run the Flask development server:
   ```
   make run
   ```

3. Open http://localhost:5000 in your browser.

### Development Dependencies

For development and testing, install:
```
make install-dev
```

### PyInstaller Build

1. Ensure dependencies are installed (see above).

2. Run the build:
   ```
   make build
   ```

3. The output executable will be in `dist/api-explorer-<VERSION>/`.

## Docker

### Building the Image

```
docker build -t api-explorer .
```

### Running the Container

```
docker run -p 5000:5000 api-explorer
```

### Using Docker Compose

```
docker-compose up -d
```

This starts the Flask app in development mode with source code mounted for live reloading.

## Data Sources

The application bundles a dataset of 461 public APIs in `data/apis.json`. Data categories include:

- Finance, Crypto, AI, Developer, Ecommerce, Email, Maps, Music, News, Sports, Storage, Video, Weather, Social, Health

The app also supports fetching live data from public APIs via proxy endpoints (`/api/proxy/<api_name>`). Fetched data is cached in the `cache/` directory.

## Usage Notes

- **No API keys required** for the bundled dataset. Proxy endpoints may require API keys configured via environment variables.
- **Stale data indicator** appears when the app falls back to cached or bundled data.
- **Configuration** should be stored in `.env` files (excluded from version control).
- **Production mode** disables debug output and does not leak stack traces.

## Roadmap

- Add API key management for authenticated endpoints
- Support for OpenAPI/Swagger spec import
- Rate limiting visualization per API
- Bookmark collections for grouping related APIs
- API documentation generation from fetched data

## Project Structure

```
api-explorer/
├── app.py                  # Flask backend with proxy and caching
├── build.bat               # PyInstaller build script
├── dependencies.bat        # Dependency installer
├── requirements.txt        # Runtime dependencies
├── requirements-build.txt  # Build-time dependencies (PyInstaller)
├── requirements-dev.txt    # Development dependencies
├── VERSION                 # Version number
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── data/
│   ├── apis.json           # Bundled API dataset (461 APIs)
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

This project is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Pure Tech.

## Security

Please see the [Security Policy](SECURITY.md) for vulnerability reporting guidelines.
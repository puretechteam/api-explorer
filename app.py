"""API Explorer backend server.

Provides a Flask-based web application for exploring REST APIs,
including a proxy endpoint, caching, and data validation.
"""

import hashlib
import ipaddress
import json
import logging
import os
import sys
import time
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

try:
    import requests
except ImportError:
    requests = None

app = Flask(__name__, static_folder="static", static_url_path="/static")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "api-explorer.log")),
        logging.StreamHandler()
    ]
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
BUNDLED_APIS_FILE = os.path.join(DATA_DIR, "apis.json")

SCHEMA_REQUIRED_FIELDS = ["name", "category", "description", "auth", "rate_limit", "endpoints", "docs_url", "tags"]

PROXY_RATE_LIMIT_WINDOW = 30
PROXY_RATE_LIMIT_MAX_REQUESTS = 1
_proxy_rate_limit_store = {}

PROXY_ENDPOINTS = {
    "stripe": "https://api.stripe.com/v1",
    "openai": "https://api.openai.com/v1",
    "github": "https://api.github.com",
    "twilio": "https://api.twilio.com/2010-04-01",
    "sendgrid": "https://api.sendgrid.com/v3",
    "mapbox": "https://api.mapbox.com",
    "weatherapi": "https://api.weatherapi.com/v1",
    "openweathermap": "https://api.openweathermap.org/data/2.5",
    "spotify": "https://api.spotify.com/v1",
    "youtube": "https://www.googleapis.com/youtube/v3",
    "twitter": "https://api.twitter.com/2",
    "reddit": "https://www.reddit.com",
    "slack": "https://slack.com/api",
    "discord": "https://discord.com/api/v10",
    "shopify": "https://api.shopify.com",
    "woocommerce": "https://api.woocommerce.com",
    "firebase": "https://firebase.googleapis.com/v1",
    "supabase": "https://api.supabase.com/v1",
    "vercel": "https://api.vercel.com",
    "netlify": "https://api.netlify.com",
    "gcp": "https://cloud.google.com/apis",
    "azure": "https://management.azure.com",
    "dockerhub": "https://hub.docker.com/v2",
    "npm": "https://registry.npmjs.org",
    "pypi": "https://pypi.org/pypi",
    "huggingface": "https://api-inference.huggingface.co/models",
    "replicate": "https://api.replicate.com/v1",
    "elevenlabs": "https://api.elevenlabs.io/v1",
    "stabilityai": "https://api.stability.ai/v1",
    "googlemaps": "https://maps.googleapis.com/maps/api",
    "here": "https://router.hereapi.com/v8",
    "tomtom": "https://api.tomtom.com",
}


def is_safe_url(url: str) -> bool:
    """Check if a URL is safe for proxying.

    Validates that the URL uses HTTPS and does not target
    private or internal IP ranges (SSRF protection).

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is safe, False otherwise.
    """
    if not url.startswith("https://"):
        return False
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_link_local:
            return False
    except ValueError:
        pass
    private_ranges = [
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("169.254.0.0/16"),
    ]
    try:
        addr = ipaddress.ip_address(hostname)
        for network in private_ranges:
            if addr in network:
                return False
    except ValueError:
        pass
    return True


def check_rate_limit(ip: str) -> bool:
    """Check if an IP address is within the rate limit.

    Allows at most one request per PROXY_RATE_LIMIT_WINDOW
    seconds per IP address.

    Args:
        ip: The client IP address.

    Returns:
        True if the request is allowed, False if rate-limited.
    """
    now = time.time()
    if ip in _proxy_rate_limit_store:
        timestamps = [t for t in _proxy_rate_limit_store[ip] if now - t < PROXY_RATE_LIMIT_WINDOW]
        _proxy_rate_limit_store[ip] = timestamps
        if len(timestamps) >= PROXY_RATE_LIMIT_MAX_REQUESTS:
            return False
    else:
        _proxy_rate_limit_store[ip] = []
    _proxy_rate_limit_store[ip].append(now)
    return True


def get_path(subdir: str) -> str:
    """Get the absolute path to a subdirectory of the project.

    Resolves correctly whether the application is running
    as a frozen PyInstaller bundle or as a regular Python script.

    Args:
        subdir: The subdirectory name (e.g., 'data', 'static').

    Returns:
        The absolute path to the requested subdirectory.
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, subdir)


def get_data_path() -> str:
    """Get the absolute path to the data directory."""
    return get_path("data")


def get_static_path() -> str:
    """Get the absolute path to the static files directory."""
    return get_path("static")


def compute_checksum(filepath: str) -> str:
    """Compute the SHA-256 checksum of a file.

    Args:
        filepath: The path to the file.

    Returns:
        The hexadecimal SHA-256 digest.
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_api_data(data: Any) -> tuple[bool, str | None]:
    """Validate that API data conforms to the required schema.

    Checks that data is a list of dicts, each containing all
    fields listed in SCHEMA_REQUIRED_FIELDS.

    Args:
        data: The data to validate.

    Returns:
        A tuple of (is_valid, error_message). error_message is
        None if validation passes.
    """
    if not isinstance(data, list):
        return False, "Data is not a list"
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            return False, f"Item {i} is not an object"
        for field in SCHEMA_REQUIRED_FIELDS:
            if field not in item:
                return False, f"Item {i} missing required field '{field}'"
    return True, None


def load_bundled_data() -> list[dict[str, Any]] | None:
    """Load and validate the bundled apis.json data.

    Verifies the file checksum and schema before returning.
    Falls back to returning None if the data is invalid or
    cannot be read.

    Returns:
        The parsed API data list, or None on failure.
    """
    checksum_path = os.path.join(DATA_DIR, "apis.json.sha256")
    if os.path.exists(checksum_path):
        with open(checksum_path) as f:
            expected_hash = f.read().strip()
        actual_hash = compute_checksum(BUNDLED_APIS_FILE)
        if actual_hash != expected_hash:
            app.logger.warning("Bundled apis.json checksum mismatch — data may be corrupted")
    try:
        with open(BUNDLED_APIS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        app.logger.error("Failed to load bundled apis.json: %s", e)
        return None
    valid, msg = validate_api_data(data)
    if not valid:
        app.logger.error("Bundled apis.json schema validation failed: %s", msg)
        return None
    return data


def get_cache_path(api_name: str) -> str:
    """Get the filesystem path for the cache file of an API.

    The cache directory is created if it does not exist.

    Args:
        api_name: The name of the API.

    Returns:
        The absolute path to the cache JSON file.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_name = api_name.lower().replace(" ", "_").replace("/", "_")
    return os.path.join(CACHE_DIR, f"{safe_name}.json")


def read_cache(api_name: str) -> Any | None:
    """Read cached proxy data for an API from disk.

    Args:
        api_name: The name of the API.

    Returns:
        The cached data if found and valid, or None.
    """
    cache_path = get_cache_path(api_name)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
    return None


def write_cache(api_name: str, data: Any) -> None:
    """Write proxy response data to the cache file for an API.

    Args:
        api_name: The name of the API.
        data: The data to cache.
    """
    cache_path = get_cache_path(api_name)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


@app.route("/")
def index() -> str:
    """Serve the main index HTML page."""
    return send_from_directory(get_static_path(), "index.html")


@app.route("/static/<path:filename>")
def static_files(filename: str) -> str:
    """Serve a static file from the static directory."""
    return send_from_directory(get_static_path(), filename)


@app.route("/api/data")
def api_data() -> Any:
    """Return the full bundled API data as JSON."""
    data = load_bundled_data()
    if data is None:
        return jsonify({"error": "Failed to load API data"}), 500
    return jsonify(data)


@app.route("/api/categories")
def api_categories() -> Any:
    """Return a sorted list of unique API categories."""
    data = load_bundled_data()
    if data is None:
        return jsonify({"error": "Failed to load API data"}), 500
    categories = sorted(set(item["category"] for item in data))
    return jsonify(categories)


@app.route("/api/proxy/<api_name>", methods=["GET"])
def proxy_fetch(api_name: str) -> Any:
    """Proxy a request to an external API endpoint.

    Validates the target URL for SSRF safety, enforces per-IP
    rate limiting, and serves cached data when available.

    Args:
        api_name: The name of the API to proxy.

    Returns:
        JSON response with the proxied data or an error message.
    """
    client_ip = request.remote_addr
    if not check_rate_limit(client_ip):
        return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

    base_url = PROXY_ENDPOINTS.get(api_name.lower())
    if not base_url:
        return jsonify({"error": f"Unknown API: {api_name}"}), 404

    if not is_safe_url(base_url):
        return jsonify({"error": f"Proxy target for {api_name} is not allowed"}), 403

    cached = read_cache(api_name)
    if cached is not None:
        return jsonify({"source": "cache", "data": cached})

    if requests is None:
        return jsonify({"error": "requests library not available"}), 503

    try:
        timeout = request.args.get("timeout", 10, type=int)
        resp = requests.get(base_url, timeout=min(timeout, 30), headers={
            "User-Agent": "api-explorer/1.0"
        })
        resp.raise_for_status()
        data = resp.json()
        write_cache(api_name, data)
        return jsonify({"source": "live", "data": data})
    except requests.exceptions.RequestException as e:
        app.logger.warning("Proxy fetch failed for %s: %s", api_name, e)
        cached = read_cache(api_name)
        if cached is not None:
            return jsonify({"source": "cache_fallback", "data": cached, "warning": "Live data unavailable; showing cached data"})
        return jsonify({"error": f"Failed to fetch data for {api_name}", "details": str(e)}), 502
    except (ValueError, KeyError) as e:
        app.logger.warning("Proxy response parsing failed for %s: %s", api_name, e)
        cached = read_cache(api_name)
        if cached is not None:
            return jsonify({"source": "cache_fallback", "data": cached, "warning": "Live data parse failed; showing cached data"})
        return jsonify({"error": f"Failed to parse response for {api_name}"}), 502


@app.route("/api/cache/list")
def list_cache() -> Any:
    """Return a list of cached API names."""
    if not os.path.exists(CACHE_DIR):
        return jsonify([])
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]
    return jsonify([f.replace(".json", "") for f in files])


@app.route("/api/cache/clear", methods=["POST"])
def clear_cache() -> Any:
    """Clear all cached proxy data files."""
    if not os.path.exists(CACHE_DIR):
        return jsonify({"message": "Cache already empty"})
    for f in os.listdir(CACHE_DIR):
        if f.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, f))
    return jsonify({"message": "Cache cleared"})


@app.errorhandler(404)
def not_found(e: Exception) -> Any:
    """Handle 404 errors with a JSON response."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e: Exception) -> Any:
    """Handle 500 errors with a JSON response."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

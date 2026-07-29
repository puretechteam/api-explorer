import os
import sys
import json
import hashlib
import threading
from flask import Flask, jsonify, send_from_directory, request

try:
    import requests
except ImportError:
    requests = None

app = Flask(__name__, static_folder="static", static_url_path="/static")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
BUNDLED_APIS_FILE = os.path.join(DATA_DIR, "apis.json")

SCHEMA_REQUIRED_FIELDS = ["name", "category", "description", "auth", "rate_limit", "endpoints", "docs_url", "tags"]

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
    "aws": "https://api.aws.amazon.com",
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
    "mapzen": "https://mapzen.com/api",
}


def get_data_path():
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return base


def compute_checksum(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_api_data(data):
    if not isinstance(data, list):
        return False, "Data is not a list"
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            return False, f"Item {i} is not an object"
        for field in SCHEMA_REQUIRED_FIELDS:
            if field not in item:
                return False, f"Item {i} missing required field '{field}'"
    return True, None


def load_bundled_data():
    checksum_path = os.path.join(DATA_DIR, "apis.json.sha256")
    if os.path.exists(checksum_path):
        with open(checksum_path, "r") as f:
            expected_hash = f.read().strip()
        actual_hash = compute_checksum(BUNDLED_APIS_FILE)
        if actual_hash != expected_hash:
            app.logger.warning("Bundled apis.json checksum mismatch — data may be corrupted")
    try:
        with open(BUNDLED_APIS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        app.logger.error("Failed to load bundled apis.json: %s", e)
        return None
    valid, msg = validate_api_data(data)
    if not valid:
        app.logger.error("Bundled apis.json schema validation failed: %s", msg)
        return None
    return data


def get_cache_path(api_name):
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_name = api_name.lower().replace(" ", "_").replace("/", "_")
    return os.path.join(CACHE_DIR, f"{safe_name}.json")


def read_cache(api_name):
    cache_path = get_cache_path(api_name)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def write_cache(api_name, data):
    cache_path = get_cache_path(api_name)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


@app.route("/api/data")
def api_data():
    data = load_bundled_data()
    if data is None:
        return jsonify({"error": "Failed to load API data"}), 500
    return jsonify(data)


@app.route("/api/categories")
def api_categories():
    data = load_bundled_data()
    if data is None:
        return jsonify({"error": "Failed to load API data"}), 500
    categories = sorted(set(item["category"] for item in data))
    return jsonify(categories)


@app.route("/api/proxy/<api_name>", methods=["GET"])
def proxy_fetch(api_name):
    base_url = PROXY_ENDPOINTS.get(api_name.lower())
    if not base_url:
        return jsonify({"error": f"Unknown API: {api_name}"}), 404

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
def list_cache():
    if not os.path.exists(CACHE_DIR):
        return jsonify([])
    files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]
    return jsonify([f.replace(".json", "") for f in files])


@app.route("/api/cache/clear", methods=["POST"])
def clear_cache():
    if not os.path.exists(CACHE_DIR):
        return jsonify({"message": "Cache already empty"})
    for f in os.listdir(CACHE_DIR):
        if f.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, f))
    return jsonify({"message": "Cache cleared"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
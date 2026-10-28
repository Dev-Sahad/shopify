"""
Shopify AI Dropshipping Importer - Flask Web Application
Provides a dashboard for:
- Testing & managing Shopify API credentials
- Selecting viral trending gadgets or extracting from any product URL
- AI enhancement (powered by Gemini) for high-converting titles, descriptions & pricing
- 1-click import into Shopify Store (as Draft or Active)
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load local environment variables
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH)

from shopify_client import ShopifyClient
from ai_enhancer import enhance_product_with_gemini, calculate_smart_pricing
from extractor import extract_from_url
from trending_gadgets import get_trending_gadgets, get_gadget_by_id

app = Flask(__name__)
CORS(app)


def save_env_values(updates: dict):
    """Updates key-value pairs in the .env file."""
    lines = []
    existing_keys = set()
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
        parts = stripped.split("=", 1)
        k = parts[0].strip()
        if k in updates:
            new_lines.append(f"{k}={updates[k]}\n")
            existing_keys.add(k)
            os.environ[k] = str(updates[k])
        else:
            new_lines.append(line)

    for k, v in updates.items():
        if k not in existing_keys:
            new_lines.append(f"{k}={v}\n")
            os.environ[k] = str(v)

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    domain = os.getenv("SHOPIFY_STORE_DOMAIN", "")
    token = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    multiplier = os.getenv("DEFAULT_PRICE_MULTIPLIER", "2.5")

    masked_token = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else ("Configured" if token else "")
    masked_gemini = f"{gemini_key[:6]}...{gemini_key[-3:]}" if len(gemini_key) > 9 else ("Configured" if gemini_key else "")

    return jsonify({
        "shopify_domain": domain,
        "shopify_connected": bool(domain and token),
        "shopify_token_masked": masked_token,
        "gemini_configured": bool(gemini_key),
        "gemini_key_masked": masked_gemini,
        "price_multiplier": float(multiplier)
    })


@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.json or {}
    updates = {}
    if "shopify_domain" in data:
        updates["SHOPIFY_STORE_DOMAIN"] = data["shopify_domain"].strip()
    if "shopify_token" in data and data["shopify_token"].strip():
        updates["SHOPIFY_ADMIN_ACCESS_TOKEN"] = data["shopify_token"].strip()
    if "gemini_key" in data and data["gemini_key"].strip():
        updates["GEMINI_API_KEY"] = data["gemini_key"].strip()
    if "price_multiplier" in data:
        updates["DEFAULT_PRICE_MULTIPLIER"] = str(data["price_multiplier"])

    save_env_values(updates)
    return jsonify({"success": True, "message": "Settings updated successfully."})


@app.route("/api/shopify/test", methods=["POST"])
def test_shopify():
    data = request.json or {}
    domain = data.get("domain") or os.getenv("SHOPIFY_STORE_DOMAIN", "")
    token = data.get("token") or os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN", "")

    client = ShopifyClient(store_domain=domain, access_token=token)
    result = client.test_connection()
    return jsonify(result)


@app.route("/api/trending", methods=["GET"])
def list_trending():
    return jsonify({"success": True, "gadgets": get_trending_gadgets()})


@app.route("/api/extract", methods=["POST"])
def extract_product():
    data = request.json or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"success": False, "error": "URL parameter is required"}), 400

    extracted = extract_from_url(url)
    return jsonify(extracted)


@app.route("/api/enhance", methods=["POST"])
def enhance_product():
    data = request.json or {}
    raw_title = data.get("raw_title", "Smart Gadget")
    raw_description = data.get("raw_description", "")
    supplier_price = float(data.get("supplier_price", 15.0))
    multiplier = float(data.get("price_multiplier", os.getenv("DEFAULT_PRICE_MULTIPLIER", 2.5)))
    gemini_key = data.get("gemini_key") or os.getenv("GEMINI_API_KEY")

    enhanced = enhance_product_with_gemini(
        raw_title=raw_title,
        raw_description=raw_description,
        supplier_price=supplier_price,
        api_key=gemini_key,
        price_multiplier=multiplier
    )

    return jsonify({"success": True, "data": enhanced})


@app.route("/api/shopify/import", methods=["POST"])
def import_to_shopify():
    data = request.json or {}
    product_data = data.get("product", {})

    if not product_data.get("title"):
        return jsonify({"success": False, "error": "Product title is required."}), 400

    client = ShopifyClient()
    result = client.create_product(product_data)
    return jsonify(result)


if __name__ == "__main__":
    port = 5000
    print(f"Starting Shopify AI Dropshipping Assistant on http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)


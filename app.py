"""
Shopify AI 24/7 Dropshipping Autonomous Management System
Flask Web Server & Comprehensive REST API
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
from gadget_hunter import get_all_gadgets, get_gadget_by_id, search_gadgets
from bot_daemon import bot_daemon
from supplier_manager import (
    generate_supplier_inquiry,
    get_supplier_interactions,
    log_supplier_interaction,
    format_order_for_supplier_dispatch
)

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


# -------------------------------------------------------------
# Web UI Root
# -------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------------------
# Configuration & System Status Endpoints
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# 24/7 Autonomous Bot Control Endpoints
# -------------------------------------------------------------

@app.route("/api/bot/status", methods=["GET"])
def get_bot_status():
    status = bot_daemon.get_status()
    return jsonify({"success": True, "bot": status})


@app.route("/api/bot/start", methods=["POST"])
def start_bot():
    result = bot_daemon.start_bot()
    return jsonify(result)


@app.route("/api/bot/stop", methods=["POST"])
def stop_bot():
    result = bot_daemon.stop_bot()
    return jsonify(result)


@app.route("/api/bot/run-now", methods=["POST"])
def run_bot_now():
    result = bot_daemon.trigger_cycle_now()
    return jsonify(result)


@app.route("/api/bot/config", methods=["POST"])
def update_bot_config():
    data = request.json or {}
    mode = data.get("mode")
    interval = data.get("interval_minutes")
    result = bot_daemon.update_config(mode=mode, interval_minutes=interval)
    return jsonify(result)


@app.route("/api/bot/logs", methods=["GET"])
def get_bot_logs():
    return jsonify({"success": True, "logs": bot_daemon.logs[:80]})


# -------------------------------------------------------------
# Smart Daily Gadgets Hunter Endpoints
# -------------------------------------------------------------

@app.route("/api/trending", methods=["GET"])
def list_trending():
    query = request.args.get("query", "")
    category = request.args.get("category", "")
    min_virality = int(request.args.get("min_virality", 0))

    if query or category or min_virality > 0:
        gadgets = search_gadgets(query=query, category=category, min_virality=min_virality)
    else:
        gadgets = get_all_gadgets()

    return jsonify({"success": True, "gadgets": gadgets, "count": len(gadgets)})


@app.route("/api/gadget/<gadget_id>", methods=["GET"])
def get_single_gadget(gadget_id):
    gadget = get_gadget_by_id(gadget_id)
    if not gadget:
        return jsonify({"success": False, "error": "Gadget not found"}), 404
    return jsonify({"success": True, "gadget": gadget})


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


# -------------------------------------------------------------
# Shopify Direct Store Operations Endpoints
# -------------------------------------------------------------

@app.route("/api/shopify/import", methods=["POST"])
def import_to_shopify():
    data = request.json or {}
    product_data = data.get("product", {})

    if not product_data.get("title"):
        return jsonify({"success": False, "error": "Product title is required."}), 400

    client = ShopifyClient()
    result = client.create_product(product_data)
    if result.get("success"):
        bot_daemon.log(f"Manual product import: '{product_data.get('title')}' successfully created in Shopify.", level="success")
    return jsonify(result)


@app.route("/api/store/metrics", methods=["GET"])
def get_store_metrics():
    client = ShopifyClient()
    metrics = client.get_store_metrics()
    return jsonify(metrics)


@app.route("/api/store/products", methods=["GET"])
def list_store_products():
    limit = int(request.args.get("limit", 50))
    status = request.args.get("status")
    client = ShopifyClient()
    result = client.get_products(limit=limit, status=status)
    return jsonify(result)


@app.route("/api/store/products/<int:product_id>/status", methods=["POST"])
def update_product_status(product_id):
    data = request.json or {}
    new_status = data.get("status", "draft")
    client = ShopifyClient()
    result = client.update_product_status(product_id, new_status)
    return jsonify(result)


@app.route("/api/store/products/<int:product_id>/price", methods=["POST"])
def update_product_price(product_id):
    data = request.json or {}
    price = float(data.get("price", 0.0))
    compare = float(data.get("compare_at_price", 0.0)) if data.get("compare_at_price") else None
    client = ShopifyClient()
    result = client.update_product_pricing(product_id, price=price, compare_at_price=compare)
    return jsonify(result)


@app.route("/api/store/products/<int:product_id>", methods=["DELETE"])
def delete_store_product(product_id):
    client = ShopifyClient()
    result = client.delete_product(product_id)
    return jsonify(result)


@app.route("/api/store/orders", methods=["GET"])
def list_store_orders():
    client = ShopifyClient()
    result = client.get_orders(limit=25)
    return jsonify(result)


@app.route("/api/store/orders/<int:order_id>/fulfill", methods=["POST"])
def fulfill_store_order(order_id):
    data = request.json or {}
    tracking = data.get("tracking_number", "")
    carrier = data.get("carrier", "USPS")
    client = ShopifyClient()
    result = client.fulfill_order(order_id, tracking_number=tracking, tracking_company=carrier)
    return jsonify(result)


@app.route("/api/store/orders/<int:order_id>/supplier-dispatch", methods=["GET"])
def get_order_supplier_dispatch(order_id):
    client = ShopifyClient()
    orders_res = client.get_orders(limit=100)
    if not orders_res.get("success"):
        return jsonify({"success": False, "error": "Could not fetch orders"}), 500

    target_order = None
    for o in orders_res.get("orders", []):
        if o.get("id") == order_id:
            target_order = o
            break

    if not target_order:
        return jsonify({"success": False, "error": "Order not found"}), 404

    dispatch_info = format_order_for_supplier_dispatch(target_order)
    return jsonify({"success": True, "dispatch": dispatch_info})


# -------------------------------------------------------------
# Supplier Sourcing & Outreach Endpoints
# -------------------------------------------------------------

@app.route("/api/suppliers", methods=["GET"])
def list_suppliers():
    gadgets = get_all_gadgets()
    suppliers_map = {}
    for g in gadgets:
        s_name = g.get("supplier_name", "Shenzhen Direct")
        if s_name not in suppliers_map:
            suppliers_map[s_name] = {
                "name": s_name,
                "platform": g.get("supplier_platform"),
                "rating": g.get("supplier_rating"),
                "shipping_time": g.get("shipping_time"),
                "gadgets": []
            }
        suppliers_map[s_name]["gadgets"].append({
            "id": g["id"],
            "name": g["name"],
            "cost": g["supplier_cost"],
            "link": g.get("supplier_link")
        })

    return jsonify({"success": True, "suppliers": list(suppliers_map.values())})


@app.route("/api/suppliers/inquiry", methods=["POST"])
def create_supplier_inquiry():
    data = request.json or {}
    gadget_id = data.get("gadget_id")
    gadget = get_gadget_by_id(gadget_id) if gadget_id else None

    if not gadget:
        # Use fallback gadget data if custom
        gadget = {
            "id": "custom-gadget",
            "name": data.get("product_name", "Smart Gadget"),
            "supplier_cost": float(data.get("supplier_cost", 15.0)),
            "supplier_link": data.get("supplier_link", ""),
            "supplier_name": data.get("supplier_name", "Factory Supplier")
        }

    inquiry = generate_supplier_inquiry(gadget, store_name=os.getenv("SHOPIFY_STORE_DOMAIN", "Smart Gadget Hub").split(".")[0].title())

    # Log interaction
    log_supplier_interaction({
        "gadget_id": gadget.get("id"),
        "gadget_name": gadget.get("name"),
        "supplier_name": gadget.get("supplier_name"),
        "status": "Inquiry Generated",
        "contact_method": "WhatsApp / Email",
        "inquiry_preview": inquiry.get("subject")
    })

    return jsonify({"success": True, "inquiry": inquiry})


@app.route("/api/suppliers/history", methods=["GET"])
def supplier_history():
    history = get_supplier_interactions()
    return jsonify({"success": True, "history": history})


if __name__ == "__main__":
    port = 5000
    print(f"Starting 24/7 Shopify AI Management System on http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)

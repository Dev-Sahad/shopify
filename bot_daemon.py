"""
24/7 Shopify Autonomous Management Bot Daemon
Runs continuously in background, automates winning smart gadget discovery,
generates AI copy & pricing, uploads to Shopify, drafts supplier inquiries,
and monitors orders 24/7.
"""

import os
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from shopify_client import ShopifyClient
from gadget_hunter import pick_winning_gadget_for_auto_pilot, get_all_gadgets
from ai_enhancer import enhance_product_with_gemini
from supplier_manager import generate_supplier_inquiry, log_supplier_interaction, format_order_for_supplier_dispatch

STATE_FILE = os.path.join(os.path.dirname(__file__), "data", "bot_state.json")

def _ensure_data_dir():
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)


class ShopifyBotDaemon:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ShopifyBotDaemon, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.running = False
        self.mode = "review"  # "autonomous" (auto-publishes as active) or "review" (publishes as draft)
        self.interval_minutes = 360  # Default every 6 hours
        self.last_run: Optional[str] = None
        self.next_run: Optional[str] = None
        self.imported_gadget_ids: List[str] = []
        self.logs: List[Dict[str, Any]] = []
        self.manual_trigger_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

        self._load_state()

        # If it was running when last saved, resume it
        if self.running:
            self._start_thread()

    def _load_state(self):
        _ensure_data_dir()
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.running = data.get("running", False)
                    self.mode = data.get("mode", "review")
                    self.interval_minutes = data.get("interval_minutes", 360)
                    self.last_run = data.get("last_run")
                    self.next_run = data.get("next_run")
                    self.imported_gadget_ids = data.get("imported_gadget_ids", [])
                    self.logs = data.get("logs", [])
            except Exception as e:
                self.log(f"Error loading bot state: {e}", level="warn")

    def _save_state(self):
        _ensure_data_dir()
        try:
            data = {
                "running": self.running,
                "mode": self.mode,
                "interval_minutes": self.interval_minutes,
                "last_run": self.last_run,
                "next_run": self.next_run,
                "imported_gadget_ids": self.imported_gadget_ids,
                "logs": self.logs[:150]  # Keep recent 150 logs
            }
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving bot state: {e}")

    def log(self, message: str, level: str = "info", details: Optional[Dict[str, Any]] = None):
        """Appends a timestamped log to the event feed."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message,
            "details": details or {}
        }
        self.logs.insert(0, entry)
        if len(self.logs) > 200:
            self.logs = self.logs[:200]
        self._save_state()
        print(f"[{entry['timestamp']}] [{level.upper()}] {message}")

    def start_bot(self) -> Dict[str, Any]:
        """Starts the 24/7 bot daemon."""
        if self.running and self.thread and self.thread.is_alive():
            return {"success": True, "message": "24/7 Bot is already active and running."}

        self.running = True
        if not self.next_run:
            self.next_run = (datetime.now() + timedelta(minutes=self.interval_minutes)).isoformat()
        self._save_state()
        self._start_thread()
        self.log("🚀 24/7 Autonomous Shopify Bot started.", level="success")
        return {"success": True, "message": "24/7 Bot successfully started."}

    def stop_bot(self) -> Dict[str, Any]:
        """Pauses the 24/7 bot daemon."""
        self.running = False
        self._save_state()
        self.log("⏸️ 24/7 Autonomous Shopify Bot paused by admin.", level="warn")
        return {"success": True, "message": "24/7 Bot paused."}

    def trigger_cycle_now(self) -> Dict[str, Any]:
        """Manually triggers an immediate execution cycle."""
        self.log("⚡ Instant cycle requested by user. Executing pipeline...", level="info")
        self.manual_trigger_event.set()
        # If thread isn't running, run cycle synchronously in background thread
        if not self.thread or not self.thread.is_alive():
            t = threading.Thread(target=self._run_single_cycle, daemon=True)
            t.start()
        return {"success": True, "message": "Immediate management cycle dispatched."}

    def update_config(self, mode: Optional[str] = None, interval_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Updates runtime configuration."""
        if mode in ["autonomous", "review"]:
            self.mode = mode
        if interval_minutes and interval_minutes >= 5:
            self.interval_minutes = int(interval_minutes)
            self.next_run = (datetime.now() + timedelta(minutes=self.interval_minutes)).isoformat()
        self._save_state()
        self.log(f"⚙️ Bot settings updated: Mode={self.mode}, Interval={self.interval_minutes}m", level="info")
        return {"success": True, "message": "Bot configuration updated."}

    def _start_thread(self):
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.thread.start()

    def _worker_loop(self):
        """Continuous 24/7 daemon loop."""
        self.log("🤖 24/7 Background Watcher thread active.", level="info")
        while self.running:
            try:
                # Check if manual trigger happened
                triggered = self.manual_trigger_event.wait(timeout=15)
                if triggered:
                    self.manual_trigger_event.clear()
                    self._run_single_cycle()
                    continue

                if not self.running:
                    break

                # Check schedule
                now = datetime.now()
                if self.next_run:
                    next_dt = datetime.fromisoformat(self.next_run)
                    if now >= next_dt:
                        self.log(f"⏰ Scheduled cycle interval triggered ({self.interval_minutes}m).", level="info")
                        self._run_single_cycle()
                else:
                    self.next_run = (now + timedelta(minutes=self.interval_minutes)).isoformat()
                    self._save_state()

            except Exception as e:
                self.log(f"Error in bot worker loop: {str(e)}", level="error")
                time.sleep(10)

    def _run_single_cycle(self):
        """Executes a full 24/7 autonomous management cycle."""
        self.last_run = datetime.now().isoformat()
        self.next_run = (datetime.now() + timedelta(minutes=self.interval_minutes)).isoformat()
        self._save_state()

        client = ShopifyClient()
        is_shopify_live = client.is_configured

        self.log("🔍 [Step 1/5] Scanning viral gadgets database for high-converting daily life gadgets...", level="info")

        # Pick winning gadget
        gadget = pick_winning_gadget_for_auto_pilot(self.imported_gadget_ids)
        if not gadget:
            self.log("⚠️ No new gadget candidate available to import.", level="warn")
            return

        gadget_name = gadget.get("name", "Smart Gadget")
        virality = gadget.get("virality_score", 90)
        cost = gadget.get("supplier_cost", 15.0)

        self.log(f"🔥 [Step 2/5] Selected Winner: '{gadget_name}' (Virality Score: {virality}/100, Est Cost: ${cost:.2f})", level="success")

        # AI Copywriting & Optimization
        self.log(f"🧠 [Step 3/5] Generating conversion-optimized copy, specs, and pricing for '{gadget_name}'...", level="info")
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        multiplier = float(os.getenv("DEFAULT_PRICE_MULTIPLIER", "2.5"))

        enhanced = enhance_product_with_gemini(
            raw_title=gadget.get("raw_title", gadget_name),
            raw_description=gadget.get("raw_description", ""),
            supplier_price=cost,
            api_key=gemini_key,
            price_multiplier=multiplier
        )

        status_to_upload = "active" if self.mode == "autonomous" else "draft"

        product_payload = {
            "title": enhanced.get("title", gadget_name),
            "body_html": enhanced.get("body_html", ""),
            "vendor": "Smart Gadget Hub",
            "product_type": gadget.get("category", "Smart Gadgets"),
            "tags": enhanced.get("tags") or gadget.get("tags", "Smart Gadgets, Trending"),
            "price": enhanced.get("price", gadget.get("suggested_retail", 39.99)),
            "compare_at_price": enhanced.get("compare_at_price", gadget.get("compare_at_price", 59.99)),
            "status": status_to_upload,
            "images": gadget.get("images", []),
            "sku": f"SG-{gadget['id'][:8].upper()}"
        }

        # Step 4: Upload to Shopify
        if is_shopify_live:
            self.log(f"🛍️ [Step 4/5] Pushing '{enhanced['title']}' to Shopify as {status_to_upload.upper()}...", level="info")
            res = client.create_product(product_payload)
            if res.get("success"):
                prod_id = res.get("product_id")
                admin_link = res.get("admin_url")
                self.log(f"✅ Successfully published '{enhanced['title']}' to Shopify! [ID: {prod_id}]", level="success", details={"admin_url": admin_link})
                self.imported_gadget_ids.append(gadget["id"])
            else:
                self.log(f"❌ Failed to push product to Shopify: {res.get('error')}", level="error")
        else:
            self.log(f"ℹ️ [Step 4/5] Shopify credentials not connected yet. Product '{enhanced['title']}' prepared and queued for 1-click import once connected.", level="warn")
            self.imported_gadget_ids.append(gadget["id"])

        # Step 5: Supplier Outreach Generation & Logging
        self.log(f"🏭 [Step 5/5] Generating B2B supplier outreach agreement for '{gadget_name}'...", level="info")
        inquiry = generate_supplier_inquiry(gadget, store_name="Smart Gadget Hub")
        log_supplier_interaction({
            "gadget_id": gadget["id"],
            "gadget_name": gadget_name,
            "supplier_name": gadget.get("supplier_name"),
            "status": "Inquiry Generated / Ready to Dispatch",
            "contact_method": "WhatsApp / Email",
            "inquiry_preview": inquiry.get("subject")
        })
        self.log(f"📬 Supplier outreach ready for {gadget.get('supplier_name')} (WhatsApp & Email drafted).", level="success")

        # Step 6: Scan store orders & health
        if is_shopify_live:
            orders_res = client.get_orders(limit=10)
            if orders_res.get("success"):
                unfulfilled = [o for o in orders_res.get("orders", []) if o.get("fulfillment_status") in [None, "unfulfilled"]]
                if unfulfilled:
                    self.log(f"📦 Detected {len(unfulfilled)} unfulfilled customer order(s) in Shopify. Generating dropship slips...", level="info")
                    for ord_item in unfulfilled[:3]:
                        slip = format_order_for_supplier_dispatch(ord_item)
                        self.log(f"📋 Dispatch slip prepared for order {slip['order_name']} ({slip['recipient']}, {slip['country']})", level="info")

        self.log(f"🎉 24/7 Management cycle completed. Next scheduled check: {self.next_run}", level="success")
        self._save_state()

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive status for API and UI."""
        return {
            "running": self.running,
            "mode": self.mode,
            "interval_minutes": self.interval_minutes,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "total_imported_count": len(self.imported_gadget_ids),
            "imported_ids": self.imported_gadget_ids,
            "recent_logs": self.logs[:50]
        }


# Global singleton daemon instance
bot_daemon = ShopifyBotDaemon()


# 🤖 24/7 Smart Gadget AI Dropshipping Store Manager for Shopify

An autonomous 24/7 AI-powered Shopify management system tailored specifically for **Smart Daily Life Gadgets**. It hunts viral, high-margin problem-solving gadgets, crafts conversion-optimized product copy and pricing, automatically imports them to Shopify, negotiates with dropshipping suppliers, monitors incoming customer orders, and manages your full store on autopilot.

---

## 🌟 Key Capabilities

### 1. 🤖 24/7 Autonomous Background Auto-Pilot
- **Non-stop background daemon**: Hunts, writes copy, pushes products, and monitors orders continuously on your chosen schedule (every 30m, 1h, 6h, 12h, or 24h).
- **Two operational modes**:
  - **Full Auto**: Immediately publishes winning gadgets as **Active** products to your live Shopify storefront.
  - **Review Mode (Copilot)**: Pushes winning gadgets as **Drafts** for your 1-click review and approval.
- **Live Decision Stream**: Real-time terminal in the dashboard displaying every algorithmic action, trend score, copy generation step, and upload status.
- **Instant Cycle Trigger**: 1-click manual trigger to run a complete cycle immediately.

### 2. 🔥 Winning Smart Daily Life Gadgets Hunter
- Pre-vetted library of high-converting smart gadgets across key daily categories:
  - **Smart Home & Bedroom**: Anti-Gravity Water Droplet Humidifiers, Magnetic Levitating 3D Moon Lamps, Touchless Sensor Cans.
  - **Smart Kitchen & Dining**: Cordless Food & Garlic Choppers, Automatic Electric Smart Wine Vacuum Preservers.
  - **Tech Desk & Content Creation**: 360° AI Face-Tracking Camera Mounts, 3-in-1 Foldable Magnetic Travel Chargers.
  - **Smart Cleaning & Hygiene**: 360° High-Frequency Ultrasonic Cleaners, Cordless High-Power Electric Spin Scrubbers.
  - **Smart Health & Wellness**: EMS Pulse Heated Neck Massagers, Heated Air Compression Eye Massagers.
  - **Everyday Carry (EDC)**: Wireless Pocket Inkless Thermal Printers.
- **Algorithmic Virality Score (89–97/100)**: Evaluates problem-solving factor, TikTok/Reels visual appeal, and profit margin potential.
- **URL Scraper**: Paste any link from AliExpress, CJ Dropshipping, or Amazon to extract specs and images.

### 3. 🧠 AI Copywriter & Dynamic Pricing Formula
- Powered by **Google Gemini** (with built-in offline smart copywriting fallback).
- Removes messy manufacturer spam and keyword stuffing.
- Generates customer benefit bullet points, sleek specifications tables, FAQs, and a 30-Day Money-Back Guarantee.
- Dynamic pricing engine: converts wholesale cost $\rightarrow$ high-converting `$XX.99` retail price with a 40–50% compare-at discount anchor (e.g. \$16.80 cost $\rightarrow$ \$49.99 retail, \$79.99 compare-at).

### 4. 🏭 B2B Supplier Outreach & Order Fulfillment
- **Automated Supplier Negotiation Generator**:
  - Dual-language outreach (**English & Chinese**) tailored for AliExpress and factory direct suppliers (Shenzhen, Yiwu, Ningbo).
  - Negotiates blind dropshipping (no Chinese leaflets/invoices), 24–48h dispatch, VIP volume discounts, and access to unwatermarked raw video clips for ad creatives.
  - 1-Click WhatsApp web launcher (`https://wa.me/?text=...`) and instant copy.
- **Order Dropship Dispatch Slip**: Converts unfulfilled Shopify customer orders into standardized dropshipping fulfillment slips (CSV row & formatted message) ready for supplier dispatch.

### 5. 🏪 Full Shopify Store Manager
- **Live Storefront Synchronization**: View all products currently in your Shopify catalog with image, pricing, SKU, and status.
- **1-Click Status Toggle**: Switch products between `Draft` and `Active` with one click.
- **Order Monitoring**: Tracks recent orders, revenue, unfulfilled customer orders, and customer shipping destinations.
- **Store KPI Dashboard**: Live tracking of store revenue, active catalog count, and pending orders.

---

## 🛠️ Quick Setup Guide

### 1. Configure Shopify Admin API (Takes 2 minutes)
1. Go to your **Shopify Admin** dashboard.
2. Click **Settings** (bottom left) $\rightarrow$ **Apps and sales channels**.
3. Click **Develop apps** (enable custom app development if prompted).
4. Click **Create an app** and name it `24/7 Smart Gadget Bot`.
5. Under **Configuration**, click **Configure Admin API integration**.
6. Check the following scopes under **Products** & **Orders**:
   - `write_products`, `read_products`
   - `write_orders`, `read_orders`
   - `write_fulfillments`, `read_fulfillments`
7. Click **Save**, then click **Install app**.
8. Click **Reveal token once** and copy your token (`shpat_...`).

### 2. Configure Google Gemini API (Free)
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Click **Create API Key**.
3. Enter your key in the dashboard settings or `.env` file. *(The bot includes an offline copywriter fallback if no key is entered.)*

---

## 🚀 How to Launch the System

### Option A: 1-Click Batch Launcher
Double-click `run.bat` in this folder.

### Option B: Terminal Command
```powershell
& "C:\Users\sahad\AppData\Local\Python\bin\python.exe" app.py
```

Then open your browser at:
👉 **`http://localhost:5000`**

Click **"Start 24/7 Bot"** to put the autonomous management engine into action!

---

## 📁 Architecture Overview

```
shopify/
├── app.py                 # Flask server & unified REST API
├── bot_daemon.py          # 24/7 Background daemon & scheduler
├── gadget_hunter.py       # Winning smart daily life gadgets & virality scoring
├── supplier_manager.py    # Supplier directory, B2B negotiations & order slips
├── shopify_client.py      # Shopify Admin REST API client (products, orders, metrics)
├── ai_enhancer.py         # Gemini AI copywriter + smart offline fallback
├── extractor.py           # Web scraper for custom supplier links
├── trending_gadgets.py    # Backward-compatible catalog wrapper
├── templates/
│   └── index.html         # Modern 24/7 Control Center Web Dashboard
├── data/
│   ├── bot_state.json     # Persistent bot operational state & logs
│   └── supplier_interactions.json # Supplier contact history
├── run.bat                # 1-Click launcher
├── requirements.txt       # Dependencies
└── .env                   # Configuration & API credentials
```

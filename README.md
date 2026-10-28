# 🚀 Smart Gadget AI Dropshipping Assistant for Shopify

An intelligent dropshipping companion designed specifically for **Smart & Trending Gadgets**. It finds viral gadgets, extracts specifications, uses AI to write high-converting sales copy, calculates optimal profit margins, and imports products directly into your Shopify store with 1 click.

---

## ✨ Features

- **🔥 Pre-Vetted Viral Gadget Library**: Comes loaded with winning smart gadgets ready to import (Anti-Gravity Humidifiers, Magnetic Levitating Lamps, Ultrasonic Cleaners, Smart Neck Massagers, etc.).
- **🌐 1-Click Product URL Extractor**: Paste any product page link (AliExpress, CJ Dropshipping, Amazon, etc.) to automatically extract titles, specs, and images.
- **🧠 AI Copywriter (Google Gemini)**:
  - Eliminates messy manufacturer keyword spam.
  - Crafts catchy, brandable product titles.
  - Generates benefit-driven bullet points, specifications tables, FAQs, and 30-day money-back guarantee sections.
- **💰 Smart Profit Margin Formula**:
  - Automatically calculates 2.0x–3.5x pricing ending in `.99` (e.g. $14 cost $\rightarrow$ $39.99 retail, $59.99 compare-at price).
- **🛍️ Direct Shopify Admin API Sync**:
  - Pushes images, tags, pricing, and formatted descriptions directly into your Shopify catalog as a **Draft** (safe for review) or **Active** product.

---

## 🛠️ Quick Setup Guide

### 1. How to Get Your Shopify Admin API Token (Takes 2 minutes)
1. Log in to your **Shopify Admin** dashboard.
2. Go to **Settings** (bottom left) $\rightarrow$ **Apps and sales channels**.
3. Click **Develop apps** (enable custom app development if prompted).
4. Click **Create an app** and name it `AI Gadget Importer`.
5. Under **Configuration**, click **Configure Admin API integration**.
6. Check the following scopes under **Products**:
   - `write_products`
   - `read_products`
7. Click **Save**, then click **Install app**.
8. Click **Reveal token once** and copy your token (it starts with `shpat_...`).
9. Note your store domain (e.g. `your-store-name.myshopify.com`).

### 2. How to Get a Free Google Gemini API Key (Optional but recommended)
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Click **Create API Key**.
3. Copy your key. *(The tool includes an intelligent offline copywriting engine if you don't have a key right away!)*

---

## 🚀 How to Run the App

### Option A: Double-Click
Simply double-click the `run.bat` file in this folder.

### Option B: Terminal Command
```bash
& "C:\Users\sahad\AppData\Local\Python\bin\python.exe" app.py
```

Then open your browser at:
👉 **`http://localhost:5000`**

---

## 📁 Project Structure

```
shopify-ai-importer/
├── app.py                # Main Flask web application & REST API
├── shopify_client.py     # Shopify Admin API client
├── ai_enhancer.py        # Gemini AI copywriter + smart offline fallback
├── extractor.py          # Web scraper & metadata extractor
├── trending_gadgets.py   # Catalog of viral smart gadgets
├── templates/
│   └── index.html        # Interactive web dashboard
├── run.bat               # 1-click launcher
├── requirements.txt      # Python dependencies
└── .env                  # Store credentials & configuration
```


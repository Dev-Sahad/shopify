"""
AI Copywriter & Product Enhancer for Smart Gadgets
Uses Google Gemini API to generate high-converting product pages,
with a smart offline fallback so the app works seamlessly even without an API key.
"""

import os
import json
import re
from typing import Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def calculate_smart_pricing(cost_price: float, multiplier: float = 2.5) -> Dict[str, str]:
    """
    Calculates consumer-friendly dropshipping prices ending in .99.
    E.g. $12 cost * 2.5 = $30 -> rounded to $29.99.
    Compare-at price provides a ~40% discount anchor.
    """
    if cost_price <= 0:
        cost_price = 15.0

    target = cost_price * multiplier
    # Round to nearest .99
    suggested_val = max(19.99, round(target) - 0.01)
    # If rounded landed on .00 or unexpected, force .99
    suggested_val = float(f"{int(suggested_val)}.99")

    # Compare at price is roughly 1.4x - 1.6x the selling price
    compare_val = float(f"{int(suggested_val * 1.5)}.99")

    return {
        "price": f"{suggested_val:.2f}",
        "compare_at_price": f"{compare_val:.2f}",
        "profit_margin": f"{(suggested_val - cost_price):.2f}"
    }


def generate_fallback_copy(raw_title: str, supplier_price: float, features_hint: str = "") -> Dict[str, Any]:
    """
    Generates high-converting, professional product copy offline
    when Gemini API key is not configured or offline.
    """
    # Clean up spammy supplier keywords
    cleaned_title = re.sub(r"(?i)\b(202[0-9]|new|hot sale|wholesale|drop shipping|dropshipping|aliexpress|free shipping|factory price|for|with|and)\b", " ", raw_title)
    cleaned_title = re.sub(r"\s+", " ", cleaned_title).strip().title()
    words = cleaned_title.split()
    if len(words) > 6:
        cleaned_title = " ".join(words[:6])
    if not cleaned_title:
        cleaned_title = "Smart Next-Gen Gadget"

    pricing = calculate_smart_pricing(supplier_price)

    # Rich Shopify body HTML
    body_html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1a1a1a;">
  <p style="font-size: 1.15em; font-weight: 500; color: #2563eb; margin-bottom: 15px;">
    🚀 <strong>Upgrade Your Everyday Routine with the {cleaned_title}</strong>
  </p>
  
  <p>
    Tired of outdated, clunky gadgets that complicate your day? Meet the <strong>{cleaned_title}</strong>—engineered with precision tech to give you smart, seamless performance right when you need it most.
  </p>

  <h3 style="margin-top: 25px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">✨ Why You'll Love It:</h3>
  <ul style="padding-left: 20px;">
    <li><strong>Smart Automation:</strong> Intuitive controls engineered for hands-free, effortless convenience.</li>
    <li><strong>Sleek &amp; Modern Design:</strong> Compact, aerospace-grade aesthetic that elevates your workspace or home.</li>
    <li><strong>Long-Lasting Performance:</strong> High-efficiency energy management for uninterrupted daily use.</li>
    <li><strong>Plug &amp; Play Simplicity:</strong> No complicated setup required—ready to elevate your lifestyle right out of the box.</li>
  </ul>

  <h3 style="margin-top: 25px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">📋 Specifications:</h3>
  <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.95em;">
    <tr style="background-color: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: 600;">Category</td><td style="padding: 8px; border: 1px solid #e2e8f0;">Smart Gadgets &amp; Tech</td></tr>
    <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: 600;">Compatibility</td><td style="padding: 8px; border: 1px solid #e2e8f0;">Universal / USB Powered</td></tr>
    <tr style="background-color: #f8fafc;"><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: 600;">Materials</td><td style="padding: 8px; border: 1px solid #e2e8f0;">Premium ABS &amp; Eco-friendly Alloy</td></tr>
    <tr><td style="padding: 8px; border: 1px solid #e2e8f0; font-weight: 600;">Warranty</td><td style="padding: 8px; border: 1px solid #e2e8f0;">1-Year Free Replacement Guarantee</td></tr>
  </table>

  <h3 style="margin-top: 25px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px;">🛡️ Our Risk-Free Guarantee</h3>
  <p>
    We believe you'll adore this gadget as much as we do. That's why we back every order with a <strong>30-Day Money-Back Guarantee</strong> and 24/7 dedicated customer support.
  </p>
</div>
"""

    return {
        "title": cleaned_title,
        "tagline": "The smarter, faster way to elevate your daily routine.",
        "price": pricing["price"],
        "compare_at_price": pricing["compare_at_price"],
        "tags": "Smart Gadgets, Trending, TikTok Made Me Buy It, Home Tech, Best Sellers",
        "product_type": "Smart Gadgets",
        "vendor": "Smart Gadget Hub",
        "body_html": body_html.strip(),
        "ai_powered": False
    }


def enhance_product_with_gemini(
    raw_title: str,
    raw_description: str,
    supplier_price: float,
    api_key: Optional[str] = None,
    price_multiplier: float = 2.5
) -> Dict[str, Any]:
    """
    Uses Gemini API to create ultra high-converting copy, clean titles,
    and structured HTML formatted for Shopify.
    """
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    pricing = calculate_smart_pricing(supplier_price, price_multiplier)

    if not key or not GENAI_AVAILABLE:
        # Fallback to local intelligent copywriter
        return generate_fallback_copy(raw_title, supplier_price)

    prompt = f"""
You are an elite e-commerce copywriter specializing in viral Smart Gadgets dropshipping (products that go viral on TikTok, Instagram Reels, and YouTube Shorts).

Transform this raw supplier product info into a high-converting, professional Shopify product listing.

Raw Product Title: {raw_title}
Raw Product Description / Features: {raw_description}
Supplier Cost Price: ${supplier_price:.2f}
Suggested Retail Price: ${pricing['price']}
Compare-At Price: ${pricing['compare_at_price']}

Requirements:
1. "title": Create a catchy, memorable, brandable gadget name (3 to 6 words max). Strip out all keyword stuffing like "2024 New Hot Sale Dropshipping Wholesale".
2. "tagline": A 1-sentence punchy hook that highlights the #1 transformation.
3. "features": List of 4-5 bullet points with relevant emojis detailing key benefits (not just technical features—explain why the customer cares).
4. "tags": Comma-separated tags suitable for Shopify (e.g., "Smart Gadgets, Trending, Viral Tech, Home Office").
5. "body_html": Write a stunning, modern HTML product description using clean inline CSS and semantic HTML (headers <h3>, bullet points <ul>, a 2-column specifications <table>, and a "30-Day Money Back Guarantee" section). Do NOT include markdown code blocks inside body_html—return raw HTML string.

Return ONLY a valid JSON object with these exact keys:
{{
  "title": "string",
  "tagline": "string",
  "tags": "string",
  "features": ["string", "string"],
  "body_html": "string"
}}
"""

    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        
        return {
            "title": data.get("title", raw_title),
            "tagline": data.get("tagline", ""),
            "price": pricing["price"],
            "compare_at_price": pricing["compare_at_price"],
            "tags": data.get("tags", "Smart Gadgets, Trending Tech"),
            "product_type": "Smart Gadgets",
            "vendor": "Smart Gadget Hub",
            "body_html": data.get("body_html", ""),
            "ai_powered": True
        }
    except Exception as e:
        print(f"Gemini API call failed, using fallback copy: {e}")
        fallback = generate_fallback_copy(raw_title, supplier_price)
        fallback["error_note"] = f"AI fallback used: {str(e)}"
        return fallback

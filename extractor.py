"""
Product Web Extractor
Fetches metadata, title, images, and descriptions from product URLs
using OpenGraph, Schema.org (JSON-LD), and HTML parsing.
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def extract_from_url(url: str) -> Dict[str, Any]:
    """
    Extracts product info, images, and pricing hints from a product link.
    """
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        return {
            "success": False,
            "error": f"Could not fetch product page ({str(e)}). Please verify the link or enter details manually."
        }

    soup = BeautifulSoup(html, "html.parser")

    # 1. Try JSON-LD (Schema.org Product)
    title = ""
    description = ""
    images: List[str] = []
    price: float = 15.0  # sensible default for smart gadgets

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                data = data[0]
            if isinstance(data, dict):
                # Search for Product type or nested
                if data.get("@type") == "Product" or "name" in data:
                    title = data.get("name", title)
                    description = data.get("description", description)
                    img_data = data.get("image", [])
                    if isinstance(img_data, list):
                        images.extend(img_data)
                    elif isinstance(img_data, str):
                        images.append(img_data)

                    # Look for offers/price
                    offers = data.get("offers")
                    if isinstance(offers, dict) and "price" in offers:
                        try:
                            price = float(offers["price"])
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(offers, list) and len(offers) > 0 and "price" in offers[0]:
                        try:
                            price = float(offers[0]["price"])
                        except (ValueError, TypeError):
                            pass
                    break
        except Exception:
            continue

    # 2. OpenGraph Meta Fallbacks
    if not title:
        og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
        if og_title and og_title.get("content"):
            title = og_title["content"]
        elif soup.title and soup.title.string:
            title = soup.title.string.strip()

    if not description:
        og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if og_desc and og_desc.get("content"):
            description = og_desc["content"]

    og_image = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
    if og_image and og_image.get("content"):
        img_url = og_image["content"]
        if img_url not in images:
            images.insert(0, img_url)

    # 3. Collect prominent images if none found
    if not images:
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and (src.startswith("http://") or src.startswith("https://")):
                # Filter out small tracking icons/logos
                if not any(bad in src.lower() for bad in ["logo", "icon", "badge", "avatar", "1x1", "pixel"]):
                    images.append(src)
                if len(images) >= 4:
                    break

    # Clean extracted title
    title = re.sub(r"\s+", " ", title).strip()
    # Strip site name suffixes like " - AliExpress", " | Amazon"
    title = re.split(r"\s*[-|–]\s*(?:AliExpress|Amazon|eBay|Walmart|Shopify)\b", title, flags=re.IGNORECASE)[0]

    return {
        "success": True,
        "title": title or "Smart Gadget",
        "description": description or "Innovative next-generation smart gadget designed for everyday convenience.",
        "images": images[:6],
        "supplier_price": price,
        "source_url": url
    }


"""
Shopify Admin API Client for Smart Gadget Product Importer
Handles authentication, connection tests, and draft/active product creation.
"""

import os
import requests
from typing import Dict, Any, Optional

class ShopifyClient:
    def __init__(self, store_domain: Optional[str] = None, access_token: Optional[str] = None, api_version: str = "2024-10"):
        raw_domain = store_domain or os.getenv("SHOPIFY_STORE_DOMAIN", "")
        self.store_domain = self._normalize_domain(raw_domain)
        self.access_token = access_token or os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN", "")
        self.api_version = api_version or os.getenv("SHOPIFY_API_VERSION", "2024-10")

    def _normalize_domain(self, domain: str) -> str:
        """Sanitizes store domain input."""
        domain = domain.strip().lower()
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        if domain and not domain.endswith(".myshopify.com"):
            domain = f"{domain}.myshopify.com"
        return domain

    @property
    def is_configured(self) -> bool:
        return bool(self.store_domain and self.access_token and self.access_token.startswith("shpat_"))

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }

    def test_connection(self) -> Dict[str, Any]:
        """Tests the connection to Shopify Admin API and retrieves store info."""
        if not self.store_domain or not self.access_token:
            return {
                "success": False,
                "error": "Store domain and Admin API Access Token (shpat_...) are required."
            }

        url = f"https://{self.store_domain}/admin/api/{self.api_version}/shop.json"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                shop_info = response.json().get("shop", {})
                return {
                    "success": True,
                    "shop_name": shop_info.get("name"),
                    "domain": shop_info.get("myshopify_domain"),
                    "currency": shop_info.get("currency", "USD"),
                    "email": shop_info.get("email"),
                    "message": f"Successfully connected to {shop_info.get('name')} ({shop_info.get('currency')})"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed (401 Unauthorized). Please check your Admin API Access Token."
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Store not found (404). Check if domain '{self.store_domain}' is spelled correctly."
                }
            else:
                return {
                    "success": False,
                    "error": f"Shopify returned error {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error connecting to Shopify: {str(e)}"
            }

    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a product in Shopify via Admin REST API.
        Default status is 'draft' for safety so the user can review before publishing.
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Shopify credentials are not fully configured. Please configure your store in settings."
            }

        url = f"https://{self.store_domain}/admin/api/{self.api_version}/products.json"

        # Build variants payload
        variants = []
        variant_price = str(product_data.get("price", "29.99"))
        compare_price = product_data.get("compare_at_price")

        variant_obj: Dict[str, Any] = {
            "price": variant_price,
            "requires_shipping": True
        }
        if compare_price:
            variant_obj["compare_at_price"] = str(compare_price)
        if product_data.get("sku"):
            variant_obj["sku"] = str(product_data.get("sku"))

        variants.append(variant_obj)

        # Build images payload
        images = []
        raw_images = product_data.get("images", [])
        if isinstance(raw_images, list):
            for img in raw_images:
                if isinstance(img, str) and (img.startswith("http://") or img.startswith("https://")):
                    images.append({"src": img})
                elif isinstance(img, dict) and "src" in img:
                    images.append({"src": img["src"]})

        payload = {
            "product": {
                "title": product_data.get("title", "Smart Gadget"),
                "body_html": product_data.get("body_html", ""),
                "vendor": product_data.get("vendor", "Smart Gadget Hub"),
                "product_type": product_data.get("product_type", "Smart Gadgets"),
                "tags": product_data.get("tags", "Smart Gadgets, Trending"),
                "status": product_data.get("status", "draft"),
                "variants": variants,
                "images": images
            }
        }

        try:
            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=20)
            if response.status_code in [200, 201]:
                created = response.json().get("product", {})
                prod_id = created.get("id")
                admin_url = f"https://{self.store_domain}/admin/products/{prod_id}"
                return {
                    "success": True,
                    "product_id": prod_id,
                    "title": created.get("title"),
                    "status": created.get("status"),
                    "admin_url": admin_url,
                    "message": f"Product successfully imported as {created.get('status').upper()}!"
                }
            else:
                return {
                    "success": False,
                    "error": f"Shopify Error {response.status_code}: {response.text}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to push product to Shopify: {str(e)}"
            }


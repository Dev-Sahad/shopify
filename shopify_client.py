"""
Shopify Admin API Client for 24/7 Smart Gadget Store Management
Handles complete lifecycle: authentication, product imports, live store sync,
inventory status, pricing management, and order fulfillment.
"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH)


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
        # Only append .myshopify.com if there is no domain extension (e.g. 'my-store' -> 'my-store.myshopify.com')
        if domain and "." not in domain:
            domain = f"{domain}.myshopify.com"
        return domain

    @property
    def is_configured(self) -> bool:
        return bool(self.store_domain and self.access_token and (self.access_token.startswith("shpat_") or len(self.access_token) > 20))

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }

    def _base_url(self) -> str:
        return f"https://{self.store_domain}/admin/api/{self.api_version}"

    def test_connection(self) -> Dict[str, Any]:
        """Tests the connection to Shopify Admin API and retrieves store info."""
        if not self.store_domain or not self.access_token:
            return {
                "success": False,
                "error": "Store domain and Admin API Access Token (shpat_...) are required."
            }

        url = f"{self._base_url()}/shop.json"
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
                    "plan_name": shop_info.get("plan_name", "Shopify Store"),
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
        Can be published as 'draft' or 'active'.
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Shopify credentials are not fully configured. Please configure your store in settings."
            }

        url = f"{self._base_url()}/products.json"

        # Build variants payload
        variants = []
        variant_price = str(product_data.get("price", "29.99"))
        compare_price = product_data.get("compare_at_price")
        sku = product_data.get("sku") or f"SMART-{product_data.get('id', 'GADGET')[:6].upper()}"

        variant_obj: Dict[str, Any] = {
            "price": variant_price,
            "requires_shipping": True,
            "sku": sku,
            "inventory_management": "shopify",
            "inventory_policy": "continue"
        }
        if compare_price:
            variant_obj["compare_at_price"] = str(compare_price)

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
                "tags": product_data.get("tags", "Smart Gadgets, Daily Life, Trending"),
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

    def get_products(self, limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves products from the store with prices, images, and status.
        """
        if not self.is_configured:
            return {"success": False, "error": "Shopify credentials not configured", "products": []}

        url = f"{self._base_url()}/products.json?limit={limit}"
        if status:
            url += f"&status={status}"

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=15)
            if response.status_code == 200:
                raw_products = response.json().get("products", [])
                cleaned_products = []
                for p in raw_products:
                    first_variant = p.get("variants", [{}])[0] if p.get("variants") else {}
                    first_img = p.get("images", [{}])[0].get("src") if p.get("images") else None
                    cleaned_products.append({
                        "id": p.get("id"),
                        "title": p.get("title"),
                        "status": p.get("status"),
                        "vendor": p.get("vendor"),
                        "product_type": p.get("product_type"),
                        "price": first_variant.get("price", "0.00"),
                        "compare_at_price": first_variant.get("compare_at_price"),
                        "inventory_quantity": first_variant.get("inventory_quantity", 0),
                        "sku": first_variant.get("sku", ""),
                        "image": first_img,
                        "created_at": p.get("created_at"),
                        "admin_url": f"https://{self.store_domain}/admin/products/{p.get('id')}"
                    })
                return {"success": True, "products": cleaned_products, "count": len(cleaned_products)}
            else:
                return {"success": False, "error": f"Shopify Error {response.status_code}: {response.text}", "products": []}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}", "products": []}

    def update_product_status(self, product_id: int, new_status: str) -> Dict[str, Any]:
        """
        Updates product status: 'active', 'draft', or 'archived'.
        """
        if not self.is_configured:
            return {"success": False, "error": "Shopify credentials not configured"}

        url = f"{self._base_url()}/products/{product_id}.json"
        payload = {"product": {"id": product_id, "status": new_status}}
        try:
            response = requests.put(url, headers=self._get_headers(), json=payload, timeout=12)
            if response.status_code == 200:
                prod = response.json().get("product", {})
                return {"success": True, "status": prod.get("status"), "message": f"Product status set to {new_status.upper()}"}
            else:
                return {"success": False, "error": f"Shopify Error {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_product_pricing(self, product_id: int, price: float, compare_at_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Updates product variant pricing.
        """
        if not self.is_configured:
            return {"success": False, "error": "Shopify credentials not configured"}

        # Fetch product to get variant ID
        url_get = f"{self._base_url()}/products/{product_id}.json"
        try:
            resp = requests.get(url_get, headers=self._get_headers(), timeout=12)
            if resp.status_code != 200:
                return {"success": False, "error": f"Could not find product {product_id}"}
            product = resp.json().get("product", {})
            variants = product.get("variants", [])
            if not variants:
                return {"success": False, "error": "Product has no variants to price"}

            variant_id = variants[0]["id"]
            var_url = f"{self._base_url()}/variants/{variant_id}.json"
            var_payload: Dict[str, Any] = {"variant": {"id": variant_id, "price": f"{price:.2f}"}}
            if compare_at_price:
                var_payload["variant"]["compare_at_price"] = f"{compare_at_price:.2f}"

            var_resp = requests.put(var_url, headers=self._get_headers(), json=var_payload, timeout=12)
            if var_resp.status_code == 200:
                return {"success": True, "message": f"Updated price to ${price:.2f}"}
            else:
                return {"success": False, "error": f"Error updating price: {var_resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Deletes a product from Shopify."""
        if not self.is_configured:
            return {"success": False, "error": "Shopify credentials not configured"}

        url = f"{self._base_url()}/products/{product_id}.json"
        try:
            resp = requests.delete(url, headers=self._get_headers(), timeout=12)
            if resp.status_code in [200, 204]:
                return {"success": True, "message": "Product deleted successfully."}
            return {"success": False, "error": f"Failed to delete: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_orders(self, status: str = "any", limit: int = 25) -> Dict[str, Any]:
        """
        Retrieves store orders, line items, and fulfillment status.
        """
        if not self.is_configured:
            return {"success": False, "error": "Shopify credentials not configured", "orders": []}

        url = f"{self._base_url()}/orders.json?status={status}&limit={limit}"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=15)
            if response.status_code == 200:
                raw_orders = response.json().get("orders", [])
                formatted = []
                for o in raw_orders:
                    formatted.append({
                        "id": o.get("id"),
                        "name": o.get("name"),
                        "total_price": o.get("total_price"),
                        "currency": o.get("currency", "USD"),
                        "financial_status": o.get("financial_status"),
                        "fulfillment_status": o.get("fulfillment_status") or "unfulfilled",
                        "created_at": o.get("created_at"),
                        "customer": o.get("customer", {}),
                        "shipping_address": o.get("shipping_address", {}),
                        "line_items": o.get("line_items", [])
                    })
                return {"success": True, "orders": formatted, "count": len(formatted)}
            else:
                return {"success": False, "error": f"Shopify Error {response.status_code}: {response.text}", "orders": []}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}", "orders": []}

    def fulfill_order(self, order_id: int, tracking_number: str = "", tracking_company: str = "USPS") -> Dict[str, Any]:
        """
        Marks an order as fulfilled and adds tracking information.
        """
        if not self.is_configured:
            return {"success": False, "error": "Shopify credentials not configured"}

        url = f"{self._base_url()}/orders/{order_id}/fulfillments.json"
        payload = {
            "fulfillment": {
                "notify_customer": True,
                "tracking_number": tracking_number,
                "tracking_company": tracking_company
            }
        }
        try:
            resp = requests.post(url, headers=self._get_headers(), json=payload, timeout=15)
            if resp.status_code in [200, 201]:
                return {"success": True, "message": "Order fulfilled and tracking dispatched to customer!"}
            else:
                return {"success": False, "error": f"Fulfillment error: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_store_metrics(self) -> Dict[str, Any]:
        """
        Calculates store KPIs: active/draft products count, unfulfilled orders, estimated revenue.
        """
        if not self.is_configured:
            return {
                "success": False,
                "connected": False,
                "total_products": 0,
                "active_products": 0,
                "draft_products": 0,
                "total_orders": 0,
                "unfulfilled_orders": 0,
                "total_revenue": 0.0
            }

        products_res = self.get_products(limit=100)
        orders_res = self.get_orders(limit=100)

        products = products_res.get("products", []) if products_res.get("success") else []
        orders = orders_res.get("orders", []) if orders_res.get("success") else []

        active_count = sum(1 for p in products if p.get("status") == "active")
        draft_count = sum(1 for p in products if p.get("status") == "draft")

        unfulfilled_count = sum(1 for o in orders if o.get("fulfillment_status") in [None, "unfulfilled", "partial"])
        total_rev = sum(float(o.get("total_price", 0)) for o in orders if o.get("financial_status") in ["paid", "partially_paid"])

        return {
            "success": True,
            "connected": True,
            "store_domain": self.store_domain,
            "total_products": len(products),
            "active_products": active_count,
            "draft_products": draft_count,
            "total_orders": len(orders),
            "unfulfilled_orders": unfulfilled_count,
            "total_revenue": round(total_rev, 2)
        }

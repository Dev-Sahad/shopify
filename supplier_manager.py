"""
Supplier Communication & Dropship Management Module
Automates supplier inquiries, negotiations, pricing agreements,
and order dispatch formatting for winning smart gadgets.
"""

import os
import json
import urllib.parse
from typing import Dict, Any, List, Optional
from datetime import datetime

SUPPLIERS_LOG_FILE = os.path.join(os.path.dirname(__file__), "data", "supplier_interactions.json")

def _ensure_data_dir():
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)


def get_supplier_interactions() -> List[Dict[str, Any]]:
    """Loads all logged supplier interactions."""
    _ensure_data_dir()
    if not os.path.exists(SUPPLIERS_LOG_FILE):
        return []
    try:
        with open(SUPPLIERS_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def log_supplier_interaction(record: Dict[str, Any]) -> None:
    """Logs an outreach, quote or agreement with a supplier."""
    _ensure_data_dir()
    history = get_supplier_interactions()
    record["timestamp"] = datetime.now().isoformat()
    history.insert(0, record)
    # Keep last 100
    with open(SUPPLIERS_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:100], f, indent=2)


def generate_supplier_inquiry(gadget: Dict[str, Any], store_name: str = "Smart Gadget Hub") -> Dict[str, Any]:
    """
    Generates high-converting, professional B2B supplier outreach messages
    in both English and Chinese for AliExpress, CJ, or factory suppliers.
    """
    product_name = gadget.get("name") or gadget.get("raw_title", "Smart Gadget")
    target_cost = gadget.get("supplier_cost", 15.0)

    # 1. Professional English Inquiry
    message_en = f"""Hello Supplier Sales Team,

I hope this message finds you well.

My name is the Purchasing Director for {store_name}, an established smart consumer electronics and lifestyle gadget e-commerce brand based in the US & Europe.

We are actively scaling marketing campaigns for your product:
📦 Product: {product_name}
🔗 Reference: {gadget.get('supplier_link', 'Direct Factory Catalog')}

We are projecting 20 to 50+ orders per day starting this week and would like to establish a reliable direct dropshipping partnership with your team.

Could you please confirm the following:
1. ✈️ Shipping Carrier & Delivery Times: What is your fastest delivery method to the US, UK, and EU (e.g. YunExpress, CJPacket, 4PX, USPS)? Can you achieve 6-9 business days?
2. 📦 Blind Dropshipping: Can you guarantee blind shipping (NO Chinese invoices, promotional flyers, or supplier price tags inside the package)?
3. ⚡ Processing Time: Can you provide tracking numbers within 24 to 48 hours of order submission?
4. 💰 VIP Pricing: Can you offer tiered pricing for daily volumes of 10, 30, and 50+ units?
5. 🎬 Media Assets: Do you have raw, unwatermarked high-definition product demonstration videos and lifestyle photos we can use for ad creatives?

We look forward to building a long-term, high-volume relationship with your factory.

Best regards,
Procurement & Sourcing Team
{store_name}
"""

    # 2. High-Efficiency Chinese Inquiry (Suppliers respond 3x faster in Chinese)
    message_zh = f"""您好！

我们是 {store_name} 跨境电商供应链采购负责人。目前我们在欧美主流市场运营智能生活家居品类，正在主推贵司的产品：
📦 产品名称: {product_name}
🔗 产品链接: {gadget.get('supplier_link', '工厂直供目录')}

我们预计本周起日出单量在 20-50+ 单以上，希望与贵司建立长期稳定的直发合作（一件代发 / Dropshipping）。

请确认以下合作细节：
1. ✈️ 物流时效：发往美国/英国/欧洲主流国家使用什么专线（如云途 YunExpress / CJPacket / 4PX）？时效能否稳定在 6-9 个工作日？
2. 📦 盲发要求：支持无痕盲发（包裹内严禁放入任何中文发票、好评返现卡及供应商广告信息）。
3. ⚡ 上网时效：订单发出后能否保证 24-48 小时内出追踪单号并有物流揽收信息？
4. 💰 合作底价：针对稳定日出 20-50 单以上的客户，能否给予 VIP 协议采购底价？
5. 🎬 视频素材：是否可提供无水印高清产品实拍、使用演示视频与白底/场景原图？

期待与贵厂建立长期双赢合作！如方便请留下微信或 WhatsApp，方便快速推单对账。
谢谢！
"""

    encoded_en = urllib.parse.quote(message_en)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_en}"

    return {
        "gadget_id": gadget.get("id"),
        "gadget_name": product_name,
        "supplier_name": gadget.get("supplier_name", "Shenzhen Factory Direct"),
        "supplier_platform": gadget.get("supplier_platform", "AliExpress / CJ Dropshipping"),
        "supplier_link": gadget.get("supplier_link", ""),
        "shipping_time": gadget.get("shipping_time", "6-9 business days"),
        "supplier_cost": target_cost,
        "message_en": message_en,
        "message_zh": message_zh,
        "whatsapp_url": whatsapp_url,
        "subject": f"Direct Dropship Partnership Inquiry - {product_name} [{store_name}]"
    }


def format_order_for_supplier_dispatch(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes an unfulfilled Shopify order and converts it into a clean,
    standardized dropship supplier fulfillment dispatch slip (CSV row & text).
    """
    shipping = order.get("shipping_address", {})
    customer = order.get("customer", {})
    line_items = order.get("line_items", [])

    items_summary = []
    for item in line_items:
        items_summary.append({
            "sku": item.get("sku", "SMART-GADGET-01"),
            "title": item.get("title", "Smart Gadget"),
            "quantity": item.get("quantity", 1),
            "variant": item.get("variant_title", "Standard")
        })

    first_name = shipping.get("first_name", customer.get("first_name", "Customer"))
    last_name = shipping.get("last_name", customer.get("last_name", ""))
    full_name = f"{first_name} {last_name}".strip()

    address1 = shipping.get("address1", "")
    address2 = shipping.get("address2", "")
    city = shipping.get("city", "")
    province = shipping.get("province", "")
    zip_code = shipping.get("zip", "")
    country = shipping.get("country", "")
    phone = shipping.get("phone", customer.get("phone", "N/A"))

    # Generate CSV row (compatible with CJ Dropshipping / DSers / AutoDS custom import)
    csv_row = f'"{order.get("name", "Order")}","{full_name}","{address1}","{address2}","{city}","{province}","{zip_code}","{country}","{phone}"'

    # Plain text format for supplier WhatsApp / WeChat
    dispatch_text = f"""📦 NEW DROPSHIP FULFILLMENT ORDER
Order ID: {order.get("name", "#1001")}
Recipient: {full_name}
Phone: {phone}
Address: {address1} {address2}
City: {city}, State/Province: {province} {zip_code}
Country: {country}
Items:
"""
    for item in items_summary:
        dispatch_text += f"- {item['title']} (Qty: {item['quantity']}, SKU: {item['sku']})\n"
    dispatch_text += "\n*Note: BLIND DROPSHIPPING ONLY - No supplier flyers or invoices inside package.*"

    return {
        "order_id": order.get("id"),
        "order_name": order.get("name"),
        "recipient": full_name,
        "country": country,
        "items": items_summary,
        "csv_row": csv_row,
        "dispatch_text": dispatch_text
    }


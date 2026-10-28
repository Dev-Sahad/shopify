"""
Curated Library of High-Converting, Viral Smart Gadgets.
Beginners can use these 1-click templates to immediately populate their store
with high-margin, visually viral gadgets.
"""

TRENDING_GADGETS = [
    {
        "id": "anti-gravity-humidifier",
        "name": "Anti-Gravity Optical Water Droplet Humidifier",
        "category": "Home Tech & Wellness",
        "supplier_cost": 16.80,
        "suggested_retail": 49.99,
        "viral_factor": "Optical illusion of water droplets floating upward goes mega-viral on TikTok / Reels.",
        "raw_title": "2024 New Anti Gravity Water Droplet Humidifier Ultrasonic Cool Mist Maker Levitating Water Drop Air Purifier With Led Clock Night Light",
        "raw_description": "Anti-gravity design uses black optical technology to make water drops appear to flow slowly upward while producing soothing mist. Features 800ml large capacity tank, 8-hour continuous runtime, intelligent anti-dry burning sensor with automatic shut-off, ultra-quiet 36dB operation, and ambient LED digital clock night light. Perfect for bedroom, home office desk, and relaxation.",
        "images": [
            "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1544717305-2782549b5136?w=800&auto=format&fit=crop&q=80"
        ]
    },
    {
        "id": "magnetic-levitating-lamp",
        "name": "Smart Magnetic Levitating Moon Lamp",
        "category": "Desk Setup & Lighting",
        "supplier_cost": 22.50,
        "suggested_retail": 69.99,
        "viral_factor": "Suspended in mid-air with zero contact, spins silently 360 degrees. High perceived value.",
        "raw_title": "Magnetic Levitation 3D Moon Lamp Floating And Spinning In Air With Wireless Base Led Night Light Desk Decor Gift",
        "raw_description": "Patented magnetic levitation technology suspends the 3D printed lunar surface lamp in mid-air. Wireless induction powers the warm/cool LED illumination through magnetic fields. Smooth 360-degree silent floating rotation. Touch-controlled base changes between warm white, cold white, and warm yellow lighting modes. Energy saving and durable PLA construction.",
        "images": [
            "https://images.unsplash.com/photo-1517991104123-1d56a6e81ed9?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&auto=format&fit=crop&q=80"
        ]
    },
    {
        "id": "ultrasonic-cleaner",
        "name": "360° Smart Ultrasonic Multi-Purpose Cleaner",
        "category": "Smart Cleaning Gadgets",
        "supplier_cost": 9.20,
        "suggested_retail": 29.99,
        "viral_factor": "Visually dramatic before-and-after cleaning of jewelry, glasses, and retainers in seconds.",
        "raw_title": "Portable Ultrasonic Cleaning Machine 45000Hz High Frequency Vibration Cleaner For Eyeglasses Jewelry Watches Makeup Brush Toothbrush",
        "raw_description": "45,000Hz high-frequency acoustic waves produce millions of microscopic bubbles that gently dislodge dirt, grease, and bacteria from intricate crevices in just 3 minutes. One-touch operation with smart timer. Stainless steel 304 tank with 350ml capacity. Compact, battery or USB powered, ideal for eyeglasses, rings, watches, aligners, and razor heads.",
        "images": [
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&auto=format&fit=crop&q=80"
        ]
    },
    {
        "id": "smart-neck-massager",
        "name": "Pulse Smart Neck Massager with Heat Therapy",
        "category": "Health & Posture Tech",
        "supplier_cost": 14.00,
        "suggested_retail": 44.99,
        "viral_factor": "Relieves desk neck strain and tech-neck. Directly targets gamers, office workers, and students.",
        "raw_title": "Smart Neck Massager TENS EMS Electric Pulse Cervical Vertebra Relieve Pain Heated Neck Massager Wireless Remote Control",
        "raw_description": "Combines Low-frequency TENS/EMS microcurrent pulses with 107°F (42°C) soothing constant heat therapy. Features 4 massage modes (Kneading, Tapping, Shiatsu, Acupuncture) with 15 intensity levels. Ergonomic 3D U-shaped floating electrode pads contour comfortably to any neck shape. Ultra-lightweight at 160g with 1200mAh USB rechargeable battery giving up to 10 days on a single charge.",
        "images": [
            "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&auto=format&fit=crop&q=80"
        ]
    },
    {
        "id": "foldable-3in1-wireless-charger",
        "name": "3-in-1 Foldable Magnetic Travel Charging Station",
        "category": "Mobile & Travel Tech",
        "supplier_cost": 13.50,
        "suggested_retail": 39.99,
        "viral_factor": "Folds into a pocket-sized square. Cleans up messy cables for iPhone, Apple Watch, and AirPods.",
        "raw_title": "3 In 1 Magnetic Wireless Charger Fast Charging Stand For iPhone 16 15 14 Pro Max Apple Watch Airpods Foldable Travel Charger",
        "raw_description": "Foldable magnetic design transforms effortlessly between a sleek desk charging stand and a travel-friendly compact puck. 15W Qi-certified rapid charging for smartphones, 5W for AirPods, and 2.5W for smartwatches simultaneously. Equipped with foreign object detection, temperature control, and overcharge protection. Soft silicone hinge withstands over 10,000 folds.",
        "images": [
            "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1616440347437-b1c73416efc2?w=800&auto=format&fit=crop&q=80"
        ]
    }
]

def get_trending_gadgets():
    return TRENDING_GADGETS

def get_gadget_by_id(gadget_id: str):
    for g in TRENDING_GADGETS:
        if g["id"] == gadget_id:
            return g
    return None


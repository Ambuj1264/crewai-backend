"""
Mock product database for the E-commerce Shopping Assistant.
Products are organized by category. Prices are in INR (₹).
"""

PRODUCT_DATABASE = {
    "laptops": [
        {
            "id": "L001",
            "name": "ASUS ROG Strix G15",
            "brand": "ASUS",
            "price": 89999,
            "category": "laptop",
            "rating": 4.5,
            "features": [
                "AMD Ryzen 9 7945HX",
                "NVIDIA RTX 4070 8GB",
                "16GB DDR5 RAM",
                "512GB NVMe SSD",
                "15.6\" 165Hz FHD Display",
                "Wi-Fi 6E",
                "RGB Backlit Keyboard",
                "Windows 11",
            ],
            "use_cases": ["gaming", "coding", "video editing"],
            "reviews": [
                "Blazing fast performance for gaming and coding tasks.",
                "Runs hot under heavy load.",
                "Excellent display quality and keyboard feel.",
                "Battery life could be better.",
                "Best bang for buck gaming laptop under 1 lakh.",
            ],
        },
        {
            "id": "L002",
            "name": "Lenovo IdeaPad Gaming 3",
            "brand": "Lenovo",
            "price": 67999,
            "category": "laptop",
            "rating": 4.2,
            "features": [
                "Intel Core i7-12700H",
                "NVIDIA RTX 3060 6GB",
                "16GB DDR5 RAM",
                "512GB NVMe SSD",
                "15.6\" 120Hz FHD Display",
                "Wi-Fi 6",
                "Backlit Keyboard",
                "Windows 11 Home",
            ],
            "use_cases": ["gaming", "coding", "casual use"],
            "reviews": [
                "Great value for money for a gaming laptop.",
                "Speaker quality is average.",
                "Solid build quality for the price.",
                "Gets warm during gaming but manageable.",
                "Good for everyday coding and gaming.",
            ],
        },
        {
            "id": "L003",
            "name": "HP Omen 16",
            "brand": "HP",
            "price": 94999,
            "category": "laptop",
            "rating": 4.4,
            "features": [
                "Intel Core i7-13700HX",
                "NVIDIA RTX 4060 8GB",
                "16GB DDR5 RAM",
                "1TB NVMe SSD",
                "16.1\" 165Hz FHD Display",
                "Wi-Fi 6E",
                "4-Zone RGB Keyboard",
                "Windows 11 Home",
            ],
            "use_cases": ["gaming", "coding", "content creation"],
            "reviews": [
                "Excellent cooling system.",
                "Premium build with great performance.",
                "Slightly heavy to carry around.",
                "Best display among competitors.",
                "OMEN Command Center software is handy.",
            ],
        },
        {
            "id": "L004",
            "name": "Dell G15 Ryzen Edition",
            "brand": "Dell",
            "price": 74999,
            "category": "laptop",
            "rating": 4.3,
            "features": [
                "AMD Ryzen 7 7745HX",
                "NVIDIA RTX 4060 8GB",
                "16GB DDR5 RAM",
                "512GB NVMe SSD",
                "15.6\" 165Hz FHD Display",
                "Wi-Fi 6",
                "White Backlit Keyboard",
                "Windows 11 Home",
            ],
            "use_cases": ["gaming", "coding", "multi-tasking"],
            "reviews": [
                "Excellent thermal performance.",
                "Good value gaming laptop.",
                "Display is crisp and color accurate.",
                "Chassis feels sturdy.",
                "Runs cool compared to other gaming laptops.",
            ],
        },
        {
            "id": "L005",
            "name": "Acer Nitro 5",
            "brand": "Acer",
            "price": 62999,
            "category": "laptop",
            "rating": 4.1,
            "features": [
                "Intel Core i5-12500H",
                "NVIDIA RTX 3050 4GB",
                "8GB DDR4 RAM",
                "512GB SSD",
                "15.6\" 144Hz FHD Display",
                "Wi-Fi 6",
                "4-Zone RGB Keyboard",
                "Windows 11 Home",
            ],
            "use_cases": ["casual gaming", "coding", "student use"],
            "reviews": [
                "Budget-friendly entry-level gaming laptop.",
                "Good for beginner coders.",
                "Can struggle with high-end games at max settings.",
                "Keyboard and display are satisfactory.",
                "Best entry-level gaming laptop in India.",
            ],
        },
        {
            "id": "L006",
            "name": "MSI Katana 15",
            "brand": "MSI",
            "price": 79999,
            "category": "laptop",
            "rating": 4.3,
            "features": [
                "Intel Core i7-13620H",
                "NVIDIA RTX 4060 8GB",
                "16GB DDR5 RAM",
                "512GB NVMe SSD",
                "15.6\" 144Hz FHD Display",
                "Wi-Fi 6",
                "Single-Zone RGB Keyboard",
                "Windows 11 Home",
            ],
            "use_cases": ["gaming", "coding", "streaming"],
            "reviews": [
                "Solid mid-range gaming laptop.",
                "MUX switch significantly boosts gaming performance.",
                "Build quality is decent.",
                "Fan noise is noticeable under load.",
                "Great performance per rupee.",
            ],
        },
        {
            "id": "L007",
            "name": "Apple MacBook Air M2",
            "brand": "Apple",
            "price": 99900,
            "category": "laptop",
            "rating": 4.8,
            "features": [
                "Apple M2 Chip (8-core CPU, 10-core GPU)",
                "8GB Unified Memory",
                "256GB SSD",
                "13.6\" Liquid Retina Display",
                "MagSafe Charging",
                "fanless design",
                "macOS Ventura",
                "18-hour battery life",
            ],
            "use_cases": ["coding", "creative work", "everyday use"],
            "reviews": [
                "Best battery life of any laptop.",
                "Fanless and completely silent.",
                "macOS ecosystem is unmatched.",
                "Not ideal for hardcore gaming.",
                "Best laptop for iOS/macOS development.",
            ],
        },
    ],
    "smartphones": [
        {
            "id": "S001",
            "name": "Samsung Galaxy S24",
            "brand": "Samsung",
            "price": 74999,
            "category": "smartphone",
            "rating": 4.6,
            "features": ["Snapdragon 8 Gen 3", "12GB RAM", "256GB storage", "50MP camera"],
            "use_cases": ["photography", "gaming", "business"],
            "reviews": ["Excellent camera quality.", "Fast and smooth performance."],
        },
    ],
}


def search_products(query: str, max_results: int = 7) -> list:
    """Simple keyword-based product search from the mock database."""
    query_lower = query.lower()
    all_products = []

    # Flatten all products
    for category, products in PRODUCT_DATABASE.items():
        all_products.extend(products)

    # Score each product by relevance to query
    scored = []
    keywords = query_lower.split()

    for product in all_products:
        score = 0
        searchable_text = (
            product["name"].lower()
            + " "
            + product["brand"].lower()
            + " "
            + product["category"].lower()
            + " "
            + " ".join(product.get("use_cases", [])).lower()
            + " "
            + " ".join(product.get("features", [])).lower()
        )

        for keyword in keywords:
            if keyword in searchable_text:
                score += 1

        # Budget matching
        budget_keywords = {
            "lakh": 100000,
            "lakhs": 100000,
            "lac": 100000,
        }
        for bk, bv in budget_keywords.items():
            if bk in query_lower:
                # extract number before "lakh"
                parts = query_lower.split()
                for i, part in enumerate(parts):
                    if part == bk and i > 0:
                        try:
                            multiplier = float(parts[i - 1])
                            budget = multiplier * bv
                            if product["price"] <= budget:
                                score += 2
                        except ValueError:
                            pass

        if score > 0:
            scored.append((score, product))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        # Return top products from "laptops" as default
        return all_products[:max_results]

    return [p for _, p in scored[:max_results]]

"""Read and filter the single shared Rijema Dira storefront catalog."""

import json
import logging
import re
from pathlib import Path

from pydantic import ValidationError

from models.schemas import StoreProduct
from utils.text_normalizer import normalisasi

logger = logging.getLogger(__name__)
_CATALOG_PATH = Path(__file__).resolve().parents[2] / "shared" / "products.json"
_CATEGORIES = {
    "cleanser": "Cleanser", "pembersih": "Cleanser",
    "moisturizer": "Moisturizer", "pelembap": "Moisturizer", "pelembab": "Moisturizer",
    "serum": "Serum", "sunscreen": "Sunscreen", "tabir surya": "Sunscreen",
}
_SKIN_TYPES = {
    "berminyak": ("berminyak",), "oily": ("berminyak",),
    "kering": ("kering",), "sensitif": ("sensitif",),
    "kombinasi": ("kombinasi",), "normal": ("normal",),
    "jerawat": ("jerawat", "berkomedo"), "berjerawat": ("jerawat", "berkomedo"),
}
_SEARCH_STOPWORDS = {
    "produk", "products", "produkku", "ada", "cari", "tampilkan",
    "rekomendasi", "rekomendasikan", "recommend", "recommendation",
    "untuk", "kulit", "yang", "apa", "saya", "dengan", "tokoku", "toko",
    "rijema", "dira", "mu", "di", "the", "store", "in", "my",
    "please", "show", "find", "which", "suitable", "cocok", "paling",
    "bandingkan", "perbandingan", "dua", "beda", "perbedaan", "antara", "dan",
}


class ProductCatalogService:
    def __init__(self, catalog_path=_CATALOG_PATH):
        self.catalog_path = Path(catalog_path)

    def list_products(self):
        try:
            with self.catalog_path.open(encoding="utf-8") as catalog_file:
                products = [StoreProduct.model_validate(item) for item in json.load(catalog_file)]
            ids = [product.id for product in products]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate product IDs in shared catalog")
            return products
        except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
            logger.error("Unable to load validated store product catalog: error=%s", type(exc).__name__)
            return []

    def get_by_ids(self, product_ids):
        by_id = {product.id: product for product in self.list_products()}
        return [by_id[product_id] for product_id in dict.fromkeys(product_ids) if product_id in by_id]

    def category_from_query(self, query):
        normalized = normalisasi(query)
        return next((category for phrase, category in _CATEGORIES.items()
                     if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalized)), None)

    def skin_type_from_query(self, query):
        normalized = normalisasi(query)
        return next((value for phrase, value in _SKIN_TYPES.items()
                     if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalized)), None)

    def ingredient_from_query(self, query):
        normalized = normalisasi(query)
        for product in self.list_products():
            for ingredient in product.ingredients:
                candidate = normalisasi(ingredient)
                if re.search(rf"(?<!\w){re.escape(candidate)}(?!\w)", normalized):
                    return ingredient
        return None

    def search(self, query="", *, category=None, skin_type=None, ingredient=None, product_ids=None, limit=6):
        products = self.list_products()
        normalized_query = normalisasi(query)
        category = category or self.category_from_query(normalized_query)
        if skin_type is None:
            skin_type = self.skin_type_from_query(normalized_query)
        normalized_ingredient = normalisasi(ingredient) if ingredient else None

        matches = []
        query_terms = [
            term for term in re.findall(r"[a-z0-9]+", normalized_query)
            if len(term) > 2 and term not in _SEARCH_STOPWORDS
        ]
        for product in products:
            if product_ids is not None and product.id not in product_ids:
                continue
            if category and product.category != category:
                continue
            skin = normalisasi(product.skin)
            if skin_type and not ("semua jenis kulit" in skin or any(tag in skin for tag in skin_type)):
                continue
            ingredients = [normalisasi(item) for item in product.ingredients]
            if normalized_ingredient and not any(normalized_ingredient in item for item in ingredients):
                continue

            searchable = normalisasi(" ".join((product.name, product.category, *product.ingredients)))
            if query_terms and not any(term in searchable for term in query_terms):
                # Category and skin-type filters carry the intent for natural-language asks.
                if not category and not skin_type and not normalized_ingredient and product_ids is None:
                    continue
            matches.append(product)
        return matches[:max(0, limit)]


product_catalog = ProductCatalogService()

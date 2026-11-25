import json
import tempfile
import unittest
from pathlib import Path

from services.product_catalog_service import ProductCatalogService, product_catalog


class ProductCatalogTests(unittest.TestCase):
    def test_catalog_is_the_existing_store_data(self):
        products = product_catalog.list_products()
        self.assertEqual(len(products), 6)
        self.assertEqual(product_catalog.get_by_ids([3])[0].name, "Daily UV Sunscreen")
        self.assertEqual(product_catalog.get_by_ids([3])[0].price, 95000)

    def test_category_search_returns_actual_sunscreen(self):
        products = product_catalog.search("Ada sunscreen?")
        self.assertEqual([product.name for product in products], ["Daily UV Sunscreen"])

    def test_skin_filter_uses_only_catalog_skin_metadata(self):
        products = product_catalog.search("produk untuk kulit berminyak")
        self.assertTrue(products)
        self.assertTrue(all(
            "semua jenis kulit" in product.skin.lower() or "berminyak" in product.skin.lower()
            for product in products
        ))

    def test_ingredient_filter_does_not_invent_matches(self):
        self.assertEqual(product_catalog.search("produk kandungan X", ingredient="X"), [])
        matches = product_catalog.search("serum niacinamide", ingredient="Niacinamide")
        self.assertEqual({product.id for product in matches}, {4})

    def test_missing_catalog_file_returns_no_products(self):
        with tempfile.TemporaryDirectory() as directory:
            service = ProductCatalogService(Path(directory) / "missing.json")
            self.assertEqual(service.list_products(), [])


if __name__ == "__main__":
    unittest.main()

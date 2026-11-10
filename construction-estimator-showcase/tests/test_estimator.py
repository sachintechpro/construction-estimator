import unittest
from decimal import Decimal
from pathlib import Path
from app.estimator import estimate, load_catalog

CATALOG = load_catalog(Path(__file__).resolve().parents[1] / 'data' / 'catalog.csv')

class EstimateTests(unittest.TestCase):
    def test_known_totals(self):
        result = estimate({'items': [{'code': 'PAINT', 'quantity': 100}],
            'labor_rate': 50, 'waste_percent': 10, 'overhead_percent': 10,
            'profit_markup_percent': 20, 'material_tax_percent': 5}, CATALOG)
        t = result['totals']
        self.assertEqual(t['materials_including_waste'], '49.50')
        self.assertEqual(t['labor'], '400.00')
        self.assertEqual(t['material_tax'], '2.48')
        self.assertEqual(t['direct_cost'], '451.98')
        self.assertEqual(t['overhead'], '45.20')
        self.assertEqual(t['profit_markup'], '99.44')
        self.assertEqual(t['estimated_price'], '596.62')

    def test_rejects_unknown_item(self):
        with self.assertRaisesRegex(ValueError, 'unknown catalog code'):
            estimate({'items': [{'code': 'NOPE', 'quantity': 1}]}, CATALOG)

    def test_rejects_negative_or_nonfinite(self):
        for value in ['-1', 'NaN', 'Infinity', 'not a number']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                estimate({'items': [{'code': 'FLOOR', 'quantity': value}]}, CATALOG)

    def test_rejects_missing_items(self):
        with self.assertRaisesRegex(ValueError, 'between 1 and 100'):
            estimate({'items': []}, CATALOG)

    def test_multiple_lines(self):
        result = estimate({'items': [{'code': 'WINDOW', 'quantity': 2}, {'code': 'PAINT', 'quantity': 50}]}, CATALOG)
        self.assertEqual(len(result['items']), 2)
        self.assertGreater(Decimal(result['totals']['estimated_price']), Decimal(result['totals']['direct_cost']))

if __name__ == '__main__':
    unittest.main()

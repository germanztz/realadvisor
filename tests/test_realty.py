import unittest
import sys
sys.path.append('report')
from realty import Realty

class TestRealty(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            'link': '/inmueble/123456/',
            'type_v': 'piso',
            'address': 'calle test 123',
            'town': 'barcelona',
            'price': 250000,
            'price_old': 260000.0,
            'info': "['80 m²', '3 hab.']",
            'description': "Piso en venta en Barcelona",
            'tags': 'Reformado, Exterior',
            'agent': None,
            'created': '2024-03-20 10:00:00'
        }
        
    def test_create_realty(self):
        realty = Realty(**self.sample_data)
        self.assertEqual(realty.link, '/inmueble/123456/')
        self.assertEqual(realty.price, 250000)
        self.assertEqual(realty.price_old, 260000.0)
        
    def test_from_dict(self):
        realty = Realty.from_dict(self.sample_data)
        self.assertEqual(realty.type_v, 'piso')
        self.assertEqual(realty.address, 'calle test 123')
        
    def test_str_representation(self):
        realty = Realty.from_dict(self.sample_data)
        str_output = str(realty)
        self.assertIn('Piso en calle test 123', str_output)
        self.assertIn('250,000€', str_output.replace(' ', ''))
        self.assertIn('Reformado, Exterior', str_output)
        
    def test_optional_fields(self):
        data = self.sample_data.copy()
        data['price_old'] = None
        data['tags'] = None
        data['agent'] = None
        realty = Realty.from_dict(data)
        self.assertIsNone(realty.price_old)
        self.assertIsNone(realty.tags)
        self.assertIsNone(realty.agent)

if __name__ == '__main__':
    unittest.main() 
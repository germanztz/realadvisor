import unittest
import sys
sys.path.append('src')
from realty import Realty

class TestRealty(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            'link': '/inmueble/123456/',
            'type_v': 'piso',
            'address': 'calle test 123, sant andreu, barcelona',
            'town': 'sant andreu',
            'price': 250000,
            'price_old': 260000.0,
            'info': "['80 m²', '3 hab.']",
            'description': "Piso en venta en<br> Barcelona reformado y con terraza",
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
        self.assertEqual(realty.address, 'calle test 123, sant andreu, barcelona')
        
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

    def test_get_tags(self):
        tags = Realty.get_tags(self.sample_data['description'])
        self.assertEqual(tags, ['terraza', 'Barcelona reformado'])

    def test_map_place(self):
        place = Realty.map_place(self.sample_data['town'], ['barcelona', 'sant andreu', 'valencia'])
        self.assertEqual(place, ('sant andreu', 1.0))

    def test_get_occupation(self):
        occupation = Realty.get_occupation(self.sample_data['description'])
        self.assertEqual(occupation, 'disponible')

    def test_get_hood(self):
        hood = Realty.get_hood(self.sample_data['address'])
        self.assertEqual(hood, 'sant andreu')

    def test_clean_description(self):
        clean_description = Realty.clean_description(self.sample_data['description'])
        self.assertEqual(clean_description, 'piso en venta en barcelona reformado y con terraza')

    def test_get_n_hab(self):
        n_hab = Realty.get_n_hab(self.sample_data['info'])
        self.assertEqual(n_hab, 3)


if __name__ == '__main__':
    unittest.main() 
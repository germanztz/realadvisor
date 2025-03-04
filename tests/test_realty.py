import unittest
import sys
sys.path.append('src')
from realty import Realty

class TestRealty(unittest.TestCase):
    def setUp(self):
        self.realty = Realty.get_sample()
        
    def test_create_realty(self):
        realty = Realty(**Realty.get_sample_data())
        self.assertEqual(realty.link, 'https://example.com/inmueble/123456/')
        self.assertEqual(realty.price, 250000)
        self.assertEqual(realty.price_old, 260000)
        self.assertEqual(realty.tags, ['Reformado', 'Exterior'])
        self.assertEqual(len(realty.description), 1398)
        self.assertEqual(realty.town, 'Sant Andreu, Barcelona')
        self.assertEqual(realty.images, 'https://static.fotocasa.es/images/ads/68760093-40a0-4485-94ea-6532fd9500a7?rule=original')
             
    def test_str_representation(self):
        realty = Realty(**Realty.get_sample_data())
        str_output = str(realty)
        self.assertIn('https://example.com/inmueble/123456/', str_output)
        self.assertIn('calle test 123', str_output)
        
    def test_optional_fields(self):
        data = Realty.get_sample_data()
        data['price_old'] = None
        data['tags'] = None
        data['agent'] = None
        realty = Realty(**data)
        self.assertIsNone(realty._price_old)
        self.assertIsNone(realty._tags)
        self.assertIsNone(realty._agent)

    def test_to_dict(self):
        realty = Realty(**Realty.get_sample_data())
        dict_output = realty.to_dict()
        self.assertEqual(dict_output['link'], 'https://example.com/inmueble/123456/')
        self.assertEqual(dict_output['price'], 250000)
        self.assertEqual(dict_output['price_old'], 260000.0)

    def test_parse_price(self):
        self.assertEqual(Realty.parse_price('123456'), 123456.0)
        self.assertEqual(Realty.parse_price('123.456.789,01'), 123456789.01)
        self.assertEqual(Realty.parse_price('12.345'), 12345.0)
        self.assertEqual(Realty.parse_price('1,234'), 1234.0)
        self.assertEqual(Realty.parse_price('1,234,567'), 1234567.0)
        self.assertEqual(Realty.parse_price('1234.567'), 1234.567)
        
    def test_tags_setter(self):
        realty = Realty(**Realty.get_sample_data())
        
        # Test setting None
        realty.tags = None
        self.assertIsNone(realty._tags)
        
        # Test setting string
        realty.tags = "Terraza, Ascensor"
        self.assertEqual(realty._tags, ['Terraza', 'Ascensor'])
        
        # Test adding new string tags
        realty.tags = "Exterior, Terraza"
        self.assertEqual(realty._tags, ['Terraza', 'Ascensor', 'Exterior'])
        
        # Test setting list
        realty.tags = ["Parking", "Reformado"]
        self.assertEqual(realty._tags, ['Terraza', 'Ascensor', 'Exterior', 'Parking', 'Reformado'])
        
        # Test invalid type
        realty.tags = 123
        self.assertIsNone(realty._tags)

    def test_price_old_setter(self):
        realty = Realty(**Realty.get_sample_data())
        
        realty.price_old = '123.456'
        self.assertEqual(realty._price_old, 123456)
        
        realty.price_old = '6543,21'
        self.assertEqual(realty._price_old, 6543)
        
        realty.price_old = '1.234,56'
        self.assertEqual(realty._price_old, 1234)
        
        realty.price_old = '1,234.56'
        self.assertEqual(realty._price_old, 1234)
        
        realty.price_old = '1234'
        self.assertEqual(realty._price_old, 1234)
        
        realty.price_old = '1234 €'
        self.assertEqual(realty._price_old, 1234)
        
        realty.price_old = '1.234.567'
        self.assertEqual(realty._price_old, 1234567)
        
        realty.price_old = None
        self.assertEqual(realty._price_old, None)
        
        realty.price_old = 'invalid'
        self.assertEqual(realty._price_old, None)
        
        realty.price_old = 12345
        self.assertEqual(realty._price_old, 12345)
        
        realty.price_old = 123.45
        self.assertEqual(realty._price_old, 123)



if __name__ == '__main__':
    unittest.main() 
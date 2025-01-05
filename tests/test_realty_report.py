import unittest
import sys
sys.path.append('src/report')
from realty_report import RealtyReport # type: ignore

class TestRealtyReport(unittest.TestCase):
    def setUp(self):
        self.sample_data = RealtyReport.get_sample_data()
        self.sample_data2 = {'created': '2025-01-04 09:36:20', 'link': '/inmueble/106576974/', 'type_v': 'Estudio', 'address': 'Les Roquetes', 'town': 'Nou Barris, Barcelona', 'price': '33.000', 'price_old': None, 'info': ['51 m² construidos, 46 m² útiles', 'Sin habitación', '2 baños', 'Segunda mano/buen estado', 'Orientación norte, este', 'Construido en 1968', 'No dispone de calefacción', 'Bajo exterior', 'Sin ascensor', '<span>Consumo: </span><span class="icon-energy-c-e">411 kWh/m² año</span>', '<span>Emisiones: </span><span class="icon-energy-c-e"></span>'], 'description': "Tecnocasa Estudi Mina de la Ciutat S. L tiene el placer de presentarles este inmueble el cual tenemos en exclusiva:<br/><br/>DOS ESTUDIOS POR 33.000 CADA UNO, dispone de 51m&sup2; de construcci&oacute;n, distribuidos cada uno de ellos de la siguiente manera: Un espacio di&aacute;fano tipo loft donde se puede hacer la cocina americana con sal&oacute;n comedor, un espaci&oacute; para descansar y un cuarto de ba&ntilde;o, Los locales se venden juntos y se encuentran ubicados en una de las calles principales del barrio, haciendo que los mismos se encuentre muy cerca de todos los servicios b&aacute;sicos, calles peatonales, se encuentra en una zona inmejorable en cuanto a comunicaciones, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPONEN DE CEDULA DE HABITABILIDAD.<br/><br/>Informaci&oacute;n al consumidor: Le informamos que el precio de venta ofertado no incluye los gastos de compraventa (notar&iacute;a, registro, gestor&iacute;a, inmobiliaria, impuestos estatales ITP y tasas y gastos bancarios). Si desea visitar este inmueble, cualquiera de nuestros agentes le informar&aacute; detalladamente de estos gastos antes de visitarlo.<br/><br/>La red Kiron del Grupo Tecnocasa te ayudar&aacute; a buscar la financiaci&oacute;n que mejor se adapte a tus necesidades. Son expertos en el sector financiero y est&aacute;n a tu disposici&oacute;n para que elijas la hipoteca que mejor se adapte a ti. Hasta un 100%.<br/><br/>Tecnocasa Estudi Mina de la Ciutat S. L t&eacute; el plaer de presentar-vos aquest immoble el qual tenim en exclusiva:<br/><br/>DOS ESTUDIS PER 33.000 CADASCUN, disposa de 51m&sup2; de construcci&oacute;, distribu&iuml;ts cadascun d'ells de la seg&uuml;ent manera: Un espai di&agrave;fan tipus loft on es pot fer la cuina americana amb sal&oacute; menjador, un espai per descansar i una cambra de bany, Els locals es venen junts i es troben ubicats en un dels carrers principals del barri, fent que aquests es trobi molt a prop de tots els serveis b&agrave;sics, carrers de vianants, es troba en una zona immillorable quant a comunicacions, metro (L3), parada de Bus TMB V29, 11, 27, 127. NO DISPOSEN DE CEDULA D'HABITABILITAT.<br/><br/>Informaci&oacute; al consumidor: Us informem que el preu de venda oferit no inclou les despeses de compravenda (notaria, registre, gestoria, inmobiliaria, impostos estatals ITP i taxes i despeses banc&agrave;ries). Si voleu visitar aquest immoble, qualsevol dels nostres agents us informar&agrave; detalladament d'aquestes despeses abans de visitar-lo.<br/><br/>La xarxa Kiron del Grup Tecnocasa us ajudar&agrave; a buscar el finan&ccedil;ament que millor s'adapti a les vostres necessitats. S&oacute;n experts en el sector financer i estan a la teva disposici&oacute; perqu&egrave; tri&iuml;s la hipoteca que s'adapti millor a tu. Fins a un 100%.", 'tags': None, 'agent': None}
        self.realty = RealtyReport(**self.sample_data)
        
    def test_create_realty(self):
        realty = RealtyReport(**self.sample_data)
        self.assertEqual(realty.link, 'https://example.com/inmueble/123456/')
        self.assertEqual(realty.price, 250000)
        self.assertEqual(realty.price_old, 260000)
        self.assertEqual(realty.tags, ['terraza', 'barcelona reformado'])
        self.assertEqual(realty.description, 'piso en venta en barcelona reformado y con terraza ocupada')
        self.assertEqual(realty.town, 'sant andreu')
             

    # Test abstract methods of the class
    def test_get_tags(self):
        tags = RealtyReport.extract_tags(self.sample_data['description'])
        self.assertEqual(tags, ['terraza', 'Barcelona reformado'])

    def test_map_place(self):
        realty = RealtyReport(**self.sample_data)
        place = RealtyReport.map_place(realty.town, ['barcelona', 'sant andreu', 'valencia'])
        self.assertEqual(place, ('sant andreu', 1.0))

    def test_get_occupation(self):
        occupation = RealtyReport.get_occupation(self.sample_data['description'])
        self.assertEqual(occupation, 'ocupada')

    def test_get_hood(self):
        hood = RealtyReport.get_hood(self.sample_data['town'])
        self.assertEqual(hood, 'sant andreu')

    def test_clean_description(self):
        clean_description = RealtyReport.clean_description(self.sample_data['description'])
        self.assertEqual(clean_description, 'piso en venta en barcelona reformado y con terraza ocupada')

    def test_get_n_hab(self):
        n_hab = RealtyReport.get_n_hab(self.sample_data['info'])
        self.assertEqual(n_hab, 3)

    def test_to_dict(self):
        realty = RealtyReport(**self.sample_data)
        dict_output = realty.to_dict()
        self.assertEqual(dict_output['link'], 'https://example.com/inmueble/123456/')
        self.assertEqual(dict_output['price'], 250000)
        self.assertEqual(dict_output['price_old'], 260000.0)

    def test_parse_price(self):
        self.assertEqual(RealtyReport.parse_price('123456'), 123456.0)
        self.assertEqual(RealtyReport.parse_price('123.456.789,01'), 123456789.01)
        self.assertEqual(RealtyReport.parse_price('12.345'), 12345.0)
        self.assertEqual(RealtyReport.parse_price('1,234'), 1234.0)
        self.assertEqual(RealtyReport.parse_price('1,234,567'), 1234567.0)
        self.assertEqual(RealtyReport.parse_price('1234.567'), 1234.567)
        
    def test_tags_setter(self):
        realty = RealtyReport(**self.sample_data)
        
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


    def test_estandarizar(self):
        self.assertEqual(RealtyReport.estandarizar("Barcelona - Sant Andreu"), "barcelona  sant andreu")
        self.assertEqual(RealtyReport.estandarizar("La Teixonera"), "la teixonera")

    def test_get_hood(self):
        self.assertEqual(RealtyReport.get_hood("calle test 123,Sant Andreu, Barcelona"), "sant andreu")

    def test_clean_description(self):
        self.assertEqual(RealtyReport.clean_description("Piso en venta en<br> Barcelona reformado y con terraza ocupada"), "piso en venta en barcelona reformado y con terraza ocupada")
        self.assertEqual(RealtyReport.clean_description(None), "")

    def test_get_n_hab(self):
        self.assertEqual(RealtyReport.find_min_int(["80 m²", "3 hab."], RealtyReport.RX_HAB), 3)
        self.assertIsNone(RealtyReport.find_min_int(None, RealtyReport.RX_HAB))
        self.assertIsNone(RealtyReport.find_min_int("Invalid text", RealtyReport.RX_HAB))

    def test_get_sup_m2(self):
        self.assertEqual(RealtyReport.find_min_int('["80 m²", "3 hab."]', RealtyReport.RX_M2), 80)
        self.assertEqual(RealtyReport.find_min_int(['51 m² construidos, 46 m² útiles'], RealtyReport.RX_M2), 46)
        self.assertIsNone(RealtyReport.find_min_int(None, RealtyReport.RX_M2))
        self.assertIsNone(RealtyReport.find_min_int("Invalid text", RealtyReport.RX_M2))

    def test_get_occupation(self):
        self.assertEqual(RealtyReport.get_occupation("ocupada"), "ocupada")
        self.assertEqual(RealtyReport.get_occupation("alquilada"), "alquilada")
        self.assertEqual(RealtyReport.get_occupation("disponible"), "disponible")

    def test_extract_tags(self):
        description = "Piso en venta reformado y con terraza ocupada, con vistas al mar"
        tags = RealtyReport.extract_tags(description)
        self.assertEqual(tags, ['terraza', 'venta reformado'])

    def test_map_place(self):
        places = ["Barcelona", "Madrid", "Paris"]
        result = RealtyReport.map_place("Barcelona", places)
        self.assertEqual(result, ("Barcelona", 1.0))

    def test_get_price_m2(self):
        price = 100000
        sup_m2 = 80
        result = RealtyReport.get_price_m2(price, sup_m2)
        self.assertEqual(result, 1250)

    def test_get_price_desv_media(self):
        price_m2 = 1200
        price_venta_1y = 25000
        result = RealtyReport.get_price_desv_media(price_m2, price_venta_1y)
        self.assertEqual(result, 0.05)

    def test_get_price_stars(self):
        price_desv_media = 0.4
        result = RealtyReport.get_price_stars(price_desv_media)
        self.assertEqual(result, 3)

    def test_get_price_alquiler_estimado(self):
        precio_alquiler_1y = 14.53
        sup_m2 = 100
        result = RealtyReport.get_price_alquiler_estimado(precio_alquiler_1y, sup_m2)
        self.assertEqual(result, 1453)

    def test_get_price_venta_estimado(self):
        precio_venta_1y = 2619.8571
        sup_m2 = 456
        result = RealtyReport.get_price_venta_estimado(precio_venta_1y, sup_m2)
        self.assertEqual(result, 1194654)

    def test_get_global_score_stars(self):
        precio_venta_stars = 4
        rentabilidad_10y_stars = 3
        grow_acu_venta_10y_stars = 3
        grow_acu_alquiler_10y_stars = 3
        disponibilidad = "disponible"
        result = RealtyReport.get_global_score_stars(precio_venta_stars, rentabilidad_10y_stars, grow_acu_venta_10y_stars, grow_acu_alquiler_10y_stars, disponibilidad)
        self.assertEqual(result, 3.6)


if __name__ == '__main__':
    unittest.main() 
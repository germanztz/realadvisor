from dataclasses import dataclass, field
from typing import Optional
from difflib import SequenceMatcher
import html
import re
import unicodedata
import sys
sys.path.append('src')
from realty import Realty

@dataclass
class RealtyReport(Realty):
    # Property characteristics (additional to Realty)
    n_hab: Optional[int] = field(default=None, init=False, repr=False)
    sup_m2: int = field(default=None, init=False, repr=False)
    disponibilidad: str = field(default=None, init=False, repr=False)
    
    # Location info
    barrio: str = field(default=None, init=False, repr=False)
    barrio_ratio: float = field(default=None, init=False, repr=False)
    id: int = field(default=None, init=False, repr=False)
    nombre: str = field(default=None, init=False, repr=False)
    sup_id: int = field(default=None, init=False, repr=False)
    sup_nombre: str = field(default=None, init=False, repr=False)
    tipo: str = field(default=None, init=False, repr=False)
    
    # Market statistics - 1y
    precio_venta_1y: float = field(default=None, init=False, repr=False)
    superficie_venta_1y: float = field(default=None, init=False, repr=False)
    elasticidad_1y: float = field(default=None, init=False, repr=False)
    precio_alquiler_1y: float = field(default=None, init=False, repr=False)
    rentabilidad_1y: float = field(default=None, init=False, repr=False)
    grow_acu_alquiler_1y: float = field(default=None, init=False, repr=False)
    grow_acu_venta_1y: float = field(default=None, init=False, repr=False)
    grow_acu_superficie_venta_1y: float = field(default=None, init=False, repr=False)
    
    # Market statistics - 5y
    precio_venta_5y: float = field(default=None, init=False, repr=False)
    superficie_venta_5y: float = field(default=None, init=False, repr=False)
    elasticidad_5y: float = field(default=None, init=False, repr=False)
    precio_alquiler_5y: float = field(default=None, init=False, repr=False)
    rentabilidad_5y: float = field(default=None, init=False, repr=False)
    grow_acu_alquiler_5y: float = field(default=None, init=False, repr=False)
    grow_acu_venta_5y: float = field(default=None, init=False, repr=False)
    grow_acu_superficie_venta_5y: float = field(default=None, init=False, repr=False)
    
    # Market statistics - 10y
    precio_venta_10y: float = field(default=None, init=False, repr=False)
    superficie_venta_10y: float = field(default=None, init=False, repr=False)
    elasticidad_10y: float = field(default=None, init=False, repr=False)
    precio_alquiler_10y: float = field(default=None, init=False, repr=False)
    rentabilidad_10y: float = field(default=None, init=False, repr=False)
    grow_acu_alquiler_10y: float = field(default=None, init=False, repr=False)
    grow_acu_venta_10y: float = field(default=None, init=False, repr=False)
    grow_acu_superficie_venta_10y: float = field(default=None, init=False, repr=False)  
    
    # Stars ratings
    elasticidad_1y_stars: int = field(default=None, init=False, repr=False)
    rentabilidad_1y_stars: int = field(default=None, init=False, repr=False)
    grow_acu_alquiler_1y_stars: int = field(default=None, init=False, repr=False)
    grow_acu_venta_1y_stars: int = field(default=None, init=False, repr=False)
    elasticidad_5y_stars: int = field(default=None, init=False, repr=False)
    rentabilidad_5y_stars: int = field(default=None, init=False, repr=False)
    grow_acu_alquiler_5y_stars: int = field(default=None, init=False, repr=False)
    grow_acu_venta_5y_stars: int = field(default=None, init=False, repr=False)
    elasticidad_10y_stars: int = field(default=None, init=False, repr=False)
    rentabilidad_10y_stars: int = field(default=None, init=False, repr=False)
    grow_acu_alquiler_10y_stars: int = field(default=None, init=False, repr=False)
    grow_acu_venta_10y_stars: int = field(default=None, init=False, repr=False)
    global_score_stars: float = field(default=None, init=False, repr=False)
    
    # Property analysis
    precio_m2: int = field(default=None, init=False, repr=False)
    precio_desv_media: float = field(default=None, init=False, repr=False)
    precio_venta_stars: int = field(default=None, init=False, repr=False)
    precio_alquiler_estimado: float = field(default=None, init=False, repr=False)
    precio_venta_estimado: float = field(default=None, init=False, repr=False)


    _okupadas_words = ['okupada', 'okupado', 'ocupado', 'ocupada', 'ocupacional', 'sin posesión', 'sin posesion','ilegal']
    _alquiladas_words = ['alquilado', 'alquilada', 'inquilinos', 'inquilino', 'usufructuarios', 'usufructuario', 'arrendado']

    # Lista de palabras clave para el análisis inmobiliario
    _single_keywords = [
        "inversi.n", "oportunidad" ,"rendimiento", "renta.ilidad", "inversores", 'nuda'
        "rehabilitad.", "metro", 
        "estacionamiento", "calefacci.n", "la.adero",
        "terraza", "luminoso", "balc.n", "patio",
        "bajo", "local", "estudio"
    ]

    _double_keywords = [
        "reforma.?", "reformad.", "integral", "c.dula",
        "baños","banos", "ascensor", "amueblad.","blindad.",
        "exterior", "comercial"
    ]

    RX_HAB = re.compile(r'(\d+?) hab\.')
    RX_M2 = re.compile(r'(\d+?) m²')
    RX_BARRIOS = re.compile(r"([^,]+),[^,]+$")
    RX_HTML_TAG = re.compile(r"<.*?>")

    RX_SINGLE_TAG = re.compile(r'\b(?:' + '|'.join(_single_keywords) + r')\b')
    RX_DOUBLE_TAG = re.compile(r'\b(\w+\s+(?:' + '|'.join(_double_keywords) + r'))\b')

    GLOBAL_SCORE_WEIGHTS = {
        'precio_venta_stars': 0.6,          # Precio competitivo es el factor más importante
        'rentabilidad_10y_stars': 0.2,      # Rentabilidad actual
        'grow_acu_alquiler_10y_stars': 0.1, # Crecimiento histórico de alquileres
        'grow_acu_venta_10y_stars': 0.1     # Crecimiento histórico de ventas
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Clean and standardize basic fields
        self._town = RealtyReport.estandarizar(self._town)
        self._description = RealtyReport.clean_description(self._description)
        self._type_v = RealtyReport.estandarizar(self._type_v)
        self._address = RealtyReport.estandarizar(self._address)
        self.n_hab = RealtyReport.find_min_int(self._info, RealtyReport.RX_HAB)
        self.sup_m2 = RealtyReport.find_min_int(self._info, RealtyReport.RX_M2)

        self.disponibilidad = RealtyReport.get_occupation(self._description)
        self._tags = RealtyReport.extract_tags(self._description)

    def set_indicadores(self, **indicadores):
        for key, value in indicadores.items():
            if getattr(self, key, None) is None:
                setattr(self, key, value)

        self.precio_m2 = RealtyReport.get_price_m2(self._price, self.sup_m2)
        self.precio_desv_media = RealtyReport.get_price_desv_media(self.precio_m2, self.precio_venta_1y)
        self.precio_venta_stars = RealtyReport.get_price_stars(self.precio_desv_media)
        self.precio_alquiler_estimado = RealtyReport.get_price_alquiler_estimado(self.precio_alquiler_1y, self.sup_m2)
        self.precio_venta_estimado = RealtyReport.get_price_venta_estimado(self.precio_venta_1y, self.sup_m2)
        self.global_score_stars = RealtyReport.get_global_score_stars(self.precio_venta_stars, self.rentabilidad_10y_stars, self.grow_acu_venta_10y_stars, self.grow_acu_alquiler_10y_stars, self.disponibilidad)

    def to_dict(self):
        return {
            # Realty
            'link': self._link,
            'type_v': self._type_v,
            'address': self._address,
            'town': self._town,
            'price': self._price,
            'info': self._info,
            'description': self._description,
            'price_old': self._price_old,
            'tags': self._tags,
            'agent': self._agent,
            'created': self._created,

            # Property characteristics
            'n_hab': self.n_hab,
            'sup_m2': self.sup_m2,
            'disponibilidad': self.disponibilidad,

            # Location info
            'barrio': self.barrio,
            'barrio_ratio': self.barrio_ratio,
            'id': self.id,
            'nombre': self.nombre,
            'sup_id': self.sup_id,
            'sup_nombre': self.sup_nombre,
            'tipo': self.tipo,

            # Market statistics - 1y
            'precio_venta_1y': self.precio_venta_1y,
            'superficie_venta_1y': self.superficie_venta_1y,
            'elasticidad_1y': self.elasticidad_1y,
            'precio_alquiler_1y': self.precio_alquiler_1y,
            'rentabilidad_1y': self.rentabilidad_1y,
            'grow_acu_alquiler_1y': self.grow_acu_alquiler_1y,
            'grow_acu_venta_1y': self.grow_acu_venta_1y,
            'grow_acu_superficie_venta_1y': self.grow_acu_superficie_venta_1y,

            # Market statistics - 5y
            'precio_venta_5y': self.precio_venta_5y,
            'superficie_venta_5y': self.superficie_venta_5y,
            'elasticidad_5y': self.elasticidad_5y,
            'precio_alquiler_5y': self.precio_alquiler_5y,
            'rentabilidad_5y': self.rentabilidad_5y,
            'grow_acu_alquiler_5y': self.grow_acu_alquiler_5y,
            'grow_acu_venta_5y': self.grow_acu_venta_5y,
            'grow_acu_superficie_venta_5y': self.grow_acu_superficie_venta_5y,

            # Market statistics - 10y
            'precio_venta_10y': self.precio_venta_10y,
            'superficie_venta_10y': self.superficie_venta_10y,
            'elasticidad_10y': self.elasticidad_10y,
            'precio_alquiler_10y': self.precio_alquiler_10y,
            'rentabilidad_10y': self.rentabilidad_10y,
            'grow_acu_alquiler_10y': self.grow_acu_alquiler_10y,
            'grow_acu_venta_10y': self.grow_acu_venta_10y,
            'grow_acu_superficie_venta_10y': self.grow_acu_superficie_venta_10y,

            # Stars ratings
            'elasticidad_1y_stars': self.elasticidad_1y_stars,
            'rentabilidad_1y_stars': self.rentabilidad_1y_stars,
            'grow_acu_alquiler_1y_stars': self.grow_acu_alquiler_1y_stars,
            'grow_acu_venta_1y_stars': self.grow_acu_venta_1y_stars,
            'elasticidad_5y_stars': self.elasticidad_5y_stars,
            'rentabilidad_5y_stars': self.rentabilidad_5y_stars,
            'grow_acu_alquiler_5y_stars': self.grow_acu_alquiler_5y_stars,
            'grow_acu_venta_5y_stars': self.grow_acu_venta_5y_stars,
            'elasticidad_10y_stars': self.elasticidad_10y_stars,
            'rentabilidad_10y_stars': self.rentabilidad_10y_stars,
            'grow_acu_alquiler_10y_stars': self.grow_acu_alquiler_10y_stars,
            'grow_acu_venta_10y_stars': self.grow_acu_venta_10y_stars,
            'global_score_stars': self.global_score_stars,
    
            # Property analysis
            'precio_m2': self.precio_m2,
            'precio_desv_media': self.precio_desv_media,
            'precio_venta_stars': self.precio_venta_stars,
            'precio_alquiler_estimado': self.precio_alquiler_estimado,
            'precio_venta_estimado': self.precio_venta_estimado,
        }
    
    def __str__(self):
        return str(self.to_dict())

    @staticmethod
    def estandarizar(x):
        """ Estandariza el nombre de un barrio o distrito:
            - Quita entidades HTML y UTF-8
            - Normaliza el texto a forma NFD (descompone caracteres con diacríticos)
            - Filtra caracteres con categoría de diacrítico (Mn)
            - Pasa a minúsculas
            - Reemplaza guiones por espacios
            - Quita espacios dobles
        """
        # Unescape HTML and UTF-8 entities
        x = html.unescape(x)
        # Normalizar el texto a forma NFD (descompone caracteres con diacríticos)
        x = unicodedata.normalize('NFD', x)
        # Filtrar caracteres con categoría de diacrítico (Mn)
        x = ''.join(c for c in x if unicodedata.category(c) != 'Mn')
        return x.split(' - AEI ')[0].replace('-', ' ').replace('  ', ' ').lower()

    @staticmethod
    def get_town(x):
        x1 = ''.join(RealtyReport.RX_BARRIOS.findall(x)).strip() 
        x1 = x1 if len(x1)>1 else x
        return RealtyReport.estandarizar(x1)

    @staticmethod
    def clean_description(text: str) -> str:
        return RealtyReport.estandarizar(RealtyReport.RX_HTML_TAG.sub('', text.lower() if text else ''))
    
    @staticmethod
    def find_min_int(text, rx) -> Optional[int]:
        # Handle None or non-string input
        if text is None:
            return None
        
        # Convert to string if not already
        text = str(text)

        # Extract square meters
        matches = rx.findall(text)
        if matches:
            return int(min(matches))
        return None
    
    @staticmethod
    def get_occupation(text: str) -> str:
        if any(word.lower() in text.lower() for word in RealtyReport._okupadas_words): return 'ocupada'
        if any(word.lower() in text.lower() for word in RealtyReport._alquiladas_words): return 'alquilada'
        return 'disponible'
    
    @staticmethod
    def extract_tags(description: str) -> list[str]:
        tags = RealtyReport.RX_SINGLE_TAG.findall(description) + RealtyReport.RX_DOUBLE_TAG.findall(description)
        tags = list(dict.fromkeys(tags))
        return tags

    def match_place(self, places):

        matches = []
        for a in self.address.split(',') + self.town.split(','):
            matches.append(RealtyReport.map_place(a.strip(), places))
        
        # sort matches by 3 element
        matches = sorted(matches, key=lambda x: x[2])
        # get first non none match
        match = next((x for x in matches if x is not None), None)
        if match is not None:
            self.barrio , self.barrio_ratio = match[0], match[1]
    
    @staticmethod
    def map_place(x, places):
        if x is None: return None
        match = None
        best = 0
        place_idx = None
        for i, y in enumerate(places):
            ratio = SequenceMatcher(None, x, y).ratio()
            if ratio > best:
                place_idx = i
                best = ratio
                match = y
            if ratio == 1:
                break
        if(best > .5):
            return (match, best, place_idx)
        return None
    
    @staticmethod
    def get_price_m2(price, sup_m2) -> Optional[int]:
        # Handle None values
        if price is None or sup_m2 is None or sup_m2 == 0:
            return None
        
        return int(price / sup_m2)
    
    @staticmethod
    def get_price_desv_media(price_m2, price_venta_1y) -> Optional[float]:
        # Handle None values or zero division
        if price_m2 is None or price_venta_1y is None or price_venta_1y == 0:
            return None
        
        return round(price_m2 / price_venta_1y, 2)
    
    @staticmethod
    def get_price_stars(price_desv_media) -> Optional[int]:
        # Handle None values
        if price_desv_media is None:
            return None
        
        if price_desv_media < 0.25: return 5
        if price_desv_media < 0.40: return 4
        if price_desv_media < 0.75: return 3
        if price_desv_media < 1.00: return 2
        return 1
    
    @staticmethod
    def get_price_alquiler_estimado(precio_alquiler_1y, sup_m2) -> Optional[int]:
        # Handle None values
        if precio_alquiler_1y is None or sup_m2 is None:
            return None
        
        return int(precio_alquiler_1y * sup_m2)
    
    @staticmethod
    def get_price_venta_estimado(precio_venta_1y, sup_m2) -> Optional[int]:
        # Handle None values
        if precio_venta_1y is None or sup_m2 is None:
            return None
        
        return int(precio_venta_1y * sup_m2)

    @staticmethod
    def get_global_score_stars(precio_venta_stars, rentabilidad_10y_stars, grow_acu_venta_10y_stars, grow_acu_alquiler_10y_stars, disponibilidad) -> Optional[float]:
        # Handle None values
        if any(x is None for x in [precio_venta_stars, rentabilidad_10y_stars, grow_acu_venta_10y_stars, grow_acu_alquiler_10y_stars]):
            return None

        score = round((precio_venta_stars * RealtyReport.GLOBAL_SCORE_WEIGHTS['precio_venta_stars'] + 
                      rentabilidad_10y_stars * RealtyReport.GLOBAL_SCORE_WEIGHTS['rentabilidad_10y_stars'] + 
                      grow_acu_venta_10y_stars * RealtyReport.GLOBAL_SCORE_WEIGHTS['grow_acu_venta_10y_stars'] + 
                      grow_acu_alquiler_10y_stars * RealtyReport.GLOBAL_SCORE_WEIGHTS['grow_acu_alquiler_10y_stars']), 1)

        return score - 1 if disponibilidad == 'ocupada' else score

    @staticmethod
    def get_example():
        data = {
            'link': 'https://example.com/inmueble/123456/',
            'address': 'calle test 123',
            'town': 'Sant Andreu, Barcelona',
            'price': 250000,
            'description': "Piso en venta en<br> Barcelona reformado y con terraza ocupada",
            'created': '2024-03-20 10:00:00',
            'type_v': 'piso',
            'price_old': '260000.0',
            'info': "['80 m²', '3 hab.']",
            'tags': 'Reformado, Exterior',
            'agent': None,
            'n_hab': None,
            'sup_m2': 94,
            'disponibilidad': 'disponible',
            'barrio': 'la teixonera',
            'barrio_ratio': 1.0,
            'id': 80738,
            'nombre': 'la teixonera',
            'sup_id': 80700,
            'sup_nombre': 'horta guinardo',
            'tipo': 'barri',
            'precio_venta_1y': 2619.8571,
            'superficie_venta_1y': 456.0,
            'elasticidad_1y': -0.1742,
            'precio_alquiler_1y': 14.53,
            'rentabilidad_1y': 0.0666,
            'grow_acu_alquiler_1y': -0.1795621657754011,
            'grow_acu_venta_1y': -0.0280005530973451,
            'grow_acu_superficie_venta_1y': -0.209299628942486,
            'precio_venta_5y': 2464.8684,
            'superficie_venta_5y': 452.4286,
            'elasticidad_5y': -0.0438,
            'precio_alquiler_5y': 13.3635,
            'rentabilidad_5y': 0.065,
            'grow_acu_alquiler_5y': -0.0924861240233042,
            'grow_acu_venta_5y': 0.2326230426824659,
            'grow_acu_superficie_venta_5y': -0.5021826624677757,
            'precio_venta_10y': 2239.8145,
            'superficie_venta_10y': 1001.4476,
            'elasticidad_10y': 0.1162,
            'precio_alquiler_10y': 12.2823,
            'rentabilidad_10y': 0.0666,
            'grow_acu_alquiler_10y': 0.1589295902084413,
            'grow_acu_venta_10y': 0.2861947238519174,
            'grow_acu_superficie_venta_10y': 14.032363695636494,
            'elasticidad_1y_stars': 1,
            'rentabilidad_1y_stars': 4,
            'grow_acu_alquiler_1y_stars': 1,
            'grow_acu_venta_1y_stars': 3,
            'elasticidad_5y_stars': 1,
            'rentabilidad_5y_stars': 3,
            'grow_acu_alquiler_5y_stars': 1,
            'grow_acu_venta_5y_stars': 4,
            'elasticidad_10y_stars': 2,
            'rentabilidad_10y_stars': 3,
            'grow_acu_alquiler_10y_stars': 3,
            'grow_acu_venta_10y_stars': 3,
            'precio_m2': 1042,
            'precio_desv_media': 0.39773161673588986,
            'precio_venta_stars': 4,
            'precio_alquiler_estimado': 1365.82,
            'precio_venta_estimado': 246266.56740000003,
            'global_score_stars': 3.6
        }
        return RealtyReport(**data)
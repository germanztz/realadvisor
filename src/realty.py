from dataclasses import dataclass, field
from typing import Optional
import re
import unicodedata
import html
from difflib import SequenceMatcher

@dataclass
class Realty:
    # Basic property info
    _link: str = field(default=None, init=False, repr=False)
    _type_v: str = field(default=None, init=False, repr=False)
    _address: str = field(default=None, init=False, repr=False)
    _town: str = field(default=None, init=False, repr=False)
    _price: int = field(default=None, init=False, repr=False)
    _info: str = field(default=None, init=False, repr=False)
    _description: str = field(default=None, init=False, repr=False)
    _price_old: Optional[int] = field(default=None, init=False, repr=False)
    _tags: Optional[list[str]] = field(default=None, init=False, repr=False)
    _agent: Optional[float] = field(default=None, init=False, repr=False)
    _created: str = field(default=None, init=False, repr=False)

    _okupadas_words = ['okupada', 'okupado', 'ocupado', 'ocupada', 'ocupacional', 'sin posesión', 'sin posesion','ilegal']
    _alquiladas_words = ['alquilado', 'alquilada', 'inquilinos', 'inquilino', 'usufructuarios', 'usufructuario', 'arrendado']

    # Lista de palabras clave para el análisis inmobiliario
    _single_keywords = [
        "inversi.n", "oportunidad" ,"rendimiento", "renta.ilidad", "inversores", 'nuda\ propiedad'
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

    RX_HAB = re.compile(r'\'(\d+?) hab\.\'')
    RX_M2 = re.compile(r'\'(\d+?) m²\'')
    RX_BARRIOS = re.compile(r"([^,]+),[^,]+$")
    RX_CLEAN_DESCRIPTION = re.compile(r"<.*?>")

    RX_SINGLE_TAG = re.compile(r'\b(?:' + '|'.join(_single_keywords) + r')\b')
    RX_DOUBLE_TAG = re.compile(r'\b(\w+\s+(?:' + '|'.join(_double_keywords) + r'))\b')

    def __init__(self, link: str, type_v: str, address: str, town: str, price: int, info: str, 
                 description: str, price_old: Optional[int] = None, tags: Optional[str] = None, 
                 agent: Optional[float] = None, created: str = None):
        self.link = link
        self.type_v = type_v
        self.address = address
        self.town = town
        self.price = price
        self.info = info
        self.description = description
        self.price_old = price_old
        self.tags = tags
        self.agent = agent
        self.created = created

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def link(self):
        return self._link
    
    @link.setter 
    def link(self, value):
        self._link = value

    @property
    def type_v(self):
        return self._type_v
    
    @type_v.setter
    def type_v(self, value):
        self._type_v = value

    @property
    def address(self):
        return self._address
    
    @address.setter
    def address(self, value):
        self._address = value

    @property
    def town(self):
        return self._town
    
    @town.setter
    def town(self, value):
        self._town = value

    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        self._price = int(Realty.parse_price(value)) if Realty.parse_price(value) else None

    @property
    def info(self):
        return self._info
    
    @info.setter
    def info(self, value):
        self._info = value

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = self.clean_description(value)

    @property
    def price_old(self):
        return self._price_old
    
    @price_old.setter
    def price_old(self, value):
        self._price_old = int(Realty.parse_price(value)) if Realty.parse_price(value) else None
 
    @property
    def tags(self):
        return self._tags
    
    @tags.setter
    def tags(self, value):
        current_tags = self._tags or []
        if isinstance(value, list):
            self._tags = list(dict.fromkeys(current_tags + value))
        elif isinstance(value, str):
            self._tags = list(dict.fromkeys(current_tags + [tag.strip() for tag in value.split(',')]))
        else:
            self._tags = None

    @property
    def agent(self):
        return self._agent
    
    @agent.setter
    def agent(self, value):
        self._agent = value

    @property
    def created(self):
        return self._created
    
    @created.setter
    def created(self, value):
        self._created = value

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @classmethod
    def from_list_dict(cls, data: list) -> list:
        """Create a list of Realty objects from a list of dictionaries"""
        return [cls.from_dict(item) for item in data]
    
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
    def get_hood(x):
        x1 = ''.join(Realty.RX_BARRIOS.findall(x)).strip() 
        x1 = x1 if len(x1)>1 else x
        return Realty.estandarizar(x1)

    @staticmethod
    def clean_description(text: str) -> str:
        return Realty.RX_CLEAN_DESCRIPTION.sub('', text.lower() if text else '')
    
    @staticmethod
    def get_n_hab(text: str) -> int:
        return int(''.join(Realty.RX_HAB.findall(text))) if Realty.RX_HAB.findall(text) else None
    
    @staticmethod
    def get_sup_m2(text: str) -> int:
        return int(''.join(Realty.RX_M2.findall(text))) if Realty.RX_M2.findall(text) else None
    
    @staticmethod
    def get_occupation(text: str) -> str:
        if any(word.lower() in text.lower() for word in Realty._okupadas_words): return 'ocupada'
        if any(word.lower() in text.lower() for word in Realty._alquiladas_words): return 'alquilada'
        return 'disponible'
    
    @staticmethod
    def extract_tags(description: str) -> list[str]:
        tags = Realty.RX_SINGLE_TAG.findall(description) + Realty.RX_DOUBLE_TAG.findall(description)
        tags = list(dict.fromkeys(tags))
        return tags
    
    @staticmethod
    def map_place(x, places):
        match = None
        best = 0
        for y in places:
            ratio = SequenceMatcher(None, x, y).ratio()
            if ratio == 1:
                return (y, ratio)
            if ratio > best:
                best = ratio
                match = y
        return (match if best > 0.5 else None, round(best,2))

    @staticmethod
    def parse_price(value) -> Optional[float]:
        """Convert string numbers to integer, handling different formats"""

        # Remove currency symbols and spaces
        value = str(value).strip().replace('€', '').replace(' ', '')
        dots = value.count('.')
        commas = value.count(',')
        value = value.replace('.', ',').split(',')

        if commas == 0 and dots == 0 and value[0].isdigit():
            # Format: 123456 -> 123456.0
            return float(value[0])
        elif dots > 0 and commas > 0:
            # Format: 123.456.789,01 -> 123456789.01
            # Format: 123,456,789.01 -> 123456789.01
            return float(f'{"".join(value[:-1])}.{value[-1]}')
        elif commas == 1 or dots == 1:
            if len(value[-1]) != 3 or len(value[-2]) > 3:
                # Format: 1234.567 -> 1234.567
                # Format: 123456,7 -> 123456.7
                # Format: 123.4567 -> 123.4567
                # Format: 123,45 -> 123.45
                return float(f'{"".join(value[:-1])}.{value[-1]}')
            else:
                # Format: 12.345 -> 12345.0
                # Format: 12,345 -> 12345.0
                return float("".join(value))
        elif commas > 1 or dots > 1:
            # Format: 1.234.567 -> 1234567.0
            # Format: 1,234,567 -> 1234567.0    
            return float("".join(value))
        else:
            return None

    def to_dict(self):
        return {
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
            'created': self._created
        }

    def __str__(self):
        return f"""
        {self._type_v.title()} en {self._address}
        Precio: {self._price:,}€
        Info: {self._info}
        Descripción: {self._description}
        Tags: {self._tags or 'N/A'}
        Creado: {self._created}
        """ 
 
    def __eq__(self, other):
        return self._link == other._link

    def __hash__(self):
        return hash(self._link)

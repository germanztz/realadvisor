from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Realty:
    # Basic property info
    _created: str = field(default=None, init=False, repr=False)
    _link: str = field(default=None, init=False, repr=False)
    _price: int = field(default=None, init=False, repr=False)
    _rooms: int = field(default=None, init=False, repr=False)
    _surface: int = field(default=None, init=False, repr=False)
    _description: str = field(default=None, init=False, repr=False)
    _address: str = field(default=None, init=False, repr=False)
    _town: str = field(default=None, init=False, repr=False)
    _type_v: Optional[str] = field(default=None, init=False, repr=False)
    _info: Optional[str] = field(default=None, init=False, repr=False)
    _price_old: Optional[int] = field(default=None, init=False, repr=False)
    _tags: Optional[list[str]] = field(default=None, init=False, repr=False)
    _agent: Optional[str] = field(default=None, init=False, repr=False)


    def __init__(self, link: str, type_v: str, address: str, town: str, price: int, rooms: int, surface: int, info: str, 
                 description: str, price_old: Optional[int] = None, tags: Optional[str] = None, 
                 agent: Optional[float] = None, created: str = None):
        
        self.__init__({'link': link,'type_v': type_v,'address': address,'town': town,'price': price, 'rooms': rooms, 'surface': surface,
            'info': info,'description': description,'price_old': price_old,'tags': tags,
            'agent': agent,'created': created })

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if self._town != self._address:
            self._address = self._address + ', ' + self._town

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
    def rooms(self):
        return self._rooms
    
    @rooms.setter
    def rooms(self, value):
        self._rooms = value

    @property
    def surface(self):
        return self._surface
    
    @surface.setter
    def surface(self, value):
        self._surface = value

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
        self._description = value

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

    def to_dict(self):
        return {
            'link': self._link,
            'type_v': self._type_v,
            'address': self._address,
            'town': self._town,
            'price': self._price,
            'rooms': self._rooms,
            'surface': self._surface,
            'info': self._info,
            'description': self._description,
            'price_old': self._price_old,
            'tags': self._tags,
            'agent': self._agent,
            'created': self._created
        }

    def __str__(self):
        return str(self.to_dict())
    
    def to_markdown(self):
        return str("".join([f"- **{key}:** {value}\n" for (key, value) in self.to_dict().items()]))

    def __eq__(self, other):
        return self._link == other._link

    def __hash__(self):
        return hash(self._link)
    
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

    @staticmethod
    def get_sample():
        return Realty(**Realty.get_sample_data())
    
    @staticmethod
    def get_sample_data():
        return {
            'link': 'https://example.com/inmueble/123456/',
            'address': 'calle test 123',
            'town': 'Sant Andreu, Barcelona',
            'price': 250000,
            'rooms': 3,
            'surface': 80,
            'description': "Piso en venta en<br> Barcelona reformado y con terraza ocupada",
            'created': '2024-03-20 10:00:00',
            'type_v': 'piso',
            'price_old': '260000.0',
            'info': "['80 m²', '3 hab.']",
            'tags': 'Reformado, Exterior',
            'agent': None,
        }
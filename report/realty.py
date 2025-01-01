from dataclasses import dataclass
from typing import Optional

@dataclass
class Realty:
    # Basic property info
    link: str
    type_v: str
    address: str
    town: str
    price: int
    price_old: Optional[float]
    info: str
    description: str
    tags: Optional[str]
    agent: Optional[float]
    created: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def __str__(self):
        return f"""
        {self.type_v.title()} en {self.address}
        Precio: {self.price:,}€
        Info: {self.info}
        Descripción: {self.description}
        Tags: {self.tags or 'N/A'}
        Creado: {self.created}
        """ 
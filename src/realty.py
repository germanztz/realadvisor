from dataclasses import dataclass
from typing import Optional
import re
import unicodedata
import html
from difflib import SequenceMatcher

@dataclass
class Realty:
    # Basic property info
    link: str
    type_v: str
    address: str
    town: str
    price: int
    info: str
    description: str
    price_old: Optional[int]
    tags: Optional[str]
    agent: Optional[float]
    created: str

    okupadas_words = ['okupada', 'okupado', 'ocupado', 'ocupada', 'ocupacional', 'sin posesión', 'sin posesion','ilegal']
    alquiladas_words = ['alquilado', 'alquilada', 'inquilinos', 'inquilino', 'usufructuarios', 'usufructuario', 'arrendado']


    # Lista de palabras clave para el análisis inmobiliario
    single_keywords = [
        "inversi.n", "oportunidad" ,"rendimiento", "renta.ilidad", "inversores", 'nuda\ propiedad'
        "rehabilitad.", "metro", 
        "estacionamiento", "calefacci.n", "la.adero",
        "terraza", "luminoso", "balc.n", "patio",
        "bajo", "local", "estudio"
    ]

    double_keywords = [
        "reforma.?", "reformad.", "integral", "c.dula",
        "baños","banos", "ascensor", "amueblad.","blindad.",
        "exterior", "comercial"
    ]

    hab_rx = re.compile(r'\'(\d+?) hab\.\'')
    m2_rx = re.compile(r'\'(\d+?) m²\'')
    barrio_rx = re.compile(r"([^,]+),[^,]+$")
    clean_description_rx = re.compile(r"<.*?>")

    single_tag_rx = re.compile(r'\b(?:' + '|'.join(single_keywords) + r')\b')
    double_tag_rx = re.compile(r'\b(\w+\s+(?:' + '|'.join(double_keywords) + r'))\b')

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

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
        x1 = ''.join(Realty.barrio_rx.findall(x)).strip() 
        x1 = x1 if len(x1)>1 else x
        return Realty.estandarizar(x1)

    @staticmethod
    def clean_description(text: str) -> str:
        return Realty.clean_description_rx.sub('', text.lower() if text else '')
    
    @staticmethod
    def get_n_hab(text: str) -> int:
        return int(''.join(Realty.hab_rx.findall(text))) if Realty.hab_rx.findall(text) else None
    
    @staticmethod
    def get_sup_m2(text: str) -> int:
        return int(''.join(Realty.m2_rx.findall(text))) if Realty.m2_rx.findall(text) else None
    
    @staticmethod
    def get_occupation(text: str) -> str:
        if any(word.lower() in text.lower() for word in Realty.okupadas_words): return 'ocupada'
        if any(word.lower() in text.lower() for word in Realty.alquiladas_words): return 'alquilada'
        return 'disponible'
    
    @staticmethod
    def get_tags(text: str) -> list[str]:
        tags = Realty.single_tag_rx.findall(text) + Realty.double_tag_rx.findall(text)
        return list(dict.fromkeys(tags))
    
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

    
    def __str__(self):
        return f"""
        {self.type_v.title()} en {self.address}
        Precio: {self.price:,}€
        Info: {self.info}
        Descripción: {self.description}
        Tags: {self.tags or 'N/A'}
        Creado: {self.created}
        """ 
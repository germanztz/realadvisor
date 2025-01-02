from dataclasses import dataclass
from typing import Optional
from src.realty import Realty

@dataclass
class RealtyReport(Realty):
    # Property characteristics (additional to Realty)
    n_hab: Optional[int]
    sup_m2: int
    disponibilidad: str
    
    # Location info
    barrio: str
    barrio_ratio: float
    id: int
    nombre: str
    sup_id: int
    sup_nombre: str
    tipo: str
    
    # Market statistics - 1y
    precio_venta_1y: float
    superficie_venta_1y: float
    elasticidad_1y: float
    precio_alquiler_1y: float
    rentabilidad_1y: float
    grow_acu_alquiler_1y: float
    grow_acu_venta_1y: float
    grow_acu_superficie_venta_1y: float
    
    # Market statistics - 5y
    precio_venta_5y: float
    superficie_venta_5y: float
    elasticidad_5y: float
    precio_alquiler_5y: float
    rentabilidad_5y: float
    grow_acu_alquiler_5y: float
    grow_acu_venta_5y: float
    grow_acu_superficie_venta_5y: float
    
    # Market statistics - 10y
    precio_venta_10y: float
    superficie_venta_10y: float
    elasticidad_10y: float
    precio_alquiler_10y: float
    rentabilidad_10y: float
    grow_acu_alquiler_10y: float
    grow_acu_venta_10y: float
    grow_acu_superficie_venta_10y: float
    
    # Stars ratings
    elasticidad_1y_stars: int
    rentabilidad_1y_stars: int
    grow_acu_alquiler_1y_stars: int
    grow_acu_venta_1y_stars: int
    elasticidad_5y_stars: int
    rentabilidad_5y_stars: int
    grow_acu_alquiler_5y_stars: int
    grow_acu_venta_5y_stars: int
    elasticidad_10y_stars: int
    rentabilidad_10y_stars: int
    grow_acu_alquiler_10y_stars: int
    grow_acu_venta_10y_stars: int
    global_score_stars: float
    
    # Property analysis
    precio_m2: int
    precio_desv_media: float
    precio_venta_stars: int
    precio_alquiler_estimado: float
    precio_venta_estimado: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    
    def __str__(self):
        def stars_to_emoji(stars):
            if isinstance(stars, (int, float)):
                full_stars = int(stars)
                return "⭐" * full_stars
            return ""

        # Split tags and add emoji
        tags_list = self.tags.split(", ") if self.tags else []
        formatted_tags = [f"🏷️ {tag}" for tag in tags_list]
        tags_str = " ".join(formatted_tags)

        # Get availability emoji
        availability_emoji = {
            'disponible': '✅',
            'alquilada': '⚠️',
            'ocupada': '🚨'
        }.get(self.disponibilidad.lower(), '')

        markdown = f"""
        **{self.type_v} En [{self.address.title()}]({self.link})** {stars_to_emoji(self.global_score_stars)}

        ### Análisis de Inversión

        - **Estrellas Globales:** {stars_to_emoji(self.global_score_stars)} ({self.global_score_stars})
        - **Estrellas de Precio:** {stars_to_emoji(self.precio_venta_stars)} ({self.precio_venta_stars})
        - **Estrellas de Rentabilidad:** {stars_to_emoji(self.rentabilidad_10y_stars)} ({self.rentabilidad_10y_stars})
        - **Rentabilidad:** {self.rentabilidad_10y *100:.2f} %

        ### Información Básica

        - **precio:** {self.price} €
        - **metros cuadrados:** {self.sup_m2} m2
        - **precio_m2:** {self.precio_m2} €/m2 ({stars_to_emoji(self.precio_venta_stars)}) ya que es un {self.precio_desv_media*100:.0f}% del precio medio de venta de {self.barrio} : {self.precio_venta_1y} €/m2
        - **alquiler estimado:** {self.precio_alquiler_estimado} €/mes
        - **venta estimada:** {self.precio_venta_estimado} €
        - **habitaciones:** {self.n_hab}
        - **descripcion:** ```{self.description}```
        - **tags:** {tags_str}
        - **barrio:** {self.barrio}
        - **creado:** {self.created}
        - **disponibilidad:** ```{self.disponibilidad}``` {availability_emoji}
        """        
        return markdown
    @staticmethod
    def get_example():
        data = {
            'link': '/inmueble/101395290/',
            'type_v': 'estudio',
            'address': 'calle de la mare de deu dels angels, la teixonera, barcelona',
            'town': 'la teixonera',
            'price': 98000,
            'price_old': None,
            'info': "['94 m²', 'Bajo exterior sin ascensor']",
            'description': "cerca parc creueta del coll y junto hospital vall d'hebron y hospital san rafael. calle mare deu dels angels, amplio local de 90 metros aproximadamente, diafano, apto para loft vivienda, entrada por calle y vestibulo, cocina, bano completo y dos aseos, puerta y ventana a la calle, comunicado por metro linea l5 y autobu",
            'tags': 'Loft, local, metro',
            'agent': None,
            'created': '2024-11-20 14:43:11',
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
        return RealtyReport.from_dict(data)
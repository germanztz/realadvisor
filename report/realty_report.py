from dataclasses import dataclass
from typing import Optional

@dataclass
class RealtyReport:
    # Basic property info
    link: str
    type_v: str
    address: str
    town: str
    price: float
    price_old: Optional[float]
    info: str
    description: str
    tags: str
    agent: str
    created: str
    
    # Property characteristics
    n_hab: Optional[int]
    sup_m2: Optional[int]
    disponibilidad: str
    
    # Investment metrics
    precio_venta_stars: int
    precio_alquiler_estimado: float
    precio_venta_estimado: float
    
    # Location info
    barrio: str
    sup_nombre: str
    tipo: str
    
    # Market statistics
    precio_venta_10y: float
    precio_venta_1y: float
    precio_venta_5y: float
    precio_alquiler_10y: float
    precio_alquiler_1y: float
    precio_alquiler_5y: float
    
    # Market performance
    rentabilidad_10y: float
    rentabilidad_1y: float
    rentabilidad_5y: float
    
    # Growth metrics
    grow_acu_alquiler_10y: float
    grow_acu_venta_10y: float
    grow_acu_alquiler_1y: float
    grow_acu_venta_1y: float
    grow_acu_alquiler_5y: float
    grow_acu_venta_5y: float
    
    # Property analysis
    precio_m2: float
    precio_desv_media: float

    def get_investment_score(self) -> float:
        """Calculate overall investment score (0-10)"""
        weights = {
            'price_stars': 0.3,
            'rentability': 0.3,
            'growth': 0.2,
            'location': 0.2
        }
        
        price_score = self.precio_venta_stars * 2  # Convert 0-5 to 0-10
        rent_score = (self.rentabilidad_1y / 0.05) * 10  # 5% annual return = 10 points
        growth_score = ((self.grow_acu_alquiler_5y + self.grow_acu_venta_5y) / 2) * 10
        
        return (
            price_score * weights['price_stars'] +
            rent_score * weights['rentability'] +
            growth_score * weights['growth']
        )

    def get_roi_estimation(self) -> float:
        """Calculate estimated annual ROI"""
        annual_rent = self.precio_alquiler_estimado * 12
        return (annual_rent / self.price) * 100 if self.price else 0 
from dataclasses import dataclass

@dataclass
class RealtyMetrics:
    # Basic information
    id: int
    nombre: str
    sup_id: int
    sup_nombre: str
    tipo: str
    
    # 1 year metrics
    precio_venta_1y: float
    superficie_venta_1y: float
    elasticidad_1y: float
    precio_alquiler_1y: float
    rentabilidad_1y: float
    grow_acu_alquiler_1y: float
    grow_acu_venta_1y: float
    grow_acu_superficie_venta_1y: float
    
    # 5 year metrics
    precio_venta_5y: float
    superficie_venta_5y: float
    elasticidad_5y: float
    precio_alquiler_5y: float
    rentabilidad_5y: float
    grow_acu_alquiler_5y: float
    grow_acu_venta_5y: float
    grow_acu_superficie_venta_5y: float
    
    # 10 year metrics
    precio_venta_10y: float
    superficie_venta_10y: float
    elasticidad_10y: float
    precio_alquiler_10y: float
    rentabilidad_10y: float
    grow_acu_alquiler_10y: float
    grow_acu_venta_10y: float
    grow_acu_superficie_venta_10y: float
    
    # Star ratings
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
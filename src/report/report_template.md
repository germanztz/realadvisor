# Informe de Inversión Inmobiliaria
    
**{{ type_v }} En [{{ address|title }}]({{ link }})** {{ stars_to_emoji_string }}

### Análisis de Inversión

- **Estrellas Globales:** {{ stars_to_emoji_string }} ({{ global_score_stars }})
- **Estrellas de Precio:** {{ stars_to_emoji_string }} ({{ precio_venta_stars }})
- **Estrellas de Rentabilidad:** {{ stars_to_emoji_string }} ({{ rentabilidad_10y_stars }})
- **Rentabilidad:** {{ (rentabilidad_10y * 100) }} %

### Información Básica

- **precio:** {{ price }} €
- **metros cuadrados:** {{ surface }} m2
- **precio_m2:** {{ precio_m2 }} €/m2 ({{ stars_to_emoji_string }}) ya que es un {{ (precio_desv_media * 100) }}% del precio medio de venta de {{ barrio }} : {{ precio_venta_1y }} €/m2
- **alquiler estimado:** {{ precio_alquiler_estimado }} €/mes
- **venta estimada:** {{ precio_venta_estimado }} €
- **habitaciones:** {{ rooms }}
- **descripcion:** ```{{ description }}```
- **tags:** {{ tags_to_emoji_string }}
- **barrio:** {{ barrio }}
- **creado:** {{ created }}
- **disponibilidad:** ```{{ disponibilidad }}``` {{ availability_to_emoji_string }}
# Proyecto Integrador: Predictor de demanda para redes eléctricas

## Comprensión del negocio

En este bloque se explora a grandes rasgos los objetivos, fuentes, preparaciones pertinentes y evaluaciones que se realizarán a lo largo del proyecto.

| Bloque | Fase | Descripción |
| --- | --- | --- |
| Objetivo del negocio | Negocio | Predecir la demanda energética para optimizar el uso de fuentes renovables. |
| Valor del proyecto | Negocio | - **Económico:** Optimización de costes de infraestructura, venta de posibles excedentes de energía y menor dependencia de combustibles fósiles. <br><br> - **Medio ambiente:** Reducción en la contaminación del medio ambiente mediante el uso de fuentes renovables. |
| Fuentes de datos | Datos | - **API Red Eléctrica:** API con datos de Red Eléctrica España públicos. https://www.ree.es/es/datos/apidatos <br><br> - **Historial Climático:** Archivo excel con el histórico del clima publicado por la AEMET desde el 2013 hasta la actualidad. https://datosclima.es/Aemet2013/DescargaDatos.html <br><br> - **TODO** |
| Variable objetivo | Datos | **Numérica:** Predicción de consumo para un día determinado. |
| Calidad y riesgos | Datos | - **Calidad:** Pueden existir valores no válidos en los datos obtenidos por la API o el historial climático. <br><br> **Riesgos:** La demanda energética puede depende del calendario (festivos, fines de semana, vacaciones, estaciones...). |
| Preparación y features | Preparación | TODO |
| Modelado | Modelado | Uso de algoritmos de regresión basados en series temporales. |
| Evaluación (KPIs) | Evaluación | - **Técnico:** Priorizar la `precisión (accuracy)` sobre la `sensibilidad (recall)`. Obtener una precisión > 0.85. <br><br> - **Negocio:** TODO |
| Despliegue y uso | Despliege | Panel de control o dashboard interactivo para representar los valores de forma rápida y visual. |

## Comprensión de los datos

En este bloque se realizará una exploración rápida sobre los datos disponibles, identificaciones posibles relaciones y/o modificaciones y transformaciones que puedan ser adecuadas más adelante. 


```python
import datetime
```

### API Red Eléctrica


```python
API_REE_URL = "https://apidatos.ree.es"

endpoint = "/es/datos/demanda/ire-general"

start_date = datetime.datetime(2013, 1, 1)
print(start_date)
```

    2013-01-01 00:00:00


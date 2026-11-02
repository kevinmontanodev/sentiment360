# Evaluación del prototipo — Sentiment360

## 1. Objetivo

La fase de evaluación busca analizar el prototipo conceptual de Sentiment360 e identificar fortalezas, limitaciones y oportunidades de mejora en su diseño.

Debido a las restricciones de tiempo del proyecto, se realizó una evaluación heurística por parte del equipo, sin una sesión formal de pruebas de usabilidad con usuarios.

## 2. Método de evaluación

Se realizó una revisión del prototipo generado mediante Google Stitch, considerando los siguientes criterios:

- Claridad de la navegación.
- Consistencia visual.
- Jerarquía y organización de la información.
- Comprensión de las visualizaciones.
- Correspondencia entre funcionalidades y necesidades identificadas.
- Coherencia con la arquitectura conceptual de Sentiment360.

La evaluación se centró en las cuatro vistas propuestas: resumen general, exploración de opiniones, tendencias y problemas frecuentes.

## 3. Resultados de la evaluación heurística

| Criterio | Observación | Valoración |
|---|---|---|
| Navegación | El menú lateral permite identificar las principales secciones del prototipo. | Favorable |
| Consistencia visual | Las vistas mantienen una identidad visual y una estructura coherentes. | Favorable |
| Jerarquía de información | Los indicadores y gráficas permiten distinguir diferentes niveles de información. | Favorable |
| Comprensión de gráficas | Las visualizaciones ofrecen una representación inicial de la información, aunque requieren datos y etiquetas claramente contextualizados. | Mejorable |
| Correspondencia con necesidades | Las vistas representan las funcionalidades priorizadas durante la ideación. | Favorable |
| Confiabilidad | Los datos ilustrativos deben diferenciarse claramente de resultados reales. | Mejorable |
| Integración técnica | La interfaz no está conectada a una API ni a modelos ejecutables. | Pendiente |

## 4. Fortalezas identificadas

Durante la revisión del prototipo se identificaron las siguientes fortalezas:

- Organización de funcionalidades mediante vistas especializadas.
- Presentación de indicadores y gráficas en un resumen general.
- Separación entre exploración de opiniones y análisis agregado.
- Propuesta de visualización temporal de sentimientos.
- Identificación de temas frecuentes como apoyo a la interpretación.
- Consistencia visual entre las pantallas generadas.

Estas características contribuyen a representar de forma comprensible la experiencia de usuario propuesta para Sentiment360.

## 5. Oportunidades de mejora

Se identificaron las siguientes oportunidades de mejora:

| Aspecto | Mejora propuesta |
|---|---|
| Datos ilustrativos | Incorporar indicadores que distingan datos simulados de resultados reales. |
| Visualizaciones | Mejorar etiquetas, leyendas y contextualización de las gráficas. |
| Predicciones | Incorporar información sobre la clasificación y sus probabilidades cuando exista integración con el modelo. |
| Exploración | Permitir filtros por sentimiento, período y categoría. |
| Accesibilidad | Revisar contraste, tamaños de texto y legibilidad. |
| Navegación | Validar que todas las secciones sean comprensibles y accesibles. |
| Integración | Implementar posteriormente la conexión con FastAPI y los modelos. |

## 6. Validación pendiente con usuarios

La evaluación heurística no sustituye las pruebas de usabilidad con usuarios potenciales.

Como trabajo futuro, se propone realizar sesiones de evaluación en las que participantes puedan:

- Identificar la distribución general de sentimientos.
- Consultar una opinión individual.
- Interpretar una tendencia temporal.
- Identificar un problema recurrente.
- Expresar qué información adicional necesitarían.

La retroalimentación permitiría identificar dificultades de comprensión y ajustar las funcionalidades del prototipo.

## 7. Limitaciones

- La evaluación fue realizada por el equipo y no mediante pruebas formales con usuarios.
- No se recopilaron métricas de tiempo de ejecución, eficiencia de interacción o satisfacción de usabilidad.
- No se verificó la integración con modelos ni servicios backend.
- Las observaciones corresponden al diseño visual y conceptual.
- Las conclusiones no deben interpretarse como evidencia de usabilidad validada.

## 8. Conclusión

La evaluación heurística permitió revisar la organización, consistencia visual y correspondencia funcional del prototipo de Sentiment360 con las necesidades identificadas durante la encuesta exploratoria.

Se identificaron fortalezas en la organización de vistas y presentación de información, así como oportunidades de mejora relacionadas con contextualización de datos, visualizaciones, accesibilidad e integración técnica.

El prototipo constituye una representación inicial de la solución propuesta y una base para futuras iteraciones y pruebas de usabilidad.
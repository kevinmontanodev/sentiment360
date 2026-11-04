# Product Backlog — Sentiment360

## 1. Marco de gestión

El proyecto **Sentiment360** se desarrolla bajo el marco de trabajo **Scrum**, adoptando la **Opción B: Product Backlog Scrum** establecida en la guía de evaluación.

El trabajo se organiza mediante historias de usuario, estimaciones en Story Points y sprints con objetivos y entregables definidos.

## 2. Resumen del backlog

| ID | Historia de usuario | Sprint | Estimación | Estado |
|---|---|---|---:|---|
| US-01 | Documentar y validar el dataset | Sprint 1 | 3 SP | Terminada |
| US-02 | Almacenar reseñas en MongoDB | Sprint 1 | 3 SP | Terminada |
| US-03 | Procesar reseñas con Dask | Sprint 1 | 3 SP | Terminada |
| US-04 | Procesar datos con PySpark | Sprint 1 | 3 SP | Terminada |
| US-05 | Simular almacenamiento de objetos | Sprint 1 | 3 SP | Terminada |
| US-06	| Entrenar y comparar modelos clásicos | Sprint 2 | 5 SP |	Terminada |
| US-07	| Entrenar y evaluar Deep Learning | Sprint 2 | 5 SP | Terminada |
| US-08	| Optimizar umbral mediante matriz de costos |	Sprint 2 | Por definir | Terminada |
| US-09	| Documentar bitácora de desarrollo | Sprint 2 | Por definir | Terminada |
| US-10	| Validar propuesta mediante Design Thinking |	Sprint 2 | Por definir | Terminada |
| US-11 | Evaluar viabilidad tecnológica y financiera |	Sprint 2 | Por definir | Terminada |

**Nota:** Las estimaciones corresponden a los puntos iniciales definidos para cada historia.

---

# 3. Historias de usuario

## US-01: Documentar y validar el dataset

**Historia de usuario**

Como equipo de desarrollo, queremos conocer la estructura y las condiciones de uso del dataset para preparar un flujo reproducible.

**Criterios de aceptación**

- [x] Documentar la fuente, las condiciones de uso y la atribución.
- [x] Identificar las columnas y los tipos de datos.
- [x] Analizar las cinco etiquetas y su distribución.
- [x] Revisar valores nulos y registros duplicados.
- [x] Definir la estrategia de clasificación.
- [x] Registrar cómo reproducir la preparación de los datos.

**Sprint:** Sprint 1 — Ingesta y almacenamiento  
**Estimación inicial:** 3 puntos  
**Estado:** Terminada

## US-02: Almacenar reseñas en MongoDB

**Historia de usuario**

Como desarrollador, quiero cargar las reseñas en MongoDB para conservar los datos originales y consultarlos posteriormente.

**Criterios de aceptación**

- [x] Conexión configurable mediante variables de entorno.
- [x] Validación del esquema de entrada.
- [x] Evitar duplicados al repetir una carga.
- [x] Verificar el número de documentos insertados.
- [x] Probar los casos principales con pruebas automatizadas.

**Sprint:** Sprint 1 — Ingesta y almacenamiento  
**Prioridad:** Alta  
**Estimación inicial:** 3 puntos  
**Estado:** Terminada

## US-03: Procesar reseñas con Dask

**Historia de usuario**

Como analista de datos, quiero limpiar y transformar las reseñas utilizando Dask, para preparar un conjunto de datos consistente para el entrenamiento de modelos.

**Criterios de aceptación**

- [x] Leer las reseñas originales almacenadas en MongoDB.
- [x] Gestionar valores nulos, campos ausentes y registros inválidos.
- [x] Normalizar el texto sin eliminar información útil para la clasificación del sentimiento.
- [x] Conservar el identificador y la etiqueta original de las reseñas válidas.
- [x] Guardar los datos procesados en formato Parquet dentro de `data/processed/`.
- [x] Verificar que el archivo Parquet pueda leerse y que los registros y las etiquetas cumplan las condiciones esperadas.
- [x] Documentar las reglas de limpieza y las cantidades de registros leídos, conservados y rechazados.

**Sprint:** Sprint 1 — Ingesta y almacenamiento  
**Estimación inicial:** 3 puntos  
**Estado:** Terminada

## US-04: Procesar datos con PySpark

**Historia de usuario**

Como integrante del equipo, quiero procesar el conjunto de datos preparado mediante PySpark en modo local y comparar sus operaciones con Dask, para comprender y documentar sus enfoques de procesamiento.

**Criterios de aceptación**

- [x] Crear y configurar una sesión Spark en modo local.
- [x] Leer el archivo Parquet generado por la US-03.
- [x] Utilizar la API de DataFrames de PySpark para realizar transformaciones y al menos una agregación significativa, como contar las reseñas por etiqueta.
- [x] Explicar la diferencia entre transformaciones perezosas y acciones en Spark.
- [x] Realizar una operación equivalente con Dask sobre el mismo conjunto de datos.
- [x] Comprobar que los resultados de ambas herramientas sean consistentes.
- [x] Documentar la comparación y explicar en qué situaciones conviene utilizar cada herramienta.

**Entrada:** Parquet generado por la US-03.  
**Salida:** procesamiento con PySpark, resultados verificables y documentación comparativa.  
**Sprint:** Sprint 1 — Ingesta y almacenamiento  
**Estimación inicial:** 3 puntos  
**Estado:** Terminada

## US-05: Simular almacenamiento de objetos

**Historia de usuario**

Como desarrollador, quiero almacenar y recuperar un artefacto de datos del pipeline mediante un servicio local compatible con S3, para demostrar el almacenamiento desacoplado de los procesos de ingesta y transformación.

**Criterios de aceptación**

- [x] Levantar MinIO localmente mediante Docker Compose.
- [x] Configurar el endpoint, las credenciales y el nombre del bucket mediante variables de entorno.
- [x] Subir y recuperar un archivo utilizando una biblioteca compatible con S3, como `boto3`.
- [x] Utilizar como artefacto el archivo Parquet generado por la US-03, o una muestra reproducible si su tamaño dificulta las pruebas.
- [x] Verificar que el archivo recuperado sea legible y que su contenido coincida con el original.
- [x] Mantener las credenciales fuera del control de versiones.
- [x] Documentar la configuración y los pasos para iniciar MinIO, subir el archivo y recuperarlo.

**Entrada:** artefacto Parquet generado por la US-03.  
**Salida:** archivo almacenado y recuperado correctamente desde MinIO.  
**Dependencia:** US-03.  
**Sprint:** Sprint 1 — Ingesta y almacenamiento  
**Estimación inicial:** 3 puntos  
**Estado:** Terminada

---

## US-06: Entrenar y comparar modelos clásicos de Machine Learning

**Historia de usuario**

Como analista de datos, quiero evaluar diferentes familias de algoritmos clásicos utilizando una línea base y procedimientos de validación rigurosos, para identificar el modelo con mejor desempeño en la clasificación de sentimientos.

**Criterios de aceptación**

- [x] Implementar un modelo de referencia (*Dummy Classifier*) que permita establecer un rendimiento mínimo.
- [x] Evaluar al menos tres familias de algoritmos:
  - Modelos lineales: Regresión Logística.
  - Modelos basados en árboles: Random Forest.
  - Modelos de margen o distancia: SVM o k-NN.
- [x] Dividir los datos en conjuntos de entrenamiento y prueba, conservando la distribución de las cinco etiquetas mediante estratificación.
- [x] Incorporar el preprocesamiento del texto, incluyendo TF-IDF, dentro de pipelines para prevenir la fuga de información.
- [x] Aplicar validación cruzada y búsqueda de hiperparámetros mediante GridSearchCV o RandomizedSearchCV.
- [x] Evaluar los modelos utilizando accuracy, precisión, recall y F1-score.
- [x] Analizar el desempeño por clase mediante métricas y matriz de confusión.
- [x] Seleccionar el mejor modelo clásico según métricas justificadas para el problema.
- [x] Documentar los experimentos y presentar una tabla comparativa de resultados en el README.md.

**Consideraciones metodológicas**

La división estratificada será adecuada para este problema de clasificación de reseñas, siempre que no se plantee una predicción temporal. Cualquier transformación que aprenda parámetros de los datos deberá ajustarse exclusivamente con los datos de entrenamiento mediante los pipelines.

**Sprint:** Sprint 2 — Machine Learning y Deep Learning  
**Estimación inicial:** 5 puntos  
**Estado:** Terminada

---

## US-07: Entrenar y evaluar un modelo de Deep Learning

**Historia de usuario**

Como investigador, quiero evaluar una arquitectura neuronal para clasificación de texto y compararla con el mejor modelo clásico, para determinar si el aprendizaje profundo aporta mejoras al problema de análisis de sentimientos.

**Criterios de aceptación**

- [x] Definir y justificar la arquitectura de la red neuronal seleccionada.
- [x] Implementar y entrenar un modelo de Deep Learning utilizando una representación adecuada del texto.
- [x] Mantener una separación rigurosa entre entrenamiento, validación y prueba.
- [x] Aplicar medidas de regularización cuando corresponda, como Dropout y Early Stopping.
- [x] Registrar las métricas de entrenamiento y validación durante las épocas.
- [x] Generar y analizar curvas de aprendizaje (*loss* y métricas de desempeño).
- [x] Evaluar el modelo con accuracy, precisión, recall y F1-score.
- [x] Analizar los errores mediante una matriz de confusión y métricas por clase.
- [x] Comparar los resultados del modelo neuronal con el mejor modelo clásico obtenido en la US-06.
- [x] Documentar la arquitectura, los experimentos y las conclusiones en el README.md.

**Dependencia:** US-06, para disponer del mejor modelo clásico como referencia.

**Sprint:** Sprint 2 — Machine Learning y Deep Learning  
**Estimación inicial:** 5 puntos  
**Estado:** Terminada

---

## US-08: Optimizar el umbral de decisión mediante una matriz de costos

**Historia de usuario**

Como analista de experiencia del cliente, quiero evaluar diferentes umbrales de decisión mediante una matriz de costos y beneficios simulados, para identificar un punto de corte que permita priorizar la detección de reseñas desfavorables.

**Criterios de aceptación**

- [x] Definir una estrategia de decisión de negocio a partir de las cinco categorías de sentimiento.
- [x] Establecer una matriz de costos y beneficios que contemple verdaderos positivos, falsos positivos y falsos negativos.
- [x] Documentar los valores monetarios o unidades de costo utilizados y justificar sus supuestos mediante un escenario de simulación.
- [x] Implementar en `src/modelos/evaluacion.py` una función para evaluar umbrales de decisión entre 0.01 y 0.99.
- [x] Calcular el beneficio o costo neto simulado para cada umbral.
- [x] Identificar el umbral que maximiza el beneficio neto.
- [x] Comparar el resultado obtenido con el umbral convencional de 0.5.
- [x] Generar una curva de beneficio neto en función del umbral de decisión.
- [x] Documentar los resultados, los supuestos económicos y la justificación del umbral seleccionado en el README.md.

**Dependencia:** US-06 y US-07, para disponer de modelos evaluados y probabilidades de predicción.

**Sprint:** Sprint 2 — Machine Learning y Deep Learning  
**Estimación inicial:** Por definir  
**Estado:** Terminada

---
## US-09: Documentar la bitácora de desarrollo

**Historia de usuario**

Como equipo de desarrollo, queremos registrar los principales hallazgos, obstáculos y decisiones técnicas del proyecto, para mantener evidencia del proceso de desarrollo y justificar la arquitectura implementada.

**Criterios de aceptación**

- [x] Documentar los hallazgos relevantes de la exploración del dataset.
- [x] Registrar los principales obstáculos técnicos y sus soluciones.
- [x] Documentar los resultados y cuellos de botella identificados durante los experimentos de ML, DL y PySark.
- [x] Justificar las decisiones de arquitectura relacionadas con Dask, MongoDB, MinIO y almacenamiento Parquet.
- [x] Registrar los cambios y decisiones importantes durante los sprints.
- [x] Consolidar la información en un documento de bitácora.

**Sprint:** Sprint 2 — Machine Learning y evaluación del proyecto  
**Estimación inicial:** 2 puntos
**Estado:** Terminada

---

## US-10: Validar la propuesta mediante Design Thinking

**Historia de usuario**

Como equipo de desarrollo, queremos aplicar las cinco fases de Design Thinking para comprender las necesidades de los usuarios potenciales y evaluar la adecuación de Sentiment360 a sus problemas.

**Criterios de aceptación**

- [x] Identificar y describir los usuarios potenciales de la plataforma.
- [x] Documentar las necesidades y dificultades identificadas durante la fase de empatía.
- [x] Definir el problema principal que busca resolver el proyecto.
- [x] Proponer funcionalidades y alternativas de solución.
- [x] Crear un prototipo que represente la propuesta de Sentiment360.
- [x] Obtener retroalimentación de usuarios potenciales sobre el prototipo.
- [x] Documentar los resultados de las cinco fases: Empatizar, Definir, Idear, Prototipar y Evaluar.

**Sprint:** Sprint 2 — Machine Learning y evaluación del proyecto  
**Estimación inicial:** 3 puntos
**Estado:** Terminada

---

## US-11: Evaluar la viabilidad tecnológica y financiera

**Historia de usuario**

Como responsable de evaluar la propuesta, quiero analizar la viabilidad técnica y económica de implementar Sentiment360 en una institución o empresa, para estimar sus costos, beneficios potenciales y retorno de inversión.

**Criterios de aceptación**

- [x] Documentar los recursos tecnológicos necesarios para implementar la solución.
- [x] Estimar los costos de infraestructura local y servicios en la nube.
- [x] Definir los supuestos económicos utilizados en la evaluación.
- [x] Elaborar un flujo de caja simulado a 12 meses y 24 meses.
- [x] Estimar los beneficios económicos potenciales de la solución.
- [x] Calcular el ROI bajo escenarios financieros justificados.
- [x] Analizar la viabilidad técnica, económica y financiera.
- [x] Documentar los resultados y las limitaciones de la simulación.

**Sprint:** Sprint 2 — Machine Learning y evaluación del proyecto  
**Estimación inicial:** Por definir
**Estado:** Terminada

---

# 4. Planificación de sprints

| Sprint | Nombre | Objetivo | Inicio | Finalización | Estado |
|---|---|---|---|---|---|
| Sprint 1 | Ingesta y almacenamiento | Documentación del dataset, MongoDB, Dask, PySpark y almacenamiento compatible con S3 | 22/10/2026 | 26/10/2026 | Completado |
| Sprint 2 | Machine Learning y Deep Learning | Baseline, modelos clásicos, experimentación con redes neuronales, Design Thinking y evaluación de viabilidad | 30/10/2026 | 03/11/2026 | Completado |

# 5. Definition of Done (DoD)

Una historia de usuario se considerará terminada cuando cumpla las siguientes condiciones, según corresponda a su naturaleza:

- [x] Se han implementado las actividades y entregables definidos en sus criterios de aceptación.
- [x] Se han realizado las pruebas o verificaciones necesarias y los resultados son satisfactorios.
- [x] El código cumple con las convenciones y la estructura establecidas en el proyecto.
- [x] Se ha actualizado la documentación relacionada con los cambios realizados.
- [x] Los cambios han sido revisados e integrados en la rama principal del repositorio.
- [x] No existen errores conocidos que impidan cumplir el objetivo de la historia.
- [x] Existe evidencia verificable del resultado obtenido.

La historia podrá marcarse como terminada en el tablero cuando se hayan satisfecho sus criterios de aceptación y esta Definition of Done.

# 6. Responsabilidades y seguimiento

La ejecución del Sprint 2 se distribuye entre los integrantes del equipo de acuerdo con sus responsabilidades y áreas de trabajo.

| Integrante | Historias asignadas | Responsabilidades principales |
|---|---|---|
| Edwin Rommel Alberto Hernández | US-06 y US-09 | Modelos clásicos de Machine Learning y documentación de la bitácora de desarrollo. |
| Jonathan Vladimir Montes Rodriguez | US-07 | Entrenamiento y evaluación del modelo de Deep Learning. |
| Douglas Orlando López Polanco | US-08 | Optimización del umbral de decisión y evaluación mediante matriz de costos. |
| Kevin Antonio Montano Aquino | US-10 y US-11 | Validación de la propuesta mediante Design Thinking y evaluación tecnológica, económica y financiera. |

**Coordinación e integración:** Kevin Antonio Montano Aquino mantiene el seguimiento del proyecto, la planificación del trabajo, la actualización del tablero y la revisión de las integraciones.

**Seguimiento del proyecto:** el estado de las historias, las tareas y las asignaciones se gestionan mediante GitHub Projects.

**Tablero:** [Consultar GitHub Projects](URL_DEL_TABLERO)

Las historias podrán desarrollarse en paralelo cuando sus dependencias lo permitan. Los resultados de los modelos clásicos de US-06 servirán como referencia para las evaluaciones posteriores de US-07 y US-08.

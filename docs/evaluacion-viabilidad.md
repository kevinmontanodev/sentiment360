# Evaluación de Viabilidad Tecnológica, Económica y Financiera

## 1. Objetivo

Evaluar la viabilidad de Sentiment360 desde las perspectivas tecnológica, económica y financiera, considerando los recursos disponibles, las tecnologías seleccionadas, los costos de desarrollo y operación, y los beneficios potenciales de automatizar el análisis de opiniones de clientes.

El análisis permite determinar si la solución es técnicamente realizable, económicamente accesible y potencialmente sostenible en un escenario de utilización empresarial.

## 2. Alcance y metodología

La evaluación se desarrolla considerando dos perspectivas:

- **Viabilidad académica:** capacidad de construir, ejecutar y reproducir el sistema utilizando los recursos disponibles del equipo.
- **Viabilidad empresarial hipotética:** estimación de costos y beneficios potenciales para una organización que analiza opiniones de clientes periódicamente.

Los resultados experimentales del proyecto se utilizan como evidencia tecnológica. Los costos, ingresos y beneficios empresariales se consideran estimaciones o escenarios simulados, debido a que Sentiment360 no cuenta actualmente con una implementación comercial ni clientes reales.

---

## 3. Viabilidad tecnológica

### 3.1 Tecnologías seleccionadas

Sentiment360 utiliza herramientas de código abierto para implementar un flujo de procesamiento y análisis de opiniones.

| Componente | Tecnología | Propósito |
|---|---|---|
| Lenguaje | Python | Desarrollo de la solución. |
| Procesamiento distribuido | Dask | Limpieza y procesamiento de opiniones. |
| Procesamiento de datos | PySpark | Transformación y análisis de datos. |
| Almacenamiento documental | MongoDB | Persistencia de opiniones. |
| Almacenamiento de objetos | MinIO | Simulación de almacenamiento compatible con S3. |
| Machine Learning | Scikit-learn | Clasificación de sentimientos. |
| Deep Learning | Transformers / PyTorch | Experimentación con modelos neuronales. |
| Control de versiones | Git / GitHub | Colaboración y reproducibilidad. |

La selección de estas tecnologías permite desarrollar una solución modular y reproducible, sin depender obligatoriamente de infraestructura comercial.

### 3.2 Infraestructura disponible

El desarrollo y las pruebas se realizaron utilizando infraestructura local.

| Recurso | Característica |
|---|---|
| Procesador | 2 núcleos físicos y 4 lógicos. |
| Memoria RAM | Aproximadamente 7.65 GB. |
| Sistema de almacenamiento | Local. |
| Dataset | 200,000 opiniones en español. |
| Infraestructura cloud | No requerida para las pruebas académicas. |

Estas características representan una infraestructura de recursos limitados, apropiada para evaluar la ejecución local y las necesidades de optimización.

### 3.3 Resultados experimentales

El benchmark realizado permitió comparar Pandas y Dask sobre el procesamiento del conjunto de opiniones.

| Métrica | Pandas | Dask |
|---|---:|---:|
| Tiempo mediano | 1.40 s | 2.16 s |
| Memoria RSS medida | 330.92 MB | 14.25 MB |

Los resultados muestran que:

- Pandas presentó menor tiempo de ejecución para el procesamiento evaluado.
- Dask presentó un consumo RSS medido considerablemente menor durante el benchmark.
- Dask introduce sobrecarga de planificación y ejecución que puede afectar su rendimiento en conjuntos de datos pequeños.
- El conjunto evaluado pudo procesarse localmente, sin necesidad de infraestructura cloud.

La comparación demuestra que la selección de herramientas debe considerar tanto el tiempo de ejecución como el consumo de recursos.

*Nota: las mediciones de memoria corresponden al RSS observado durante el benchmark y no representan necesariamente el consumo máximo absoluto de cada herramienta.*

### 3.4 Evaluación tecnológica

| Criterio | Evaluación |
|---|---|
| Disponibilidad de herramientas | Favorable: tecnologías open source. |
| Ejecución local | Viable para el conjunto evaluado. |
| Procesamiento distribuido | Disponible mediante Dask y PySpark. |
| Reproducibilidad | Favorecida por Git, documentación y configuración del proyecto. |
| Escalabilidad | Potencialmente ampliable, sujeto a recursos y configuración. |
| Limitaciones | RAM, CPU y tiempo de entrenamiento de modelos. |

**Conclusión tecnológica:** Sentiment360 es tecnológicamente viable como prototipo académico y demostración funcional de procesamiento y análisis de opiniones. La ejecución de modelos de mayor tamaño o conjuntos de datos superiores podría requerir optimización o infraestructura adicional.

---

## 4. Viabilidad económica

### 4.1 Costos tecnológicos

La solución utiliza herramientas que pueden ejecutarse localmente y cuya utilización académica no requiere licencias comerciales.

| Concepto | Costo de licenciamiento |
|---|---|
| Python | $0 |
| Dask | $0 |
| PySpark | $0 |
| MongoDB Community | $0 |
| MinIO | $0 para el escenario local |
| Scikit-learn | $0 |
| Git / GitHub | $0 en el uso académico considerado |

Los valores corresponden al licenciamiento de las herramientas seleccionadas, no al costo total de desarrollo, operación o mantenimiento.

### 4.2 Costos de desarrollo

El desarrollo representa una inversión de tiempo y esfuerzo del equipo.

Para ilustrar su valoración económica, se considera el siguiente escenario hipotético:

| Concepto | Supuesto |
|---|---:|
| Horas de desarrollo | 160 horas |
| Valor referencial por hora | $5.00 |
| Inversión de desarrollo | $800.00 |

El valor por hora es un supuesto ilustrativo utilizado para estimar el costo del esfuerzo humano, no una tarifa salarial real ni una cotización comercial.

### 4.3 Costos operativos

Se consideran dos alternativas de operación:

**Escenario local**

- Uso de equipos existentes.
- Consumo eléctrico.
- Mantenimiento del entorno.
- Tiempo de administración.
- Actualización de dependencias.

**Escenario cloud**

- Instancias de cómputo.
- Almacenamiento de datos.
- Transferencia de información.
- Servicios administrados, cuando corresponda.
- Mantenimiento y monitoreo.

Para el proyecto académico se prioriza la ejecución local, ya que permite reducir costos directos y evitar dependencia de servicios de pago.

---

## 5. Viabilidad financiera

### 5.1. Enlace entre el desempeño analítico y el valor económico

La clasificación automática de opiniones no genera necesariamente un retorno económico directo. Su posible contribución financiera depende de que los resultados analíticos permitan mejorar procesos operativos y que dichas mejoras puedan medirse y valorarse monetariamente.

En Sentiment360 se plantea la siguiente cadena de impacto potencial:

1. **Desempeño analítico:** evaluar la capacidad del modelo para clasificar opiniones mediante métricas como precisión, recall y F1-score.
2. **Impacto operativo:** analizar si la clasificación automática permite reducir el tiempo de revisión inicial, facilitar la identificación de experiencias negativas o apoyar la detección de problemas recurrentes.
3. **Valor económico:** estimar el valor monetario de las mejoras operativas mediante mediciones de tiempo y costos asociados.
4. **Evaluación financiera:** comparar los beneficios económicos potenciales con los costos de implementación y operación.

El desempeño del modelo constituye una condición técnica necesaria, pero no demuestra por sí mismo la existencia de ahorros económicos.

### 5.2. Escenario financiero ilustrativo

Debido a que Sentiment360 no ha sido desplegado en una organización real, no existen registros transaccionales que permitan demostrar ahorros efectivos, reducción de gastos o incremento de ingresos.

Por ello, se presenta un escenario ilustrativo para identificar las variables que permitirían evaluar su potencial económico mediante un piloto operativo.

| Variable | Supuesto ilustrativo |
|---|---:|
| Opiniones procesadas mensualmente | 10,000 |
| Tiempo de revisión manual por opinión | 30 segundos |
| Tiempo de revisión asistida por opinión | 10 segundos |
| Diferencia de tiempo estimada | 20 segundos |
| Valor referencial por hora | $5.00 |

Bajo estos supuestos, el tiempo potencialmente liberado sería:

$$
H=\frac{10,000(30-10)}{3600}=55.56\text{ horas/mes}
$$

El valor económico teórico de ese tiempo sería:

$$
V = 55.56 \times 5 = 277.78\ \text{USD/mes}
$$

Este valor representa únicamente una estimación del tiempo potencialmente liberado, no un ahorro monetario comprobado.

Para reconocerlo como ahorro financiero efectivo, sería necesario demostrar que las horas liberadas producen una reducción de costos, disminuyen horas extra, evitan contrataciones adicionales o permiten reasignar recursos a actividades de valor cuantificable.

### 5.3. Costos de implementación y operación

Para ilustrar la evaluación financiera se mantiene una inversión inicial hipotética de $800.00 y un costo operativo mensual estimado de $50.00.

| Concepto | Valor |
|---|---:|
| Inversión inicial simulada | $800.00 |
| Costos operativos mensuales simulados | $50.00 |
| Costos operativos anuales | $600.00 |
| Costos totales del primer año | $1,400.00 |

Estos valores son parámetros ilustrativos del ejercicio académico y no corresponden a gastos reales registrados ni a cotizaciones de proveedores.

### 5.4. ROI condicionado a la validación operativa

El retorno de inversión se calcula mediante:

$$
ROI = \frac{\text{Beneficios monetarios} - \text{Costos totales}}{\text{Costos totales}} \times 100
$$

Sin embargo, para Sentiment360 no se dispone de beneficios monetarios efectivamente comprobados.

Por tanto, **no se presenta un ROI real ni se afirma que el proyecto haya recuperado su inversión**.

Si una organización validara posteriormente un ahorro monetario efectivo, podría calcularse el ROI utilizando:

- Inversión inicial real.
- Costos de operación y mantenimiento.
- Beneficios monetarios verificables.
- Periodo de evaluación definido.
- Registros operativos que respalden las estimaciones.

El ROI proyectado deberá distinguirse explícitamente del ROI observado.

### 5.5. Evidencia necesaria para validar el retorno

Para demostrar un retorno económico real se requeriría:

- Medición del tiempo de procesamiento manual y asistido.
- Comparación de resultados bajo condiciones operativas equivalentes.
- Registro de costos de implementación y operación.
- Identificación de beneficios monetarios efectivamente realizados.
- Evaluación de la calidad de clasificación y de la necesidad de revisión humana.
- Seguimiento de los resultados durante un periodo de prueba.

Esta información permitiría determinar si el valor económico obtenido supera los costos asociados a la solución.

---

## 6. Análisis de escenarios y sensibilidad

Debido a la ausencia de datos operativos reales, se utiliza un análisis de sensibilidad para estudiar cómo distintas condiciones podrían afectar el potencial económico de Sentiment360.

### 6.1. Variables de análisis

| Variable | Efecto esperado |
|---|---|
| Volumen de opiniones | Mayor volumen puede incrementar el tiempo potencialmente liberado. |
| Tiempo de revisión manual | Influye directamente en la oportunidad de automatización. |
| Tiempo de revisión asistida | Determina el tiempo requerido para supervisar los resultados. |
| Calidad del modelo | Una clasificación menos confiable puede aumentar la revisión manual. |
| Costos operativos | Pueden reducir o eliminar el beneficio económico potencial. |
| Aprovechamiento del tiempo liberado | Determina si el beneficio se convierte en ahorro monetario efectivo. |

### 6.2. Escenarios operativos

| Escenario | Características | Interpretación |
|---|---|---|
| Conservador | Menor volumen y mayor supervisión humana. | El tiempo potencialmente liberado puede ser reducido. |
| Base | Volumen moderado y revisión asistida. | Existe una oportunidad de mejorar la eficiencia operativa. |
| Optimista | Mayor volumen y menor tiempo de revisión asistida. | El potencial de eficiencia aumenta, sujeto a validación. |

Los escenarios representan condiciones de análisis y no resultados obtenidos mediante experimentación empresarial.

### 6.3. Limitaciones del análisis financiero

La evaluación presenta las siguientes limitaciones:

- No existen clientes reales ni contratos comerciales.
- No se dispone de registros de costos empresariales.
- Los tiempos de revisión utilizados son supuestos.
- No se han medido ahorros monetarios efectivos.
- No se ha demostrado una reducción de gastos operativos.
- No se ha validado el comportamiento económico mediante un piloto.

Por estas razones, el análisis permite identificar variables relevantes y estimar condiciones potenciales de viabilidad, pero no demostrar rentabilidad comercial.

### 6.4. Conclusión financiera

Sentiment360 presenta una oportunidad potencial de generar valor operativo mediante la automatización del análisis inicial de opiniones y la identificación de patrones de satisfacción e insatisfacción.

No obstante, la existencia de beneficios financieros depende de la calidad del modelo, la integración con procesos organizacionales y la capacidad de convertir mejoras operativas en beneficios monetarios verificables.

En consecuencia, la viabilidad financiera del proyecto se considera **potencial y condicionada**, requiriendo validación mediante un piloto operativo antes de afirmar la existencia de un retorno de inversión.

---

## 7. Riesgos y limitaciones

| Riesgo | Impacto potencial | Mitigación |
|---|---|---|
| Recursos computacionales limitados | Mayor tiempo de procesamiento y entrenamiento. | Optimización y selección adecuada de modelos. |
| Errores de clasificación | Interpretaciones incorrectas de opiniones. | Evaluación de métricas, análisis de errores y supervisión humana. |
| Desbalance de clases | Menor desempeño en determinadas categorías. | Validación por clase y estrategias de balance. |
| Costos cloud variables | Incremento de gastos operativos. | Monitoreo y evaluación de alternativas locales. |
| Beneficios económicos inciertos | ROI inferior al esperado. | Validación mediante pruebas piloto. |
| Dependencia de datos | Resultados limitados por calidad y representatividad. | Documentación de fuentes y validación de datos. |

Los beneficios económicos dependen de que el sistema alcance una calidad de clasificación suficiente y de que las recomendaciones obtenidas sean utilizadas efectivamente por la organización.

---

## 8. Consideraciones éticas y operativas

Sentiment360 debe considerarse una herramienta de apoyo analítico y no un mecanismo autónomo para tomar decisiones sobre clientes.

Se recomienda:

- Mantener supervisión humana en la interpretación de resultados.
- Evitar decisiones automatizadas basadas exclusivamente en sentimientos clasificados.
- Documentar las limitaciones del dataset.
- Proteger los datos y evitar almacenar información personal innecesaria.
- Evaluar el desempeño por categoría de sentimiento.
- Revisar periódicamente los modelos y sus resultados.

---

## 9. Conclusiones

La evaluación realizada permite identificar que Sentiment360 presenta viabilidad tecnológica para su implementación como prototipo académico, utilizando herramientas de código abierto y recursos locales.

Desde la perspectiva económica, el uso de tecnologías gratuitas y la ejecución local permiten reducir los costos directos de licenciamiento e infraestructura, aunque el desarrollo, mantenimiento y operación continúan representando costos de tiempo y recursos humanos.

La evaluación financiera identifica una oportunidad potencial de mejorar la eficiencia operativa mediante el procesamiento asistido de opiniones. Sin embargo, los beneficios económicos estimados corresponden a escenarios ilustrativos y no representan ahorros monetarios comprobados ni un retorno de inversión observado.

En conclusión, **Sentiment360 es viable como proyecto académico y presenta potencial de aplicación empresarial**, condicionado a la validación de su desempeño en un entorno operativo, la medición de mejoras de productividad y la identificación de beneficios monetarios verificables que permitan determinar su viabilidad financiera.

---

## 10. Naturaleza de las estimaciones

Los resultados del benchmark corresponden a experimentos realizados durante el desarrollo del proyecto. Las estimaciones de inversión, costos operativos, beneficios, ROI y recuperación de inversión corresponden a un escenario financiero hipotético, elaborado con fines académicos.

No representan cotizaciones, ingresos reales, clientes existentes ni garantías de rentabilidad.

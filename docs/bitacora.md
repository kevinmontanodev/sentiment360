# Bitácora de desarrollo de Sentiment360 (US-09)

Corte: **2 de noviembre de 2026**. Esta bitácora consolida los hallazgos y las
decisiones disponibles en el repositorio. Distingue resultados medidos, resultados
previamente documentados por el equipo y trabajo pendiente. No sustituye la
revisión ni la integración de cada historia.

## Cronología por sprint

| Fecha | Sprint | Cambio o decisión | Evidencia |
|---|---|---|---|
| 22–23 oct. 2026 | 1 | Exploración del corpus y comprobación de etiquetas, duplicados y particiones. | [PR #15](https://github.com/kevinmontanodev/sentiment360/pull/15), `bf9e0f7`, [dataset](dataset.md). |
| 23 oct. 2026 | 1 | Ingesta por lotes en MongoDB, validación y unicidad por ID. | [PR #16](https://github.com/kevinmontanodev/sentiment360/pull/16), `a5b9d4e`, [ingesta](ingesta-mongodb.md). |
| 23–24 oct. 2026 | 1 | Limpieza Dask, conservación de ID y etiquetas, Parquet y verificación de salida. | [PR #17](https://github.com/kevinmontanodev/sentiment360/pull/17), `8fa7ec8`, [procesamiento Dask](procesamiento-dask.md). |
| 25 oct. 2026 | 1 | Procesamiento PySpark y comparación de agregaciones con Dask. | [PR #18](https://github.com/kevinmontanodev/sentiment360/pull/18), `67b8acb`, [procesamiento PySpark](procesamiento-pyspark.md). |
| 25 oct. 2026 | 1 | Almacenamiento y recuperación verificable de artefactos en MinIO. | [PR #20](https://github.com/kevinmontanodev/sentiment360/pull/20), `5673d10`, [MinIO](almacenamiento-minio.md). |
| 30 oct. 2026 | 1 | Se centralizó la validación estricta del esquema en Pydantic. | `3dbd455`, `src/ingesta/esquemas.py`. |
| 31 oct. 2026 | 1 | Benchmark Pandas/Dask y análisis Spark con JOIN y ventanas. | [PR #21](https://github.com/kevinmontanodev/sentiment360/pull/21), [PR #22](https://github.com/kevinmontanodev/sentiment360/pull/22). |
| 31 oct. 2026 | 2 | Backlog, Definition of Done y responsabilidades del equipo. | `5af4c45`, [BACKLOG.md](../BACKLOG.md). |
| 2 nov. 2026 | 2 | Experimento de modelos clásicos y consolidación de esta bitácora. | Ramas `feature/ealberto/issue-9` y `feature/ealberto/issue-12`; resultados detallados abajo. |

Las fechas se basan en el historial de Git y en la ejecución actual. No se asignan
fechas a experimentos o revisiones que todavía no tienen evidencia.

## Exploración y calidad del dataset

Fuente: `SetFit/amazon_reviews_multi_es`. El equipo documentó 200.000 filas de
train y 5.000 en cada partición oficial de validation y test. Las cinco clases
están equilibradas; `label_text` es la cadena de la etiqueta, no un nombre de
sentimiento. Las etiquetas 0–4 representan valoraciones de una a cinco estrellas.

La exploración registró cero nulos, textos vacíos o IDs duplicados en train.
Encontró 747 textos repetidos que involucran 2.483 filas; 398 grupos presentan
etiquetas contradictorias. Por tanto, no basta con eliminar IDs repetidos para
controlar las coincidencias textuales ni se puede inferir que toda contradicción
sea un error de etiquetado.

Se detectaron 120 textos únicos compartidos por al menos dos particiones
oficiales, seis de ellos presentes en las tres. La evaluación complementaria
literal del notebook conservó 4.929 filas de validation y 4.934 de test.
Fuente de estos resultados: [docs/dataset.md](dataset.md) y
`notebooks/01_exploracion_dataset.ipynb`; no son mediciones nuevas de esta bitácora.

Para ML se repitió la preparación sobre una revisión fija del corpus con NFC,
casefold y espacios normalizados, igual que TF-IDF. Se conservaron las 200.000
filas de train, 4.918 de validation y 4.931 de test. La diferencia frente al
notebook responde a una definición más amplia de coincidencia, documentada en
la US-06. Se conservaron los datos originales y los hashes de los archivos.

## Decisiones de arquitectura

| Componente | Decisión y justificación | Límite observado |
|---|---|---|
| MongoDB | Conservar documentos originales y un índice único por `id`; leer mediante cursor y lotes. | La unicidad del ID no evita textos repetidos. La ingesta documentada contiene solo train. |
| Dask | Limpiar lotes con Bag y releer el Parquet con DataFrame; mantener acotada la lectura y reutilizar Python. | El planificador tiene sobrecarga. Dask no fue más rápido que Pandas en el benchmark local. |
| Parquet | Compartir un esquema tipado entre Dask, Pandas, PySpark y ML, sin volver a consultar MongoDB en cada experimento. | Se deben verificar columnas, tipos, conteos y etiquetas antes de reutilizar artefactos. |
| MinIO | Separar los artefactos del almacenamiento documental, usando la API compatible con S3 y configuración por entorno. | Es una simulación local; no demuestra disponibilidad, seguridad ni costos de un despliegue cloud. |
| PySpark | Comparar agregaciones y demostrar JOIN y funciones de ventana sobre el mismo Parquet. | Requiere JVM y configuración nativa compatible con el sistema operativo. |
| ML | TF-IDF y clasificador dentro de Pipeline, CV por grupos y selección por F1 macro. | La búsqueda y la muestra de entrenamiento ejecutadas son limitadas. |

Las credenciales permanecen en `.env`; ni el corpus ni los modelos serializados
se incorporan a Git. MinIO conserva objetos y MongoDB documentos: no se usan
como reemplazos intercambiables de la misma responsabilidad.

## Resultados y costos observados

### Ingesta, Dask y MinIO

La documentación de ingesta registra 200.000 documentos insertados, sin
rechazados ni duplicados en la carga inicial. La limpieza Dask se probó desde
MongoDB simulado hasta Parquet real, conservando ID y etiquetas; el comando
produce un resumen de leídos, conservados y rechazados.

La US-05 documenta la subida y recuperación de una muestra de 1.000 reseñas en
MinIO, con dos archivos y verificación de integridad satisfactoria. Es una prueba
de almacenamiento, no una muestra válida para entrenar: las primeras 1.000 filas
del corpus pertenecen a una sola etiqueta. Estas cifras proceden de la evidencia
versionada del equipo, no de una nueva ejecución contra sus servicios.

### Pandas, Dask y PySpark

El [benchmark versionado](../reports/benchmark/resultados.json) usa 200.000
reseñas, tres repeticiones y operaciones equivalentes. Las medianas fueron
1,401690 s para Pandas y 2,158424 s para Dask. El incremento de RSS mediano fue
330,92 MB y 14,25 MB, respectivamente. La memoria corresponde al proceso completo,
con ambas estructuras preparadas, y el muestreo puede omitir picos breves.
No permite atribuir esos consumos exclusivamente a una biblioteca.

El código PySpark implementa conteos, promedios, distribución, `crossJoin()` y
`dense_rank()`. La documentación muestra un ejemplo de cuatro reseñas con
distribución 1/1/2 y porcentajes 25/25/50. No contiene un benchmark de tiempos
PySpark frente a Dask; no se presenta ese ejemplo como una medición de rendimiento.

En la validación de este corte, seis pruebas PySpark fallaron al leer Parquet por
`NativeIO$Windows.access0`. El mismo error se reprodujo en un checkout limpio de
`main`, commit `5af4c45`, sin los cambios de ML. Es un bloqueo de configuración
Windows/Hadoop y no una regresión demostrada de US-06.

### Machine Learning

Experimento real con 10.000 reseñas estratificadas para entrenamiento y 4.931
reseñas complementarias de test; semilla 42 y tres folds por grupos de texto.

| Modelo | F1 macro CV | Accuracy test | F1 macro test |
|---|---:|---:|---:|
| Dummy | 0,0666 | 0,2012 | 0,0670 |
| Regresión Logística | 0,4601 | 0,4914 | 0,4892 |
| Random Forest | 0,4185 | 0,4476 | 0,4350 |
| SVM lineal | 0,4463 | 0,4794 | 0,4745 |

Se seleccionó Regresión Logística con `C=2` por F1 macro de CV, antes de consultar
test. Las categorías intermedias son las más difíciles: F1 de 0,3967, 0,3911 y
0,4163 para las etiquetas 1, 2 y 3. Las matrices muestran confusiones frecuentes
entre calificaciones vecinas. No se atribuye causalidad a esos errores sin un
análisis adicional.

Random Forest fue la familia de mayor tiempo de ajuste en esta búsqueda. No se
midió RAM por modelo ni se entrenó con los 200.000 registros completos. Se
guardaron métricas, configuraciones, tiempos y hashes; el pipeline ganador puede
cargarse desde un proceso independiente para los trabajos posteriores.

Evidencia de US-06: [protocolo de ML](https://github.com/kevinmontanodev/sentiment360/blob/feature/ealberto/issue-9/docs/modelos-clasicos.md)
y [resultados completos](https://github.com/kevinmontanodev/sentiment360/blob/feature/ealberto/issue-9/reports/ml/resultados.json).
Los enlaces apuntan a su rama mientras se revisa su integración.

### Deep Learning

Al corte, la [US-07, issue #10](https://github.com/kevinmontanodev/sentiment360/issues/10)
está abierta y asignada a `jonh-rdz`. `main` no contiene entrenamiento DL ni
métricas versionadas. Por ello no se inventan arquitectura, tiempos, consumo de
memoria ni una comparación ML/DL.

Queda pendiente incorporar, cuando se publique US-07: commit y configuración,
particiones y semilla, curvas de entrenamiento/validación, métricas por clase,
tiempo y recursos realmente medidos, obstáculos y comparación con la referencia
clásica usando las mismas particiones. La dependencia impide cerrar todavía el
criterio de resultados DL de US-09.

## Obstáculos y resolución

| Obstáculo | Evidencia y medida adoptada | Estado |
|---|---|---|
| Textos compartidos y etiquetas contradictorias | Conservar originales, filtrar evaluación y agrupar textos normalizados en CV. | Aplicado en US-06. |
| Corpus ordenado por etiqueta | Muestreo aleatorio estratificado, con 2.000 ejemplos de cada clase en el entrenamiento ejecutado. | Aplicado. |
| Posible fuga al aprender TF-IDF antes de CV | Pipeline completo dentro de GridSearchCV; prueba que el vocabulario exclusivo de test no se aprende. | Aplicado y probado. |
| Pipeline guardado desde `python -m` con un preprocesador definido en `__main__` | Mover el preprocesador a `src/modelos/texto.py` y probar la carga desde otro proceso. | Corregido antes de publicar US-06. |
| OneDrive bloquea el renombrado del directorio de preparación | Preparar y verificar en la carpeta temporal del sistema; copiar después al destino. | La preparación completa finalizó. |
| Dependencias nativas Hadoop en Windows | Reproducir el fallo en main y registrarlo; validar PySpark en un entorno con Hadoop configurado antes de afirmar que pasó la suite completa. | Pendiente de resolver en este equipo. |
| Versiones locales diferentes a requirements | Registrar las versiones efectivas en el informe de ML para no atribuir resultados a un entorno no utilizado. | Trazado; falta validar el entorno fijado completo. |
| Falta de resultados DL | Mantener US-09 abierta y registrar explícitamente la dependencia con US-07. | Pendiente del entregable del responsable. |

## Seguimiento de US-09

- [x] Hallazgos de exploración y riesgos del dataset.
- [x] Obstáculos, soluciones aplicadas y pendientes diferenciados.
- [x] Resultados ML, límites del benchmark y evidencia disponible de PySpark.
- [ ] Resultados y cuellos de botella de DL, dependientes de US-07.
- [x] Justificación de Dask, MongoDB, MinIO y Parquet.
- [x] Cambios relevantes por sprint con referencias verificables.
- [x] Consolidación en un único documento de bitácora.

La revisión e integración siguen la Definition of Done del backlog. Esta bitácora
debe actualizarse con cada experimento relevante; no se marca US-09 como
completada mientras falten los resultados DL y la revisión del equipo.

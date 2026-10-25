# Procesamiento de reseñas con PySpark y comparación con Dask (US-04)

Este documento describe el procesamiento en modo local con **PySpark** a partir de los archivos Parquet generados en la **US-03**, la verificación de consistencia frente a **Dask** y los criterios técnicos para elegir cada herramienta.

---

## 1. Ejecución del módulo

Asegúrate de haber generado previamente el dataset Parquet de la US-03 (`data/processed/reviews`). Luego ejecuta desde la raíz del proyecto:

```bash
python -m src.procesamiento.procesar_pyspark
```

Para especificar un directorio Parquet distinto:

```bash
python -m src.procesamiento.procesar_pyspark --input data/processed/reviews_prueba
```

Para ejecutar las pruebas unitarias del módulo:

```bash
pytest tests/test_procesamiento_pyspark.py -v
```

---

## 2. Transformaciones perezosas (*Lazy*) vs. Acciones en Spark

Apache Spark utiliza un modelo de **evaluación perezosa (*lazy evaluation*)** basado en un Grafo Acíclico Dirigido (**DAG**):

1. **Transformaciones perezosas (*Transformations*):**
   * Son operaciones que definen un nuevo DataFrame a partir de uno existente sin procesar los datos de inmediato.
   * Cuando se invocan métodos como `spark.read.parquet()`, `.withColumns()`, `.groupBy()`, `.agg()` u `.orderBy()`, Spark únicamente registra las instrucciones en el **plan lógico** y el optimizador *Catalyst* las combina y optimiza (por ejemplo, aplicando *predicate pushdown* y leyendo solo las columnas necesarias del archivo Parquet).
   * En `src/procesamiento/procesar_pyspark.py`, el cálculo de `char_length`, `word_count` y la agrupación por `label` son transformaciones perezosas.

2. **Acciones (*Actions*):**
   * Son operaciones que solicitan un resultado concreto al *Driver* o escriben datos en almacenamiento externo, obligando a Spark a compilar el **plan físico** y ejecutar todas las transformaciones acumuladas.
   * Ejemplos en el módulo: `df.count()` (obtiene el total de reseñas) y `df_aggregated.collect()` (recupera las métricas agregadas por etiqueta hacia Python).
   * En **Dask** ocurre un principio análogo: las operaciones sobre `dask.dataframe` construyen un grafo de tareas diferido que solo se materializa cuando se invoca la acción `dask.compute()`.

---

## 3. Comparación de resultados: PySpark vs. Dask

Ambos motores leen el directorio `data/processed/reviews` con el esquema validado (`id`, `text`, `label`, `label_text`) y ejecutan:
* Conteo total de reseñas válidas.
* Distribución de reseñas agrupadas por etiqueta (`0` a `4`).
* Longitud media de caracteres (`avg_char_length`) y promedio de palabras (`avg_word_count`) por categoría.

La función `compare_spark_and_dask()` verifica automáticamente que el conteo total, la distribución por etiquetas y los promedios coincidan entre ambas herramientas.

---

## 4. ¿Cuándo conviene utilizar cada herramienta?

| Criterio | Dask (`dask.dataframe` / `dask.bag`) | PySpark (`pyspark.sql.DataFrame`) |
| :--- | :--- | :--- |
| **Arquitectura y entorno** | 100 % nativo en Python; se ejecuta en el mismo intérprete sin requerir máquina virtual de Java (JVM). | Se ejecuta sobre la JVM (Apache Spark) y se comunica con Python mediante `Py4J`. Requiere JDK 17 y binarios de Hadoop (`winutils` en Windows). |
| **Tiempo de arranque** | Inmediato (milisegundos). Ideal para scripts CLI ligeros y pruebas rápidas. | Sobrecarga inicial de varios segundos al levantar la `SparkSession` y la JVM. |
| **Optimización de consultas** | Ejecuta grafos de tareas basados en particiones de Pandas/PyArrow. | Cuenta con el optimizador **Catalyst** y el motor **Tungsten**, que reordenan filtros, proyecciones y *joins* automáticamente. |
| **Integración de ecosistema** | Excelente integración con `pandas`, `NumPy`, `scikit-learn` y código Python arbitrario. | Estándar empresarial en plataformas Big Data (Databricks, AWS EMR, Google Dataproc, Apache Iceberg/Delta Lake). |
| **Escala de datos recomendada** | Conjuntos de datos que superan la RAM local (varios GB a cientos de GB) en una estación de trabajo o clúster Python ligero. | Procesamiento distribuido masivo (cientos de GB a múltiples Terabytes/Petabytes) en clústeres dedicados con alta tolerancia a fallos. |

### Conclusión para Sentiment360
* **Cuándo elegir Dask:** En etapas de ingesta, limpieza por lotes desde MongoDB (US-03) y prototipado local en Python, ya que arranca sin sobrecarga de JVM y se integra directamente con `pandas`, `pyarrow` y `scikit-learn`.
* **Cuándo elegir PySpark:** Cuando el volumen histórico de reseñas escale a nivel de *Data Lake* empresarial, se requieran cruces complejos optimizados por SQL/*Catalyst* o el pipeline se despliegue en clústeres administrados de Spark.

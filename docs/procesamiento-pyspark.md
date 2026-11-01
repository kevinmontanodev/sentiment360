# Procesamiento de reseñas con PySpark y comparación con Dask (US-04)

Este documento describe el procesamiento en modo local con **PySpark** a partir de los archivos Parquet generados en la **US-03**, la verificación de consistencia frente a **Dask** y el análisis de distribución y ranking de las categorías de sentimiento.

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

Apache Spark utiliza un modelo de **evaluación perezosa (*lazy evaluation*)** basado en un Grafo Acíclico Dirigido (**DAG**).

### 2.1. Transformaciones perezosas (*Transformations*)

Son operaciones que construyen un plan de procesamiento sin ejecutar inmediatamente los cálculos sobre los datos.

En nuestro módulo:

- `session.read.parquet()`: crea un DataFrame a partir de los archivos Parquet y establece la fuente de datos del procesamiento.
- `withColumns()`: genera las columnas derivadas `char_length` y `word_count`.
- `groupBy().agg()`: agrupa las reseñas por etiqueta y calcula sus métricas.
- `crossJoin()`: combina las estadísticas por etiqueta con el total global de reseñas.
- `withColumn()`: incorpora el porcentaje y el ranking.
- `orderBy()`: establece el orden de los resultados.

Spark registra estas operaciones en el plan lógico. Posteriormente, el optimizador **Catalyst** analiza y optimiza el plan antes de su ejecución.

### 2.2. Acciones (*Actions*)

Son operaciones que solicitan resultados concretos y provocan la ejecución del plan de procesamiento.

En nuestro módulo, la operación principal es:

- `df_distribution.collect()`: ejecuta el procesamiento y recupera las métricas agregadas hacia el programa Python.

En **Dask** ocurre un principio análogo: las operaciones sobre `dask.dataframe` construyen un grafo de tareas diferido que se materializa cuando se invoca `dask.compute()`.

---

## 3. Comparación de resultados: PySpark vs. Dask

Ambos motores leen el directorio `data/processed/reviews` con el esquema validado (`id`, `text`, `label`, `label_text`) y ejecutan operaciones equivalentes:

- Conteo total de reseñas válidas.
- Distribución de reseñas agrupadas por etiqueta (`0` a `4`).
- Longitud media de caracteres (`avg_char_length`) y promedio de palabras (`avg_word_count`) por categoría.

La función `compare_spark_and_dask()` verifica automáticamente que el conteo total, la distribución por etiquetas y los promedios coincidan entre ambas herramientas, admitiendo una tolerancia de `0.05` en las métricas decimales.

---

## 4. Análisis avanzado con PySpark

Además de las agregaciones anteriores, se implementó un análisis complementario para estudiar la distribución de las categorías de sentimiento y su posición relativa según la cantidad de reseñas.

Este análisis utiliza operaciones de unión (*JOIN*) y funciones de ventana (*Window Functions*).

### 4.1. Unión de estadísticas globales mediante `crossJoin()`

Primero se calcula el total general de reseñas mediante una agregación:

```python
global_stats = df.agg(
    F.count("*").alias("total_reviews")
)
```

Después, se combina este resultado con las estadísticas agrupadas por etiqueta:

```python
df_distribution = df_aggregated.crossJoin(global_stats)
```

Se utiliza `crossJoin()` porque `global_stats` contiene una única fila con el total general. De esta manera, cada categoría recibe el mismo valor de referencia para calcular su porcentaje de participación.

La proporción de cada etiqueta se calcula mediante:

```python
df_distribution = df_distribution.withColumn(
    "percentage",
    F.round(
        F.col("count") / F.col("total_reviews") * 100,
        2,
    ),
)
```

### 4.2. Ranking mediante funciones de ventana (*Window*)

Para identificar la posición de cada categoría según su cantidad de reseñas, se utiliza una ventana global ordenada de forma descendente:

```python
ranking_window = Window.orderBy(F.desc("count"))

df_distribution = df_distribution.withColumn(
    "ranking",
    F.dense_rank().over(ranking_window),
)
```

La función `dense_rank()` asigna la misma posición a las categorías que tienen igual cantidad de registros. A diferencia de `rank()`, no deja posiciones vacías después de un empate.

Por ejemplo, si dos categorías comparten el primer puesto, la siguiente categoría recibe la posición 2.

### 4.3. Ejemplo de resultados

Con el conjunto de prueba de cuatro reseñas, la distribución esperada es:

| Etiqueta | Cantidad | Porcentaje | Ranking |
|---|---:|---:|---:|
| 0 | 1 | 25.00 % | 2 |
| 2 | 1 | 25.00 % | 2 |
| 4 | 2 | 50.00 % | 1 |

La salida se incorpora al resultado de `process_with_pyspark()` mediante la propiedad `distribution_by_label`.

**Consideración sobre datasets vacíos:** cuando no existen reseñas, la distribución devuelve una lista vacía y el total general permanece en cero. Esto evita realizar divisiones entre cero.

Los porcentajes se redondean a dos decimales, por lo que en conjuntos con muchas categorías podrían existir pequeñas diferencias acumuladas respecto al 100 %.

---

## 5. ¿Cuándo conviene utilizar cada herramienta?

| Criterio | Dask (`dask.dataframe` / `dask.bag`) | PySpark (`pyspark.sql.DataFrame`) |
|---|---|---|
| **Arquitectura y entorno** | Ecosistema nativo de Python, integrado con Pandas y otras bibliotecas. No requiere JVM. | API de Python sobre Apache Spark, cuyo motor se ejecuta en la JVM y se comunica mediante Py4J. |
| **Tiempo de arranque** | Generalmente presenta una sobrecarga inicial menor en ejecuciones locales. | La inicialización de `SparkSession` y la JVM introduce una sobrecarga inicial adicional. |
| **Optimización de consultas** | Construye grafos de tareas sobre particiones y permite utilizar distintos planificadores. | Catalyst optimiza los planes de consulta y el motor de ejecución utiliza técnicas de optimización como las asociadas a Tungsten. |
| **Integración de ecosistema** | Buena integración con Pandas, NumPy, PyArrow y herramientas del ecosistema Python. | Integración con Spark SQL, procesamiento estructurado y plataformas de datos distribuidos. |
| **Escalabilidad** | Puede distribuir el procesamiento entre varios núcleos o máquinas mediante su planificador distribuido. | Puede ejecutar procesamiento local o distribuido en clústeres, con soporte para grandes volúmenes de datos. |

### Conclusión para Sentiment360

- **Cuándo elegir Dask:** en etapas de ingesta, limpieza por lotes desde MongoDB (US-03) y prototipado local en Python, debido a su integración con Pandas, PyArrow y otras herramientas del proyecto.
- **Cuándo elegir PySpark:** cuando se requiera procesamiento estructurado mediante DataFrames, agregaciones, uniones entre conjuntos de datos y funciones de ventana, especialmente si el volumen de información justifica utilizar su motor distribuido.

La implementación de ambas herramientas permite comparar resultados y comprender sus diferencias de ejecución, optimización y aplicación dentro de un flujo de procesamiento de datos.

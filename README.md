# Sentiment360

**Plataforma reproducible de análisis de sentimiento de reseñas de clientes en español.**

Sentiment360 es un proyecto integrador de Python orientado al procesamiento de texto y la clasificación automática de opiniones de clientes. El proyecto busca comparar técnicas de aprendizaje automático clásico y Deep Learning mediante un flujo de datos reproducible, desde la ingesta y el almacenamiento hasta la exposición de predicciones mediante una API.

## Objetivos

- Procesar y almacenar reseñas utilizando MongoDB, Dask y PySpark.
- Construir un baseline y comparar modelos de clasificación mediante métricas adecuadas.
- Evaluar una arquitectura de Deep Learning frente a los modelos clásicos.
- Exponer el modelo seleccionado mediante FastAPI.
- Documentar la arquitectura, las decisiones técnicas y los pasos necesarios para reproducir los resultados.

## Estado del proyecto

En desarrollo — Semana 14: propuesta, ingesta y almacenamiento.

## Dataset y condiciones de uso

Sentiment360 utiliza como fuente candidata `SetFit/amazon_reviews_multi_es`, una versión en español del *Multilingual Amazon Reviews Corpus*.

- **Fuente:** https://huggingface.co/datasets/SetFit/amazon_reviews_multi_es
- **Licencia y condiciones del corpus original:** https://github.com/awslabs/open-data-docs/blob/main/docs/amazon-reviews-ml/license.txt
- **Uso previsto:** proyecto académico de clasificación de sentimiento.
- **Distribución:** el repositorio del proyecto no incluirá el corpus completo. Los datos se obtendrán por separado y se documentarán las instrucciones de preparación.

La licencia del código fuente de Sentiment360 es independiente de las condiciones aplicables al dataset. Antes de distribuir datos derivados, muestras de reseñas o artefactos entrenados, se revisarán las condiciones aplicables.

## Tecnologías

Python · MongoDB · Dask · PySpark · scikit-learn · Deep Learning · FastAPI · Docker.

## Reproducibilidad

Las instrucciones de instalación, ejecución, pruebas y uso de la API se completarán conforme se implementen y verifiquen los componentes.

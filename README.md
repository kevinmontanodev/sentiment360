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

Sentiment360 utiliza como fuente `SetFit/amazon_reviews_multi_es`, una versión en español del *Multilingual Amazon Reviews Corpus*.

- **Fuente:** https://huggingface.co/datasets/SetFit/amazon_reviews_multi_es
- **Licencia y condiciones del corpus original:** https://github.com/awslabs/open-data-docs/blob/main/docs/amazon-reviews-ml/license.txt
- **Uso previsto:** proyecto académico de clasificación de sentimiento.
- **Distribución:** el repositorio del proyecto no incluirá el corpus completo. Los datos se obtendrán por separado y se documentarán las instrucciones de preparación.

La licencia del código fuente de Sentiment360 es independiente de las condiciones aplicables al dataset. Antes de distribuir datos derivados, muestras de reseñas o artefactos entrenados, se revisarán las condiciones aplicables.

## Tecnologías

Python · MongoDB · Dask · PySpark · scikit-learn · Deep Learning · FastAPI · Docker.

## Requisitos previos

- Python 3.10 o superior.
- pip y un entorno virtual de Python.
- Docker y Docker Compose.
- Acceso a internet para obtener el dataset desde Hugging Face.

## Instalación y configuración

Clona el repositorio y entra en su directorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd sentiment360
```

Crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Crea tu archivo local de configuración:

```bash
cp .env.example .env
```

Edita `.env` y configura las credenciales locales de MongoDB. La URI debe coincidir con las credenciales configuradas para el contenedor. No compartas este archivo ni lo subas al repositorio.

## Iniciar MongoDB

Desde la raíz del proyecto, ejecuta:

```bash
docker-compose -f compose.yaml up -d
```

Comprueba el estado del contenedor:

```bash
docker-compose -f compose.yaml ps
```

Para detener el servicio:

```bash
docker-compose -f compose.yaml down
```

El volumen de Docker conserva los datos de MongoDB entre reinicios del contenedor.

## Ingesta de reseñas

La ingesta utiliza el split `train` del dataset `SetFit/amazon_reviews_multi_es`, con lectura mediante streaming y procesamiento por lotes de 500 reseñas.

Para cargar el dataset completo en la colección configurada:

```bash
python -m src.ingesta.cargar_dataset
```

Para realizar una prueba limitada de 10 reseñas en una colección separada:

```bash
python -m src.ingesta.cargar_dataset --limit 10 --collection reviews_us02_prueba
```

La ingesta valida el esquema, evita duplicados mediante un índice único por `id` y muestra un resumen con las reseñas recibidas, insertadas, duplicadas, rechazadas y el total almacenado.

La colección de producción predeterminada es `reviews`. El nombre de la base de datos y la URI se configuran mediante variables de entorno.

Consulta [docs/ingesta-mongodb.md](docs/ingesta-mongodb.md) para obtener los detalles técnicos y los resultados de validación.

## Pruebas

Ejecuta las pruebas automatizadas desde la raíz del proyecto:

```bash
pytest -v
```

Las pruebas cubren la validación de reseñas, el repositorio MongoDB y el servicio de ingesta. Se utiliza `mongomock` para simular operaciones de MongoDB en las pruebas unitarias.

## Reproducibilidad

El repositorio incluye la configuración de dependencias, la configuración de pruebas, un archivo de ejemplo de variables de entorno y la definición del servicio MongoDB mediante Docker Compose.

El corpus completo, las credenciales locales, los entornos virtuales y los archivos generados no deben versionarse.

Las instrucciones de procesamiento, entrenamiento, evaluación y uso de la API se ampliarán conforme se implementen y verifiquen esos componentes.

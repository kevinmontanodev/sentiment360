# Sentiment360

**Plataforma reproducible de análisis de opiniones de clientes en español mediante aprendizaje automático y procesamiento de datos.**

## Descripción del proyecto

Sentiment360 es un proyecto integrador de Python que busca transformar reseñas de productos escritas en español en información útil para el análisis de la experiencia del cliente.

Las empresas que reciben grandes volúmenes de opiniones pueden tener dificultades para revisar manualmente todos los comentarios, identificar patrones recurrentes y detectar señales de insatisfacción. Aunque las calificaciones numéricas permiten obtener una visión general, el texto de las reseñas puede aportar contexto adicional sobre las experiencias de los clientes.

Sentiment360 propone un flujo de procesamiento que permite almacenar, preparar y analizar reseñas, entrenar modelos de clasificación y exponer predicciones mediante una API. El proyecto también compara enfoques de aprendizaje automático clásico y aprendizaje profundo para evaluar sus resultados y limitaciones.

El objetivo es desarrollar un prototipo reproducible que demuestre cómo las técnicas de análisis de texto pueden apoyar la toma de decisiones empresariales a partir de opiniones de clientes.

## Problema y oportunidad de negocio

El análisis manual de reseñas puede consumir tiempo y dificultar la identificación de tendencias cuando aumenta el volumen de comentarios. Por otro lado, limitarse a promediar calificaciones no permite comprender completamente el contenido de las opiniones expresadas por los clientes.

Sentiment360 busca abordar este problema mediante la clasificación automática de reseñas y la generación de resultados que faciliten su análisis.

Entre sus posibles aplicaciones se encuentran:

- **Experiencia del cliente:** identificar señales de satisfacción e insatisfacción en las opiniones recibidas.
- **Mejora de productos y servicios:** localizar reseñas negativas que requieran una revisión más detallada.
- **Priorización del análisis:** facilitar que los equipos enfoquen su atención en grupos de comentarios relevantes.
- **Seguimiento de tendencias:** comparar la distribución de las categorías de sentimiento entre conjuntos de reseñas.

La solución no pretende sustituir la evaluación humana ni determinar por sí sola las causas de la insatisfacción. Su propósito es ofrecer una herramienta de apoyo que permita analizar opiniones a mayor escala y orientar investigaciones posteriores.

## Objetivo general

Diseñar e implementar un pipeline reproducible de análisis de sentimiento de reseñas en español que integre almacenamiento de datos, procesamiento distribuido, modelos de aprendizaje automático y aprendizaje profundo, y exposición de predicciones mediante una API.

## Objetivos específicos

- Ingerir y almacenar reseñas en una base de datos adecuada para información semiestructurada.
- Limpiar y transformar los datos para preparar conjuntos de entrenamiento y evaluación consistentes.
- Implementar un baseline y comparar al menos tres algoritmos de aprendizaje automático de familias distintas.
- Evaluar una arquitectura de aprendizaje profundo y comparar sus resultados con el mejor modelo clásico.
- Aplicar métricas, validación y análisis de errores para estudiar el rendimiento y las limitaciones de los modelos.
- Demostrar operaciones de procesamiento con Dask y PySpark, documentando sus diferencias y casos de uso.
- Exponer el modelo seleccionado mediante una API y documentar cómo reproducir el proyecto.

## Usuarios y beneficiarios previstos

El prototipo está orientado principalmente a:

- **Analistas de datos:** para explorar opiniones y obtener resúmenes cuantitativos.
- **Equipos de atención al cliente y experiencia del cliente:** para identificar grupos de reseñas que requieran atención.
- **Equipos de producto y negocio:** para utilizar los resultados como una fuente complementaria de información en la mejora de productos y servicios.

Estos son usuarios potenciales de la solución. Su utilidad real deberá evaluarse mediante los resultados obtenidos y, en una etapa posterior, con datos y necesidades de una empresa concreta.

## Alcance del proyecto

El proyecto contempla la construcción de un pipeline de datos, el entrenamiento y la evaluación de modelos, y la exposición de predicciones mediante una API.

La evaluación se centrará en la calidad de los datos, el rendimiento de clasificación, la comparación entre modelos, la reproducibilidad del procesamiento y la correcta integración de los componentes.

El prototipo no incluye, en su alcance actual, la integración con sistemas empresariales de producción, la monitorización de opiniones en tiempo real ni la toma automática de decisiones comerciales.

## Tecnologías y justificación

Las tecnologías se seleccionan en función de las responsabilidades que desempeñan dentro del pipeline y de los objetivos técnicos del proyecto.

| Tecnología | Propósito y justificación |
|---|---|
| **Python** | Lenguaje principal para integrar el procesamiento de datos, el entrenamiento de modelos y la API. |
| **MongoDB** | Almacenar las reseñas originales como documentos, conservando su estructura y los campos asociados. |
| **Dask** | Preparar y transformar conjuntos de datos mediante operaciones que pueden ejecutarse de forma paralela y escalar más allá de un procesamiento exclusivamente secuencial. |
| **PySpark** | Demostrar el procesamiento con Spark en modo local y comparar su enfoque con Dask sobre datos equivalentes. |
| **Parquet** | Almacenar los datos procesados en un formato columnar que facilite su lectura y reutilización entre etapas del pipeline. |
| **MinIO y S3 compatible** | Simular el almacenamiento de objetos y demostrar la carga y recuperación de artefactos sin depender de un servicio cloud de pago. |
| **scikit-learn** | Implementar baselines y modelos clásicos, además de pipelines, validación cruzada y búsqueda de hiperparámetros. |
| **PyTorch** | Implementar y evaluar una arquitectura de aprendizaje profundo para clasificación de texto. |
| **FastAPI** | Exponer las predicciones del modelo seleccionado mediante una interfaz HTTP. |
| **Docker** | Facilitar la ejecución reproducible de los servicios que requieren infraestructura local, como MongoDB y MinIO. |
| **pytest** | Automatizar pruebas para comprobar el comportamiento de los componentes y prevenir regresiones. |

Dask y PySpark no se incorporan con la intención de duplicar el procesamiento sin motivo. Su uso permitirá implementar operaciones comparables y documentar sus diferencias, limitaciones y escenarios de aplicación.

MinIO se utilizará como simulación local de almacenamiento compatible con S3, evitando que el desarrollo dependa de contratar infraestructura cloud.

## Dataset y condiciones de uso

El proyecto utiliza como fuente de datos `SetFit/amazon_reviews_multi_es`, un conjunto de reseñas de productos en español derivado del *Multilingual Amazon Reviews Corpus*.

- **Fuente:** https://huggingface.co/datasets/SetFit/amazon_reviews_multi_es
- **Licencia y condiciones del corpus original:** https://github.com/awslabs/open-data-docs/blob/main/docs/amazon-reviews-ml/license.txt
- **Uso previsto:** experimentación académica con clasificación de reseñas.
- **Gestión de los datos:** el repositorio no incluirá el conjunto de datos completo. Las instrucciones de obtención y preparación se documentarán para permitir la reproducción del proyecto.

El dataset contiene etiquetas asociadas a las valoraciones de las reseñas. Estas etiquetas deben interpretarse correctamente antes de definir las categorías de sentimiento y evaluar los modelos; no se asumirá que las valoraciones y las categorías positivo, neutral y negativo son equivalentes sin establecer una correspondencia explícita.

La licencia del código fuente es independiente de las condiciones aplicables al dataset. Antes de redistribuir datos, muestras de reseñas o artefactos derivados, se revisarán las condiciones de uso correspondientes.

## Evaluación y criterios de éxito

El proyecto se evaluará mediante criterios técnicos y de calidad:

- Integridad y trazabilidad de los datos procesados.
- Reproducibilidad de la ingesta, el procesamiento y los experimentos.
- Comparación de modelos mediante métricas adecuadas para el problema, no únicamente exactitud.
- Análisis de errores, validación y prevención de fuga de datos.
- Comparación razonada entre aprendizaje automático clásico y aprendizaje profundo.
- Funcionamiento verificable de la API y de las pruebas automatizadas.
- Documentación de las decisiones técnicas, limitaciones y resultados obtenidos.

Los resultados cuantitativos se documentarán una vez ejecutados los experimentos. No se presupone de antemano que el modelo de aprendizaje profundo superará a los modelos clásicos.

## Estado del proyecto

**En desarrollo — Sprint 1: ingesta y almacenamiento.**

El proyecto se implementará de forma incremental, con historias de usuario, pruebas y documentación versionada en el repositorio.

## Reproducibilidad y documentación

El repositorio incluirá instrucciones de instalación, configuración del entorno, ejecución de los componentes y pruebas automatizadas. Las credenciales se gestionarán mediante variables de entorno y no se incluirán en el control de versiones.

Los datos completos y otros artefactos generados durante la ejecución se mantendrán fuera del repositorio cuando corresponda. Las decisiones de arquitectura, los experimentos y las limitaciones se documentarán para facilitar la revisión técnica del proyecto.

## Requisitos previos

- Python 3.10 o superior.
- pip y un entorno virtual de Python.
- Docker y Docker Compose.
- Acceso a internet para obtener el dataset desde Hugging Face.

## Instalación y configuración

Clona el repositorio y entra en su directorio:

```bash
git clone https://github.com/kevinmontanodev/sentiment360
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

Edita `.env` y configura las credenciales locales de MongoDB. La URI debe coincidir con las credenciales configuradas para el contenedor.

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

## Procesamiento de reseñas con Dask

Después de la ingesta, limpia las reseñas de MongoDB y genera el dataset Parquet:

```bash
python -m src.procesamiento.procesar_resenas
```

La salida se guarda en `data/processed/reviews/`, junto con `_resumen.json`, que
indica los registros leídos, conservados y rechazados. El proceso conserva los
identificadores y las etiquetas, valida el Parquet y no modifica MongoDB.

Para una ejecución limitada y separada:

```bash
python -m src.procesamiento.procesar_resenas --limit 10 --output data/processed/reviews_prueba
```

Usa un directorio nuevo en cada ejecución. Consulta
[docs/procesamiento-dask.md](docs/procesamiento-dask.md) para las reglas de limpieza,
las opciones y los resultados de las pruebas.

## Procesamiento de reseñas con PySpark

Para procesar el dataset Parquet en modo local con PySpark y verificar la consistencia de las agregaciones frente a Dask:

```bash
python -m src.procesamiento.procesar_pyspark
```

## Pruebas

Ejecuta las pruebas automatizadas desde la raíz del proyecto:

```bash
pytest -v
```

Las pruebas cubren la validación de reseñas, el repositorio MongoDB, el servicio de ingesta y el procesamiento con Dask hasta la lectura del Parquet. Se utiliza `mongomock` para simular operaciones de MongoDB en las pruebas unitarias.

## Reproducibilidad

El repositorio incluye la configuración de dependencias, la configuración de pruebas, un archivo de ejemplo de variables de entorno y la definición del servicio MongoDB mediante Docker Compose.

El corpus completo, las credenciales locales, los entornos virtuales y los archivos generados no deben versionarse.

Las instrucciones de procesamiento, entrenamiento, evaluación y uso de la API se ampliarán conforme se implementen y verifiquen esos componentes.

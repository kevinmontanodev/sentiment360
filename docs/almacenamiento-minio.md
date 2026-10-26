# Almacenamiento de objetos con MinIO (US-05)

El proceso sube a MinIO el artefacto Parquet generado por el procesamiento
(US-03), lo descarga en otro directorio y verifica que la copia recuperada sea
idéntica y legible. MinIO implementa la API de Amazon S3, por lo que el mismo
código funcionaría con S3 cambiando solo las variables de entorno. Así, el
almacenamiento de artefactos queda desacoplado de la ingesta (MongoDB) y de la
transformación (Dask).

## Configuración

El servicio `minio` está definido en `compose.yaml`. Las credenciales y la
conexión se leen de `.env`, que no se versiona; `.env.example` solo contiene
valores de ejemplo.

|Variable|Uso|
|-|-|
|`MINIO\_ROOT\_USER`, `MINIO\_ROOT\_PASSWORD`|Credenciales con las que arranca el servidor MinIO. La contraseña debe tener al menos 8 caracteres.|
|`S3\_ENDPOINT\_URL`|Dirección de la API S3 que usa `boto3` (`http://localhost:9010`).|
|`S3\_ACCESS\_KEY`, `S3\_SECRET\_KEY`|Credenciales del cliente. En local coinciden con las de MinIO.|
|`S3\_BUCKET`|Bucket donde se guardan los artefactos. Se crea si no existe.|

Se separan las variables del servidor (`MINIO\_\*`) y del cliente (`S3\_\*`) para
que el código no dependa de MinIO: para usar otro servicio S3 basta con cambiar
las variables `S3\_\*`.

### Decisiones técnicas

* **Imagen `cgr.dev/chainguard/minio`.** La imagen oficial `minio/minio` fue
retirada de Docker Hub en 2026 y ya no se puede descargar. Se usa la
compilación del mismo servidor MinIO que mantiene Chainguard.
* **Puertos 9010 (API) y 9011 (consola).** MinIO usa internamente los puertos
9000 y 9001, que suelen estar ocupados por otras aplicaciones. En el equipo
local se publican como 9010 y 9011, solo en `127.0.0.1`.
* **Sin healthcheck.** La imagen de Chainguard no incluye `curl` ni `wget`, por
lo que no se reutilizó el healthcheck habitual de MinIO.

## Ejecutar

### 1\. Iniciar MinIO

```bash
docker compose -f compose.yaml up -d
docker compose -f compose.yaml ps
```

La consola web queda disponible en http://localhost:9011 con el usuario y la
contraseña de `.env`.

### 2\. Generar el artefacto (US-03)

Se usa una muestra reproducible de 1000 reseñas para que las pruebas sean
rápidas:

```bash
python -m src.ingesta.cargar\_dataset --limit 1000 --collection reviews\_muestra
python -m src.procesamiento.procesar\_resenas --collection reviews\_muestra --output data/processed/reviews\_muestra
```

La muestra contiene solo la etiqueta `0`, porque el split `train` del dataset
está ordenado por etiqueta. No afecta a esta historia, que valida el
almacenamiento, pero no debe usarse `--limit` de esta forma para entrenar
modelos.

### 3\. Subir, recuperar y verificar

```bash
python -m src.almacenamiento.transferir\_artefacto --source data/processed/reviews\_muestra --destination data/recovered/reviews\_muestra --prefix reviews\_muestra
```

El comando:

1. crea el bucket si no existe;
2. sube cada archivo del directorio bajo el prefijo indicado;
3. descarga los objetos de ese prefijo en el directorio de destino;
4. compara la lista de archivos y el hash SHA-256 de cada uno;
5. lee ambos Parquet con pandas y comprueba que los datos sean iguales.

Sin argumentos usa `data/processed/reviews` como origen. Para repetir una
ejecución, elige un `--destination` nuevo; el programa rechaza destinos
existentes para no mezclar descargas.

### 4\. Detener los servicios

```bash
docker compose -f compose.yaml stop
```

Los objetos se conservan en el volumen `minio\_data`.

## Pruebas

```bash
pytest tests/test\_almacenamiento\_s3.py -v
```

Las pruebas usan `moto` para simular S3 en memoria, por lo que no necesitan
MinIO en ejecución. Cubren las variables obligatorias, la creación del bucket
cuando ya existe, la subida y recuperación de un directorio Parquet y la
detección de un archivo modificado.

## Resultados de validación



Pruebas automatizadas:



```text

tests/test\_almacenamiento\_s3.py::test\_settings\_require\_all\_variables PASSED

tests/test\_almacenamiento\_s3.py::test\_ensure\_bucket\_can\_run\_twice PASSED

tests/test\_almacenamiento\_s3.py::test\_transfer\_uploads\_and\_recovers\_identical\_parquet PASSED

tests/test\_almacenamiento\_s3.py::test\_verify\_detects\_modified\_file PASSED

4 passed in 1.4s

```



Ejecución contra MinIO local con la muestra de 1000 reseñas:



```text

Resumen de almacenamiento

{

&#x20; "bucket": "sentiment360-artefactos",

&#x20; "keys": \[

&#x20;   "reviews\_muestra/\_resumen.json",

&#x20;   "reviews\_muestra/part-00000.parquet"

&#x20; ],

&#x20; "files": 2,

&#x20; "rows": 1000,

&#x20; "verified": true

}

```


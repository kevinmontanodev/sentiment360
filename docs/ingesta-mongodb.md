# Ingesta y almacenamiento de reseñas en MongoDB

## 1. Objetivo

La US-02 implementa la ingesta de reseñas originales del dataset `SetFit/amazon_reviews_multi_es` y su almacenamiento en MongoDB para permitir consultas posteriores dentro de Sentiment360.

El proceso separa la validación de datos, la lógica de ingesta y la persistencia para facilitar el mantenimiento y las pruebas automatizadas.

## 2. Arquitectura

Los componentes principales son:

| Componente | Responsabilidad |
|---|---|
| `src/config.py` | Lee y valida la configuración mediante variables de entorno. |
| `src/ingesta/validador.py` | Comprueba los campos y tipos de cada reseña. |
| `src/ingesta/servicio_ingesta.py` | Coordina la validación y la inserción por lotes. |
| `src/almacenamiento/repositorio_mongodb.py` | Gestiona la persistencia, los índices y el conteo de documentos. |
| `src/ingesta/cargar_dataset.py` | Ejecuta la ingesta desde Hugging Face. |
| `src/ingesta/inspeccionar_dataset.py` | Permite inspeccionar registros del dataset antes de la ingesta. |
| `src/ingesta/verificar_conexion.py` | Comprueba la conexión con MongoDB. |
| `src/ingesta/probar_ingesta_mongodb.py` | Ejecuta una prueba controlada de persistencia e idempotencia. |

## 3. Esquema de los documentos

Cada reseña debe contener los siguientes campos:

| Campo | Tipo | Validación |
|---|---|---|
| `id` | Cadena | Obligatorio y no vacío. |
| `text` | Cadena | Obligatorio y no vacío. |
| `label` | Entero | Valor entre 0 y 4. |
| `label_text` | Cadena | Debe coincidir con la representación textual de `label`. |

El validador rechaza los registros que no cumplen el esquema. El servicio contabiliza las reseñas rechazadas sin enviarlas al repositorio.

## 4. Configuración

Las variables de entorno se definen en `.env`, tomando `.env.example` como plantilla:

- `MONGODB_URI`: URI de conexión a MongoDB.
- `MONGODB_DATABASE`: nombre de la base de datos.
- `MONGO_ROOT_USERNAME`: usuario administrador inicial del contenedor.
- `MONGO_ROOT_PASSWORD`: contraseña del usuario administrador inicial.

La URI debe utilizar credenciales compatibles con el contenedor y especificar la base de autenticación correspondiente.

El archivo `.env` es local y no debe versionarse. Para cambiar la configuración de un entorno, se deben modificar las variables correspondientes sin introducir credenciales en el código fuente.

## 5. Ejecución

### Verificar la conexión

```bash
python -m src.ingesta.verificar_conexion
```

### Inspeccionar el dataset

```bash
python -m src.ingesta.inspeccionar_dataset
```

### Cargar una muestra de prueba

```bash
python -m src.ingesta.cargar_dataset --limit 10 --collection reviews_us02_prueba
```

### Cargar el split completo de entrenamiento

```bash
python -m src.ingesta.cargar_dataset
```

El tamaño del lote predeterminado es de 500 reseñas y puede modificarse mediante `--batch-size`.

La opción `--limit` restringe el número de registros leídos para una ejecución de prueba. Si se omite, se procesa el split completo `train`.

## 6. Control de duplicados e integridad

El repositorio crea un índice único sobre el campo `id`.

La estrategia de persistencia evita reemplazar documentos existentes. Los identificadores repetidos dentro de un lote se contabilizan como duplicados y MongoDB impide insertar nuevamente identificadores ya almacenados.

El servicio devuelve los siguientes contadores:

- `received`: reseñas procesadas por el servicio.
- `inserted`: documentos insertados durante la ejecución.
- `duplicates`: reseñas que no se insertaron por tener un identificador repetido.
- `rejected`: reseñas que no superaron la validación.
- `stored_total`: cantidad de documentos existentes en la colección después de la ejecución.

El total almacenado representa el contenido completo de la colección, no solamente las inserciones de la ejecución actual.

## 7. Pruebas automatizadas

Las pruebas se ejecutan con:

```bash
pytest -v
```

La suite incluye casos para:

- Validación de campos obligatorios y valores permitidos.
- Inserción de reseñas y manejo de lotes vacíos.
- Detección de identificadores duplicados.
- Conservación de documentos existentes.
- Rechazo de reseñas inválidas.
- Comportamiento del servicio ante ejecuciones repetidas.
- Validación del tamaño del lote.

Las pruebas unitarias del repositorio utilizan `mongomock`; la conexión, la carga limitada y la ingesta completa se comprobaron adicionalmente contra una instancia real de MongoDB.

## 8. Resultados de la ingesta inicial

Se ejecutó la ingesta completa del split `train` de `SetFit/amazon_reviews_multi_es`.

| Métrica | Resultado |
|---|---:|
| Reseñas recibidas | 200.000 |
| Documentos insertados | 200.000 |
| Duplicados | 0 |
| Rechazados | 0 |
| Total almacenado | 200.000 |

Estos resultados corresponden a la ejecución inicial realizada en el entorno de desarrollo. Las reseñas de `validation` y `test` no forman parte de esta carga.

También se verificó la idempotencia mediante una muestra de 10 reseñas: la primera ejecución insertó los documentos y la segunda no creó documentos adicionales.

La suite automatizada reportó 26 pruebas exitosas después de configurar `pytest.ini` para resolver los imports del paquete `src`.

## 9. Consideraciones

- La ingesta utiliza streaming para evitar cargar el dataset completo en memoria.
- El procesamiento por lotes reduce el tamaño de cada operación de escritura.
- Los datos del corpus no se incluyen en el repositorio Git.
- La colección `reviews_us02_prueba` se reserva para pruebas; la colección predeterminada para la ingesta es `reviews`.
- El proceso debe poder repetirse sin generar duplicados.
- Las condiciones de uso del dataset deben revisarse antes de distribuir datos derivados o artefactos entrenados.
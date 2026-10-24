# Procesamiento de reseñas con Dask (US-03)

El proceso lee las reseñas originales de MongoDB mediante un cursor, limpia un
lote a la vez y guarda archivos Parquet en `data/processed/reviews/`. No modifica
los documentos de MongoDB ni carga la colección completa en memoria.

## Ejecutar

Instala las dependencias de `requirements.txt`, configura `.env` según
`.env.example`, inicia MongoDB y realiza la [ingesta](ingesta-mongodb.md).
Después, desde la raíz del proyecto:

```bash
python -m src.procesamiento.procesar_resenas
```

La configuración de conexión utiliza `MONGODB_URI` y `MONGODB_DATABASE`.
La colección predeterminada es `reviews` y el lote predeterminado es de 5000
documentos. Para probar una colección y una salida separadas:

```bash
python -m src.procesamiento.procesar_resenas --collection reviews_us02_prueba --limit 10 --batch-size 5 --output data/processed/reviews_prueba
```

`--limit` limita los documentos leídos, incluidos los rechazados. Para repetir
una ejecución, elige un directorio de salida nuevo con `--output`; el programa
rechaza destinos existentes para no sobrescribir resultados ni mezclar muestras
con el procesamiento completo.

## Reglas de limpieza

Se reutiliza `ReviewValidator`, el mismo validador de la ingesta:

- Son obligatorios `id`, `text`, `label` y `label_text`.
- `id` y `text` deben ser cadenas no vacías; se rechazan valores nulos, campos
  ausentes y tipos incorrectos.
- `label` debe ser un entero de 0 a 4. No se convierten cadenas, decimales ni
  booleanos a etiquetas.
- `label_text` debe coincidir exactamente con la representación de `label`.
- Se normaliza el texto a Unicode NFC y se sustituyen espacios consecutivos,
  tabulaciones y saltos de línea por un espacio. Se recortan los extremos.
- Se conservan tildes, negaciones, puntuación, mayúsculas y emojis, porque pueden
  aportar información del sentimiento. No se eliminan palabras ni se aplica
  stemming.
- Se conservan el identificador y las dos etiquetas originales. La salida solo
  incluye los cuatro campos del esquema; se omite el `_id` interno de MongoDB.

Por ejemplo, `  ¡NO está mal!\nMuy útil 😊  ` queda como
`¡NO está mal! Muy útil 😊`.

No se deduplican registros en esta etapa: la ingesta ya mantiene un índice único
por `id`. Cada registro inválido se cuenta una sola vez como rechazado.

## Implementación y salida

`MongoReviewRepository.iter_reviews()` lee mediante cursor. En cada lote,
`Dask Bag` reparte la validación y limpieza en un máximo de cuatro particiones,
utilizando hilos locales. Pandas y PyArrow escriben las filas válidas de ese lote
en un archivo `part-00000.parquet`, `part-00001.parquet`, etc.

Al terminar, `Dask DataFrame` relee los Parquet y verifica:

- Columnas esperadas y ausencia de valores nulos.
- Identificadores y textos no vacíos.
- Etiquetas dentro de 0 a 4 y correspondencia de `label_text`.
- Cantidad guardada igual a la cantidad conservada.
- Distribución de etiquetas igual a la contabilizada durante la limpieza.

Una fuente vacía o con todas las reseñas rechazadas genera un Parquet vacío con
el mismo esquema. La salida se prepara en un directorio temporal junto al destino
y se mueve al destino después de validarla. Si falla la lectura, la escritura o
la validación, no se publica un resultado parcial.

El resumen se imprime en consola y se guarda en `_resumen.json`:

| Campo | Significado |
|---|---|
| `read` | Documentos leídos de MongoDB. |
| `kept` | Reseñas válidas guardadas. |
| `rejected` | Documentos descartados; `read = kept + rejected`. |
| `labels` | Cantidad conservada por cada etiqueta de 0 a 4. |
| `parquet_verified` | Confirmación de la relectura y validación. |

El prefijo `_` permite leer el directorio como dataset Parquet sin interpretar el
resumen JSON como un archivo de datos. Para cargar la salida con Dask:

```python
import dask.dataframe as dd

reviews = dd.read_parquet("data/processed/reviews")
print(reviews.head())
```

Los archivos generados y los datos del corpus no se versionan.

## Validación realizada

```bash
python -m pytest -q
```

Resultado: **53 pruebas exitosas**, incluidas las 26 pruebas previas de ingesta.
La prueba de integración usa MongoDB simulado con `mongomock`, Dask real y archivos
Parquet reales. Procesa siete documentos sintéticos en lotes de dos:

| Métrica | Resultado |
|---|---:|
| Leídos | 7 |
| Conservados | 5 |
| Rechazados | 2 |
| Por etiqueta (0, 1, 2, 3, 4) | 1 cada una |

También se prueban campos ausentes, nulos, tipos inválidos, normalización de
acentos, conservación de ID y etiquetas, colección vacía, todos los registros
rechazados, interrupción de lectura, protección del destino y ejecución de la
CLI con colección y límite. Se comprueba que MongoDB conserve sus documentos.

Esta validación no corresponde al corpus completo: no se dispuso de una conexión
al MongoDB del equipo con las 200.000 reseñas. Al ejecutar allí el comando,
`_resumen.json` registrará las cantidades reales.

Referencias: [Dask Bag](https://docs.dask.org/en/stable/bag.html) y
[lectura de Parquet con Dask](https://docs.dask.org/en/latest/dataframe-parquet.html).

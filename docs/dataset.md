# Documentación del dataset — Sentiment360

## 1. Información general

- **Proyecto:** Sentiment360
- **Dataset:** [SetFit/amazon_reviews_multi_es](https://huggingface.co/datasets/SetFit/amazon_reviews_multi_es)
- **Fuente original:** Multilingual Amazon Reviews Corpus.
- **Tarea:** clasificación de reseñas en español según su calificación.
- **Partición analizada:** `train`.
- **Registros analizados:** 200,000.
- **Notebook de exploración:** `notebooks/01_exploracion_dataset.ipynb`.

El objetivo de esta exploración es comprender la estructura, distribución, integridad y posibles problemas de calidad de los datos antes de realizar transformaciones o entrenar modelos.

## Reproducibilidad

### Requisitos previos

- Python compatible con las dependencias del proyecto.
- Git para clonar el repositorio.
- Conexión a Internet para descargar el dataset desde Hugging Face.
- Dependencias instaladas desde `requirements.txt`.

### Preparación del entorno

Desde la raíz del repositorio, crear y activar un entorno virtual e instalar las dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows, la activación del entorno virtual se realiza mediante:

```powershell
.venv\Scripts\Activate.ps1
```

### Ejecución de la exploración

Abrir `notebooks/01_exploracion_dataset.ipynb` en Jupyter Notebook, JupyterLab o Google Colab y ejecutar las celdas en orden.

El notebook carga las particiones oficiales del dataset `SetFit/amazon_reviews_multi_es` desde Hugging Face y realiza las comprobaciones de estructura, distribución de etiquetas, calidad de los datos y solapamiento entre particiones.

Posteriormente, construye los conjuntos de evaluación complementarios mediante coincidencias exactas de texto, verifica que no existan intersecciones entre las particiones resultantes y comprueba la distribución de las cinco clases.

### Verificación de resultados

Al finalizar la ejecución, se deben comprobar los siguientes resultados de referencia:

| Partición | Registros esperados |
|---|---:|
| Train | 200,000 |
| Validation complementario | 4,929 |
| Test complementario | 4,934 |

Las intersecciones de textos entre las tres particiones complementarias deben ser iguales a cero. La distribución de las etiquetas en validación y prueba debe permanecer aproximadamente equilibrada.

Estos valores permiten detectar posibles diferencias en la ejecución. Si cambian los datos remotos, las versiones de las dependencias o el código, los resultados podrían variar.

### Trazabilidad

El notebook contiene el código, las comprobaciones y los resultados de la exploración. Este documento resume los hallazgos y las decisiones metodológicas.

Los conjuntos originales no se modifican ni se sustituyen por los conjuntos complementarios. El filtrado se aplica únicamente para construir una alternativa de evaluación reproducible.

Para mantener la trazabilidad, se recomienda conservar el notebook actualizado junto con esta documentación y registrar los cambios relevantes en el control de versiones.

## 2. Estructura de los datos

La partición analizada contiene cuatro columnas:

| Columna | Tipo observado | Descripción |
|---|---|---|
| `id` | String | Identificador de la reseña. |
| `text` | String | Texto de la reseña en español. |
| `label` | Entero | Etiqueta numérica de clasificación, con valores de 0 a 4. |
| `label_text` | String | Representación textual de la etiqueta numérica. |

**Observación:** `label_text` contiene cadenas como `"0"`, `"1"`, `"2"`, `"3"` y `"4"`. No contiene nombres descriptivos de sentimientos.

Las etiquetas representan cinco niveles de calificación, derivados de las estrellas originales:

| Etiqueta | Calificación original |
|---:|---:|
| 0 | 1 estrella |
| 1 | 2 estrellas |
| 2 | 3 estrellas |
| 3 | 4 estrellas |
| 4 | 5 estrellas |

Por tanto, el problema se puede formular como clasificación de cinco clases ordinales. La conversión posterior a sentimientos positivos, neutrales y negativos requeriría definir y justificar explícitamente una estrategia adicional.

## 3. Distribución de clases

La partición `train` presenta la siguiente distribución:

| Etiqueta | Registros | Porcentaje |
|---:|---:|---:|
| 0 | 40,000 | 20 % |
| 1 | 40,000 | 20 % |
| 2 | 40,000 | 20 % |
| 3 | 40,000 | 20 % |
| 4 | 40,000 | 20 % |
| **Total** | **200,000** | **100 %** |

Las cinco clases están equilibradas en la partición analizada. Este resultado describe únicamente la distribución observada y no garantiza que otras particiones o datos reales presenten la misma distribución.

## 4. Comprobaciones de calidad

Los siguientes resultados corresponden a la revisión inicial de la partición `train`.

| Comprobación | Resultado |
|---|---:|
| Registros analizados | 200,000 |
| IDs nulos | 0 |
| Textos nulos | 0 |
| Textos vacíos | 0 |
| IDs duplicados | 0 |
| Filas involucradas en textos repetidos | 2,483 |
| Textos únicos que aparecen más de una vez | 747 |
| Grupos de textos repetidos con una sola etiqueta | 349 |
| Grupos con etiquetas contradictorias | 398 |
| Porcentaje de grupos repetidos contradictorios | 53.28 % |

### Interpretación de los duplicados

Se encontraron 747 textos únicos que aparecen en más de una fila. En conjunto, estos grupos involucran 2,483 filas.

De los 747 grupos, 349 tienen una única etiqueta y 398 presentan dos o más etiquetas distintas para un mismo texto. Por ello, el 53.28 % de los grupos de textos repetidos presenta etiquetas contradictorias.

Un texto idéntico puede aparecer con distintas calificaciones porque las reseñas breves pueden ser ambiguas o porque el texto por sí solo no contiene suficiente información para recuperar la valoración original. Estos resultados no demuestran por sí mismos que las etiquetas sean incorrectas.

También es importante distinguir los duplicados exactos de las variantes textuales: diferencias de puntuación, mayúsculas o espacios pueden hacer que dos textos similares no se consideren duplicados en una comparación literal.

## 5. Riesgos identificados

1. **Ambigüedad de etiquetas:** un mismo texto puede estar asociado a distintas calificaciones.
2. **Posible fuga de información:** si textos iguales aparecen en entrenamiento y evaluación, las métricas podrían resultar demasiado optimistas.
3. **Duplicados aproximados:** una comparación exacta no detecta todas las variantes de un mismo texto.
4. **Generalización pendiente:** el balance de clases observado en `train` no garantiza una distribución idéntica en otros conjuntos.

## 6. Decisiones provisionales

- Conservar los datos originales sin alteraciones durante la exploración.
- No eliminar automáticamente los textos repetidos ni las etiquetas contradictorias.
- Revisar las particiones oficiales antes de definir la estrategia de evaluación.
- Investigar posibles coincidencias entre entrenamiento, validación y prueba.
- Evitar que una misma reseña o sus duplicados filtren información entre los conjuntos utilizados para entrenar y evaluar.
- Registrar cualquier transformación y justificar su efecto sobre los datos.
- Comparar las métricas de los modelos con una línea base sencilla y analizar sus errores.

Estas decisiones son provisionales y se revisarán después del análisis completo de las particiones.

## 7. Fuente y condiciones de uso

Dataset: [SetFit/amazon_reviews_multi_es en Hugging Face](https://huggingface.co/datasets/SetFit/amazon_reviews_multi_es).

Condiciones del corpus original: [Multilingual Amazon Reviews Corpus — licencia y condiciones](https://github.com/awslabs/open-data-docs/blob/main/docs/amazon-reviews-ml/license.txt).

El uso del corpus está sujeto a sus condiciones específicas, que contemplan el acceso para investigación académica y restricciones sobre la redistribución y el uso comercial. La licencia del código de Sentiment360 no sustituye ni modifica las condiciones aplicables al dataset.

El equipo debe verificar las condiciones vigentes antes de compartir datos, ejemplos de reseñas, modelos derivados o resultados que puedan incluir contenido del corpus. No se incorporará el corpus completo al repositorio.

## 8. Reproducibilidad y trazabilidad

- **Notebook de referencia:** `notebooks/01_exploracion_dataset.ipynb`.
- **Dataset:** `SetFit/amazon_reviews_multi_es`.
- **Partición documentada:** `train`.
- **Tamaño observado:** 200,000 registros.
- **Entorno local:** Python en un entorno virtual `.venv`; las versiones de las bibliotecas se documentan en `requirements.txt`.

En la siguiente etapa se registrarán las particiones oficiales disponibles, sus tamaños, las comprobaciones entre particiones y las decisiones definitivas de preparación de los datos.

## 9. Particiones oficiales y distribución de clases

El dataset proporciona tres particiones oficiales: entrenamiento (`train`), validación (`validation`) y prueba (`test`).

| Partición | Registros | Uso previsto |
|---|---:|---|
| `train` | 200,000 | Entrenamiento de modelos |
| `validation` | 5,000 | Selección y ajuste de modelos |
| `test` | 5,000 | Evaluación final |
| **Total** | **210,000** | |

Las tres particiones presentan una distribución uniforme de las cinco etiquetas:

| Etiqueta | Train | Validation | Test |
|---:|---:|---:|---:|
| 0 | 40,000 (20 %) | 1,000 (20 %) | 1,000 (20 %) |
| 1 | 40,000 (20 %) | 1,000 (20 %) | 1,000 (20 %) |
| 2 | 40,000 (20 %) | 1,000 (20 %) | 1,000 (20 %) |
| 3 | 40,000 (20 %) | 1,000 (20 %) | 1,000 (20 %) |
| 4 | 40,000 (20 %) | 1,000 (20 %) | 1,000 (20 %) |
| **Total** | **200,000** | **5,000** | **5,000** |

Esta distribución permite evaluar el rendimiento por clase sin que una clase tenga mayor representación que las demás dentro de las particiones analizadas.

### Estrategia de evaluación

Se conservarán las particiones oficiales del dataset. `train` se utilizará para entrenar; `validation`, para seleccionar modelos y ajustar hiperparámetros; y `test` se reservará para la evaluación final.

Antes de completar la evaluación, se comprobarán posibles coincidencias de texto entre las particiones. El balance de clases no garantiza por sí mismo que estén libres de duplicados o de otras formas de fuga de información.

## 10. Coincidencias entre particiones

Se compararon los textos exactos de las particiones oficiales `train`, `validation` y `test`.

| Comparación | Textos compartidos | Con etiquetas contradictorias |
|---|---:|---:|
| Train ∩ Validation | 66 | 41 |
| Train ∩ Test | 57 | 40 |
| Validation ∩ Test | 9 | 3 |

Los textos compartidos se identificaron mediante comparación literal de la columna `text`. Se considera que una coincidencia tiene etiquetas contradictorias cuando el conjunto de etiquetas asociado al texto en ambas particiones contiene más de un valor.

Los resultados muestran coincidencias de texto entre todas las parejas de particiones. Una parte importante de estas coincidencias presenta etiquetas diferentes, lo que puede dificultar la interpretación de las métricas de evaluación.

Estos conteos corresponden a comparaciones por pares y no representan necesariamente textos únicos globales, dado que un mismo texto puede aparecer en las tres particiones.

### Implicaciones para la evaluación

- No se asumirá que las particiones originales están libres de coincidencias textuales.
- Se conservará el dataset original sin modificaciones para mantener la trazabilidad.
- Antes de entrenar los modelos, se definirá una estrategia para gestionar las coincidencias y evitar que el rendimiento se interprete sin considerar este riesgo.
- Se documentarán las decisiones adoptadas y su posible impacto sobre la comparabilidad con resultados obtenidos usando las particiones originales.

La comparación realizada detecta duplicados exactos; no identifica todas las variantes textuales ni demuestra por sí sola que exista fuga de información en todos los modelos posibles.

## 11. Solapamiento global entre particiones

Para evitar contar un mismo texto varias veces al sumar las intersecciones por pares, se calculó la unión de las coincidencias entre `train`, `validation` y `test`.

| Indicador | Textos únicos |
|---|---:|
| Presentes en las tres particiones | 6 |
| Presentes en al menos dos particiones | 120 |
| Exclusivos de `train` | 198,147 |
| Exclusivos de `validation` | 4,926 |
| Exclusivos de `test` | 4,934 |

Los valores de exclusividad corresponden a textos únicos presentes únicamente en la partición indicada, no al número total de filas.

### Interpretación

Se identificaron 120 textos únicos compartidos por al menos dos particiones, incluidos 6 que aparecen en las tres. Por tanto, las particiones oficiales presentan cierto solapamiento de texto exacto.

Este resultado complementa la comprobación anterior de etiquetas contradictorias. Antes de entrenar y evaluar los modelos, se deberá decidir cómo gestionar las coincidencias entre particiones y mantener el mismo protocolo de evaluación para todas las familias de modelos.

Se conservarán intactos los datos originales. Cualquier conjunto de evaluación alternativo deberá generarse mediante un procedimiento documentado y reproducible, sin utilizar el conjunto de prueba para ajustar hiperparámetros ni seleccionar modelos.

## 12. Evaluación complementaria sin solapamiento entre particiones

### Objetivo

Se construyó una variante complementaria de los conjuntos de validación y prueba para evitar que un mismo texto exacto aparezca en más de una partición. Esta medida busca reducir el riesgo de fuga de datos (*data leakage*) durante la evaluación de los modelos.

El dataset original se conserva sin modificaciones. El conjunto de entrenamiento permanece intacto y únicamente se excluyen de validación y prueba las filas que contienen textos presentes en particiones anteriores.

### Procedimiento aplicado

1. **Train:** se conserva íntegramente, con 200,000 registros.
2. **Validation complementario:** se excluyen las filas cuyo texto aparece en `train`.
3. **Test complementario:** se excluyen las filas cuyo texto aparece en `train` o en el conjunto original de `validation`.

Este orden de prioridad conserva primero el entrenamiento, después la validación y finalmente la prueba. Las exclusiones se realizan por coincidencia exacta del texto, sin modificar las etiquetas ni eliminar duplicados internos del conjunto de entrenamiento.

### Tamaños de las particiones

| Partición | Registros originales | Registros complementarios | Filas excluidas |
|---|---:|---:|---:|
| Train | 200,000 | 200,000 | 0 |
| Validation | 5,000 | 4,929 | 71 |
| Test | 5,000 | 4,934 | 66 |
| **Total** | **210,000** | **209,863** | **137** |

Se excluyeron 137 filas de los conjuntos de evaluación, equivalentes al 1.37 % de sus 10,000 registros originales.

### Distribución de clases después del filtrado

Las etiquetas representan valoraciones de una a cinco estrellas.

**Validation complementario**

| Etiqueta | Valoración | Registros | Porcentaje |
|---:|---|---:|---:|
| 0 | 1 estrella | 987 | 20.02 % |
| 1 | 2 estrellas | 996 | 20.21 % |
| 2 | 3 estrellas | 987 | 20.02 % |
| 3 | 4 estrellas | 979 | 19.86 % |
| 4 | 5 estrellas | 980 | 19.88 % |
| **Total** | | **4,929** | **100 % aprox.** |

**Test complementario**

| Etiqueta | Valoración | Registros | Porcentaje |
|---:|---|---:|---:|
| 0 | 1 estrella | 992 | 20.11 % |
| 1 | 2 estrellas | 991 | 20.09 % |
| 2 | 3 estrellas | 993 | 20.13 % |
| 3 | 4 estrellas | 984 | 19.94 % |
| 4 | 5 estrellas | 974 | 19.74 % |
| **Total** | | **4,934** | **100 % aprox.** |

La distribución permanece equilibrada: cada clase representa aproximadamente el 20 % de ambos conjuntos complementarios.

### Validación del procedimiento

Se comprobaron las intersecciones de textos entre las tres particiones complementarias:

| Intersección | Textos compartidos |
|---|---:|
| Train ∩ Validation complementario | 0 |
| Train ∩ Test complementario | 0 |
| Validation complementario ∩ Test complementario | 0 |

Las tres intersecciones tienen cero coincidencias exactas, por lo que el procedimiento cumple su objetivo de evitar solapamientos textuales entre particiones.

### Limitaciones y decisión metodológica

- El filtrado detecta coincidencias exactas, pero no identifica necesariamente paráfrasis ni textos casi duplicados.
- Se conservan los duplicados internos del entrenamiento, incluidos los casos donde un mismo texto está asociado a etiquetas diferentes.
- Los resultados obtenidos con estos conjuntos deben identificarse como evaluación complementaria y no confundirse con la evaluación sobre las particiones oficiales sin filtrar.
- Para comparar modelos de manera justa, todos deberán utilizar las mismas particiones complementarias y el mismo protocolo de evaluación.
- Si se realiza validación cruzada sobre el entrenamiento, deberá considerarse la presencia de textos repetidos para evitar que aparezcan en los subconjuntos de entrenamiento y validación de una misma iteración.

### Conclusión

La evaluación complementaria conserva 200,000 registros de entrenamiento, 4,929 de validación y 4,934 de prueba. Se eliminaron 137 filas de evaluación por coincidencias exactas con particiones anteriores. Las cinco clases mantienen una distribución cercana al 20 % y no existen coincidencias exactas entre los tres conjuntos resultantes. Esta estrategia proporciona una evaluación más controlada frente a la fuga de datos, sin alterar las particiones originales del dataset.
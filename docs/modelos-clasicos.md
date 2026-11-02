# Modelos clásicos de Machine Learning (US-06)

Se compararon Dummy, Regresión Logística, Random Forest y SVM lineal sobre las
cinco etiquetas originales. Las etiquetas 0 a 4 representan una a cinco estrellas;
no se convierten a un problema binario ni a tres sentimientos.

## Reproducir la preparación

Desde la raíz, con las dependencias del proyecto instaladas:

```bash
python -m src.modelos.preparar_datos_ml --output data/processed/ml_evaluacion
```

El comando descarga la revisión fija
`16015418b488c9186fce74b058877ea939ca934d` de
[`SetFit/amazon_reviews_multi_es`](https://huggingface.co/datasets/SetFit/amazon_reviews_multi_es),
aplica la limpieza Dask ya implementada y conserva los archivos originales fuera
de Git. Los datos se usan bajo las condiciones del corpus documentadas en
[dataset.md](dataset.md); no se redistribuyen en este repositorio.

Se conserva train y se excluyen de validation los textos presentes en train. De
test se excluyen los presentes en train o validation original. También se excluyen
IDs compartidos. La comparación usa NFC, casefold y espacios normalizados, igual
que el preprocesador de TF-IDF. Por eso los tamaños son ligeramente distintos a
la exploración basada en coincidencias literales:

| Partición | Original | Complementaria de ML | Excluidos |
|---|---:|---:|---:|
| Train | 200.000 | 200.000 | 0 |
| Validation | 5.000 | 4.918 | 82 |
| Test | 5.000 | 4.931 | 69 |

La preparación escribe los hashes de los archivos fuente, los conteos de limpieza
y la revisión en `_source.json`. Se mantiene una copia de ese registro en
[reports/ml/fuente.json](../reports/ml/fuente.json).

En este entorno, OneDrive bloqueó el renombrado de un directorio durante la
primera preparación. El comando prepara y verifica cada partición en el directorio
temporal del sistema antes de copiarla a la carpeta sincronizada.

## Reproducir el experimento ejecutado

```bash
python -m src.modelos.comparar_ml --input data/processed/ml_evaluacion/train.parquet --test-input data/processed/ml_evaluacion/test.parquet --max-train 10000 --cv 3 --max-features 20000 --seed 42 --output models/ml_20261102_final
```

Usa un directorio de salida nuevo. `--max-train` toma una muestra aleatoria
estratificada del entrenamiento completo, con 2.000 reseñas por etiqueta. Nunca
toma simplemente las primeras filas: el corpus está ordenado por clase.
Omite `--max-train` para entrenar con los 200.000 registros; esa ejecución completa
no se realizó en este experimento.

La partición oficial de test filtrada se reserva para evaluación. La selección de
modelos e hiperparámetros se hace mediante CV dentro de train; la partición
validation queda disponible para los experimentos posteriores del equipo y no se
usa aquí para ajustar decisiones adicionales.

Si ya tienes únicamente el Parquet de la ingesta, también puedes ejecutar:

```bash
python -m src.modelos.comparar_ml --input data/processed/reviews --output models/ml_interno
```

Sin `--test-input`, se genera una separación estratificada por grupos de texto:
aproximadamente 80 % de entrenamiento y 20 % de prueba. Se usa
`StratifiedGroupKFold` con cinco folds y se reserva el primero. Un texto
normalizado no puede aparecer en ambos conjuntos. El balance es aproximado porque
no se dividen grupos repetidos; esta evaluación interna debe distinguirse de la
evaluación complementaria sobre el test oficial.

## Modelos y prevención de fuga de información

Los cuatro modelos utilizan un `Pipeline` con `TfidfVectorizer` y el clasificador.
TF-IDF aprende exclusivamente de los datos de entrenamiento de cada fold:

- Unigramas y bigramas; máximo 20.000 características.
- `min_df=2` y frecuencia de término sublineal.
- NFC, casefold y normalización de espacios; conserva tildes y negaciones.
- CV con tres folds estratificados por grupo de texto normalizado, semilla 42.
- `GridSearchCV`, un trabajo a la vez y los mismos folds para todas las familias.

| Familia | Configuración fija | Hiperparámetros buscados |
|---|---|---|
| Dummy | Clase más frecuente | Sin ajuste |
| Regresión Logística | Máximo 1.000 iteraciones | C: 0,5 y 2 |
| Random Forest | 80 árboles, un trabajo | Profundidad máxima: 30 y sin límite |
| SVM lineal | Máximo 5.000 iteraciones | C: 0,5 y 2 |

Se conserva el entrenamiento original, incluidos textos repetidos y etiquetas
contradictorias. Agrupar esos textos en CV evita que se repartan entre el ajuste y
la validación de un mismo fold. El programa rechaza IDs o textos compartidos con
test y comprueba que todas las particiones y folds contengan las cinco clases.

La selección utiliza **F1 macro de CV**, que da la misma importancia a las cinco
etiquetas y penaliza un modelo que ignore alguna clase. El modelo ganador se
elige antes de predecir test. Después se evalúan los cuatro modelos sobre el mismo
test para presentar la comparación; esas métricas no se utilizan para elegirlo.

## Resultados del 2 de noviembre de 2026

Experimento con 10.000 reseñas de entrenamiento y 4.931 de prueba. Los tiempos
incluyen la búsqueda y el reajuste de cada familia sobre la muestra completa.

| Modelo | F1 macro CV | Desviación CV | Accuracy test | Precisión macro | Recall macro | F1 macro test | Ajuste (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dummy | 0,0666 | 0,0000 | 0,2012 | 0,0402 | 0,2000 | 0,0670 | 1,57 |
| Regresión Logística | **0,4601** | 0,0099 | **0,4914** | **0,4875** | **0,4917** | **0,4892** | 7,69 |
| Random Forest | 0,4185 | 0,0126 | 0,4476 | 0,4335 | 0,4479 | 0,4350 | 43,43 |
| SVM lineal | 0,4463 | 0,0081 | 0,4794 | 0,4715 | 0,4798 | 0,4745 | 3,49 |

Se seleccionó **Regresión Logística, C=2**, por el mejor F1 macro de CV. El aumento
frente al baseline y el tiempo de ajuste observado apoyan su uso como referencia
clásica para US-07 y US-08. Esto no demuestra que sea el mejor modelo posible ni
que supere a Deep Learning, que todavía no cuenta con resultados integrados.

### Desempeño por clase de la Regresión Logística

| Etiqueta | Precisión | Recall | F1 | Soporte |
|---|---:|---:|---:|---:|
| 0 | 0,6095 | 0,6623 | 0,6348 | 992 |
| 1 | 0,4042 | 0,3895 | 0,3967 | 991 |
| 2 | 0,3907 | 0,3915 | 0,3911 | 991 |
| 3 | 0,4347 | 0,3994 | 0,4163 | 984 |
| 4 | 0,5984 | 0,6156 | 0,6069 | 973 |

Matriz de confusión: filas reales, columnas predichas; orden de etiquetas 0 a 4.

| Real / predicha | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| 0 | 657 | 221 | 84 | 18 | 12 |
| 1 | 261 | 386 | 250 | 71 | 23 |
| 2 | 108 | 223 | 388 | 203 | 69 |
| 3 | 27 | 82 | 184 | 393 | 298 |
| 4 | 25 | 43 | 87 | 219 | 599 |

Las categorías intermedias presentan los F1 más bajos. Hay, por ejemplo, 298
reseñas de etiqueta 3 predichas como 4 y 261 de etiqueta 1 predichas como 0.
Esto es compatible con la ambigüedad de las calificaciones cercanas detectada en
la exploración, pero no identifica por sí solo la causa de cada error.

Random Forest requirió el mayor tiempo de ajuste: 43,43 segundos frente a 7,69
de Regresión Logística. Es el principal costo observado en esta búsqueda; no se
midió consumo de RAM por modelo ni se realizó un perfil de CPU.

## Evidencia y límites

Los [resultados JSON](../reports/ml/resultados.json) incluyen métricas por clase,
matrices de los cuatro modelos, todas las configuraciones buscadas, tiempos,
conteos por etiqueta, hashes de los conjuntos y versiones del entorno.
Las matrices también están disponibles como CSV en `reports/ml/`.

El comando conserva el pipeline ganador en `models/ml_20261102_final/best_model.joblib`
y los IDs de las particiones en `particiones.csv`, fuera de Git. La API y los
experimentos DL pueden reutilizar ese pipeline local; no se suben modelos ni
reseñas al repositorio.

Entorno medido: Windows 11, Python 3.14.6, scikit-learn 1.9.0, pandas 3.0.5 y
NumPy 2.5.2. Estas son las versiones efectivamente disponibles en el entorno de
validación; no coinciden en todos los casos con las versiones fijadas en
`requirements.txt`. Los hashes y la semilla facilitan comparar ejecuciones, pero
no garantizan resultados idénticos entre versiones.

Limitaciones: muestra de entrenamiento reducida, búsqueda pequeña, coincidencias
normalizadas que no detectan paráfrasis y etiquetas ordinales tratadas como
multiclase. No se utiliza un protocolo temporal. Una nueva búsqueda, una muestra
mayor o datos de otra empresa pueden cambiar los resultados. El conjunto de
prueba no debe reutilizarse para ajustar hiperparámetros después de esta evaluación.

## Pruebas

```bash
python -m pytest tests/test_comparar_ml.py -q
python -m pytest -q -p no:cacheprovider
```

Las 12 pruebas nuevas pasaron. Cubren particiones por grupos, entradas inválidas,
normalización, exclusión de coincidencias, búsqueda real de los cuatro modelos,
persistencia del pipeline, métricas, matrices y ausencia de vocabulario exclusivo
de test en el modelo ajustado.

La suite completa dio **70 exitosas y 6 fallidas**. Las seis fallas corresponden
a pruebas preexistentes de PySpark por `NativeIO$Windows.access0`, con
`HADOOP_HOME` sin configurar. Se reprodujo el fallo de consistencia PySpark/Dask
en un checkout limpio de `main`, commit `5af4c45`, sin estos cambios. La suite
completa no se presenta como aprobada y no se deshabilitan esas pruebas.

Referencias técnicas: [Pipeline y TF-IDF](https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_text_feature_extraction.html),
[GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)
y [validación por grupos](https://scikit-learn.org/stable/modules/cross_validation.html).

# Procesamiento de reseñas con PySpark y comparación con Dask (US-04)

Este documento describe el procesamiento en modo local con **PySpark** a partir de los archivos Parquet generados en la **US-03**, la verificación de consistencia frente a **Dask** y los criterios técnicos para elegir cada herramienta.

---

## 1. Ejecución del módulo

Asegúrate de haber generado previamente el dataset Parquet de la US-03 (`data/processed/reviews`). Luego ejecuta desde la raíz del proyecto:

```bash
python -m src.procesamiento.procesar_pyspark

### Paso 3: Ejecutar toda la suite de pruebas del proyecto

Comprueba que todas las pruebas del repositorio (las de tus compañeros más las tuyas) pasen en verde:

```powershell
pytest -v
```
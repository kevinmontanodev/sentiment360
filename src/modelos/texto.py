"""Preprocesador importable al cargar el pipeline desde otro proceso."""

import unicodedata


def normalize_text(text: str) -> str:
    """Normalización sin aprender parámetros; conserva tildes y negaciones."""
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())

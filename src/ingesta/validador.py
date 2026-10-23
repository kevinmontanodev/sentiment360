
from collections.abc import Mapping


class ReviewValidator:
    """Valida la estructura de una reseña del dataset."""

    REQUIRED_FIELDS = ("id", "text", "label", "label_text")
    MIN_LABEL = 0
    MAX_LABEL = 4

    def validate(self, review: Mapping[str, object]) -> None:
        """Valida una reseña; lanza una excepción si no es válida."""

        if not isinstance(review, Mapping):
            raise TypeError("La reseña debe ser un objeto tipo Mapping.")

        missing_fields = [
            field for field in self.REQUIRED_FIELDS
            if field not in review
        ]

        if missing_fields:
            raise ValueError(
                f"Faltan campos obligatorios: {', '.join(missing_fields)}"
            )

        review_id = review["id"]
        text = review["text"]
        label = review["label"]
        label_text = review["label_text"]

        if not isinstance(review_id, str) or not review_id.strip():
            raise ValueError("'id' debe ser una cadena no vacía.")

        if not isinstance(text, str) or not text.strip():
            raise ValueError("'text' debe ser una cadena no vacía.")

        if type(label) is not int:
            raise ValueError("'label' debe ser un entero.")

        if not self.MIN_LABEL <= label <= self.MAX_LABEL:
            raise ValueError("'label' debe estar entre 0 y 4.")

        if not isinstance(label_text, str):
            raise ValueError("'label_text' debe ser una cadena.")

        if label_text != str(label):
            raise ValueError(
                "'label_text' debe corresponder al valor de 'label'."
            )

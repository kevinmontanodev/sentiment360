from collections.abc import Mapping

from pydantic import ValidationError

from src.ingesta.esquemas import ReviewSchema


class ReviewValidator:
    """Valida la estructura de una reseña mediante Pydantic."""

    def validate(self, review: Mapping[str, object]) -> None:
        if not isinstance(review, Mapping):
            raise TypeError("La reseña debe ser un objeto tipo Mapping.")

        try:
            ReviewSchema.model_validate(review)

        except ValidationError as error:
            missing_fields = [
                item["loc"][0]
                for item in error.errors()
                if item["type"] == "missing"
            ]

            if missing_fields:
                raise ValueError(
                    f"Faltan campos obligatorios: {', '.join(missing_fields)}"
                ) from error

            raise ValueError(str(error)) from error

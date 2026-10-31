from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator


class ReviewSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    id: StrictStr
    text: StrictStr
    label: StrictInt = Field(ge=0, le=4)
    label_text: StrictStr

    @field_validator("id", "text")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El campo no puede estar vacío.")
        return value

    @field_validator("label_text")
    @classmethod
    def validate_label_text(cls, value: str, info) -> str:
        label = info.data.get("label")

        if label is not None and value != str(label):
            raise ValueError(
                "'label_text' debe corresponder al valor de 'label'."
            )

        return value
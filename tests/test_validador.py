import pytest

from src.ingesta.validador import ReviewValidator


@pytest.fixture
def validator():
    return ReviewValidator()


@pytest.fixture
def valid_review():
    return {
        "id": "review-001",
        "text": "El producto llegó en buenas condiciones.",
        "label": 4,
        "label_text": "4",
    }


def test_valid_review(validator, valid_review):
    assert validator.validate(valid_review) is None


def test_missing_required_field(validator, valid_review):
    del valid_review["text"]

    with pytest.raises(ValueError, match="Faltan campos"):
        validator.validate(valid_review)


@pytest.mark.parametrize("field,value", [
    ("id", ""),
    ("id", "   "),
    ("text", ""),
    ("text", "   "),
])
def test_empty_string_fields(validator, valid_review, field, value):
    valid_review[field] = value

    with pytest.raises(ValueError):
        validator.validate(valid_review)


@pytest.mark.parametrize("label", [-1, 5, 2.5, True, False, "4"])
def test_invalid_label(validator, valid_review, label):
    valid_review["label"] = label

    with pytest.raises(ValueError):
        validator.validate(valid_review)


def test_label_text_mismatch(validator, valid_review):
    valid_review["label_text"] = "3"

    with pytest.raises(ValueError, match="corresponder"):
        validator.validate(valid_review)


def test_non_mapping_input(validator):
    with pytest.raises(TypeError):
        validator.validate(None)

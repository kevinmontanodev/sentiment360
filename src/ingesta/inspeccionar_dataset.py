from datasets import load_dataset

from src.ingesta.validador import ReviewValidator


def main() -> None:
    dataset = load_dataset(
        "SetFit/amazon_reviews_multi_es",
        split="train",
        streaming=True,
    )

    validator = ReviewValidator()

    print("Características del dataset:")
    print(dataset.features)

    print("\nPrimeras tres reseñas:")
    for index, review in enumerate(dataset.take(3), start=1):
        print(f"\nReseña {index}:")
        print(f"  id: {review.get('id')!r}")
        print(f"  label: {review.get('label')!r}")
        print(f"  label_text: {review.get('label_text')!r}")

        try:
            validator.validate(review)
            print("  Validación: correcta")
        except (TypeError, ValueError) as error:
            print(f"  Validación: REVISAR — {error}")


if __name__ == "__main__":
    main()

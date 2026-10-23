from pymongo import MongoClient

from src.config import MongoSettings


def main() -> None:
    settings = MongoSettings.from_env()

    with MongoClient(
        settings.uri,
        serverSelectionTimeoutMS=5000,
    ) as client:
        client.admin.command("ping")

        database = client[settings.database]
        print("Conexión con MongoDB: correcta.")
        print(f"Base de datos configurada: {database.name}")


if __name__ == "__main__":
    main()

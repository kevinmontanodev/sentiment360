import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class MongoSettings:
    """Configuración de conexión a MongoDB."""

    uri: str
    database: str
    collection: str = "reviews"

    @classmethod
    def from_env(cls) -> "MongoSettings":
        load_dotenv()

        uri = os.getenv("MONGODB_URI", "").strip()
        database = os.getenv("MONGODB_DATABASE", "").strip()

        if not uri:
            raise ValueError(
                "Falta la variable de entorno MONGODB_URI."
            )

        if not database:
            raise ValueError(
                "Falta la variable de entorno MONGODB_DATABASE."
            )

        return cls(
            uri=uri,
            database=database,
        )

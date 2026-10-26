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


@dataclass(frozen=True)
class S3Settings:
    """Configuración de conexión al almacenamiento de objetos compatible con S3."""

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str

    @classmethod
    def from_env(cls) -> "S3Settings":
        load_dotenv()

        valores = {
            nombre: os.getenv(nombre, "").strip()
            for nombre in ("S3_ENDPOINT_URL", "S3_ACCESS_KEY", "S3_SECRET_KEY", "S3_BUCKET")
        }
        faltantes = [nombre for nombre, valor in valores.items() if not valor]
        if faltantes:
            raise ValueError(
                "Faltan variables de entorno: " + ", ".join(faltantes) + "."
            )

        return cls(
            endpoint_url=valores["S3_ENDPOINT_URL"],
            access_key=valores["S3_ACCESS_KEY"],
            secret_key=valores["S3_SECRET_KEY"],
            bucket=valores["S3_BUCKET"],
        )

import os

from typing import Any

from pydantic import (
    PostgresDsn,
    computed_field,
    validator,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_PASSWORD_FILE: str | None = None
    POSTGRES_DB: str

    @model_validator(mode="before")
    @classmethod
    def check_postgres_password(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("POSTGRES_PASSWORD_FILE") is None and data.get("POSTGRES_PASSWORD") is None:
                raise ValueError("At least one of POSTGRES_PASSWORD_FILE and POSTGRES_PASSWORD must be set.")
        return data

    @validator('POSTGRES_PASSWORD_FILE', pre=True, always=True)
    def read_password_from_file(cls, v):
        if v is not None:
            file_path = v
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    return file.read().strip()
            raise ValueError(f"Password file {file_path} does not exist.")
        return v

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD if self.POSTGRES_PASSWORD else self.POSTGRES_PASSWORD_FILE,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

settings = Settings()

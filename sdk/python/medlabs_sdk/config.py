from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class MedLabsSettings(BaseSettings):
    """App-layer configuration loaded from `.env` and environment variables.

    Source order is explicitly configured as:
    1) init kwargs
    2) `.env`
    3) process environment
    4) file secrets

    This makes `.env` higher priority than system environment variables.
    """

    openai_api_key: str = Field(validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")

    langfuse_public_key: str = Field(validation_alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(validation_alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(validation_alias="LANGFUSE_HOST")

    prompt_name: str = Field(default="medlabs.extract", validation_alias="MEDLABS_PROMPT_NAME")
    prompt_version: str = Field(default="production", validation_alias="MEDLABS_PROMPT_VERSION")

    enable_tracing: bool = Field(default=True, validation_alias="MEDLABS_ENABLE_TRACING")
    log_level: str = Field(default="INFO", validation_alias="MEDLABS_LOG_LEVEL")

    schema_dir: str | None = Field(default=None, validation_alias="MEDLABS_SCHEMA_DIR")
    sample_pdf: str | None = Field(default=None, validation_alias="MEDLABS_SAMPLE_PDF")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: EnvSettingsSource,
        dotenv_settings: DotEnvSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        del cls, settings_cls
        return (
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )

    def schema_dir_path(self) -> Path | None:
        if not self.schema_dir:
            return None
        return Path(self.schema_dir)

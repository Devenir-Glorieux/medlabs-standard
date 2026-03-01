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


def discover_dotenv_files(
    start_dir: str | Path | None = None,
    *,
    file_names: tuple[str, ...] = (".env", ".env.local"),
) -> tuple[Path, ...]:
    """Find dotenv files from filesystem root down to current directory.

    Files that are closer to the working directory are loaded later and therefore
    override values from upper-level directories.
    """

    base_dir = Path(start_dir).expanduser().resolve() if start_dir else Path.cwd().resolve()
    discovered: list[Path] = []
    for directory in reversed((base_dir, *base_dir.parents)):
        for file_name in file_names:
            candidate = directory / file_name
            if candidate.is_file():
                discovered.append(candidate)
    return tuple(discovered)


class MedLabsSettings(BaseSettings):
    """App-layer configuration loaded from dotenv hierarchy and environment variables.

    Source order is explicitly configured as:
    1) init kwargs
    2) `.env`/`.env.local` discovered in directory hierarchy
    3) process environment
    4) file secrets

    This keeps dotenv values higher priority than system environment variables.
    """

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")

    langfuse_public_key: str | None = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str | None = Field(default=None, alias="LANGFUSE_HOST")

    prompt_name: str = Field(default="medlabs.extract", alias="MEDLABS_PROMPT_NAME")
    prompt_version: str = Field(default="production", alias="MEDLABS_PROMPT_VERSION")
    enable_langfuse_prompts: bool = Field(default=True, alias="MEDLABS_ENABLE_LANGFUSE_PROMPTS")
    prompt_fallback: str = Field(
        default="Извлеки согласно схемы и верни только JSON.",
        alias="MEDLABS_PROMPT_FALLBACK",
    )
    fail_on_prompt_error: bool = Field(default=False, alias="MEDLABS_FAIL_ON_PROMPT_ERROR")

    enable_tracing: bool = Field(default=True, alias="MEDLABS_ENABLE_TRACING")
    log_level: str = Field(default="INFO", alias="MEDLABS_LOG_LEVEL")

    schema_dir: str | None = Field(default=None, alias="MEDLABS_SCHEMA_DIR")
    sample_pdf: str | None = Field(default=None, alias="MEDLABS_SAMPLE_PDF")

    model_config = SettingsConfigDict(
        env_file=None,
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
        del cls, dotenv_settings
        dotenv_hierarchy = DotEnvSettingsSource(
            settings_cls,
            env_file=discover_dotenv_files(),
            env_file_encoding="utf-8",
        )
        return (
            init_settings,
            dotenv_hierarchy,
            env_settings,
            file_secret_settings,
        )

    def schema_dir_path(self) -> Path | None:
        if not self.schema_dir:
            return None
        return Path(self.schema_dir)

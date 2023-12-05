import os
from types import SimpleNamespace
from typing import Optional

import toml

# Variables globales para el proyecto.
PROJECT_DIR = os.environ.get(
    "PROJECT_DIR", os.path.abspath(os.path.dirname(os.getcwd()))
)
ENVIRONMENT = os.environ.get("ENVIRONMENT")
SETTINGS = os.environ.get("SETTINGS")

# Ubicaciones por defecto del archivo settings.toml.
fallback_locations = [
    os.path.join(PROJECT_DIR, "settings.toml"),
    os.path.join(PROJECT_DIR, "etc", "settings.toml"),
    os.path.join(PROJECT_DIR, "api", "settings.toml"),
    "settings.toml",
    "etc/settings.toml",
    "api/settings.toml",
]


def load_toml_file(path: str = None):
    if path is not None:
        return toml.load(path)
    for fallback in fallback_locations:
        try:
            return toml.load(fallback)
        except FileNotFoundError:
            pass
        except toml.decoder.TomlDecodeError as error:
            print(f"[LOG][ERROR]: Using settings file {fallback}")
            print(
                f"[LOG][ERROR]: Line number {error.lineno}, Column number {error.colno}"
            )
            raise error
    raise FileNotFoundError("settings.toml file not found.")


def get_settings(
    settings: Optional[str] = None,
    environment: Optional[str] = None,
    **kwargs,
) -> SimpleNamespace:
    """
    Esta función carga los valores establecidos por el usuario relacionados a la
    "infraestructura" de los servidores (urls, puertos, usuarios, contraseñas, etc.).
    """
    toml_file = load_toml_file(path=settings or SETTINGS)
    environment = environment or ENVIRONMENT or [*toml_file.keys()][0]
    return SimpleNamespace(
        PROJECT_DIR=PROJECT_DIR,
        ENVIRONMENT=environment,
        **{
            key: kwargs.get(key, value)
            for key, value in dict(toml_file[environment]).items()
        },
    )


# Se definen los settings que usa el proyecto. Cualquier variable que haya sido
# seteada como envrionment variable sobreescribe a la definidas en los settings.
settings = get_settings(**dict(os.environ))

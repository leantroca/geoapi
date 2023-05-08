import os
from types import SimpleNamespace

import toml

# Variables globales para el proyecto.
PROJECT_DIR = os.environ.get("PROJECT_DIR", os.path.abspath(os.getcwd()))
ENVIRONMENT = os.environ.get("ENVIRONMENT")


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
    if path:
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


# def load_json_file(path: str = None) -> dict:
#     return {
#         "DEFAULT_CHUNKSIZE": 50,
#     }


def get_settings(
    path: str = os.path.join(PROJECT_DIR, "api", "settings.toml"),
    environment: str = ENVIRONMENT,
    **kwargs,
) -> SimpleNamespace:
    """
    Esta función carga los valores establecidos por el usuario relacionados a la
    "infraestructura" de los servidores (urls, puertos, usuarios, contraseñas, etc.).
    """
    toml_file = load_toml_file()
    environment = environment or [*toml_file.keys()][0]
    return SimpleNamespace(
        PROJECT_DIR=PROJECT_DIR,
        ENVIRONMENT=environment,
        **dict(toml_file[environment], **kwargs),
    )


# Se definen los settings que usa el proyecto.
settings = get_settings(
    # **load_json_file(),
)

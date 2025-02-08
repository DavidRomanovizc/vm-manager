import dataclasses
import os


def load_env_from_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()


@dataclasses.dataclass(slots=True, frozen=True)
class AppCfg:
    host: str
    port: int

    @staticmethod
    def from_env() -> "AppCfg":
        host = os.getenv("APP_HOST")
        port = int(os.getenv("APP_PORT"))

        return AppCfg(
            host=host,
            port=port,
        )


@dataclasses.dataclass(slots=True, frozen=True)
class Config:
    app: AppCfg


def config_provider() -> "Config":
    load_env_from_file('.env')
    return Config(
        app=AppCfg.from_env()
    )

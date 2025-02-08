import dataclasses

from environs import Env


@dataclasses.dataclass(slots=True, frozen=True)
class DatabaseCfg:
    user: str
    password: str
    host: str
    port: int
    database: str

    @staticmethod
    def from_env(env: "Env") -> "DatabaseCfg":
        user = env.str("POSTGRES_USER")
        password = env.str("POSTGRES_PASSWORD")
        host = env.str("POSTGRES_HOST")
        port = env.int("POSTGRES_PORT")
        database = env.str("POSTGRES_DB")

        return DatabaseCfg(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )


@dataclasses.dataclass(slots=True, frozen=True)
class AppCfg:
    host: str
    port: int

    @staticmethod
    def from_env(env: "Env") -> "AppCfg":
        host = env.str("APP_HOST")
        port = env.int("APP_PORT")

        return AppCfg(
            host=host,
            port=port,
        )


@dataclasses.dataclass(slots=True, frozen=True)
class Config:
    db: DatabaseCfg
    app: AppCfg


def config_provider() -> "Config":
    env = Env()
    env.read_env()

    return Config(
        db=DatabaseCfg.from_env(env=env),
        app=AppCfg.from_env(env=env)
    )

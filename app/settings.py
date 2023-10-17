from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.envdev',
                                      env_file_encoding='utf-8',
                                      extra='ignore')
    token: str
    postgres_password: str
    postgres_user: str
    postgres_db: str
    host: str
    port_db: int
    owner_id: int
    redis_host: str
    redis_port: int
    redis_db: int
    url: str
    cache_exp: int
    days: int


settings = Settings()
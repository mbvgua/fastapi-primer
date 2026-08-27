import secrets
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    this provides a better replacement for the classic "dotenv()" package.
    actual values are supplied from the ".env" file, using a 1:1
    case-insensitive matching. If no values are supplied, then the default
    values in the "Settings()" class will be used

    - "model_config" tells it to load our ".env" file that contains all our
      vital secrets, Api keys and such
    - "secret_key" is given a special type "SecretStr" from pydantic, that
      helps prevent possible key exposure. accidentally printing it displays a
      bunch of asterisks(10 to be precise, regardless of value); to see it,
      you have call it explicitly with the ".get_secret_value()" method
    - "algorithm" defines the hashing algirithm to be used
    - "access_token_expires_in_minutes" defines how long before token generated
      expires and needs to be refreshed
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str

    secret_key: SecretStr = SecretStr(secrets.token_hex(32))
    algorithm: str = "HS256"
    access_token_expiration_minutes: int = 30

    # define max image upload size(5mb)
    max_upload_size_bytes: int = 5 * 1024 * 1024

    # pagination
    posts_per_page: int = 10

    # password reset emails need to expire quickly
    reset_expiration_minutes: int = 30

    mail_server: str
    mail_port: int
    mail_username: str
    mail_password: SecretStr = SecretStr("")
    mail_from: str
    mail_use_tls: bool

    # where reset pass page will be located in frontend
    frontend_url: str


settings = Settings()

from enum import Enum

from pydantic import BaseSettings


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod

    class Config:
        env_file = "prod.env"


class UserpoolSettings(BaseSettings):
    region: str
    userpool_id: str
    app_client_id: str

    def get_jwk_key_url(self):
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.userpool_id}/.well-known/jwks.json"

    def get_iss(self):
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.userpool_id}"

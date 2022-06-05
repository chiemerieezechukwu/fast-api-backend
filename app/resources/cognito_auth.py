import time
from typing import Type

from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from jose.backends.base import Key
from jose.utils import base64url_decode
from loguru import logger
from starlette import status
from starlette.requests import Request

from app.core.settings.app import AppSettings
from app.resources import strings
from app.schemas.cognito_auth import JWK, JWKS, CognitoAuth, CognitoClaims


class CognitoBearer(HTTPBearer):
    def __init__(self, *, jwks: JWKS, settings: AppSettings) -> None:
        super().__init__()

        self.kid_jwk_map = {jwk.kid: jwk for jwk in jwks.keys}
        self.userpool_settings = settings.userpool

    async def __call__(self, request: Request) -> CognitoClaims:
        try:
            auth: HTTPAuthorizationCredentials = await super().__call__(request)
        except HTTPException as original_auth_exc:
            raise HTTPException(
                status_code=original_auth_exc.status_code,
                detail=original_auth_exc.detail,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth.credentials

        try:
            header = jwt.get_unverified_header(token)
            claims = jwt.get_unverified_claims(token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=strings.INVALID_TOKEN,
                headers={"WWW-Authenticate": "Bearer"},
            )

        message, signature = str(token).rsplit(".", 1)
        cognito_auth = CognitoAuth(
            token=token,
            headers=header,
            claims=claims,
            message=message,
            signature=signature,
        )

        if not self._verify_token(cognito_auth):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=strings.INVALID_TOKEN,
                headers={"WWW-Authenticate": "Bearer"},
            )

        return cognito_auth.claims

    def _get_jwk_key(self, kid: str) -> JWK:
        try:
            jwk_key = self.kid_jwk_map[kid]
        except KeyError:
            logger.error(f"JWK key with kid {kid} not found")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=strings.INVALID_TOKEN,
                headers={"WWW-Authenticate": "Bearer"},
            )

        return jwk_key

    def _verify_token(self, cognito_auth: CognitoAuth) -> bool:
        jwk_key = self._get_jwk_key(cognito_auth.headers.kid)
        public_key: Type[Key] = jwk.construct(jwk_key.dict())

        decoded_signature = base64url_decode(cognito_auth.signature.encode("utf-8"))

        if not public_key.verify(cognito_auth.message.encode("utf-8"), decoded_signature):
            logger.debug("Signature verification failed")
            return False

        if time.time() > cognito_auth.claims.exp:
            logger.debug("Token is expired")
            return False

        if cognito_auth.claims.aud != self.userpool_settings.app_client_id:
            logger.debug("Token is not for this app")
            return False

        if cognito_auth.claims.iss != self.userpool_settings.get_iss():
            logger.debug("Token is not for this userpool")
            return False

        return True

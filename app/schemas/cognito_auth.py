from pydantic import BaseModel, Field, HttpUrl


class JWK(BaseModel):
    alg: str
    e: str
    kid: str
    kty: str
    n: str
    use: str


class JWKS(BaseModel):
    keys: list[JWK]


class CognitoClaims(BaseModel):
    email: str
    email_verified: bool
    username: str = Field(alias="cognito:username")
    sub: str
    aud: str
    auth_time: int
    exp: int
    iat: int
    iss: HttpUrl


class CognitoHeaders(BaseModel):
    kid: str
    alg: str


class CognitoAuth(BaseModel):
    token: str
    headers: CognitoHeaders
    claims: CognitoClaims
    message: str
    signature: str

from typing import (
    List,
    Type,
)

from jose import (
    jwt,
    ExpiredSignatureError,
    JWTError,
)
from jose.exceptions import JWTClaimsError
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    OpenIdConnect as _OpenIdConnect,
    SecurityScopes,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from .models import JwtPayload
from .broker import OpenIdConnectBroker
from .utils import dict_rgetattr


class OpenIdConnect(_OpenIdConnect):
    def __init__(
        self,
        *,
        open_id_connect_url: str,
        client_id: str,
        issuer: str | None = None,
        audience: str | None = None,
        scopes: List[str] = [],
        scope_key: str = "scope",
        cache_ttl: int = 1,
        jwt_payload_model: Type[JwtPayload] = JwtPayload,
        auto_error: bool = True,
    ):
        self.open_id_connect_url = open_id_connect_url
        self.client_id = client_id
        self.issuer = issuer
        self.audience = audience or self.client_id
        self.scopes = scopes
        self.scope_key = scope_key
        self.broker = OpenIdConnectBroker(
            self.open_id_connect_url,
            cache_ttl,
        )
        self.jwt_payload_model = jwt_payload_model

        super().__init__(
            openIdConnectUrl=self.open_id_connect_url, auto_error=auto_error
        )

    def protection(
        self,
        security_scopes: SecurityScopes,
        authorization_credentials: HTTPAuthorizationCredentials
        | None = Depends(HTTPBearer()),
    ):
        return self.get_current_user(security_scopes, authorization_credentials)

    def get_current_user(
        self,
        security_scopes: SecurityScopes,
        authorization_credentials: HTTPAuthorizationCredentials
        | None = Depends(HTTPBearer()),
    ) -> JwtPayload:
        public_key = self.broker.get_public_key()
        algorithms = self.broker.get_signing_algorithms()

        try:
            payload = jwt.decode(
                authorization_credentials.credentials,
                public_key,
                algorithms,
                audience=self.audience,
                issuer=self.issuer,
            )

        except (ExpiredSignatureError, JWTError, JWTClaimsError) as err:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {err}")

        expected_scopes = [*self.scopes, *security_scopes.scopes]
        try:
            user_scopes = dict_rgetattr(payload, self.scope_key)
        except KeyError as err:
            raise Exception(
                f"JwtPayload does not include `{self.scope_key}` property: {err}"
            )

        ok = False
        for expected_scope in expected_scopes:
            if expected_scope in user_scopes:
                ok = True
                break

        if not ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Not enough permissions: expected_scopes={expected_scopes}, user_scopes={user_scopes}",
            )

        return self.jwt_payload_model(**payload)

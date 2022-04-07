from pydantic import BaseModel
from pydantic import Extra


class JwtPayload(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int

    class Config:
        extra = Extra.allow

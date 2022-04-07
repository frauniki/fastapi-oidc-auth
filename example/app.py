import uvicorn
from fastapi import (
    FastAPI,
    Security,
)

from fastapi_oidc_auth import OpenIdConnect


app = FastAPI()


oidc = OpenIdConnect(
    **{
        "open_id_connect_url": "https://<your-keycloak>/auth/realms/master",
        "client_id": "CLIENT_ID",
        "cache_ttl": 86400,
    }
)


@app.get("/protected")
async def get_catalog_task_templates(
    current_user=Security(oidc.protection),
):
    return {"messages": "Hello World!"}


@app.get("/protected/admin")
async def get_catalog_task_templates(
    current_user=Security(oidc.protection, scopes=["admin"])
):
    return {"messages": "Hello Admin!"}


if __name__ == "__main__":
    uvicorn.run(app)

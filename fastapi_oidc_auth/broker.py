from urllib.parse import urljoin
from typing import (
    Dict,
    List,
)

import requests
from cachetools import (
    cached,
    TTLCache,
)


def OpenIdConnectBroker(open_id_connect_url: str, cache_ttl: int = 1):
    class _OpenIdConnectBroker:
        def __init__(self, open_id_connect_url: str):
            self.open_id_connect_url = open_id_connect_url

        @cached(TTLCache(1, cache_ttl))
        def get_openid_config(self) -> Dict:
            base_url = self.open_id_connect_url
            if base_url[-1] != "/":
                base_url += "/"
            configuration_url = urljoin(base_url, ".well-known/openid-configuration")

            resp = requests.get(configuration_url)
            resp.raise_for_status()

            return resp.json()

        @cached(TTLCache(1, cache_ttl))
        def get_public_key(self) -> Dict:
            config = self.get_openid_config()

            resp = requests.get(config["jwks_uri"])
            resp.raise_for_status()

            return resp.json()

        def get_signing_algorithms(self) -> List[str]:
            config = self.get_openid_config()

            return config["id_token_signing_alg_values_supported"]

    return _OpenIdConnectBroker(open_id_connect_url)

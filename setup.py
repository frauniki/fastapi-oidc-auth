from setuptools import (
    setup,
    find_packages,
)


VERSION = "0.0.1"


setup(
    name="fastapi-oidc-auth",
    packages=find_packages(),
    version=VERSION,
    install_requires=[
        "cachetools",
        "fastapi",
        "pydantic",
        "python-jose",
        "requests",
    ],
    url="https://git.linecorp.com/frauniki/fastapi-oidc-auth",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable

from fastapi import FastAPI
from starlette.routing import Mount

from tests.mocks.s3 import MockS3Manager


@dataclass(frozen=True, kw_only=True, slots=True)
class _DepOverride:
    dependency: Callable
    override: Callable


def override_app_test_dependencies(app: FastAPI):
    from app.storage.s3 import get_s3

    deps: list[_DepOverride] = [
        _DepOverride(dependency=get_s3, override=get_mock_s3),
    ]
    for dep in deps:
        override_dependency(app, dep.dependency, dep.override)


def override_dependency(app: FastAPI, dependency: Callable, override: Callable) -> None:
    app.dependency_overrides[dependency] = override

    for route in app.router.routes:
        if isinstance(route, Mount):
            route.app.dependency_overrides[dependency] = override


@lru_cache
def get_mock_s3():
    from app.core.config import get_settings

    return MockS3Manager(get_settings().AWS_S3_CARS_BUCKET_NAME)

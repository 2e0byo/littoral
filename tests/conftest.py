from typing import Callable

from pydantic import BaseModel
from pytest_cases import fixture


def _compare_models(a: BaseModel, b: BaseModel):
    """Compare models as dicts for better diffs."""
    assert a.model_dump() == b.model_dump()


CompareModels = Callable[[BaseModel, BaseModel], None]

compare_models = fixture(lambda: _compare_models)

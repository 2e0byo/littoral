from datetime import datetime, timezone
from typing import Callable

from pydantic import BaseModel, TypeAdapter
from pytest_cases import fixture


def _compare_models(a: BaseModel, b: BaseModel) -> None:
    """Compare models as dicts for better diffs."""
    assert a.model_dump() == b.model_dump()


CompareModels = Callable[[BaseModel, BaseModel], None]

compare_models = fixture(lambda: _compare_models)


def _check_models_list(type_adapter: TypeAdapter, expected: str) -> None:
    """Check the parser for a list of models has the expected type."""
    assert type_adapter.validator.title == expected


check_models_list = fixture(lambda: _check_models_list)

CheckModelsList = Callable[[TypeAdapter, str], None]


@fixture
def freeze_time(mocker) -> datetime:
    now = datetime.now(timezone.utc)
    mocker.patch("littoral.auth.models.datetime", **{"now.return_value": now})
    return now

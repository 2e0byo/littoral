from typing import Generic, TypeVar

from pydantic import BaseModel

_T = TypeVar("_T", bound=BaseModel)


class TestCase(BaseModel, Generic[_T]):
    raw: bytes
    parsed: _T

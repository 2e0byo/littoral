from enum import Enum
from typing import Annotated, Any, Callable, Self

from pydantic import BaseModel, Field, NonNegativeInt, PrivateAttr

Parser = Callable[[dict], Any]


class Role(Enum):
    Artist = "Artist"
    Songwriter = "Songwriter"
    Producer = "Producer"
    Engineer = "Engineer"

    @classmethod
    def from_json(cls, json: dict) -> Self:
        return cls[json["category"]]


class TidalResource(BaseModel):
    id: NonNegativeInt
    name: str

    @classmethod
    def from_json(cls, json: dict) -> Self:
        for k, parser in cls._json_map().items():
            json[k] = parser(json)

        return cls.model_validate(json)

    @classmethod
    def _json_map(cls) -> dict[str, Parser]:
        return {}


class Artist(TidalResource):
    roles: list[Role]
    picture_uuid: str
    popularity: int

    @classmethod
    def _json_map(cls) -> dict[str, Parser]:
        return {
            "picture_uuid": lambda json: json["picture"],
            "roles": lambda json: [Role.from_json(r) for r in json["artistRoles"]],
        }

    @classmethod
    def from_json(cls, json: dict) -> Self:
        map = {
            "picture_uuid": lambda json: json["picture"],
            "roles": lambda json: [Role.from_json(r) for r in json["artistRoles"]],
        }
        for k, parser in map.items():
            json[k] = parser(json)

        return cls.model_validate(json)

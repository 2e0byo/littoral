from enum import Enum
from typing import Annotated, Self

from pydantic import BaseModel, Field, NonNegativeInt, PrivateAttr


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


class Artist(TidalResource):
    roles: list[Role]
    picture_uuid: str
    popularity: int

    @classmethod
    def from_json(cls, json: dict) -> Self:
        map = {
            "picture_uuid": lambda json: json["picture"],
            "roles": lambda json: [Role.from_json(r) for r in json["artistRoles"]],
        }
        for k, parser in map.items():
            json[k] = parser(json)

        return cls.model_validate(json)

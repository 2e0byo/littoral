from datetime import date, timedelta
from enum import Enum
from typing import Annotated, Any, Callable, Self

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PrivateAttr

Parser = Callable[[dict], Any]


def from_camel(camel: str) -> str:
    words = []
    word_start = 0
    for i, c in enumerate(camel):
        if c.isupper():
            words.append(camel[word_start:i].lower())
            word_start = i

    words.append(camel[word_start : i + 1].lower())
    return "_".join(words)


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

    @classmethod
    def from_json(cls, json: dict) -> Self:
        json = {from_camel(k): v for k, v in json.items()}
        for k, parser in cls._parser_map().items():
            json[k] = parser(json)

        for field, alias in cls._field_map().items():
            json[field] = json[alias]

        return cls.model_validate(json)

    @classmethod
    def _parser_map(cls) -> dict[str, Parser]:
        return {}

    @classmethod
    def _field_map(cls) -> dict[str, str]:
        return {}


class Artist(TidalResource):
    name: str
    roles: list[Role] | None = None
    picture_uuid: str
    popularity: int | None = None

    @classmethod
    def _parser_map(cls) -> dict[str, Parser]:
        return {
            "roles": lambda json: [Role.from_json(r) for r in json["artist_roles"]]
            if "artist_roles" in json
            else None,
        }

    @classmethod
    def _field_map(cls) -> dict[str, str]:
        return {"picture_uuid": "picture"}


class Quality(Enum):
    HiRes = "HiRes"

    @classmethod
    def from_json(cls, json: str) -> Self:
        return {"HI_RES": cls.HiRes}[json]


class Album(TidalResource):
    title: str
    duration: timedelta
    n_tracks: int
    n_videos: int
    n_volumes: int
    release_date: date
    cover_uuid: str
    popularity: int
    audio_quality: Quality
    artist: Artist

    @classmethod
    def _field_map(cls) -> dict[str, str]:
        return {
            "cover_uuid": "cover",
            "n_tracks": "number_of_tracks",
            "n_videos": "number_of_videos",
            "n_volumes": "number_of_volumes",
        }

    @classmethod
    def _parser_map(cls) -> dict[str, Parser]:
        return {
            "artist": lambda json: Artist.from_json(json["artist"]),
            "audio_quality": lambda json: Quality.from_json(json["audio_quality"]),
        }
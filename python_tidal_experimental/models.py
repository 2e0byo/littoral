from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Callable, NamedTuple, NewType, Self

from pydantic import BaseModel, NonNegativeInt

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


URL = NewType("URL", str)


class Dimensions(NamedTuple):
    x: int
    y: int


class ImageSize(Enum):
    Thumbnail = Dimensions(80, 80)
    Tiny = Dimensions(160, 160)
    Small = Dimensions(320, 320)
    Medium = Dimensions(640, 640)
    Large = Dimensions(1280, 1280)


class Album(TidalResource):
    title: str
    duration: timedelta
    n_tracks: int
    n_videos: int
    n_volumes: int
    release_date: date
    tidal_release_date: datetime
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
            "tidal_release_date": "stream_start_date",
        }

    @classmethod
    def _parser_map(cls) -> dict[str, Parser]:
        return {
            "artist": lambda json: Artist.from_json(json["artist"]),
            "audio_quality": lambda json: Quality.from_json(json["audio_quality"]),
        }

    def image_url(self, size: ImageSize = ImageSize.Small) -> URL:
        x, y = size.value
        return URL(
            f"https://resources.tidal.com/images/{self.cover_uuid.replace('-','/')}/{x}x{y}.jpg"
        )

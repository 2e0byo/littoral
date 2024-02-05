from datetime import date, datetime, timedelta
from enum import Enum
from typing import Annotated, Any, Callable, NamedTuple, NewType, Self

from pydantic import (
    AliasPath,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    NonNegativeInt,
)
from pydantic.alias_generators import to_camel
from pydantic_core import CoreSchema, core_schema

Parser = Callable[[dict], Any]


class Role(Enum):
    Artist = "Artist"
    Songwriter = "Songwriter"
    Producer = "Producer"
    Engineer = "Engineer"


def _parse_role(x: Any) -> Role:
    if isinstance(x, dict):
        return Role[x["category"]]
    else:
        return x


ParsableRole = Annotated[Role, BeforeValidator(_parse_role)]


class TidalResource(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)
    id: NonNegativeInt


class Artist(TidalResource):
    name: str
    roles: list[ParsableRole] | None = Field(
        None, validation_alias=AliasPath("artistRoles")
    )
    picture_uuid: str = Field(alias="picture")
    popularity: int | None = None


class Quality(Enum):
    HiRes = "HI_RES"


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
    n_tracks: int = Field(alias="numberOfTracks")
    n_videos: int = Field(alias="numberOfVideos")
    n_volumes: int = Field(alias="numberOfVolumes")
    release_date: date
    tidal_release_date: datetime = Field(alias="streamStartDate")
    cover_uuid: str = Field(alias="cover")
    popularity: int
    audio_quality: Quality
    artist: Artist

    def image_url(self, size: ImageSize = ImageSize.Small) -> URL:
        x, y = size.value
        return URL(
            f"https://resources.tidal.com/images/{self.cover_uuid.replace('-','/')}/{x}x{y}.jpg"
        )

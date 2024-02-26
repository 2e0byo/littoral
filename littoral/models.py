from datetime import date, datetime, timedelta
from enum import Enum
from typing import Annotated, Any, NamedTuple, Sequence

from pydantic import AliasPath, BeforeValidator, Field, NonNegativeInt, TypeAdapter

from littoral.base import CamelModel
from littoral.config import Urls
from littoral.request import URL, Request, RequestBuilder


class TidalResource(CamelModel):
    id: NonNegativeInt
    urls: Urls = Field(default_factory=Urls.default)


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


_ParsableRole = Annotated[Role, BeforeValidator(_parse_role)]


class Artist(TidalResource):
    name: str
    roles: list[_ParsableRole] | None = Field(
        None, validation_alias=AliasPath("artistRoles")
    )
    picture_uuid: str | None = Field(alias="picture")
    popularity: int | None = None


class Quality(Enum):
    HiRes = "HI_RES"
    Lossless = "LOSSLESS"


class Dimensions(NamedTuple):
    x: int
    y: int


class ImageSize(Enum):
    Thumbnail = Dimensions(80, 80)
    Tiny = Dimensions(160, 160)
    Small = Dimensions(320, 320)
    Medium = Dimensions(640, 640)
    Large = Dimensions(1280, 1280)


class Track(TidalResource):
    ...


class Video(TidalResource):
    ...


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
    copyright: str
    explicit: bool
    version: str | None = None
    available: bool = Field(alias="streamReady")
    video_cover_uuid: str | None = Field(None, alias="VideoCover")
    universal_product_number: int | None = Field(None, alias="upc")

    def image_url(self, size: ImageSize = ImageSize.Small) -> URL:
        x, y = size.value
        return URL(f"{self.urls.image}/{self.cover_uuid.replace('-','/')}/{x}x{y}.jpg")

    def image(self, size: ImageSize = ImageSize.Small) -> RequestBuilder:
        x, y = size.value
        url = f"{self.urls.image}/{self.cover_uuid.replace('-','/')}/{x}x{y}.jpg"
        return RequestBuilder(
            Album,
            Request(method="GET", url=url),
        )

    def tracks(self, limit: int | None = None, offset: int = 0) -> RequestBuilder:
        return RequestBuilder(
            TypeAdapter(list[Track]),
            Request(
                method="GET",
                url=f"{self.urls.api_v1}/albums/{self.id}/tracks",  # type: ignore
                params=(
                    {
                        "limit": limit,
                        "offset": offset,
                    }
                ),
            ),
        )

    def items(self, limit: int | None = None, offset: int = 0) -> RequestBuilder:
        return RequestBuilder(
            TypeAdapter(Sequence[Track | Video]),
            Request(
                method="GET",
                url=f"{self.urls.api_v1}/albums/{self.id}/items",  # type: ignore
                params=(
                    {
                        "limit": limit,
                        "offset": offset,
                    }
                ),
            ),
        )


class User(CamelModel):
    user_id: int
    email: str
    # Tidal has other fields, but I doubt we want them.

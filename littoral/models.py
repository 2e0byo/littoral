from datetime import date, datetime, timedelta
from enum import Enum
from typing import Annotated, Any, NamedTuple, Self

from pydantic import (
    AliasPath,
    AnyHttpUrl,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    NonNegativeInt,
)
from pydantic.alias_generators import to_camel
from pydantic_extra_types.country import CountryAlpha2

from littoral.request import URL, Request

MODEL_CONFIG = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class Urls(BaseModel):
    api_v1: AnyHttpUrl
    api_v2: AnyHttpUrl
    oauth2: AnyHttpUrl
    image: AnyHttpUrl
    video: AnyHttpUrl

    @classmethod
    def default(cls) -> Self:
        return cls(
            api_v1="https://api.tidal.com/v1",  # type: ignore
            api_v2="https://api.tidal.com/v2",  # type: ignore
            oauth2="https://auth.tidal.com/v1/oauth2/token",  # type: ignore
            image="https://resources.tidal.com/images",  # type: ignore
            video="https://resources.tidal.com/videos",  # type: ignore
        )


class TidalResource(BaseModel):
    model_config = MODEL_CONFIG
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
    picture_uuid: str = Field(alias="picture")
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

    def with_session(self, session: "Session") -> "AlbumWithSession":
        return AlbumWithSession.model_validate(self.model_dump() | {"session": session})


class Session(BaseModel):
    country: CountryAlpha2
    id: int
    access_token: str
    refresh_token: str

    def params(self) -> dict[str, str]:
        return {"countryCode": self.country, "sessionId": str(self.id)}

    def headers(self) -> dict[str, str]:
        return {"authorization": self.access_token}


class AlbumWithSession(Album):
    session: Session

    def tracks_request(self, limit: int | None = None, offset: int = 0) -> Request:
        return Request(
            method="GET",
            url=f"{self.urls.api_v1}/albums/{self.id}/tracks",  # type: ignore
            params=(
                {
                    "limit": limit,
                    "offset": offset,
                }
                | self.session.params()
            ),
            headers=self.session.headers(),
        )

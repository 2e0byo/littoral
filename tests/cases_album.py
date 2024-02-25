from datetime import date, datetime, timedelta, timezone

from littoral.models import Album, Artist, Quality
from tests.models import TestCase

AlbumCase = TestCase[Album]


def case_all_data() -> AlbumCase:
    return AlbumCase(
        raw="""
    {
      "id": 17927863,
      "title": "Some Things (Deluxe)",
      "duration": 6712,
      "streamReady": true,
      "adSupportedStreamReady": true,
      "djReady": true,
      "stemReady": false,
      "streamStartDate": "2012-10-01T00:00:00.000+0000",
      "allowStreaming": true,
      "premiumStreamingOnly": false,
      "numberOfTracks": 22,
      "numberOfVideos": 0,
      "numberOfVolumes": 2,
      "releaseDate": "2011-09-22",
      "copyright": "Sinuz Recordings (a division of HITT bv)",
      "type": "ALBUM",
      "version": "Deluxe",
      "url": "http://www.tidal.com/album/17927863",
      "cover": "30d83a8c-1db6-439d-84b4-dbfb6f03c44c",
      "vibrantColor": "#FFFFFF",
      "videoCover": null,
      "explicit": false,
      "upc": "3610151683488",
      "popularity": 44,
      "audioQuality": "LOSSLESS",
      "audioModes": [
        "STEREO"
      ],
      "mediaMetadata": {
        "tags": [
          "LOSSLESS"
        ]
      },
      "artist": {
        "id": 16147,
        "name": "Lasgo",
        "type": "MAIN",
        "picture": "42b39a18-be34-4729-8dbc-acabc0e2f377"
      },
      "artists": [
        {
          "id": 16147,
          "name": "Lasgo",
          "type": "MAIN",
        "picture": "42b39a18-be34-4729-8dbc-acabc0e2f377"
        }
      ]
    }
    """.encode(),
        parsed=Album(
            id=17927863,
            title="Some Things (Deluxe)",
            duration=timedelta(seconds=6712),
            n_tracks=22,
            n_videos=0,
            n_volumes=2,
            release_date=date(2011, 9, 22),
            tidal_release_date=datetime(2012, 10, 1, 0, 0, tzinfo=timezone.utc),
            cover_uuid="30d83a8c-1db6-439d-84b4-dbfb6f03c44c",
            popularity=44,
            audio_quality=Quality.Lossless,
            artist=Artist(
                id=16147,
                name="Lasgo",
                roles=None,
                picture_uuid="42b39a18-be34-4729-8dbc-acabc0e2f377",
                popularity=None,
            ),
            copyright="Sinuz Recordings (a division of HITT bv)",
            explicit=False,
            version="Deluxe",
            available=True,
            video_cover_uuid=None,
            universal_product_number=3610151683488,
        ),
    )


def case_picture_null() -> AlbumCase:
    return AlbumCase(
        raw="""{
    "adSupportedStreamReady": true,
    "allowStreaming": true,
    "artist": {
        "id": 2935,
        "name": "Various Artists",
        "picture": null,
        "type": "MAIN"
    },
    "artists": [
        {
            "id": 2935,
            "name": "Various Artists",
            "picture": null,
            "type": "MAIN"
        }
    ],
    "audioModes": [
        "STEREO"
    ],
    "audioQuality": "LOSSLESS",
    "copyright": "© 2016 Mercury Music Group",
    "cover": "8f0b90a8-5eae-404f-b20b-005a51b5d012",
    "djReady": true,
    "duration": 3878,
    "explicit": false,
    "id": 57642369,
    "mediaMetadata": {
        "tags": [
            "LOSSLESS"
        ]
    },
    "numberOfTracks": 24,
    "numberOfVideos": 0,
    "numberOfVolumes": 1,
    "popularity": 18,
    "premiumStreamingOnly": false,
    "releaseDate": "2016-02-26",
    "stemReady": false,
    "streamReady": true,
    "streamStartDate": "2016-02-26T00:00:00.000+0000",
    "title": "Gainsbourg London Paris 1963 - 1971",
    "type": "ALBUM",
    "upc": "00600753673829",
    "url": "http://www.tidal.com/album/57642369",
    "version": null,
    "vibrantColor": "#ac590b",
    "videoCover": null
}
""".encode(),
        parsed={
            "id": 57642369,
            "title": "Gainsbourg London Paris 1963 - 1971",
            "duration": "PT3878S",
            "n_tracks": 24,
            "n_videos": 0,
            "n_volumes": 1,
            "release_date": "2016-02-26",
            "tidal_release_date": "2016-02-26T00:00:00Z",
            "cover_uuid": "8f0b90a8-5eae-404f-b20b-005a51b5d012",
            "popularity": 18,
            "audio_quality": "LOSSLESS",
            "artist": {
                "id": 2935,
                "name": "Various Artists",
                "roles": None,
                "picture_uuid": None,
                "popularity": None,
            },
            "copyright": "© 2016 Mercury Music Group",
            "explicit": False,
            "version": None,
            "available": True,
            "video_cover_uuid": None,
            "universal_product_number": 600753673829,
        },
    )

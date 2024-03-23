# Littoral: an experimental zero-IO tidal library for python

- **Fully tested**: Littoral has 100% line and branch coverage, and it's staying there
- **Type safe**: passes `mypy --strict``
- **Swappable backends**: use as much of the open api as possible

## Quick start

## Zero-IO explanation

## Using in projects

firstly, doing everything explicitly:

```python
request_builder = Track.lookup("asdf-adsf-adsf-adsf")
session = ApiSession( # we'll come back to this
    country="GB", access_token="12345", id="123", refresh_token="456"
)
session = ApiSession(country="GB", access_token="12345", id="123", refresh_token="456") # we'll come back to this
httpx_request = request_builder.build(session).to_httpx()

with httpx.Client() as client:
    response = client.send(httpx_request)


track = request_builder.parse(Response.from_httpx(response))
```

This is a bit of a mouthful, but it's worth looking at to see the explicit data
flow.  A track *class* knows how to generate a request to lookup a particular
track.  Actually to send this request we need to authenticate it, so the request
builder takes a token and builds a request.  This a `littoral.request.Request`
object: our own minimal representation of an http request.  To send this request
we need to turn it into something an http library understands: here we use
httpx.  The response is turned into a minimal response object, and then the
builder knows which model should be built with the data it returned.  We've made
a full lookup without having to do any IO in `littoral`.

There are lots of ways of getting `RequestBuilder`s, and they all work the same
way.  On a resource:

```python
Track.lookup(id: int)
Track.search(query: str)
# We'll cover constructing resources in a moment
Track().album()
Track().artist()
Track().video()
Playlist().tracks()
... # etc
```

On a `User`:

```python
User().favourite_tracks()
User().favourite_albums()
User().favourite_artists()
User().playlists()
```

and a single top-level function:

```python
search()
```

These all return exactly the same class: a `RequestBuilder` which knows how to
(i) generate a request and (ii) parse the response into the correct model.  This
is quite neat: all network access looks exactly the same and you can use any
http library you want (or roll your own).  On the other hand the code above was
quite verbose.  Let's make it simpler.

### Doing IO

Obviously at some point in time you will have to do IO.  `littoral` ships with
both a sync and an async interface (using httpx): you can install them with `pip
install littoral[sync]` or `pip install littoral[httpx]`.  The sync interface
looks like this:

```python
from littoral.sync import Session

session = Session.login_oauth_simple()
track = session.send(Track.lookup("123-4560789"))
tracks = session.send(Track.search("hard day's night"))
```

the async interface looks like this:

```python
from littoral.async import Session

session = await Session.login_oauth_simple()
track = await session.send(Track.lookup("123-4560789"))
tracks = await session.send(Track.search("hard day's night"))
```

That's it.  `Session.send` handles authentication (including generating a new
token from the refresh token), retrying and everything else you'd expect from a
network interface.  Despite this, the implementation is only <N> lines long: if
you don't like httpx you can easily roll your own.  The *only* place IO happens
is in `Session.send` (if you chose to use our async or sync `Session`): the rest
of the code is (to a first approximation^[functional] purely functional).

## Motivation

- function colour pollution

### Using in tests


[functional]: 'Purely functional' is a very specific term: pure functions not only return
              exactly the same output for exactly the same input every time (they are a
              mapping between an output and input) they also have no side effects.  Littoral's
              code (except in the sync and async sessions) is functional in the first sense,
              but not in the second, because there is some (debug) logging, which is
              technically a side effect, and also because we use pydantic under the hod, which
              in turn calls out to rust, and whilst *most* of this code is written
              functionally, nothing in Littoral guarantees that third party libraries will
              actually be unaffected by the system.  (For instance, a data parsing library
              like pydantic might take into account the defined locale, or the system's
              timezone, or the cpu's word length.)  Nonetheless Littoral *strives* to be
              purely functional, and we avoid relying on side effects (like global state).
              This is why we return callables which require you to pass the session state in
              explicitly.

'''
Copyright (c) 2018 Modul 9/HiFiBerry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from datetime import date
import logging

import musicbrainzngs
from ac2.data.identities import host_uuid, release

musicbrainzngs.set_useragent(
    "audiocontrol2",
    host_uuid(),
    "https://github.com/hifiberry/audiocontrol2/" + release(),
)

musicbrainzngs.set_hostname("musicbrainz.hifiberry.com")


def artist_data(artistname):
    try:
        data = musicbrainzngs.search_artists(query=artistname, limit=1, strict=False)
        if len(data["artist-list"]) >= 1:
            return data["artist-list"][0]
    except Exception as e:
        logging.warning("error while loading musicbrainz data for %s: %s",
                        artistname, e)


def album_data(albumname, artistname=None):
    try:
        if artistname is None:
            data = musicbrainzngs.search_releases(query=albumname,
                                                  limit=1, strict=False)
        else:
            data = musicbrainzngs.search_releases(query=albumname,
                                                  artistname=artistname,
                                                  limit=1, strict=False)
        if len(data["release-list"]) >= 1:
            return data["release-list"][0]
    except Exception as e:
        logging.warning("error while loading musicbrainz data for %s: %s",
                        albumname, e)


def track_data(trackname, artistname=None, releaseid=None):
    try:
        query = "recording:\"{}\"".format(trackname)

        if releaseid is not None:
            data = musicbrainzngs.search_recordings(query=query,
                                                    reid=releaseid,
                                                    limit=1, strict=False)
        elif artistname is not None:
            data = musicbrainzngs.search_recordings(query=query,
                                                    artistname=artistname,
                                                    limit=1, strict=False)
        else:
            data = musicbrainzngs.search_recordings(query=query,
                                                    limit=1, strict=False)

        if len(data["recording-list"]) >= 1:
            return data["recording-list"][0]
    except Exception as e:
        logging.warning("error while loading musicbrainz data for %s: %s",
                        trackname, e)


def enrich_metadata(metadata, improve_artwork=False):
    logging.debug("enriching metadata from musicbrainz")

    if metadata.artist is None or metadata.title is None:
        logging.debug("artist and/or title undefined, can't enrich metadata")

    # Get album data
    if metadata.albummbid is None:
        if metadata.albumTitle:
            data = album_data(metadata.albumTitle,
                              artistname=metadata.artist)
            if data is not None:
                logging.info("found data for %s on musicbrainz", metadata.artist)
                metadata.albummbid = data["id"]
            else:
                logging.info("did not find album %s on musicbrainz", metadata.artist)

    # Get track data
    if metadata.mbid is None:
        data = track_data(metadata.title,
                          artistname=metadata.artist,
                          releaseid=metadata.albummbid)
        if data is not None:
            logging.info("found data for %s on musicbrainz", metadata.title)
            metadata.mbid = data["id"]

            if "tag-list" in data:
                for tag in data["tag-list"]:
                    logging.debug("adding tag %s", tag["name"])
                    metadata.add_tag(tag["name"])
            else:
                logging.debug("no tags for %s/%s on musicbrainz",
                              metadata.artist, metadata.title)

            if metadata.artistmbid is None:
                try:
                    ac = data["artist-credit"][0]
                    metadata.artistmbid = ac["artist"]["id"]
                    logging.debug("artist mbid: %s", metadata.artistmbid)
                except Exception:
                    logging.debug("did not receive artist mbid data")

            rdate = "9999-99-99"
            # Find data when this was first released and get the album mbid
            for release in data.get("release-list", []):
                if release.get("status", "").lower() == "official":

                    if metadata.albummbid is None:
                        metadata.albummbid = release.get("id")
                        logging.debug("album mbid: %s", metadata.albummbid)

                    d = release.get("date", "9999-99-99")

                    # Sometimes only a year is listed
                    if len(d) == 4:
                        d = d + "-12-31"

                    if d < rdate:
                        rdate = d
            try:
                date.fromisoformat(rdate)
                logging.debug("setting release date: %s", rdate)
                if metadata.releaseDate is None:
                    metadata.releaseDate = rdate
            except:
                # ignore invalid dates
                pass

        else:
            logging.info("did not find recording %s/%s on musicbrainz",
                         metadata.artist, metadata.title)

    return

"""
Examples
"""

"""
print(artist_data("Bruce Springsteen"))
print(artist_data("Springsteen, Bruce"))
print(artist_data("Sprteen, Brce"))
print(artist_data("Springsteen and the E-Street Band"))
"""

"""
print(artist_data("Wu Tang Clan"))
print(album_data("Enter The Wu-Tang", "0febdcf7-4e1f-4661-9493-b40427de2c13"))
print(album_data("Enter The Wu-Tang (36 Chambers)", "0febdcf7-4e1f-4661-9493-b40427de2c14"))
print(album_data("Enter The Wu-Tang (36 Chambers) [Expanded Edition]"))
"""

"""
print(artist_data("Springsteen"))
print(track_data("Shadowboxin'"))
print(track_data("Born to run"))
print(track_data("Born to Run", artistid="70248960-cb53-4ea4-943a-edb18f7d336f"))
print(track_data("Born to Run", releaseid="46e5c6a9-b0a7-4e42-9162-8f412705b09d"))
"""

"""
data = track_data("Born to Run", releaseid="46e5c6a9-b0a7-4e42-9162-8f412705b09d")
for tag in data["tag-list"]:
    print(tag)
"""


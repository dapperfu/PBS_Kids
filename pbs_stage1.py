#!/usr/bin/env python3
from __future__ import print_function

# Find the shows. Write to shows.json.
import requests
import json
import os

# URL to the PBS Kids Shows API
PBSKIDS_SHOWS = "http://pbskids.org/pbsk/video/api/getShows/"
PBSKIDS_VIDS = "http://pbskids.org/pbsk/video/api/getVideos/"

SHOWS_CACHE = "shows.json"

# Cache file to avoid hitting PBSKids.org more than once for testing
# If the file exists
if os.path.exists(SHOWS_CACHE):
    print("Loading shows from cache...")
    # Load it.
    with open(SHOWS_CACHE, 'r') as infile:
        shows_result=json.load(infile)
else:
    print("Loading shows from web...")
    # Otherwise get the response from the URL.
    resp = requests.get(PBSKIDS_SHOWS)
    shows_result = json.loads(resp.text)
    # Cache the shows.
    with open(SHOWS_CACHE, 'w') as outfile:
        json.dump(shows_result, outfile)
    # Reload from the file, just to be sure.
    with open(SHOWS_CACHE, 'r') as infile:
        shows_result2 = json.load(infile)
    # Assert that the loaded cache works.
    assert shows_result == shows_result2

# Assert that the number of shows it says it returned matches the number of entries returned
shows=shows_result["items"]
assert len(shows) ==   shows_result["count"]
# Print off all of the shows
print("Found Shows: ")
for show in shows:
    print("    \"{title}\"".format(**show))
#!/usr/bin/env python3
from __future__ import print_function

# Get all of the videos for the shows.

PBSKIDS_SHOWS = "http://pbskids.org/pbsk/video/api/getShows/"
PBSKIDS_VIDS = "http://pbskids.org/pbsk/video/api/getVideos/"
VIDEOS_CACHE = "videos.json"

# Find the shows. Write to shows.json.
import requests
import json

# Create list of all videos
all_videos = list()
# Start index
start_index = 1
# To bootstrap the while loop.
total_videos = start_index + 1  
# While our start index is less than the total number of videos
while start_index < total_videos:
    # Only get full episodes. Can be of type 'Episode' or 'Clip'.
    resp = requests.get(PBSKIDS_VIDS, params={'type': 'Episode', 
                                              'status': 'available',
                                              'startindex': start_index} )
    video_list = json.loads(resp.text)
    # These should always be the same since we are requesting the startindex
    if video_list["start"] != start_index:
        raise("Returned start index doesn't match requested @ startIdx={}".format(start_index))
    
    # Get total number of videos.
    total_videos = video_list["matched"]
    
    print("Grabbing video data: {}-{} of {}".format(video_list["start"],
                                       video_list["end"],
                                       video_list["matched"]))
    
    
    start_index = video_list["end"] + 1
    for item in video_list["items"]:
        all_videos.append(item)

# Write to cache.
with open(VIDEOS_CACHE, 'w') as outfile:
    json.dump(all_videos, outfile)

# Reload from the file, just to be sure.
with open(VIDEOS_CACHE, 'r') as infile:
    all_videos2 = json.load(infile)

assert(all_videos == all_videos2)
print("Writing Cache: "+VIDEOS_CACHE)
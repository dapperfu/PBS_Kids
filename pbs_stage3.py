#!/bin/env python3
from __future__ import print_function
import requests
import os.path
import json

print("#!/bin/sh")

# Make changes here.
DOWNLOAD_ROOT = "/mnt/box/KidsTV"

# Shows to get.              
SHOWLIST = ["Peg + Cat",
            "Sesame Street",
            "Curious George",
            "Daniel Tiger's Neighborhood",
            "The Cat in the Hat",
            "Dinosaur Train",
            "Bob the Builder",
            "Thomas & Friends"]

# Order to grab images.
IMAGE_ORDER = ['kids-mezzannine-16x9', 
               'originalres_4x3',
               'originalres_16x9']

# MP4 bitrate order
# (2500k is a compromize of quality and file size)
MP4_ORDER = ["mp4-2500k",
               "mp4-1200k",
               "mp4-800k",
               "mp4-6500k",
               "mp4-4500k",
               "mp4-400k"]
# HLS quality order
HLS_ORDER = ["hls-1080p-16x9",
                     "hls-6500k-16x9",
                     "hls-4500k-16x9",
                     "hls-2500k-16x9",
                     "hls-1200k-16x9"]
# No more changes, thanks.

PBSKIDS_VIDEOROOT = "http://kids.video.cdn.pbs.org"
VIDEOS_CACHE = "videos.json"
SHOWS_CACHE = "shows.json"


def uniqueList(seq, idfun=None):
    """
    uniqueList(seq, idfun=None)
    Uniquify a list
    http://www.peterbe.com/plog/uniqifiers-benchmark
    """
    # order preserving
    if idfun is None:
        def idfun(x):
            """
            idfun(x)
            """
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result

def get_redirect_url(short_url):
    # Get the redirected URL.
    x = requests.get(short_url, allow_redirects=False)
    l = x.headers["Location"]
    return l

# Get the highest quality image
def get_video_image(images):
    for image_quality in IMAGE_ORDER:
        if image_quality in images:
            return images[image_quality]["url"]
    return None


# Get the best mp4 video available.
def get_mp4_video(videos):
    """
    best_video(videos)
    """
    for mp4_quality in MP4_ORDER:
        if mp4_quality in videos["mp4"]:
            return get_redirect_url(videos["mp4"][mp4_quality]["url"])
    return None

# Get the best hls video available.
def get_hls_video(videos):
    """
    best_video(videos)
    """
    for mp4_quality in HLS_ORDER:
        if mp4_quality in videos["hls"]:
            return get_redirect_url(videos["hls"][mp4_quality]["url"])
    return None

def get_output_base(video):
    title =  video["series_title"]
    ep_title =  video["title"].replace("/", " and ")
    base = "{}.{}.{}".format(title, video["nola_episode"], ep_title)
    vid_file = os.path.join(DOWNLOAD_ROOT, title, base)
    return vid_file

def get_video_url(redirect):
    # print(redirect)
    video_url = PBSKIDS_VIDEOROOT + "/" + redirect.split(":")[2]
    return video_url

def download_mp4(video):
    video_url = get_video_url(get_mp4_video(video["videos"]))
    vid_file_base = get_output_base(video)
    vid_file = vid_file_base+".mp4"
    
    cmd = "curl -o \"{vid_file}\" '{video_url}'".format(video_url = video_url, vid_file=vid_file)
    if os.path.exists(vid_file):
        print("# "+cmd)
    else:
        print(cmd)

def download_hls(video):
    video_url = get_hls_video(video["videos"])
    vid_file_base = get_output_base(video)
    vid_file = "{vid_file_base}.ts".format(vid_file_base=vid_file_base)

    cmd = "hls-fetch --playlist --bandwidth=max --force --output=\"{vid_file}\" {url}".format(vid_file=vid_file, url=video_url)
    if os.path.exists(vid_file):
        print("# "+cmd)
    else:
        print(cmd)
        
def get_nfo(video):
    if len(video["nola_episode"])==3:
        video["season"]  = int(video["nola_episode"][0])
        video["episode"] = int(video["nola_episode"][1:])
    elif len(video["nola_episode"])==4:
        video["season"]  = int(video["nola_episode"][0:1])
        video["episode"] = int(video["nola_episode"][2:])
    else:
        video["season"]=""
        video["episode"]=""

    video["aired"] = video["airdate"].split(" ")[0]

    nfo = """<episodedetails>
            <title>{title}</title>
            <season>{season}</season>
            <episode>{episode}</episode>
            <plot>{description}</plot>
            <aired>{aired}</aired>
            <premiered>{aired}</premiered>
            <studio>PBS Kids</studio>
    </episodedetails>
    """.format(**video)
    
    return nfo

def process(video):
    d = os.path.dirname(get_output_base(video))
    if not os.path.exists(d):
        os.makedirs(d)
    download_mp4(video)
    download_image(video)
    write_nfo(video)
            
def write_nfo(video):
    nfo_file_base = get_output_base(video)
    nfo_file = nfo_file_base+".nfo"
    if os.path.exists(nfo_file):
        print("# NFO Exists: {}".format(nfo_file))
    else:
        with open(nfo_file, "w") as nfo:
            print(get_nfo(video), file=nfo)
            print("# Wrote NFO: {}".format(nfo_file))
        
def download_image(video):
    img_file_base = get_output_base(video)
    img_file = img_file_base+".jpg"
    url = get_video_image(video["images"])
    cmd = "curl -o \"{img_file}\" '{url}'".format(img_file=img_file, url=url)
    if not os.path.exists(img_file):
        print(cmd)
    else:
        print("# "+cmd)


with open(SHOWS_CACHE, 'r') as infile:
    shows =json.load(infile)
print("# Number of shows: {}".format(len(shows["items"])))

with open(VIDEOS_CACHE, 'r') as infile:
    videos = json.loads(infile.read())
print("# Number of available videos: {}".format(len(videos)))


for video in videos:
    title = video["series_title"]
    if title not in SHOWLIST:
        continue
    if video["type"]=="Episode":
        process(video)
    elif video["type"]=="Clip":
        pass
    else:
        raise Exception("Unknown video type: {}".format(video["type"]))

# PBS Kids

Show downloader for PBS Kids in Python.

*If* you live in an area with good internet [PBS Kids](http://pbskids.org/apps/) is hands down one of the best streaming apps out there. We don't live in such an area.

Streaming on our phones eats data.

## pbs_stage1.py

Downloads a list of all available shows and prints them. Caches data it ```shows.json```.

## pbs_stage2.py

Download a list of available videos and caches them to ```videos.json```.

Currently only grabs full Episodes. 



If you find these scripts useful please consider a donation to PBS: http://www.pbs.org/donate/


#### Notes:

1. This was quickly thrown together and not completely documented.
2. It could use some code refactoring but it's not worth it.
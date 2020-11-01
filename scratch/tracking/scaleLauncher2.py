import json
import time
from multiprocessing.pool import ThreadPool as Pool
import subprocess as sp

pool_size = 100
pool = Pool(pool_size)
count = 0

def worker(url,count,id):
    sp.run(["python3", "scaleInstance.py", url, str(count), id])

dicctter = [ ("rtmp", "rtmpt://167.21.72.35:80/live/KCAM028.stream"),
  ("rtsp" , "rtsp://167.21.72.35:554/live/KCAM028.stream"),
  ("f4m" , "http://167.21.72.35:1935/live/KCAM028.stream/manifest.f4m"),
  ("m3u8" , "http://167.21.72.35:1935/live/KCAM028.stream/playlist.m3u8"),
  ("m3u8s" , "https://video.deldot.gov:443/live/KCAM028.stream/playlist.m3u8"),
  ("mssmooth" , "http://167.21.72.35:1935/live/KCAM028.stream/Manifest")
]


for p in dicctter:
    count = count + 1
    #print('Name: ' + p['cameraID'])
    pool.apply_async(worker, (p[1],str(count),p[0],))

pool.close()
pool.join()
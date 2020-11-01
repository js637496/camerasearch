import cv2
import time
import numpy as np
import subprocess as sp
import requests
from lxml.html import fromstring

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:100]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies
dicctter = { "rtmp" : "rtmpt://167.21.72.35:80/live/KCAM028.stream",
  "rtsp" : "rtsp://167.21.72.35:554/live/KCAM028.stream",
  "f4m" : "http://167.21.72.35:1935/live/KCAM028.stream/manifest.f4m",
  "m3u8" : "http://167.21.72.35:1935/live/KCAM028.stream/playlist.m3u8",
  "m3u8s" : "https://video.deldot.gov:443/live/KCAM028.stream/playlist.m3u8",
  "mssmooth" : "http://167.21.72.35:1935/live/KCAM028.stream/Manifest"
}

proxies = list(get_proxies())
print(proxies)

FFMPEG_BIN = "ffmpeg"

VIDEO_URL = "https://s51.nysdot.skyvdn.com:443/rtplive/R4_040/playlist.m3u8"

videoArr = [#"https://s51.nysdot.skyvdn.com:443/rtplive/R2_041/playlist.m3u8",
            "rtmpt://167.21.72.35:80/live/KCAM029.stream"
            #"https://s51.nysdot.skyvdn.com:443/rtplive/R1_066/playlist.m3u8",
            #"https://s51.nysdot.skyvdn.com:443/rtplive/R7_007/playlist.m3u8",
            #"https://s51.nysdot.skyvdn.com:443/rtplive/R7_006/playlist.m3u8"
]

vidPropArr = []


for i in range(len(videoArr)):
    vidProp = {}

    VIDEO_URL = videoArr[i]

    sp.run([FFMPEG_BIN, "-re", "-i", VIDEO_URL, "-vframes", "1", "output_image.jpg", "-y"])
    img = cv2.imread("output_image.jpg")
    IMG_H = img.shape[0]
    IMG_W = img.shape[1]

    vidProp["w"] = IMG_W
    vidProp["h"] = IMG_H

    pipe = sp.Popen([FFMPEG_BIN, "-re", "-i", VIDEO_URL,
                     "-loglevel", "quiet",  # no text output
                     "-http_proxy", proxies[i],
                     "-an",  # disable audio
                     "-f", "image2pipe",
                     "-pix_fmt", "bgr24",
                     "-filter:v", "fps=fps=2",
                     "-vcodec", "rawvideo", "-"],
                    stdin=sp.PIPE, stdout=sp.PIPE)

    vidProp["pipe"] = pipe

    frame1 = pipe.stdout.read(IMG_W * IMG_H * 3)
    frame2 = pipe.stdout.read(IMG_W * IMG_H * 3)

    frame1 = np.frombuffer(frame1, dtype='uint8').reshape((IMG_H, IMG_W, 3))
    frame2 = np.frombuffer(frame2, dtype='uint8').reshape((IMG_H, IMG_W, 3))

    vidProp["frame1"] = frame1
    vidProp["frame2"] = frame2

    #out = cv2.VideoWriter('outpy'+str(i)+'.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (IMG_W, IMG_H))
    #vidProp["out"] = out

    vidPropArr.append(vidProp)
counter = 0

print("STARTING TO WRITE VIDS")
while True:
    for i in range(len(vidPropArr)):
        IMG_H = vidPropArr[i]["h"]
        IMG_W = vidPropArr[i]["w"]
        cv2.imshow("Stream" + str(i), vidPropArr[i]["frame1"])
        #vidPropArr[i]["out"].write(vidPropArr[i]["frame1"])
        vidPropArr[i]["frame1"] = vidPropArr[i]["frame2"]
        frame2 = vidPropArr[i]["pipe"].stdout.read(IMG_W * IMG_H * 3)
        vidPropArr[i]["frame2"] = np.frombuffer(frame2, dtype='uint8').reshape((IMG_H, IMG_W, 3))
    counter = counter + 1

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
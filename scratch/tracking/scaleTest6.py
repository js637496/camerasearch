import cv2
import time
import numpy as np
import subprocess as sp


FFMPEG_BIN = "ffmpeg"

VIDEO_URL = "https://s51.nysdot.skyvdn.com:443/rtplive/R4_040/playlist.m3u8"

videoArr = [
            "https://s51.nysdot.skyvdn.com:443/rtplive/R4_295/playlist.m3u8"]

vidPropArr = []


for i in range(len(videoArr)):
    vidProp = {}

    VIDEO_URL = videoArr[i]

    sp.run([FFMPEG_BIN, "-re", "-i", VIDEO_URL, "-vframes", "1", "output_image6.jpg", "-y"])
    img = cv2.imread("output_image6.jpg")
    IMG_H = img.shape[0]
    IMG_W = img.shape[1]

    vidProp["w"] = IMG_W
    vidProp["h"] = IMG_H

    pipe = sp.Popen([FFMPEG_BIN, "-re", "-i", VIDEO_URL,
                     "-loglevel", "quiet",  # no text output
                     #"-http_proxy", "http://188.40.183.184:1080",
                     "-an",  # disable audio
                     "-f", "image2pipe",
                     "-pix_fmt", "bgr24",
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
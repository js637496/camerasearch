import cv2
import time
import numpy as np
import subprocess as sp


FFMPEG_BIN = "ffmpeg"

VIDEO_URL = "https://s51.nysdot.skyvdn.com:443/rtplive/R4_040/playlist.m3u8"

cv2.namedWindow("Stream",cv2.WINDOW_AUTOSIZE)

### Heres the plan
# we will have bounding boxes in each lane large enough to fit trucks
# each bounding box will also have a smaller box assocaited with it that will be ysed to count
# count will be based on color change threshold % in small box, when back to normal +1
# when count is triggered we will look at the contours in the larger bounding box over the next few frames to
# see how big this individual vic is

countBox2 = [(216, 195), (176, 208), (187, 220), (226, 202), (217, 195)]
lane2 = np.array(countBox2)
countBox1 = [(171, 203), (128, 217), (122, 207), (163, 194), (173, 204)]
lane1 = np.array(countBox1)
countBox3 = [(215, 192), (243, 179), (252, 186), (226, 201), (218, 194)]
lane3 = np.array(countBox3)

sizeBox = []

lastDif = 0
carCount = -1
lastlane1out = []
lastlane2out = []
lastlane3out = []

lane1Count = 0
lane2Count = 0
lane3Count = 0

while True:
    sp.run([FFMPEG_BIN, "-i", VIDEO_URL, "-vframes", "1", "output_image.jpg", "-y"])
    img = cv2.imread("output_image.jpg")

    IMG_H = img.shape[0]
    IMG_W = img.shape[1]

    pipe = sp.Popen([FFMPEG_BIN, "-i", VIDEO_URL,
                     "-loglevel", "quiet",  # no text output
                     "-an",  # disable audio
                     "-f", "image2pipe",
                     "-pix_fmt", "bgr24",
                     "-vcodec", "rawvideo", "-"],
                    stdin=sp.PIPE, stdout=sp.PIPE)

    frame1 = pipe.stdout.read(IMG_W * IMG_H * 3)
    frame2 = pipe.stdout.read(IMG_W * IMG_H * 3)

    frame1 = np.frombuffer(frame1, dtype='uint8').reshape((IMG_H, IMG_W, 3))
    frame2 = np.frombuffer(frame2, dtype='uint8').reshape((IMG_H, IMG_W, 3))

    lastAvg = [0]

    while True:
        cv2.imshow("Stream", frame1)

        mask = np.zeros((frame1.shape[0], frame1.shape[1]))
        cv2.fillConvexPoly(mask, lane1, 1)
        mask = mask.astype(np.bool)
        lane1out = np.zeros_like(frame1)
        lane1out[mask] = frame1[mask]
        cv2.imshow('lane1out', lane1out)

        if len(lastlane1out) > 0:
            res = cv2.matchTemplate(lastlane1out, lastlane1out, cv2.TM_CCOEFF)
            _, hundred_p_val, _, _ = cv2.minMaxLoc(res)
            res = cv2.matchTemplate(lastlane1out, lane1out, cv2.TM_CCOEFF)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            difference_percentage = max_val / hundred_p_val

            if difference_percentage > 1.15 or difference_percentage < .85:
                lane1Count = lane1Count + 1
                print("L1:")
                print(lane1Count)

        mask = np.zeros((frame1.shape[0], frame1.shape[1]))
        cv2.fillConvexPoly(mask, lane3, 1)
        mask = mask.astype(np.bool)
        lane3out = np.zeros_like(frame1)
        lane3out[mask] = frame1[mask]
        cv2.imshow('lane3out', lane3out)

        if len(lastlane3out) > 0:
            res = cv2.matchTemplate(lastlane3out, lastlane3out, cv2.TM_CCOEFF)
            _, hundred_p_val, _, _ = cv2.minMaxLoc(res)
            res = cv2.matchTemplate(lastlane3out, lane3out, cv2.TM_CCOEFF)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            difference_percentage = max_val / hundred_p_val

            if difference_percentage > 1.15 or difference_percentage < .85:
                lane3Count = lane3Count + 1
                print("L3:")
                print(lane3Count)

        mask = np.zeros((frame1.shape[0], frame1.shape[1]))
        cv2.fillConvexPoly(mask, lane2, 1)
        mask = mask.astype(np.bool)
        lane2out = np.zeros_like(frame1)
        lane2out[mask] = frame1[mask]
        cv2.imshow('lane2out', lane2out)

        if len(lastlane2out) > 0:
            res = cv2.matchTemplate(lastlane2out, lastlane2out, cv2.TM_CCOEFF)
            _, hundred_p_val, _, _ = cv2.minMaxLoc(res)
            res = cv2.matchTemplate(lastlane2out, lane2out, cv2.TM_CCOEFF)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            difference_percentage = max_val / hundred_p_val

            if difference_percentage > 1.15 or difference_percentage < .85:
                lane2Count = lane2Count + 1
                print("L2:")
                print(lane2Count)

        lastlane1out = lane1out
        lastlane2out = lane2out
        lastlane3out = lane3out

        frame1 = frame2
        frame2 = pipe.stdout.read(IMG_W * IMG_H * 3)
        frame2 = np.frombuffer(frame2, dtype='uint8').reshape((IMG_H, IMG_W, 3))
        if cv2.waitKey(40) == ord('b'):
            drawPoly = True
        if cv2.waitKey(40) == 32:
            break

    iVid = iVid + 1
    if cv2.waitKey(40) == 27:
        break
cv2.destroyAllWindows()
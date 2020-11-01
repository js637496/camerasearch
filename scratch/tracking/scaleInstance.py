import sys
import cv2
import time
import numpy as np
import subprocess as sp
import os
from ast import literal_eval
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

VIDEO_URL = sys.argv[1]
count = sys.argv[2]
id = sys.argv[3]
polyRaw = sys.argv[4]
polyArr = literal_eval(polyRaw)

FFMPEG_BIN = "ffmpeg"

vidProp = {}

sp.run([FFMPEG_BIN, "-re", "-i", VIDEO_URL, "-vframes", "1", "images/output_image"+str(count)+".jpg", "-y"])
img = cv2.imread("images/output_image"+str(count)+".jpg")
IMG_H = img.shape[0]
IMG_W = img.shape[1]

vidProp["w"] = IMG_W
vidProp["h"] = IMG_H
(H, W) = (IMG_H, IMG_W)

if IMG_W >= 1080 or True:

    pipe = sp.Popen([FFMPEG_BIN, "-re", "-i", VIDEO_URL,
                     "-loglevel", "quiet",  # no text output
                     #"-http_proxy", "http://103.254.167.74:35594",
                     "-an",  # disable audio
                     #"-filter:v", " fps=fps=0.5",
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

    counter = 0

    if not os.path.exists(id):
        os.makedirs(id)
    polycontours = []
    for poly in polyArr:
        polycontours.append(np.array([poly]))
    while True:

        rects = []
        frame1 = vidProp["frame1"]
        frame2 = vidProp["frame2"]

        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cnt = 0
        for contour in contours:
            (x,y,w,h) = cv2.boundingRect(contour)
            x1 = -1
            for poly in polycontours:
                x1 = cv2.pointPolygonTest(poly, (x,y), False)
                if x1 == 1:
                    break
            if cv2.contourArea(contour) < 500 or x1 == -1:
                continue

            box = [x,y,x+w,y+h] * np.array([1, 1, 1, 1])
            rects.append(box.astype("int"))
            millis = int(round(time.time() * 1000))
            cv2.rectangle(frame1, (x,y), (x+w, y+h), (0,255,0), 2)
            cnt = cnt + 1
            crop_img = frame1[y:y + h, x:x + w]
            cv2.imwrite(id + "/" + str(millis) + "-" + str(cnt) + ".png", crop_img)

        # objects = ct.update(rects)
        # for (objectID, centroid) in objects.items():
        #     # draw both the ID of the object and the centroid of the
        #     # object on the output frame
        #     text = "Car {}".format(objectID)
        #     cv2.putText(frame1, text, (centroid[0] - 10, centroid[1] - 10),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #     cv2.circle(frame1, (centroid[0], centroid[1]), 4, (0, 0, 255), -1)

        IMG_H = vidProp["h"]
        IMG_W = vidProp["w"]
        cv2.imshow(id, vidProp["frame1"])
        vidProp["frame1"] = vidProp["frame2"]
        frame2 = vidProp["pipe"].stdout.read(IMG_W * IMG_H * 3)
        vidProp["frame2"] = np.frombuffer(frame2, dtype='uint8').reshape((IMG_H, IMG_W, 3))

        counter = counter + 1

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()


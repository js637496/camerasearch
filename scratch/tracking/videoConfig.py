import cv2
import time
import numpy as np
import subprocess as sp
import json
import numpy as np
import cv2
import os
# ============================================================================



FINAL_LINE_COLOR = (255, 255, 255)
WORKING_LINE_COLOR = (127, 127, 127)

# ============================================================================

class PolygonDrawer(object):
    def __init__(self, window_name, frame1, h, w):
        self.CANVAS_SIZE = (h, w)
        self.window_name = window_name # Name for our window

        self.done = False # Flag signalling we're done
        self.current = (0, 0) # Current position, so we can draw the line-in-progress
        self.points = [] # List of points defining our polygon


    def on_mouse(self, event, x, y, buttons, user_param):
        # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)

        if self.done: # Nothing more to do
            return

        if event == cv2.EVENT_MOUSEMOVE:
            # We want to be able to draw the line-in-progress, so update current mouse position
            self.current = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            # Left click means adding a point at current position to the list of points
            print("Adding point #%d with position(%d,%d)" % (len(self.points), x, y))
            self.points.append((x, y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Right click means we're done
            print("Completing polygon with %d points." % len(self.points))
            self.done = True


    def run(self):
        # Let's create our working window and set a mouse callback to handle events
        cv2.namedWindow(self.window_name, flags=cv2.WINDOW_AUTOSIZE)
        cv2.imshow(self.window_name, frame1)
        cv2.waitKey(1)
        cv2.setMouseCallback(self.window_name, self.on_mouse)

        while(not self.done):
            # This is our drawing loop, we just continuously draw new images
            # and show them in the named window
            canvas = frame1
            if (len(self.points) > 0):
                # Draw all the current polygon segments
                cv2.polylines(canvas, np.array([self.points]), False, FINAL_LINE_COLOR, 1)
                # And  also show what the current segment would look like
                cv2.line(canvas, self.points[-1], self.current, WORKING_LINE_COLOR)
            # Update the window
            cv2.imshow(self.window_name, canvas)
            # And wait 50ms before next iteration (this will pump window messages meanwhile)
            if cv2.waitKey(50) == ord('a'):
                self.done = True
        return canvas

FFMPEG_BIN = "ffmpeg"

VIDEO_URL = "https://s51.nysdot.skyvdn.com:443/rtplive/R4_040/playlist.m3u8"

vidArr = [
    "https://s51.nysdot.skyvdn.com:443/rtplive/R4_040/playlist.m3u8",
    "https://s51.nysdot.skyvdn.com:443/rtplive/R7_007/playlist.m3u8",
    "https://s51.nysdot.skyvdn.com:443/rtplive/R7_006/playlist.m3u8"
    ]

data = []
with open('ny.json') as json_file:
    data = json.load(json_file)
    # for p in data['data']:
    #     count = count + 1
    #     #print('Name: ' + p['cameraID'])
    #     pool.apply_async(worker, (p['streamSource'],str(count),p['cameraID'],))

cv2.namedWindow("Stream",cv2.WINDOW_AUTOSIZE)

### Heres the plan
# we will have bounding boxes in each lane large enough to fit trucks
# each bounding box will also have a smaller box assocaited with it that will be ysed to count
# count will be based on color change threshold % in small box, when back to normal +1
# when count is triggered we will look at the contours in the larger bounding box over the next few frames to
# see how big this individual vic is
dumper = {}
dumper['data'] = []
iVid = 0
done = False
drawPoly = True
while True:
    VIDEO_URL = data['data'][iVid]['streamSource']
    data['data'][iVid]['poly'] = []
    sp.run([FFMPEG_BIN, "-i", VIDEO_URL, "-vframes", "1", "output_imagex" + str(iVid) + ".jpg", "-y"])
    if (os.path.exists("output_imagex" + str(iVid) + ".jpg") == False):
        iVid = iVid + 1
        continue
    img = cv2.imread("output_imagex" + str(iVid) + ".jpg")


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
    polycount = 0
    while True:
        cv2.imshow("Stream", frame1)
        if drawPoly:
            pd = PolygonDrawer("Stream", frame1, IMG_H, IMG_W)
            image = pd.run()
            print("Polygon = %s" % pd.points)
            data['data'][iVid]['poly'].append(pd.points)
            polycount = polycount + 1
            drawPoly = False

        frame1 = frame2
        frame2 = pipe.stdout.read(IMG_W * IMG_H * 3)
        frame2 = np.frombuffer(frame2, dtype='uint8').reshape((IMG_H, IMG_W, 3))
        if cv2.waitKey(40) == ord('b'):
            drawPoly = True
        if cv2.waitKey(40) == 27:
            done = True
            break
        if cv2.waitKey(40) == 32:
            break

    dumper['data'].append(data['data'][iVid])
    iVid = iVid + 1
    if done:
        break

with open('nypoly.json', 'w') as outfile:
    json.dump(dumper, outfile)
cv2.destroyAllWindows()

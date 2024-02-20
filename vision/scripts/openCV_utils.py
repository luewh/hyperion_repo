import cv2

def printCaptureProp(capture):
    print("width  : ",capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    print("height : ",capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("fps    : ",capture.get(cv2.CAP_PROP_FPS))
    print("fCount : ",capture.get(cv2.CAP_PROP_FRAME_COUNT))

def setCaptureScale(capture,width,height):
    if not capture.set(cv2.CAP_PROP_FRAME_WIDTH,width):
        print("Can not set width")
    if not capture.set(cv2.CAP_PROP_FRAME_HEIGHT,height):
        print("Can not set height")
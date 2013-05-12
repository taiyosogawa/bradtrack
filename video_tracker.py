from numpy import *
import cv2
import lktrack

#detect in first frame, track in the remaining
cap = cv2.VideoCapture(0)


ret, im = cap.read()
lkt = lktrack.LKTracker()
lkt.update(im)
lkt.detect_points()
lkt.draw()

while True:
	pass
	ret, im = cap.read()
	lkt.update(im)
	lkt.track_points()
	lkt.draw()
	if cv2.waitKey(10) == 27:
		break

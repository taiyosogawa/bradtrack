from numpy import *
import cv2
import lktrack

imnames = ['bt.003.pgm', 'bt.002.pgm', 'bt.001.pgm', 'bt.000.pgm']

# create tracker object
#lkt = lktrack.LKTracker(imnames)


"""
for im, ft in lkt.track():
	print 'tracking %d features' % len(ft)

# plot the tracks
	figure()
	imshow(im)

	for p in ft:
		plot(p[0], p[1], 'bo')
	for t in lkt.tracks:
		plot([p[0] for p in t], [p[1] for p in t])
	axis('off')
	show()

"""


#detect in first frame, track in the remaining
cap = cv2.VideoCapture(0)


ret, im = cap.read()
lkt = lktrack.LKTracker()
lkt.update(im)
lkt.detect_points()
lkt.draw()
while True:
	#pass
	ret, im = cap.read()
	lkt.update(im)
	lkt.track_points()
	lkt.draw()
	if cv2.waitKey(10) == 27:
		break


"""
while True:
	# get grayscale image
	ret, im = cap.read()
	gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

	#compute flow
	flow = cv2.calcOpticalFlowFarneback(prev_gray,gray,0.5,1,3,15,3,5,1)
	prev_gray = gray

	#plot the flow vectors
	cv2.imshow('Optical flow', draw_flow(gray, flow))
	if cv2.waitKey(10) == 27:
		break
"""
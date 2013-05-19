import numpy as np
import cv2
import lktrack
from win32api import GetSystemMetrics

#detect in first frame, track in the remaining
cap = cv2.VideoCapture(0)


ret, im = cap.read()
lkt = lktrack.LKTracker(im)
lkt.update(im)

bigX = GetSystemMetrics (0)
bigY = GetSystemMetrics (1)

minX = bigX
minY = bigY
maxX = 0
maxY = 0

while True:
	ret, im = cap.read()
	lkt.update(im)
	key = cv2.waitKey(10)

	if key == 112:		#p
		minX = min(minX, lkt.get_points()[0])
		minY = min(minY, lkt.get_points()[1])
	elif key == 109:	#m
		minX = min(minX, lkt.get_points()[0])
		maxY = max(maxY, lkt.get_points()[1])
	elif key == 122:	#z
		maxX = max(maxX, lkt.get_points()[0])
		maxY = max(maxY, lkt.get_points()[1])
	elif key == 113: 	#q
		maxX = max(maxX, lkt.get_points()[0])
		minY = min(minY, lkt.get_points()[1])
	elif key == 27:
		print minX
		print maxX
		print minY
		print maxY
		break

scaleX = bigX / (maxX - minX)
scaleY = bigY / (maxY - minY)
lkt.set_mapping(minX, minY, scaleX, scaleY)

while True:
	ret, im = cap.read()
	lkt.update(im, mouse=True)
	if (cv2.waitKey(10) == 27):
		break

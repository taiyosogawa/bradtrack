from numpy import *
import cv2
import win32api, win32con, math, time

MIN_POINTS = 1
MAX_POINTS = 3
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, .03))
subpix_params = dict(zeroZone=(-1, -1), winSize=(10, 10), criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 20, .03))
feature_params = dict(maxCorners=MAX_POINTS, qualityLevel=.5, minDistance=10)

class LKTracker(object):
	""" Class for Lucas-Kanade tracking with 
		pyramidal optical flow."""

	def __init__(self, img):
		if MAX_POINTS < MIN_POINTS:
			print "The maximum number of points is less than the minimum number of points specified"
		self.features = []
		self.tracks = []
		self.current_frame = 0
		self.avg = float32(img)

	def update(self, img, mouse=False):
		self.img = img
		if len(self.features) < MIN_POINTS or floor(time.time())%1000 == 0:
			self.detect_points()
		self.track_points(mouse)
		self.draw()

	def detect_points(self):
		""" Detect 'good features to track' (corners)
			in the current current_frame using
			sub-pixel accuracy. """
		# load the image and create grayscale
		self.filter()

		# search for good points
		features = cv2.goodFeaturesToTrack(self.gray, **feature_params)

		(cb, gray, cr) = cv2.split(self.img)
		gray = cv2.threshold(gray, 150, 255, cv2.THRESH_TOZERO)[1]
		circles = cv2.HoughCircles(gray,cv2.cv.CV_HOUGH_GRADIENT,3,100,param1=100,param2=30,minRadius=3,maxRadius=20)
		self.circles = circles
		confirmed_features = []
        
		if features != None:
			if circles != None:
				for feature in features:
					x1 = int(feature[0][0])
					y1 = int(feature[0][1])

					for circle in circles:
						x2 = circle[0][0]
						y2 = circle[0][1]

						if sqrt( (x2 - x1)**2 + (y2 - y1)**2 ) < circle[0][2] * 1.1:
							confirmed_features.append(feature)
							break

			else:
				confirmed_features = features

			# initialize the tracking
			self.features = confirmed_features
			self.tracks = [[p] for p in features.reshape((-1, 2))]
			self.prev_gray = self.gray

	def get_points(self):
		return self.features[0][0]

	def set_mapping(self, mX=0, mY=0, sX=1, sY=1):
		self.minX = mX
		self.minY = mY
		self.scaleX = sX
		self.scaleY = sY

	def track_points(self, mouse=False):
		""" Track the detected features. """
		if self.features != []:

			if mouse:
				x = int(win32api.GetSystemMetrics (0) - (self.features[0][0][0] - self.minX) * self.scaleX)
				y = int((self.features[0][0][1] - self.minY) * self.scaleY)

				win32api.SetCursorPos((x, y))

			#load the image and create grayscale
			self.filter()
			
			# reshape to fit input format
			tmp = float32(self.features).reshape(-1, 1, 2)

			# calculate optical flow
			self.prev_features = self.features
			features, status, track_error = cv2.calcOpticalFlowPyrLK(self.prev_gray, self.gray, tmp, None, **lk_params)

			# remove points lost
			self.features = [p for (st, p) in zip(status, features) if st]

			# clean tracks from lost points

			features = array(features).reshape((-1, 2))
			for i, f in enumerate(features):
				self.tracks[i].append(f)
			ndx = [i for (i, st) in enumerate(status) if not st]
			ndx.reverse() # remove from back
			for i in ndx:
				self.tracks.pop(i)

			self.prev_gray = self.gray


	def draw(self):
		""" Draw the current image with points using
			OpenCV's own drawing functions. """

		# draw points as green circles for point in self.features:
		for point in self.features:
			cv2.circle(self.img, (int(point[0][0]), int(point[0][1])), 4, (0, 255, 0), -1)
			cv2.circle(self.gray, (int(point[0][0]), int(point[0][1])), 4, (0, 255, 0), -1)

		if self.circles != None:
			for circle in self.circles[0,:]:
				cv2.circle(self.img,(int(circle[0]), int(circle[1])), int(circle[2] * 1.05), (255, 0, 0), 1)  # draw the outer circle
				cv2.circle(self.img,(int(circle[0]), int(circle[1])), 2, (0, 0, 255), 3)     # draw the center of the circle

		cv2.imshow('color', self.img)
		cv2.imshow('gray', self.gray)

	def filter(self):
		cv2.accumulateWeighted(self.img, self.avg, 0.5)
		self.img = cv2.convertScaleAbs(self.avg)
		(cb, gray, cr) = cv2.split(self.img)
		self.gray = cv2.threshold(gray, 150, 255, cv2.THRESH_TOZERO)[1]
		self.cb = cv2.threshold(cb, 150, 255, cv2.THRESH_TOZERO)[1]
		self.cr = cv2.threshold(cr, 150, 255, cv2.THRESH_TOZERO)[1]

					
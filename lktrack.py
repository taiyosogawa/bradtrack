from numpy import *
import cv2

MIN_POINTS = 2
MAX_POINTS = 2
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, .03))
subpix_params = dict(zeroZone=(-1, -1), winSize=(10, 10), criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 20, .03))
feature_params = dict(maxCorners=MAX_POINTS, qualityLevel=.5, minDistance=10)

class LKTracker(object):
	""" Class for Lucas-Kanade tracking with 
		pyramidal optical flow."""

	def __init__(self):
		if MAX_POINTS > MIN_POINTS:
			print "The maximum number of points is less than the minimum number of points specified"
		self.features = []
		self.tracks = []
		self.current_frame = 0

	def update(self, img):
		self.img = img
		if len(self.features) < MIN_POINTS:
			self.detect_points()

	def detect_points(self):
		""" Detect 'good features to track' (corners)
			in the current current_frame using
			sub-pixel accuracy. """
		# load the image and create grayscale
		self.filter()

		# search for good points
		features = cv2.goodFeaturesToTrack(self.gray, **feature_params)
		
		if features != None:
			# refine the corner locations
			#cv2.cornerSubPix(self.gray, features, **subpix_params)
			self.features = features
			self.tracks = [[p] for p in features.reshape((-1, 2))]
			self.prev_gray = self.gray


	def track_points(self):
		""" Track the detected features. """
		if self.features != []:
			#load the image and create grayscale
			self.filter()
			
			# reshape to fit input format
			tmp = float32(self.features).reshape(-1, 1, 2)

			# calculate optical flow
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

		self.img = cv2.cvtColor(self.gray, cv2.COLOR_GRAY2BGR)

		# draw points as green circles for point in self.features:
		for point in self.features:
			cv2.circle(self.img, (int(point[0][0]), int(point[0][1])), 3, (0, 255, 0), -1)

		cv2.imshow('LKtrack', self.img)

	def filter(self):
		gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
		self.gray = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)[1]

					
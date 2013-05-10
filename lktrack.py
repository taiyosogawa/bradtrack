from numpy import *
import cv2

lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, .03))
subpix_params = dict(zeroZone=(-1, -1), winSize=(10, 10), criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 20, .03))
feature_params = dict(maxCorners=50, qualityLevel=.01, minDistance=10)

class LKTracker(object):
	""" Class for Lucas-Kanade tracking with 
		pyramidal optical flow."""

	def __init__(self):
		self.features = []
		self.tracks = []
		self.current_frame = 0

	def update(self, im):
		self.im = im

	def detect_points(self):
		""" Detect 'good features to track' (corners)
			in the current current_frame using
			sub-pixel accuracy. """

		# load the image and create grayscale
		self.gray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)

		# search for good points
		features = cv2.goodFeaturesToTrack(self.gray, **feature_params)

		# refine the corner locations
		cv2.cornerSubPix(self.gray, features, **subpix_params)

		self.features = features
		self.tracks = [[p] for p in features.reshape((-1, 2))]
		self.prev_gray = self.gray

	def track_points(self):
		""" Track the detected features. """
		if len(self.features) < 2:
			self.detect_points()
		if self.features != []:
			#load the image and create grayscale
			self.gray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)

			# reshape to fit input format
			tmp = float32(self.features).reshape(-1, 1, 2)

			# calculate optical flow
			features, status, track_error = cv2. calcOpticalFlowPyrLK(self.prev_gray, self.gray, tmp, None, **lk_params)

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
			OpenCV's own drawing functions. Press any
			key to close window. """

		# draw points as green circles for point in self.features:
		for point in self.features:
			cv2.circle(self.im, (int(point[0][0]), int(point[0][1])), 3, (0, 255, 0), -1)

		cv2.imshow('LKtrack', self.im)


	def track(self):
		""" Generator for stepping through a sequence """

		if self.features == []:
			self.detect_points()
		else:
			self.track_points()

		# create a copy in RGB
		f = array(self.features).reshape(-1, 2)
		im = cv2.cvtColor(self.im, cv2.COLOR_BGR2RGB)
		yield im, f

from numpy import *
import cv2
import win32api, win32con, math, time

MIN_POINTS = 1
MAX_POINTS = 3
PIXEL_THRESHOLD = 130
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, .03))
feature_params = dict(maxCorners=MAX_POINTS, qualityLevel=.5, minDistance=10)

class IRTracker(object):

	def __init__(self, img):
		if MAX_POINTS < MIN_POINTS:
			print "The maximum number of points is less than the minimum number of points specified"
		self.features = []
		self.tracks = []
		self.current_frame = 0
		self.avg = float32(img)

	def update(self, img, mouse=False):
		self.img = img
		if len(self.features) < MIN_POINTS or floor(time.time())% 60000== 0:
			self.detect_points()
		self.track_points(mouse)
		self.draw()

	def detect_points(self):
		# load the image and create grayscale
		self.filter(track=False)

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
		if len(self.features) > 0:
			return self.features[0][0]
		else:
			return []

	def set_mapping(self, mX=0, mY=0, sX=1, sY=1):
		self.minX = mX
		self.minY = mY
		self.scaleX = sX
		self.scaleY = sY
		self.x = 0
		self.y = 0 

	def track_points(self, mouse=False):
		""" Track the detected features. """
		if self.features != []:

			if mouse:
				self.x = int(.7*self.x + .3*(win32api.GetSystemMetrics (0) - (self.features[0][0][0] - self.minX) * self.scaleX))
				self.y = int(.7*self.y + .3*((self.features[0][0][1] - self.minY) * self.scaleY))

				win32api.SetCursorPos((self.x, self.y))

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

		cv2.imshow('Brad Track', self.img)
		cv2.moveWindow('Brad Track', win32api.GetSystemMetrics(0) - 700, 50)
		

	def filter(self, track=True):
		#cv2.imshow('original', self.img)
		#Remove jitter

		cv2.accumulateWeighted(self.img, self.avg, 0.5)
		self.img = cv2.convertScaleAbs(self.avg)

		(cb, cg, cr) = cv2.split(self.img)
		gray_threshold = cv2.threshold(cg, PIXEL_THRESHOLD, 255, cv2.THRESH_TOZERO)[1]
		#cv2.imshow('threshold', gray_threshold)
		color_threshold = cv2.cvtColor(gray_threshold, cv2.COLOR_GRAY2BGR)

		""" create a contour mask """
		contour_mask = zeros(gray_threshold.shape, uint8)
		contours, hier = cv2.findContours(gray_threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		for cnt in contours:
			if 15 < cv2.contourArea(cnt) < 800:
				cv2.drawContours(color_threshold, [cnt], 0, (255, 0, 255), 1)
				cv2.drawContours(contour_mask, [cnt], 0, 255, -1)
				cv2.drawContours(self.img, [cnt], 0, (255, 0, 255), 1)

		color_contour = cv2.bitwise_and(color_threshold, color_threshold, mask=contour_mask)

		""" create a circle mask """
		circle_mask = zeros(gray_threshold.shape, uint8)
		color_threshold = cv2.cvtColor(gray_threshold, cv2.COLOR_GRAY2BGR)
		circles = cv2.HoughCircles(gray_threshold,cv2.cv.CV_HOUGH_GRADIENT,3,100,param1=100,param2=30,minRadius=3,maxRadius=20)
		if circles != None:
			for circle in circles[0,:]:
				cv2.circle(color_threshold, (int(circle[0]), int(circle[1])), int(circle[2] * 1.05), (255, 0, 0), 1)
				cv2.circle(circle_mask, (int(circle[0]), int(circle[1])), int(circle[2] * 1.05), 255, -1)
				cv2.circle(self.img, (int(circle[0]), int(circle[1])), int(circle[2] * 1.05), (255, 0, 0), 1)

		color_circle = cv2.bitwise_and(color_threshold, color_threshold, mask=circle_mask)

		""" create a mask of both contours and circles """
		double_mask = cv2.bitwise_and(contour_mask, circle_mask)
		color_double = cv2.bitwise_and(color_threshold, color_threshold, mask=double_mask)
		gray_double = cv2.bitwise_and(gray_threshold, gray_threshold, mask=double_mask)

		"""
		cv2.imshow('cg', cg)
		
		cv2.imshow('contour mask', color_contour)
		cv2.imshow('circle mask', color_circle)
		cv2.imshow('double mask', color_double)
		"""

		if track:
			self.gray = gray_threshold
		else:
			self.gray = gray_double
		

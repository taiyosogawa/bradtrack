import cv2
import numpy as np
import sys, time, os
import irtrack, clicklistener
from PIL import ImageTk
from win32api import GetSystemMetrics
from Tkinter import *

class BradTrack:
    def __init__(self, master):
        os.chdir("c:\\platform-tools\\bradtrack")
        self.cap = cv2.VideoCapture(0)
        ret, img = self.cap.read()
        self.lkt = irtrack.IRTracker(img)
        self.listener = clicklistener.Listener()

        # Set default values for the bounding box
        self.minX = 0
        self.minY = 0
        self.maxX = GetSystemMetrics(0)
        self.maxY = GetSystemMetrics(1)

        self.clock = 0

        self.master = master
        frame = Frame(master)
        frame.pack()

        self.corner = 0
        self.corner_array = ["arrow_nw.gif", "arrow_sw.gif", "arrow_se.gif", "arrow_ne.gif"]
        arrow_img = ImageTk.PhotoImage(file=self.corner_array[self.corner])

        self.arrow_label = Label(frame, image=arrow_img)
        self.arrow_label.image = arrow_img
        self.arrow_label.pack(side=LEFT)

        self.timer = StringVar()
        self.timer.set("5")
        timer_label = Label(frame, textvariable=self.timer, font=("Helvetica", 64), padx=40).pack(side=LEFT)

    def runtimer(self):
        self.master.attributes("-topmost", True)
        self.clock = self.clock + 10
        if self.clock % 200 == 0:
            if self.tick():
                self.corner = self.corner + 1
                if self.corner > 3:
                    self.master.destroy()
                    return
                else:
                    arrow_img = ImageTk.PhotoImage(file=self.corner_array[self.corner])
                    self.arrow_label.configure(image = arrow_img)
                    self.arrow_label.image = arrow_img

            
        else:
            ret, img = self.cap.read()
            self.lkt.update(img)
        self.master.after(10, self.runtimer)

    def tick(self):
        #print "tick"
        time_left = int(self.timer.get())
        if time_left > 0:
            self.timer.set(str(time_left - 1))
            return False
        else:
            #print "timeout"
            ret, img = self.cap.read()
            self.lkt.update(img)
            points = self.lkt.get_points()
        
            if len(points) > 0:
                if self.corner == 0:
                    self.minX = points[0]
                    self.minY = points[1]
                elif self.corner == 1:
                    self.minX = points[0]
                    self.maxY = points[1]
                elif self.corner == 2:
                    self.maxX = points[0]
                    self.maxY = points[1]
                elif self.corner == 3:
                    self.maxX = points[0]
                    self.minY = points[1]

            self.timer.set("3")
            return True

    def track(self):
        scaleX = GetSystemMetrics(0) / (self.maxX - self.minX)
        scaleY = GetSystemMetrics(1) / (self.maxY - self.minY)
        self.lkt.set_mapping(self.minX, self.minY, scaleX, scaleY)

        while True:
            self.listener.listen()
            ret, img = self.cap.read()
            self.lkt.update(img, mouse=True)
            if (cv2.waitKey(10) == 27):
                break

root = Tk()

bradtrack = BradTrack(root)

root.geometry("450x300+" + str(max(100, GetSystemMetrics(0) - 1225)) + "+150")
root.after(10, bradtrack.runtimer)
root.mainloop()
bradtrack.track()
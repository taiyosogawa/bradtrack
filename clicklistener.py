import pyaudio
import struct
import math
import win32api, win32con

INPUT_BLOCK_TIME = 0.04

"""-----------------------------------------------------------------
CONSTANTS FOR ADJUSTMENT
-----------------------------------------------------------------"""

# The min and max thresholds for a tongue click
# According to my measurements, this should be .014 to .04
RMS_MIN_THRESHOLD = 0.1
RMS_MAX_THRESHOLD = .25

# if the noise was longer than this many blocks, it's too long
MAX_TAP_BLOCKS = 0.08/INPUT_BLOCK_TIME

"""-----------------------------------------------------------------
DO NOT EDIT BELOW THIS LINE
-----------------------------------------------------------------"""

FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100  
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)



def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def get_rms( block ):
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class Listener(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.rms_min = RMS_MIN_THRESHOLD
        self.rms_max = RMS_MAX_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0
        self.tapno = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            #print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    #print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        #if device_index == None:
            #print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):

        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def tapDetected(self):
        print "Tap " + str(self.tapno)
        self.tapno += 1
        x, y = win32api.GetCursorPos()
        click(x, y)

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError, e: 
            self.errorcount += 1
            #print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return

        amplitude = get_rms( block )
        if self.rms_min <= amplitude <= self.rms_max:
            #print(amplitude)
            # noisy block
            self.quietcount = 0
            self.noisycount += 1

        else:            
            # quiet block.
            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                self.tapDetected()
            self.noisycount = 0
            self.quietcount += 1

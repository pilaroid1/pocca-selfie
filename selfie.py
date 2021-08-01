"""
    VisionCam BrainCraft
"""

from colorama import Fore, Back, Style
import time
import threading
import configparser
import os
import sys
import signal

import sys
sys.path.append("../")
import time
import configparser
import os
import signal

from pocca.display.interface import Interface
from pocca.vision.camera import Camera #Pi Camera Manager
from pocca.vision.effects import Effects # OpenCV Effects
from pocca.controls.buttons import Buttons # Joystick / Buttons

# Detect a CTRL-C abord program interrupt, and gracefully exit the application
def sigint_handler(signal, frame):
    print(TEXT.DEV_STOP)
    going = False
    sys.exit(0)

# Enable abord program interrupt
signal.signal(signal.SIGINT, sigint_handler)

settings = configparser.ConfigParser()
settings.read("/media/usb/pocca.ini")
if settings["APPLICATION"]["lang"]:
    from pocca.localization.fr import TEXT
else:
    from pocca.localization.en import TEXT
path_images = settings["FOLDERS"]["pictures"]
path_temp = settings["FOLDERS"]["temp"]

print("\033c", end="") # Clear Terminal
print(" ~~~~~~ 📷 POCCA GIF 📷 ~~~~~~")
print(TEXT.LOCK_WARNING)

interface = Interface(settings)
camera = Camera(settings, TEXT)
effects = Effects()
buttons = Buttons(TEXT)

interface.start()
camera.start()
camera.clear_temp() # Remove Previous Images

going = True
start_timer = 0
countdown = 0
# Enable Screen
tft_enable = True

while going:
    # Viewfinder (Live preview)
    if interface.state == "viewfinder":
        try:
            # Capture frame continously
            for frame in camera.stream.capture_continuous(camera.rawCapture, format='bgr', use_video_port=True):

                # Get array of RGB from images
                frame = frame.array

                # Effects
                if(effects.id == effects.EFFECT_CONTOURS):
                    # Canny Detection Effects (contours)
                    frame = effects.canny_edge(frame)
                    frame = effects.color_change(frame, (0,0,255)) # RED

                # Resize image to screen resolution
                frame_resize = camera.resize(frame, (interface.resolution))
                # Copy image to screen
                interface.to_screen(frame_resize)

                interface.top_left(interface.state)
                interface.top_right("photo")

                camera.rawCapture.truncate(0)

                if(countdown > 0):
                    interface.bottom(str(countdown))

                if interface.state == "countdown" :
                    if time.time() > (start_timer + 1):
                        print(TEXT.TIMER + " : " + str(countdown))
                        if countdown > 0:
                            countdown = countdown - 1
                        else:
                            interface.state = "record"
                        start_timer = time.time()

                # If we are in record mode
                if interface.state == "record":
                    filename = camera.save_uid(frame, path_images, "selfie") # Save frame to disk
                    interface.state = "viewfinder"

                # Check if a button is pressed
                pressed = buttons.check()

                # If the button is pressed
                if pressed == buttons.BTN: # or  web_action == 1:
                    start_timer = time.time()
                    countdown = 3
                    interface.state = "countdown"
                elif pressed == buttons.BTN2:
                    if(effects.id == effects.EFFECT_NONE):
                        effects.id = effects.EFFECT_CONTOURS
                    else:
                        effects.id = effects.EFFECT_NONE
                camera.rawCapture.truncate(0)

        # If the video capture failed, crash gracefully
        except Exception as error:
            raise # Add this to check error
            print("❌ ➡️" + str(error))
            going = False

# If we exit the application, we go here
print(TEXT.SHUTDOWN_APP)
camera.stop()
interface.stop()
sys.exit(0)

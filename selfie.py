"""
    Pilaroid - Selfie (P.O.C.C.A)
    https://github.com/usini/pocca-selfie
"""
import sys
sys.path.append("/media/usb/apps")
from pocca.display.interface import Interface
from pocca.display.countdown import Countdown
from pocca.vision.camera import Camera #Pi Camera Manager
from pocca.vision.effects import Effects # OpenCV Effects
from pocca.controls.buttons import Buttons # Joystick / Buttons
from pocca.utils.app import App # Application Manager (Settings / Secrets / utilities)

app = App()
app.clear_terminal()
print(app.TEXT.LOCK_WARNING)
print(" ~~~~~~ 📷 Pilaroid SELFIE 📷  ~~~~~~")
print(" https://github.com/usini/pocca-selfie")

interface = Interface(app.settings, app.system)
countdown = Countdown(app.settings, app.TEXT)

buttons = Buttons(app.TEXT)

camera = Camera(app.settings, app.TEXT, app.camera_resolution)
camera.clear_temp() # Remove Previous Images

effects = Effects(app.settings)

color_id = 0
# If we exit the application, we go here
def stop(signal, frame):
    print(app.TEXT.SHUTDOWN_APP)
    app.running = False
app.stop_function(stop)

def run():
    for frame in camera.stream.capture_continuous(camera.rawCapture, format='bgr', use_video_port=True):
        # Get array of RGB from images
        frame = frame.array

        if not app.running:
            sys.exit(0)

        # Effects
        if(effects.id == effects.CONTOURS):
            # Canny Detection Effects (contours)
            frame = effects.canny_edge(frame)
            frame = effects.color_change(frame)

        # Resize image to screen resolution
        frame_resize = camera.resize(frame, (interface.resolution))
        interface.to_screen(frame_resize)

        if countdown.running():
            if countdown.started:
                interface.bottom(str(countdown.current()))
            else:
               filename = camera.save_uid(frame, app.path["images"], "selfie_") # Save frame to disk
               camera.save_timestamp(filename)

        interface.top_left(interface.state)
        interface.top_right("photo")

        interface.update()

        interface.clock.tick()
        camera.refresh()
        controls()


def controls():
    global color_id
    # Check if a button is pressed
    pressed = buttons.check()

    # If the button is pressed
    if pressed == buttons.BTN:
        if not countdown.running():
            countdown.start()
    elif pressed == buttons.BTN2:
        if color_id < 6:
            effects.id = effects.CONTOURS
            color_id += 1
            if color_id == 1:
                effects.color_lines = (0,0,1)
                effects.color_background = (0,0,0)
            elif color_id == 2:
                effects.color_lines = (0,1,0)
                effects.color_background = (0,0,0)
            elif color_id == 3:
                effects.color_lines = (1,0,0)
                effects.color_background = (0,0,0)
            elif color_id == 4:
                effects.color_lines = (1,1,1)
                effects.color_background = (0,0,255)
            elif color_id == 5:
                effects.color_lines = (1,1,1)
                effects.color_background = (0,255,0)
            elif color_id == 6:
                effects.color_lines = (1,1,1)
                effects.color_background = (255,0,0)
        else:
            color_id = 0
            effects.id = effects.NO

run()

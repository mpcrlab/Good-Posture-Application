'''
Camera Example
==============

This example demonstrates a simple use of the camera. It shows a window with
a buttoned labelled 'play' to turn the camera on and off. Note that
not finding a camera, perhaps because gstreamer is not installed, will
throw an exception during the kv language processing.

'''

# Uncomment these lines to see all the messages
# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Ellipse, Color
from kivy.graphics.instructions import InstructionGroup

from collections import deque

from PIL import Image
import requests

import time
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')

def relative_coord_to_pixel(coord, size, widget_pos, widget_size, preserve_aspect_ratio=True):
    range_x, range_y = widget_size[0], widget_size[1]
    if preserve_aspect_ratio:
        range_avg = sum(widget_size) / len(widget_size)
        range_x, range_y = range_avg, range_avg

    size_pixels = (size[0] * range_x, size[1] * range_y)
    return (widget_size[0] * coord[0] + widget_pos[0] - size_pixels[0] / 2, widget_size[1] * coord[1] + widget_pos[1] - size_pixels[1] / 2), size_pixels


dot_size = (0.02, 0.02)

class CameraClick(BoxLayout):
    dots = deque()

    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        #timestr = time.strftime("%Y%m%d_%H%M%S")
        #camera.export_to_png("IMG_{}.png".format(timestr))
        
        #print(requests.get('http://127.0.0.1:5000'))
        print(camera.texture.height)
        print(camera.texture.width)
        print(len(camera.texture.pixels))
        data = requests.post('http://127.0.0.1:5000/image', data={"height":str(camera.texture.height), "width": str(camera.texture.width)}, files={'media': camera.texture.pixels}).text
        
        #Fix Later
        people = eval(data)
        people = [list(map(lambda: (x[0], x[1], 1-x[2]), person)) for person in people]

        while len(self.dots) > 0:
            camera.canvas.remove(self.dots.pop())
        for person in people:
            for keypoint in person:
                dot = InstructionGroup()
                dot.add(Color(1., 0, 0))
                (x, y), size = relative_coord_to_pixel((keypoint[1], keypoint[2]), dot_size, camera.pos, camera.size)
                dot.add(Ellipse(pos=(x, y), size=size))
                camera.canvas.add(dot)
                self.dots.append(dot)


class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()

people = [[(0, 0.5092592592592593, 0.45108695652173914), (16, 0.4444444444444444, 0.45652173913043476), (14, 0.48148148148148145, 0.42934782608695654), (15, 0.5231481481481481, 0.41847826086956524)]]
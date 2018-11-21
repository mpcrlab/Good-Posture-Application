import argparse
import logging
import time

import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

from flask import Flask
from flask import request

from PIL import Image

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    args = parser.parse_args()

    w, h = model_wh("432x368")
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path('mobilenet_thin'), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path('mobilenet_thin'), target_size=(432, 368))

app = Flask(__name__)

@app.route("/image", methods=['POST'])
def image():
    img = Image.frombytes('RGBA', (640, 480), request.files['media'].read()).convert('RGB')
    np_img = np.array(img)
    np_img = np.swapaxes(np_img, 0, 1)
    print(np_img.shape)
    
    fixed_image = Image.fromarray(np_img, 'RGB')
    fixed_image.show()


    humans = e.inference(np_img, resize_to_default=True, upsample_size=4)
    print(humans)
    return "ok"

@app.route("/")
def home():
    return "home page"

app.run()
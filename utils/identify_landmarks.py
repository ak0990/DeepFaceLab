import os
import sys
import argparse
#from utils import Path_utils
from core import pathex
from utils import os_utils
from pathlib import Path
import numpy as np
from utils.DFLPNG import DFLPNG
from tqdm import tqdm
import cv2

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception("This program requires at least Python 3.2")

def get_img_list(input_path):
    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

        if filepath.suffix != '.png':
            print ("%s is not a png file required for sort_by_origname" % (filepath.name) )
            continue

        img_list.append(str(filepath))

    return img_list

def get_aligned_img_list(input_path):

    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

        if filepath.suffix != '.png':
            print ("%s is not a png file required for sort_by_origname" % (filepath.name) )
            continue

        a_png = DFLPNG.load (str(filepath))
        if a_png is None:
            print ("%s failed to load" % (filepath.name) )
            continue

        d = a_png.getDFLDictData()

        if d is None or d['landmarks'] is None:
            print ("%s - no embedded data found " % (filepath.name) )
            continue

        img_list.append( [str(filepath), d['landmarks']] )

    return img_list

# 0-7   left jaw
#       left temple = 0
# 8     chin
# 9-16  right jaw
#       right temple = 16
# 17-21 left eyebrow
# 22-26 right eyebrow
# 27-35 nose
#       27 = top of bridge
#       30 = tip
# 36-41 left eye
#       36 outside
#       39 inside / tear duct
#       40-41 bottom
# 42-47
#       42 inside / tear duct
#       45 outside
#       46-47 bottom
# 48-67 mouth
#       48 left corner
#       54 right corner
#       57 bottom center
#       60 left corner
#       61-67 inner
def draw_landmarks(img_list):
    font = cv2.FONT_HERSHEY_SIMPLEX
    for filepath, image_landmarks in img_list:
        image = cv2.imread( str(filepath) )

        if len(image_landmarks) != 68:
            raise Exception('get_image_eye_mask works only with 68 landmarks')

        for i, point in enumerate(image_landmarks):
            point = tuple(point)
            print(point)
            cv2.putText( image, str(i), point, font, 0.5, (0,255,0), 1 )
            cv2.imshow("image", image)
            cv2.waitKey(0)


if __name__ == "__main__":
    source_dir = sys.argv[1]

    source_img_list = get_aligned_img_list(source_dir)
    draw_landmarks(source_img_list)

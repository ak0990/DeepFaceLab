import os
import sys
import re
import argparse
#from utils import Path_utils
#import Path_utils
from core import pathex
from pathlib import Path
import numpy as np
#from DFLIMG.DFLPNG import DFLPNG
from DFLIMG.DFLJPG import DFLJPG
from tqdm import tqdm
from core.interact import interact

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception("This program requires at least Python 3.2")

class fixPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_img_list(input_path):
    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

        if filepath.suffix != '.png' and filepath.suffix != '.jpg':
            print ("%s is not a png file" % (filepath.name) )
            continue

        img_list.append(str(filepath))

    return img_list

def get_aligned_img_list(input_path):
    print ("Loading files: %s" %input_path)

    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

        if filepath.suffix != '.png' and filepath.suffix != '.jpg':
            print ("%s is not a png file" % (filepath.name) )
            continue

        if filepath.suffix == '.png':
            a_img = DFLPNG.load (str(filepath))
            if a_img is None:
                print ("%s failed to load" % (filepath.name) )
                continue
        elif filepath.suffix == '.jpg':
            a_img = DFLJPG.load (str(filepath))
            if a_img is None:
                print ("%s failed to load" % (filepath.name) )
                continue

        d = a_img.getDFLDictData()

        if d is None or d['source_filename'] is None:
            print ("%s - no embedded data found required for sort_by_origname" % (filepath.name) )
            continue

        img_list.append( [str(filepath), d['source_filename']] )

    return img_list

def decimate(img_list, target):
    total = len(img_list)

    target_set = False
    while not target_set:
        mod = total / int(target)
        mod = int(mod)

        print("Total files:     %s" %(total))
        print("Target:          %s" %(target))
        print("Modulus:         %s" %(mod))
        if total < int(target):
            print("ERROR: Target remaining must be less than total files")
            print("Exiting")
            sys.exit(1)
        print("Est Remaining:   %s" %(int(total/mod)))
        response = interact.input_in_time ("Press enter in 10 seconds to override settings.", 10)
        if response == True:
            target = interact.input_int("Target: ", 1500)
        else:
            target_set = True

    i = 0
    removed = 0
    pbar = tqdm(img_list)
    for train_img in pbar:
        #train_filename = Path(train_img[0]) # could be number.png or number_index.png
        train_filename = train_img # could be number.png or number_index.png
        #train_orig = train_img[1]
        #train_trimmed = re_train.sub('', train_orig)

        if i % mod == 0:
            # Keep
            pass
        else:
            pbar.set_description("Removed: %s" %train_filename)
            os.remove(train_filename)
            removed += 1

        i += 1
    print("Removed total files:   %s" %(removed))
    print("Remaining total files: %s" %(total-removed))


if __name__ == "__main__":
    try:
        train_dir = sys.argv[1]
        target = sys.argv[2]
    except:
        print("Usage: %s faces_to_train_path " %(sys.argv[0]))

    #debug_img_list = get_img_list(debug_dir)
    #train_img_list = get_aligned_img_list(train_dir)
    train_img_list = get_img_list(train_dir)
    decimate(train_img_list, target)

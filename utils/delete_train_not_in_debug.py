import os
import sys
import re
import argparse
#import Path_utils
from core import pathex
from pathlib import Path
from DFLPNG import DFLPNG
from DFLJPG import DFLJPG
from tqdm import tqdm

print("start")
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

def process_sort(arguments):
    from mainscripts import Sorter
    Sorter.main (input_path=arguments.input_dir, sort_by_method=arguments.sort_by_method)


def get_img_list(input_path):
    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

        if filepath.suffix != '.png' and filepath.suffix != '.jpg':
            print ("%s is not a image file" % (filepath.name) )
            continue

        img_list.append(str(filepath))

    return img_list

def get_aligned_img_list(input_path):
    #print ("Sort by original filename...")

    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

        if filepath.suffix != '.png' and filepath.suffix != '.jpg':
            print ("%s is not a image file" % (filepath.name) )
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

def remove_train_not_in_debug(debug_img_list, train_img_list):
    re_debug = re.compile(r'_debug')
    re_train = re.compile(r'_[0-9]+')
    re_jpg = re.compile(r'jpg')

    #print("Count debug: %s -- Count train: %s" %(len(debug_img_list), len(train_img_list)))
    if len(debug_img_list) == len(train_img_list):
        print("Number of debug files == number of train files - aborting")
        return
    if len(debug_img_list) == 0:
        print("No debug images found - aborting")
        return

    print("Formatting debug filenames")
    debug_img_list_formatted = []
    for debug_img in debug_img_list:
        #debug_img_trimmed = os.path.basename(re_debug.sub('', debug_img))
        debug_img_trimmed = os.path.basename(re_jpg.sub('png', debug_img))
        debug_img_list_formatted.append(debug_img_trimmed)

    pbar = tqdm(train_img_list)
    for train_img in pbar:
        train_filename = Path(train_img[0]) # could be number.png or number_index.png
        train_orig = train_img[1]
        train_trimmed = re_train.sub('', train_orig)

        found = False
        if train_trimmed in debug_img_list_formatted:
            found = True
        else:
            #print("\nREMOVING Train: %-15s " %(train_filename))
            pbar.set_description("Removed: %s" %train_filename)
            os.remove(train_filename)


if __name__ == "__main__":
    try:
        train_dir = sys.argv[1]
        debug_dir = sys.argv[2]
    except:
        print("Usage: %s faces_to_train_path debug_img_path" %(sys.argv[0]))

    print("Debug dir: %s" %debug_dir)
    print("Train dir: %s" %train_dir)
    debug_img_list = get_img_list(debug_dir)
    train_img_list = get_aligned_img_list(train_dir)
    remove_train_not_in_debug(debug_img_list, train_img_list)

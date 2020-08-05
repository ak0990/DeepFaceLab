import os
import sys
import argparse
#import Path_utils
from core import pathex
from pathlib import Path
import numpy as np
#from DFLIMG.DFLPNG import DFLPNG
from DFLIMG.DFLJPG import DFLJPG
from tqdm import tqdm
import shutil

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
            print ("%s failed to load" % (filepath.name) )
            continue

        img_list.append(str(filepath))

    return img_list

def get_aligned_img_list(input_path):
    #print ("Sort by original filename...")

    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

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

        d = a_img.get_dict()

        if d is None or d['source_filename'] is None:
            print ("%s - no embedded data found" % (filepath.name) )
            continue

        img_list.append( [str(filepath), d['source_filename']] )

    #print ("Sorting...")
    #img_list = sorted(img_list, key=operator.itemgetter(1))
    return img_list

def setup_dirs(source_dir, merge_dir):
    source_sample_dir = os.path.join(source_dir, "source_samples")
    merge_sample_dir = os.path.join(merge_dir, "merge_samples")

    try:
        shutil.rmtree(source_sample_dir, ignore_errors=True)
        shutil.rmtree(merge_sample_dir, ignore_errors=True)
        # Just in case a stupid file was created with the name
        os.remove(source_sample_dir)
        os.remove(merge_sample_dir)
    except:
        print("Error removing directories/files")

    try:
        os.makedirs(source_sample_dir)
        os.makedirs(merge_sample_dir)
        pass
    except:
        print("Error making directories")
        sys.exit(1)


def create_samples(source_dir, merge_dir, source_img_list, merge_img_list, sample_count):
    source_sample_dir = os.path.join(source_dir, "source_samples")
    merge_sample_dir = os.path.join(merge_dir, "merge_samples")

    faces_total = len(merge_img_list)
    faces_mod = int(faces_total / sample_count)
    pbar = tqdm(merge_img_list)
    for i, merge_img in enumerate(pbar):
        if (i % faces_mod != 0):
            continue

        merge_filename = Path(merge_img[0])
        merge_orig = merge_img[1]

        for source_img in source_img_list:
            source_filename = Path(source_img)
            if source_filename.name == merge_orig:
                pbar.set_description("Source: %-15s Merged: %s" %(source_filename.name, merge_filename.name))
                shutil.copy2(os.path.join(source_dir, source_filename.name), source_sample_dir)
                shutil.copy2(os.path.join(merge_dir, merge_filename.name), merge_sample_dir)


if __name__ == "__main__":
    source_dir = sys.argv[1]
    merge_dir = sys.argv[2]

    source_img_list = get_img_list(source_dir)
    merge_img_list = get_aligned_img_list(merge_dir)
    setup_dirs(source_dir, merge_dir)
    create_samples(source_dir, merge_dir, source_img_list, merge_img_list, 50)

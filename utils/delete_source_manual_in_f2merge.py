import os
import sys
import re
import argparse
#import Path_utils
from core import pathex
from pathlib import Path
from tqdm import tqdm
import interact.interact
from DFLPNG import DFLPNG
from DFLJPG import DFLJPG

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

def delete_imgs(source_dir, f2merge_img_list):
    total = len(f2merge_img_list)

    i = 0
    removed = 0
    pbar = tqdm(f2merge_img_list)
    for f2merge_img in pbar:
        f2merge_source = Path(f2merge_img[1])
        source_filename = Path(source_dir) / Path(f2merge_source.stem + f2merge_source.suffix)
        pbar.set_description("Removed: %s" %source_filename)
        try:
            os.remove(source_filename)
        except:
            pass
        removed += 1

        i += 1
    print("Removed total files:   %s" %(removed))
    #print("Remaining total files: %s" %(total-removed))


if __name__ == "__main__":
    try:
        source_dir = sys.argv[1]
        f2merge_dir = sys.argv[2]
    except:
        print("Usage: %s source_dir f2merge_dir " %(sys.argv[0]))

    #source_img_list = get_img_list(source_dir)
    print("Source Dir: %s" %source_dir)
    print("f2merge Dir: %s" %f2merge_dir)
    f2merge_img_list = get_aligned_img_list(f2merge_dir)
    delete_imgs(source_dir, f2merge_img_list)

import os
import sys
import argparse
#import Path_utils
from core import pathex
import os_utils
from pathlib import Path
import numpy as np
from DFLPNG import DFLPNG
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

        if filepath.suffix != '.png':
            print ("%s is not a png file required for sort_by_origname" % (filepath.name) )
            continue

        img_list.append(str(filepath))

    return img_list

def get_aligned_img_list(input_path):
    #print ("Sort by original filename...")

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

        if d is None or d['source_filename'] is None:
            print ("%s - no embedded data found required for sort_by_origname" % (filepath.name) )
            continue

        img_list.append( [str(filepath), d['source_filename']] )

    #print ("Sorting...")
    #img_list = sorted(img_list, key=operator.itemgetter(1))
    return img_list

def print_matches(source_img_list, merge_img_list):
    for merge_img in merge_img_list:
        merge_filename = Path(merge_img[0])
        merge_orig = merge_img[1]

        for source_img in source_img_list:
            source_filename = Path(source_img)
            if source_filename.name == merge_orig:
                print("Source: %-15s Merged: %s" %(source_filename.name, merge_filename.name))


        #dst = input_path / ('%.5d_%s' % (i, src.name ))
        #try:
        #    src.rename (dst)
        #except:
        #    print ('fail to rename %s' % (src.name) )

    #for i in tqdm( range(0,len(img_list)) , desc="Renaming" ):
    #    src = Path (img_list[i][0])

    #    src = input_path / ('%.5d_%s' % (i, src.name))
    #    dst = input_path / ('%.5d%s' % (i, src.suffix))
        #try:
        #    src.rename (dst)
        #except:
        #    print ('fail to rename %s' % (src.name) )

if __name__ == "__main__":
    source_dir = sys.argv[1]
    merge_dir = sys.argv[2]

    source_img_list = get_img_list(source_dir)
    merge_img_list = get_aligned_img_list(merge_dir)
    print_matches(source_img_list, merge_img_list)

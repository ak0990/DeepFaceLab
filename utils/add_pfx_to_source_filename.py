import os
import sys
import re
import argparse
from core import pathex
from pathlib import Path
#from DFLIMG.DFLJPG import DFLJPG
from DFLIMG import DFLIMG
from tqdm import tqdm
from pprint import pprint

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


def update_filenames(input_path, new_pfx):
    img_list = []
    for filepath in tqdm(pathex.get_image_paths(input_path)):
        filepath = Path(filepath)

        if filepath.suffix != '.png' and filepath.suffix != '.jpg':
            print ("%s is not a image file" % (filepath.name) )
            continue

        if filepath.suffix == '.png':
            a_img = DFLIMG.load(filepath)
            if a_img is None:
                print ("%s failed to load - only JPG supported" % (filepath.name) )
                continue
        elif filepath.suffix == '.jpg':
            a_img = DFLIMG.load(filepath)
            if a_img is None:
                print ("%s failed to load" % (filepath.name) )
                continue

        d = a_img.get_dict()

        if d is None or d['source_filename'] is None:
            print ("%s - no embedded data found required for sort_by_origname" % (filepath.name) )
            continue

        new_name = "%s_%s" %(new_pfx, d['source_filename'])
        d['source_filename'] = new_name
        a_img.set_dict(d)
        a_img.save()

    return


def usage():
    print("Usage: %s metadata_img_path" %(sys.argv[0]))
    sys.exit(1)


if __name__ == "__main__":
    try:
        metadata_img_dir = sys.argv[1]
    except:
        usage()

    new_pfx = input('Enter a prefix: ')
    if len(new_pfx) < 1:
        print("No prefix set")
    update_filenames(metadata_img_dir, new_pfx)

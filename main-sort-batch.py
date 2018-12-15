import os
import sys
import time
import argparse
import multiprocessing
import subprocess
#from utils import Path_utils
from core import pathex
from utils import os_utils
from pathlib import Path
from pprint import pprint
import pickle
import models
import shutil
import json

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    raise Exception("This program requires at least Python 3.6")

class fixPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))



def sort_by_img_path(input_path, sort_by, batch=None):
    pass

def sort_by_img_files(input_path, sort_by, batch=None):
    img_paths = pathex.get_image_paths(input_path)
    img_path_len = len(img_paths)
    if batch and batch > 0:
        print("Sorting in batches of %s" %batch)
        sorted_list = []
        for x in range(0, img_list_len-1, batch):
            end_slice = x + batch
            tmp_list = img_paths[x:end_slice]
            #sorted_list = sorted_list + _sort_by_hist_batch(tmp_list, desc="Sorting %s-%s" %(x, end_slice))
            sorted_list = sorted_list + Sorter.HistSsimSubprocessor(tmp_list).run()
        img_list = sorted_list
    else:
        img_list = Sorter.HistSsimSubprocessor(img_paths).run()


def process_sort(arguments):
    os_utils.set_process_lowest_prio()
    from mainscripts import Sorter
    #Sorter.main (input_path=arguments.input_dir, sort_by_method=arguments.sort_by_method, batch=arguments.batch_size)
    #Sorter.main (input_path=arguments.input_dir, sort_by_method=arguments.sort_by_method)

    input_path = arguments.input_dir
    sort_by_method = arguments.sort_by_method
    batch=arguements.batch_size

    img_list, trash_img_list = Sorter.whatever
    input_path = Path(input_path)
    sort_by_method = sort_by_method.lower()

    io.log_info ("Running sort tool.\r\n")

    img_list = []
    trash_img_list = []
    if sort_by_method == 'blur':            img_list, trash_img_list = sort_by_blur (input_path)
    elif sort_by_method == 'face':          img_list, trash_img_list = sort_by_face (input_path) #no
    elif sort_by_method == 'face-dissim':   img_list, trash_img_list = sort_by_face_dissim (input_path) #no
    elif sort_by_method == 'face-yaw':      img_list, trash_img_list = sort_by_face_yaw (input_path) #no
    elif sort_by_method == 'face-pitch':    img_list, trash_img_list = sort_by_face_pitch (input_path) #no
    elif sort_by_method == 'hist':          img_list = sort_by_hist (input_path)
    elif sort_by_method == 'hist-dissim':   img_list, trash_img_list = sort_by_hist_dissim (input_path)
    elif sort_by_method == 'brightness':    img_list = sort_by_brightness (input_path) #no
    elif sort_by_method == 'hue':           img_list = sort_by_hue (input_path) #no
    elif sort_by_method == 'black':         img_list = sort_by_black (input_path) #no
    elif sort_by_method == 'origname':      img_list, trash_img_list = sort_by_origname (input_path) #no
    elif sort_by_method == 'oneface':       img_list, trash_img_list = sort_by_oneface_in_image (input_path) #no
    elif sort_by_method == 'vggface':       img_list, trash_img_list = sort_by_vggface (input_path) #no
    elif sort_by_method == 'final':         img_list, trash_img_list = sort_final (input_path)
    elif sort_by_method == 'final-no-blur': img_list, trash_img_list = sort_final (input_path, include_by_blur=False)


def main():
    multiprocessing.set_start_method("spawn")
    if sys.argv[1] != 'sort':
        print("This script only works for sorting")
        sys.exit(1)

    p = subparsers.add_parser( "sort", help="Sort faces in a directory.")
    p.add_argument('--input-dir', required=True, action=fixPathAction, dest="input_dir", help="Input directory. A directory containing the files you wish to process.")
    p.add_argument('--by',
        required=True,
        dest="sort_by_method",
        choices=("blur",
            "face",
            "face-dissim",
            "face-yaw",
            "face-pitch",
            "hist",
            "hist-dissim",
            "brightness",
            "hue",
            "black",
            "origname",
            "oneface",
            "final",
            "final-no-blur",
            "vggface",
            "test"),
        help="Method of sorting. 'origname' sort by original filename to recover original sequence." )
    p.add_argument('--batch', required=False, type=int, dest="batch_size", help="Sort in batches of the designated batch-size. Greatly increases overall sort time of large filesets at the expense of only comparing images within a batch-size set rather than the entire image set")
    p.set_defaults(func=process_sort)

if __name__ == "__main__":
    main()

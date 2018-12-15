import os
import sys
import argparse
#from utils import Path_utils
from core import pathex
from utils import os_utils
from pathlib import Path
from tqdm import tqdm

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception("This program requires at least Python 3.2")


def get_img_list(input_path):
    img_list = []
    #for filepath in tqdm(pathex.get_image_paths(input_path)):
    for dirpath, dirnames, filenames in os.walk(input_path):
        paths = [Path(filename) for filename in filenames]
        stems = [filename.stem for filename in paths]
        for filename in sorted(stems, key=int):
            img_list.append(filename)

    return img_list


def rename_files(soure_dir, img_list):
    for i, filename in tqdm(enumerate(img_list)):
        oldname = os.path.join(source_dir, "%s.png" %filename)
        newname = os.path.join(source_dir, "%0.5d_%s.png" %(i, filename))
        #print("rename %s to %s" %(oldname, newname))
        os.rename(oldname, newname)
    for i, filename in tqdm(enumerate(img_list)):
        oldname = os.path.join(source_dir, "%0.5d_%s.png" %(i, filename))
        newname = os.path.join(source_dir, "%0.5d.png" %i)
        #print("rename %s to %s" %(oldname, newname))
        os.rename(oldname, newname)


if __name__ == "__main__":
    source_dir = sys.argv[1]

    source_img_list = get_img_list(source_dir)
    rename_files(source_dir, source_img_list)

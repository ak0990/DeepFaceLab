import os
import sys
import re
import argparse
#import Path_utils
from core import pathex
from pathlib import Path
#from DFLIMG.DFLPNG import DFLPNG
from DFLIMG.DFLJPG import DFLJPG
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

        d = a_img.get_dict()

        if d is None or d['source_filename'] is None:
            print ("%s - no embedded data found required for sort_by_origname" % (filepath.name) )
            continue

        img_list.append( [str(filepath), d['source_filename']] )

    return img_list

def remove_metadata_not_in_plain(plain_img_list, metadata_img_list):
    re_plain = re.compile(r'_plain')
    re_metadata = re.compile(r'_[0-9]+')
    re_jpg = re.compile(r'jpg')

    #print("Count plain: %s -- Count metadata: %s" %(len(plain_img_list), len(metadata_img_list)))
    if len(plain_img_list) == len(metadata_img_list):
        print("Number of plain files == number of metadata files - aborting")
        return
    if len(plain_img_list) == 0:
        print("No plain images found - aborting")
        return

    print("Formatting plain filenames")
    plain_img_list_formatted = []
    for plain_img in plain_img_list:
        #plain_img_trimmed = os.path.basename(re_plain.sub('', plain_img))
        plain_img_trimmed = os.path.basename(re_jpg.sub('png', plain_img))
        plain_img_list_formatted.append(plain_img_trimmed)

    pbar = tqdm(metadata_img_list)
    for metadata_img in pbar:
        metadata_filename = Path(metadata_img[0]) # could be number.png or number_index.png
        metadata_orig = metadata_img[1]
        metadata_trimmed = re_metadata.sub('', metadata_orig)

        found = False
        if metadata_trimmed in plain_img_list_formatted:
            found = True
        else:
            #print("\nREMOVING metadata: %-15s " %(metadata_filename))
            pbar.set_description("Removed: %s" %metadata_filename)
            os.remove(metadata_filename)

def remove_plain_not_in_metadata(plain_img_list, metadata_img_list):
    re_plain = re.compile(r'_plain')
    re_metadata = re.compile(r'_[0-9]+\.')
    re_source_name_format = re.compile(r'[0-9]+\.')
    re_metadata_name_format = re.compile(r'[0-9]+_*[0-9]\.')

    print("Validating filenames")
    validation = True
    for metadata_img in metadata_img_list:
        metadata_source_filename = metadata_img[1]
        metadata_filename = metadata_img[0]
        if not re_source_name_format.search(metadata_source_filename):
            print("Bad source name format - skipping: %s" %metadata_source_filename)
            validation = False
        if not re_metadata_name_format.search(metadata_filename):
            print("Bad metadata name format - skipping: %s" %metadata_filename)
            validation = False

    if validation == False:
        print("\nBad filename(s) found - exiting")
        return

    print("Formatting metadata filenames")
    metadata_img_list_formatted = []
    for metadata_img in metadata_img_list:
        metadata_filename = Path(metadata_img[0])
        metadata_orig = metadata_img[1]
        metadata_trimmed = re_metadata.sub('.', metadata_orig)
        metadata_trimmed = Path(metadata_trimmed).stem
        metadata_img_list_formatted.append(metadata_trimmed)

    print("Searching for files to remove")
    pbar = tqdm(plain_img_list)
    for plain_img in pbar:
        found = False
        plain_img_trimmed = os.path.basename(re_plain.sub('', plain_img))
        plain_img_trimmed = Path(plain_img_trimmed).stem
        if plain_img_trimmed in metadata_img_list_formatted:
                found = True
        else:
            #print("NOMATCH plain: %-40s # metadata: %-40s # Orig: %s" %(plain_img_trimmed, metadata_trimmed, metadata_orig))
            #print("REMOVING plain: %-15s " %(plain_img))
            pbar.set_description("Removed: %s" %plain_img)
            os.remove(plain_img)

def usage():
    print("Usage: %s metadata_img_path plain_img_path delete_target" %(sys.argv[0]))
    print("  delete_target:")
    print("         metadata) delete metadata images not in plain images")
    print("         plain   ) delete plain images not in metadata images")
    sys.exit(1)


if __name__ == "__main__":
    pprint(sys.argv)
    try:
        metadata_img_dir = sys.argv[1]
        plain_img_dir = sys.argv[2]
        delete_target = sys.argv[3]
    except:
            usage()

    print("plain dir: %s" %plain_img_dir)
    print("metadata dir: %s" %metadata_img_dir)

    plain_img_list = get_img_list(plain_img_dir)
    metadata_img_list = get_aligned_img_list(metadata_img_dir)

    if delete_target == 'metadata':
        print("Deleting metadata images not in plain images dir")
        remove_metadata_not_in_plain(plain_img_list, metadata_img_list)
    elif delete_target == 'plain':
        print("Deleting plain images not in metadata images dir")
        remove_plain_not_in_metadata(plain_img_list, metadata_img_list)
    else:
        usage()

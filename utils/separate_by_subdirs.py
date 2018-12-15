import os
import sys
from pathlib import Path
#from utils import Path_utils
from core import pathex
from tqdm import tqdm

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception("This program requires at least Python 3.2")

def separate(input_path, batch):

    print ("Separating faces into subdirs")

    batch = int(batch)
    img_list = []
    for x in tqdm(pathex.get_image_paths(input_path), desc="Loading"):
        img_list.append(Path(x))
        #img = cv2.imread(x)
        #img_list.append ([x, cv2.calcHist([img], [0], None, [256], [0, 256]),
        #                     cv2.calcHist([img], [1], None, [256], [0, 256]),
        #                     cv2.calcHist([img], [2], None, [256], [0, 256])
        #                 ])

    img_list_len = len(img_list)
    counter = 1
    if batch and batch > 0:
        print("Separating in batches of: %s" %batch)
        #sorted_list = []
        for x in range(0, img_list_len-1, batch):
            end_slice = x + batch
            tmp_list = img_list[x:end_slice]
            #sorted_list = sorted_list + _sort_by_hist_batch(tmp_list, desc="Sorting %s-%s" %(x, end_slice))
            new_path = os.path.join(input_path, "temp_%s" %counter)

            try:
                os.mkdir(new_path)
            except FileExistsError:
                pass
            for img_file in tqdm(tmp_list):
                new_file = os.path.join(new_path, os.path.basename(img_file))
                #print("old: %s    new: %s" %(img_file, new_file))
                os.rename(img_file, new_file)
            counter += 1


    return img_list


if __name__ == "__main__":
    try:
        faces_dir = sys.argv[1]
        batch = sys.argv[2]
    except:
        print("Usage: %s faces_dir batch_size" %(sys.argv[0]))

    separate(faces_dir, batch)

import json
import pickle
import os
import re
import shlex
import shutil
import subprocess
import sys
from pprint import pprint
from pathlib import Path
from core import pathex
import time
import yaml
from tqdm import tqdm


class Menu(object):
    """ Display menu options, execute choices """

    def __init__(self, configs):
        self.configs = configs
        self.menu_name = 'main'


    def menu_options(self, menu_name):
        """ Return a list of tuples describing options in the format of:
            (function_name, description)
            Order is important since it used both to 
            display the menu and to execute the chosen command
        """
        # Options is a tuple of 2 or 3 elements
        # (function_to_call, display_name, is_submenu?)
        if menu_name == 'main':
            self.options = [
            #    "Source Images: %s" %os.environ['source_img_path',
                ("setup_dirs",                         "Setup directories"),
                ("extract_frames",                     "Extract frames from video"),
                ("detect_faces",                       "Detect Faces"),
                ("f2merge_menu",                       "Faces to Merge Menu", True),
                ("f2train_menu",                       "Faces to Train Menu", True),
                ("xseg_menu",                          "XSeg Menu", True),
                ("train_menu",                         "Train Menu", True),
                ("util_menu",                          "Utils/Config Menu", True),
                ("merge",                              "Merge"),
                ("video",                              "Video"),        
            ]
        if menu_name == 'f2merge':
            self.options = [
                ("f2merge_separate_by_subdirs",        "Separate by subdirs"),
                ("f2merge_sort_histogram",             "Sort by histogram"),
                #("f2merge_sort_brightness",            "      - brightness"),
                #("f2merge_sort_absdiff",               "      - absolute diff"),
                #   MANUAL delete bad training faces
                ("f2merge_restore_orig_filenames",     "Restore original filenames"),
                ("f2merge_unseparate_by_subdirs",      "Un-Separate by subdirs"),
                ("pack_f2merge",                       "f2merge faceset Pack"),
                ("unpack_f2merge",                     "f2merge faceset Unpack"),
                ("prefix_f2merge_name",                "Add prefix to f2merge source filenames"),
            ]
        if menu_name == 'f2train':
            self.options = [
                ("copy_f2merge_to_f2train",            "Copy f2merge to f2train"),
                ("f2train_separate_by_subdirs",        "Separate by subdirs"),
                ("f2train_sort_black_pixels",          "Sort by black pixels"),
                ("f2train_sort_brightness",            "      - brightness"),
                ("f2train_sort_absdiff",               "      - absolute diff (very slow)"),
                ("f2train_sort_rect_size",             "      - rect size"),
                ("f2train_sort_histogram",             "      - histogram"),
                #   MANAUL delete bad training faces
                ("f2train_restore_orig_filenames",     "Restore original filenames"),
                ("f2train_unseparate_by_subdirs",      "Un-Separate by subdirs"),
                ("f2train_decimate",                   "Decimate"),
                ("delete_debug_not_in_train",          "Delete debug not in train"),
                #   MANAUL delete bad debug matches
                ("delete_train_not_in_debug",          "Delete train not in debug"),
                ("f2train_metadata_save",              "Save metadata   - SRC ONLY"),
                #("f2train_enhance",                    "AI Enhance      - SRC ONLY"),
                ("f2train_metadata_restore",           "Restore metdata - SRC ONLY"),
                ("pack_f2train",                       "f2train Pack"),
                ("unpack_f2train",                     "f2train Unpack"),
                ("prefix_f2train_name",                "Add prefix to f2train source filenames"),
            ]
        if menu_name == 'xseg':
            self.options = [
                ("copy_pretrained_xseg_model",         "Copy Pre-trained XSeg model"),
                ("xseg_apply_f2train_dst",             "Apply XSeg Model to f2train dest"),
                ("xseg_edit",                          "Edit XSeg Mask on f2train"),
                ("xseg_train",                         "Train XSeg Model"),
                ("xseg_apply_f2train_dst",             "Apply XSeg Model to f2train dest (again)"),
                ("xseg_apply_f2train_src",             "Apply XSeg Model to f2train source"),
                #("xseg_apply_f2merge",                 "Apply XSeg Model to f2merge - Overwrites face detect masks"),
                ("xseg_fetch",                         "Fetch f2train images that contain XSeg Polys"),
                ("xseg_remove_mask_f2train",           "Remove XSeg Trained Mask from f2train"),
                ("xseg_remove_polys_f2train",          "Remove XSeg Edited Polys from f2train"),
                ("xseg_remove_mask_f2merged",          "Remove XSeg Trained Mask from f2merged"),
                ("xseg_remove_polys_f2merged",         "Remove XSeg Edited Polys from f2merged"),
            ]
        if menu_name == 'train':
            self.options = [
                ("copy_pretrained_model",              "Copy Pre-trained src model"),
                ("train_sequenced",                    "Train Sequenced"),
                ("train_delayed",                      "Train after delay"),
                ("train_basic",                        "Train Basic or New"),
                ("pretrain_model",                     "Pre-Train SRC Model"),
            ]
        if menu_name == 'utils':
            self.options = [
                ("create_samples",                     "Create Samples"),
                ("merge_samples",                      "Merge Samples"),
                ("change_fps",                         "Change video FPS to 25"),
                ("set_model_label",                    "Set model label"),
                ("zip_all_faces",                      "Zip all faces"),
                ("unzip_all_faces",                    "Unzip all faces"),
                #("xseg_apply_f2merge_samples",         "Apply XSeg Model to f2merge samples"),
            ]
        if menu_name == 'model_type':
            self.options = [
            ]
        if menu_name == 'face_detector':
            self.options = [
            ]

    
    
    def display_menu(self):
        configs = self.configs
        self.menu_options(self.menu_name)
        
        header = [
            "",
            "-------------------------------------------- Main Menu ---------------------------------------------------",
            "%-15s: %-60s | %-15s: %s" %('Train Source', configs['f2train_src'], 'Model Type', configs['model_type']),
            "%-15s: %-60s | %-15s: %s" %('Train Dest', configs['f2train_dst'], 'Model Label', configs['model_label']),
            "%-15s: %-60s | %-15s: %s" %('Input Video', configs['input_video'], 'FPS', configs['video_info']['fps']),
            "%-15s: %-60s | %-15s: %s" %('Menu', self.menu_name, 'Source', configs['f2train_src_name']),
            "----------------------------------------------------------------------------------------------------------",
        ]
    
        for line in header:
            print(line)
        for i, option in enumerate(self.options):
            if len(option) > 2 and option[2] == True:
                menu_char = '\u251c' + '\u2500'
            else:
                menu_char = '\u2502'
            print("%2s. %s %s" %(i, menu_char, option[1]))
        footer = []
        if self.menu_name != 'main':
            footer.append("%2s. %s" %('M', "Main Menu"))
        footer.append("%2s. %s" %('Q', "Quit"))
        for line in footer:
            print(line)

        # Add blank lines to clear the screen
        used_lines = len(header) + len(self.options) + len(footer)
        blank_lines = 29 - used_lines
        print('\n' * blank_lines)
    

def f2merge_menu(configs):
    configs['menu'].menu_name = 'f2merge'
def f2train_menu(configs):
    configs['menu'].menu_name = 'f2train'
def util_menu(configs):
    configs['menu'].menu_name = 'utils'
def model_menu(configs):
    configs['menu'].menu_name = 'model_type'
def xseg_menu(configs):
    configs['menu'].menu_name = 'xseg'
def train_menu(configs):
    configs['menu'].menu_name = 'train'
def detector_menu(configs):
    configs['menu'].menu_name = 'face_detector'


def execute_option(configs, options, choice):
    try:
        choice = int(choice)
    except:
        choice = choice.lower()
    
    if isinstance(choice, int) and choice >= 0 and choice < len(options):        
        function_to_call = options[choice][0] 
        print(function_to_call)  
        # call the function
        globals()[function_to_call](configs)
    elif choice == 'm':
        print("change model type")
        configs['menu'].menu_name = 'main'
    elif choice == 'd':
        print("change detector type")
    elif choice == 't':
        print("Train")
        function_to_call = "train_sequenced"
        globals()[function_to_call](configs)
    elif choice == 'q':
        sys.exit(0)
    else:
        print("Bad choice... try again")
        return


def get_configs():
    config_file = os.path.join(os.getcwd(), 'config.yaml')
    try:
        with open(config_file, 'r') as stream:
            local_configs = yaml.load(stream, Loader=yaml.SafeLoader)
    except:
        print("Error reading config file: %s" %config_file)
        sys.exit(1)

    global_config_file = local_configs['global_config_file']
    try:
        with open(global_config_file, 'r') as stream:
            global_configs = yaml.load(stream, Loader=yaml.SafeLoader)
    except:
        print("Error reading config file: %s" %config_file)
        sys.exit(1)
    
    # Merge global and local - local wins on conflict
    configs = {**global_configs, **local_configs}

    required_configs = [
        'basepath',
        'subdirs_batch',
        'model_type',
        'face_detector',
    ]
    for config in required_configs:
        if config not in configs:
            print("Missing mandatory config: %s" %config)
            sys.exit(1)
    # Source can either be a full path, or a basepath+name+trainpath
    # Broken into pieces makes it easier to extract the name for the output label
    if 'f2train_src_base' in configs and 'f2train_src_name' in configs:
        configs['f2train_src'] = os.path.join(
            configs['f2train_src_base'],
            configs['f2train_src_name'],
            '2_faces',
            'faces_to_train'
        )
        configs['model_label'] = configs['f2train_src_name']
    else:
        print("Failed to find source image configs")
        sys.exit(1)
    

    configs['config_file'] = config_file
    configs['workspace'] = os.getcwd()
    configs['title'] = os.path.split(configs['workspace'])[1]
    configs['bindir'] = os.path.join(configs['basepath'], '_internal')
    configs['dfl_root'] = os.path.join(configs['bindir'], 'DeepFaceLab')
    configs['dfl_main'] = os.path.join(configs['dfl_root'], 'main.py')
    configs['python_path'] = os.path.join(configs['bindir'], 'python-3.6.8')
    configs['python_exe'] = os.path.join(configs['python_path'], 'python.exe')

    configs['1_source'] = os.path.join(configs['workspace'], '1_source')
    configs['2_faces'] = os.path.join(configs['workspace'], '2_faces')
    configs['debug_dir'] = os.path.join(configs['2_faces'], 'faces_to_merge_debug')
    configs['f2merge'] = os.path.join(configs['2_faces'], 'faces_to_merge')
    configs['f2train_dst'] = os.path.join(configs['2_faces'], 'faces_to_train')
    configs['3_model'] = os.path.join(configs['workspace'], '3_model')
    configs['4_merged'] = os.path.join(configs['workspace'], '4_merged')
    configs['5_video'] = os.path.join(configs['workspace'], '5_video')
    #configs['train_seq_json'] = os.path.join(configs['workspace'], 'training_sequence.json')

    configs['input_video'] = os.path.join(os.getcwd(), configs['title'] + '.mp4')

    configs['video_info'] = get_video_info(configs)
    frames, seconds = configs['video_info']['r_frame_rate'].split('/')
    fps = "%.2f" %(float(frames) / float(seconds))
    configs['video_info']['fps'] = fps
    return configs


def get_model_data(model_path, model_type):
    model_data_path = Path("%s\\%s_data.dat" %(model_path, model_type))

    if not os.path.exists(model_data_path):
        print("Model file does not exist: %s" %model_data_path)
        return None

    model_data = pickle.loads( model_data_path.read_bytes() )
    return model_data


def set_model_data(model_path, model_type, model_data):
    model_file = os.path.join(model_path, "%s_data.dat" %model_type)

    with open(model_file, 'wb') as f:
        f.write( pickle.dumps(model_data) )

    return


def get_video_info(configs):
    """ Return a dict of video info from the first video stream of the input file """

    ffprobe_path = os.path.join(configs['bindir'], 'ffmpeg', 'ffprobe.exe')
    cmd = '%s -v error -select_streams v -show_entries stream -of json -i %s' %(ffprobe_path, configs['input_video'])
    p_cmd = subprocess.Popen(   
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    stdout, stderr = p_cmd.communicate()
    try:
        video_info = json.loads(stdout)
    except:
        print("Error loading json from video streams")
        return {"r_frame_rate": "999999/1"}
    return video_info['streams'][0]


def shell_command(cmd):
    print("--------------------------------------------------------")
    print("Executing command:")
    print(cmd)
    #print(subprocess.list2cmdline(cmd))
    print("--------------------------------------------------------")
    #with subprocess.Popen(cmd,
    #                    stdout=subprocess.PIPE, 
    #                    stderr=subprocess.STDOUT,
    #                    universal_newlines=True) as pcmd:
    #    print("Output:")
    #    for line in pcmd.stdout:
    #        print(line, end='')
    with subprocess.Popen(   
        cmd,
        env=os.environ,
        stdout=None,
        stderr=subprocess.STDOUT,
        universal_newlines=True) as pcmd:
        pass

    return pcmd.returncode


def setup_dirs(configs):
    try:
        basedir = configs['workspace']
        os.makedirs(os.path.join(basedir, '1_source'),                      exist_ok=True)
        os.makedirs(os.path.join(basedir, '2_faces'),                       exist_ok=True)
        os.makedirs(os.path.join(basedir, '2_faces', 'faces_to_merge'),     exist_ok=True)
        os.makedirs(os.path.join(basedir, '2_faces', 'faces_to_train'), exist_ok=True)
        os.makedirs(os.path.join(basedir, '3_model'),                       exist_ok=True)
        os.makedirs(os.path.join(basedir, '4_merged'),                      exist_ok=True)
        os.makedirs(os.path.join(basedir, '5_video'),                       exist_ok=True)
    except:
        print("ERROR in setupdirs")

    #recursive_copy(configs['f2train_src_orig'], configs['f2train_src'])


def set_model_label(configs):
    # Find existing model names, if any
    choice = input("Model Label: ")
    configs['model_label'] = choice
    return configs


def change_fps(configs):
    ffmpeg_path = os.path.join(configs['bindir'], 'ffmpeg', 'ffmpeg.exe')
    cmdstr = '%s -y -threads 11 -i "%s" -r 25 "video_25fps.mp4"' %(
        ffmpeg_path,
        configs['input_video'],
    )
    rc = shell_command(cmdstr)


def extract_frames(configs):
    ffmpeg_path = os.path.join(configs['bindir'], 'ffmpeg', 'ffmpeg.exe')
    source_img_path = configs['1_source']
    source_img_output = os.path.join(source_img_path, configs['title'] + r'_%5d.png')
    #cmdstr = '%s -threads 11 -i "%s" "%s"' %(
    #    ffmpeg_path,
    #    configs['input_video'],
    #    source_img_output
    #)
    cmdstr = '%s -threads 0 -i "%s" "%s"' %(
        ffmpeg_path,
        configs['input_video'],
        source_img_output
    )
    rc = shell_command(cmdstr)
    

def detect_faces(configs):
    #cmd = '%s %s extract --input-dir %s --output-dir %s --detector %s --debug-dir %s' %(
    cmd = '%s %s extract --input-dir %s --output-dir %s --detector %s --output-debug' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['1_source'],
        configs['f2merge'],
        configs['face_detector'],
    )
    rc = shell_command(cmd)


def f2merge_separate_by_subdirs(configs):
    cmd = '%s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'separate_by_subdirs.py'),
        configs['f2merge'],
        configs['subdirs_batch'],
    )
    rc = shell_command(cmd)


def f2train_separate_by_subdirs(configs):
    cmd = '%s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'separate_by_subdirs.py'),
        configs['f2train_dst'],
        configs['subdirs_batch'],
    )
    rc = shell_command(cmd)


def f2merge_unseparate_by_subdirs(configs):
    unseparate_by_subdirs(configs, configs['f2merge'])


def f2train_unseparate_by_subdirs(configs):
    unseparate_by_subdirs(configs, configs['f2train_dst'])


def unseparate_by_subdirs(configs, basedir):
    
    for root, dirs, files in os.walk(basedir):
        for dirname in dirs:
            if re.search(r'^temp_[0-9].*', dirname) is None:
                continue
            recursive_copy(os.path.join(root, dirname), basedir, delete=True)
            try:
                # Only works if directory is empty, so no need to do extra checks
                os.rmdir(os.path.join(root, dirname))
            except OSError:
                pass
            

def sort(configs, basedir, sortby):
    cmd = '%s %s sort --input-dir %s --by %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        basedir,
        sortby
    )
    rc = shell_command(cmd)
    # Loop through each subdir
    for root, dirs, files in os.walk(basedir):
        for subdir in dirs:
            cmd = '%s %s sort --input-dir %s --by %s' %(
                configs['python_exe'],
                configs['dfl_main'],
                os.path.join(root, subdir),
                sortby
            )
            rc = shell_command(cmd)

def f2merge_sort_histogram(configs):
    sort(configs, configs['f2merge'], 'hist')


def f2merge_sort_brightness(configs):
    sort(configs, configs['f2merge'], 'brightness')


def f2merge_sort_absdiff(configs):
    sort(configs, configs['f2merge'], 'absdiff')


def delete_debug_not_in_f2merge(configs):
    metadata_img_dir = configs['f2merge']
    plain_img_dir = configs['debug_dir']
    delete_target = 'plain'
    cmd = '%s %s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'delete_dir1_files_not_in_dir2.py'),
        metadata_img_dir,
        plain_img_dir,
        delete_target
    )
    rc = shell_command(cmd)


def copy_source_to_manual(configs):
    # copy files from sourcepath to source/manual
    pass


def delete_f2merge_not_in_debug(configs):
    metadata_img_dir = configs['f2merge']
    plain_img_dir = configs['debug_dir']
    delete_target = 'metadata'
    cmd = '%s %s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'delete_dir1_files_not_in_dir2.py'),
        metadata_img_dir,
        plain_img_dir,
        delete_target
    )
    rc = shell_command(cmd)


def f2merge_restore_orig_filenames(configs):
    restore_orig_filenames(configs, configs['f2merge'])


def f2train_restore_orig_filenames(configs):
    restore_orig_filenames(configs, configs['f2train_dst'])


def restore_orig_filenames(configs, basedir):
    cmd = '%s %s util --input-dir %s --recover-original-aligned-filename' %(
        configs['python_exe'],
        configs['dfl_main'],
        basedir,
    )
    rc = shell_command(cmd)
    # Loop through each batched subdir
    for root, dirs, files in os.walk(basedir):
        for subdir in dirs:
            cmd = '%s %s util --input-dir %s --recover-original-aligned-filename' %(
                configs['python_exe'],
                configs['dfl_main'],
                os.path.join(root, subdir)
            )
            rc = shell_command(cmd)


def delete_source_manual_in_f2merge(configs):
    cmd = '%s %s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'delete_source_manual_in_f2merge.py'),
        os.path.join(configs['1_source'], 'manual'),
        configs['f2merge']
    )
    rc = shell_command(cmd)


def detect_faces_manual(configs):
    cmd = '%s %s extract --input-dir %s --output-dir %s --detector %s --debug-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        os.path.join(configs['1_source'], 'manual'),
        os.path.join(configs['2_faces'], 'manual'),
        'manual',
        os.path.join(configs['debug_dir'], 'manual')
    )
    rc = shell_command(cmd)


def recursive_copy(src, dst, delete=False):
    src_base = os.path.basename(src)
    if not os.path.exists(dst):
        print("Making directory: %s" %dst)
        os.makedirs(dst, exist_ok=True)
    pbar = tqdm(os.listdir(src), desc=src, ascii=True)
    for filename in pbar:
        dst_path = os.path.join(dst, filename)
        #print("   src=%-40s dst=%-40s filename=%s" %(src, dst, filename))
        src_path = os.path.join(src, filename)
        if os.path.isdir(src_path):
            recursive_copy(src_path, dst_path)
        else:
            if not os.path.isfile(dst_path):
                #print("%s to %s" %(src_path, dst_path))
                shutil.copy2(src_path, dst_path)
                if delete:
                    os.remove(src_path)
            

def copy_f2merge_to_f2train(configs):
    recursive_copy(configs['f2merge'], configs['f2train_dst'])
    #shutil.copytree(
    #    configs['f2merge'],
    #    configs['f2train_dst'],
    #)


def f2train_sort_black_pixels(configs):
    sort(configs, configs['f2train_dst'], 'black')


def f2train_sort_histogram(configs):
    sort(configs, configs['f2train_dst'], 'hist')


def f2train_sort_brightness(configs):
    sort(configs, configs['f2train_dst'], 'brightness')


def f2train_sort_absdiff(configs):
    sort(configs, configs['f2train_dst'], 'absdiff')


def f2train_sort_rect_size(configs):
    sort(configs, configs['f2train_dst'], 'face-source-rect-size')


def f2train_decimate(configs):
    cmd = '%s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'decimate.py'),
        configs['f2train_dst'],
        configs['decimate_target']
    )
    rc = shell_command(cmd)


def delete_debug_not_in_train(configs):
    metadata_img_dir = configs['f2train_dst']
    plain_img_dir = configs['debug_dir']
    delete_target = 'plain'
    cmd = '%s %s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'delete_dir1_files_not_in_dir2.py'),
        metadata_img_dir,
        plain_img_dir,
        delete_target
    )
    rc = shell_command(cmd)


def delete_train_not_in_debug(configs):
    metadata_img_dir = configs['f2train_dst']
    plain_img_dir = configs['debug_dir']
    delete_target = 'metadata'
    cmd = '%s %s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'delete_dir1_files_not_in_dir2.py'),
        metadata_img_dir,
        plain_img_dir,
        delete_target
    )
    rc = shell_command(cmd)


def xseg_edit(configs):
    cmd = '%s %s xseg editor --input-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def xseg_train(configs):
    cmd = '%s %s train --training-data-src-dir %s --training-data-dst-dir %s --model-dir %s --model %s --force-gpu-idxs 0' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_src'],
        configs['f2train_dst'],
        os.path.join(configs['3_model']),
        'XSeg',
    )
    rc = shell_command(cmd)


def xseg_apply_f2train_src(configs):
    cmd = '%s %s xseg apply --input-dir %s --model-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_src'],
        os.path.join(configs['3_model']),
    )
    rc = shell_command(cmd)


def xseg_apply_f2train_dst(configs):
    cmd = '%s %s xseg apply --input-dir %s --model-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
        os.path.join(configs['3_model']),
    )
    rc = shell_command(cmd)


def xseg_apply_f2merge(configs):
    cmd = '%s %s xseg apply --input-dir %s --model-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2merge'],
        os.path.join(configs['3_model']),
    )
    rc = shell_command(cmd)


def xseg_fetch(configs):
    cmd = '%s %s xseg fetch --input-dir %s ' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def xseg_remove_mask_f2train(configs):
    cmd = '%s %s xseg remove --input-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def xseg_remove_polys_f2train(configs):
    cmd = '%s %s xseg remove_labels --input-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)

def xseg_remove_mask_f2merge(configs):
    cmd = '%s %s xseg remove --input-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2merge'],
    )
    rc = shell_command(cmd)


def xseg_remove_polys_f2merge(configs):
    cmd = '%s %s xseg remove_labels --input-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2merge'],
    )
    rc = shell_command(cmd)


def pretrain_model(configs):
    cmd = '%s %s train --pretraining-data-dir %s --training-data-src-dir %s --training-data-dst-dir %s --model-dir %s --model %s --force-gpu-idxs 0' %(
        configs['python_exe'],
        configs['dfl_main'],
        os.path.join(configs['pretrain_src'], '2_faces', 'faces_to_train'),
        configs['f2train_src'],
        configs['f2train_dst'],
        os.path.join(configs['3_model'], configs['model_type']),
        configs['model_type']
    )
    rc = shell_command(cmd)
    

def copy_pretrained_xseg_model(configs):
    copy_from = os.path.join(configs['pretrain_src'], '3_model')
    copy_to = os.path.join(configs['3_model'])
    if not os.path.exists(copy_to):
        print("Making directory: %s" %copy_to)
        os.makedirs(copy_to, exist_ok=True)
    print("Copy pretrained XSeg model")
    print("  from: %s" %copy_from)
    print("  to  : %s" %copy_to)
    for filename in os.listdir(copy_from):
        if re.search(r'^XSeg_.*', filename) is None:
            continue
        src_path = os.path.join(copy_from, filename)
        dst_path = os.path.join(copy_to, filename)
        #print("  filename=%s" %(filename))
        print("%s to %s" %(src_path, dst_path))
        if os.path.isfile(dst_path):
            print("  Model file exists, removing: %s" %dst_path)
            os.remove(dst_path)
        shutil.copy2(src_path, dst_path)


def copy_pretrained_model(configs):
    copy_from = os.path.join(configs['pretrain_src'], '3_model', configs['model_type'])
    copy_to = os.path.join(configs['3_model'], configs['model_type'])
    recursive_copy(copy_from, copy_to)

    # Rename pretrain model to src label
    oldname = 'pretrain'
    newname = configs['model_label']
    skipped = False
    print("Renaming pretraining model to src label: %s -> %s" %(oldname, newname))
    for filepath in pathex.get_paths(copy_to):
        filepath_name = filepath.name
        if re.search(r'^%s_.*' %oldname, filepath_name) is None:
            continue
        model_filename, remain_filename = filepath_name.split('_', 1)
        if model_filename == oldname:
            new_filepath = filepath.parent / ( newname + '_' + remain_filename )
            if new_filepath.exists():
                print("  Model file exists, skipping: %s" %new_filepath)
                skipped = True
                continue
            filepath.rename(new_filepath)

    if skipped:
        junk = input("Some files skipped")

    # Disable pretraining
    model_file = Path("%s\\%s_%s_data.dat" %(copy_to, newname, configs['model_type']))
    print("Disabling pretrain option and reset iterations: %s" %(model_file))
    model_data = pickle.loads( model_file.read_bytes())
    model_data['options']['pretrain'] = False
    model_data['iter'] = 1
    with open(model_file, 'wb') as f:
        f.write( pickle.dumps(model_data))


def train_basic(configs):
    cmd = '%s %s train --training-data-src-dir %s --training-data-dst-dir %s --model-dir %s --model %s --force-gpu-idxs 0' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_src'],
        configs['f2train_dst'],
        os.path.join(configs['3_model'], configs['model_type']),
        configs['model_type'],
    )
    rc = shell_command(cmd)


def train_delayed(configs):
    choice = input("Enter seconds to delay: ")
    time.sleep(int(choice))
    train_sequenced(configs)


def train_sequenced(configs):
    print("# Reminder: ")
    print("# * xseg-model must be applied to f2train before training")
    cmd = '%s %s train --training-data-src-dir %s --training-data-dst-dir %s --model-dir %s --model-label %s --model %s --config %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'main-sequenced.py'),
        configs['f2train_src'],
        configs['f2train_dst'],
        os.path.join(configs['3_model'], configs['model_type']),
        configs['model_label'],
        configs['model_type'],
        configs['config_file'],
    )
    rc = shell_command(cmd)


def f2train_enhance(configs):
    cmd = '%s %s facesettool enhance --input-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def f2train_metadata_save(configs):
    cmd = '%s %s util --input-dir %s --save-faceset-metadata' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def f2train_metadata_restore(configs):
    cmd = '%s %s util --input-dir %s --restore-faceset-metadata' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def zip_all_faces(configs):
    #cmd = '%s %s util --input-dir %s --pack-faceset' %(
    #    configs['python_exe'],
    #    configs['dfl_main'],
    #    configs['1_source'],
    #)
    cmd = '%s a %s -sdel -mx1 "%s"' %(
        configs['zip_exe'],
        '2_faces.7z',
        configs['2_faces']
    )
    rc = shell_command(cmd)
    

def unzip_all_faces(configs):
    zipfile = '2_faces.7z'
    cmd = '%s x %s ' %(
        configs['zip_exe'],
        zipfile,
    )
    rc = shell_command(cmd)
    os.remove(zipfile)


def pack_f2merge(configs):
    cmd = '%s %s util --input-dir %s --pack-faceset' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2merge'],
    )
    rc = shell_command(cmd)


def unpack_f2merge(configs):
    cmd = '%s %s util --input-dir %s --unpack-faceset' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2merge'],
    )
    rc = shell_command(cmd)


def pack_f2train(configs):
    cmd = '%s %s util --input-dir %s --pack-faceset' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def unpack_f2train(configs):
    cmd = '%s %s util --input-dir %s --unpack-faceset' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def prefix_f2train_name(configs):
    cmd = '%s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'add_pfx_to_source_filename.py'),
        configs['f2train_dst'],
    )
    rc = shell_command(cmd)


def prefix_f2merge_name(configs):
    cmd = '%s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'add_pfx_to_source_filename.py'),
        configs['f2merge'],
    )
    rc = shell_command(cmd)


def create_samples(configs):
    cmd = '%s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'create_samples.py'),
        configs['1_source'],
        configs['f2merge']
    )
    rc = shell_command(cmd)


def xseg_apply_f2merge_samples(configs):
    cmd = '%s %s xseg apply --input-dir %s --model-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        os.path.join(configs['f2merge'], 'merge_samples'),
        os.path.join(configs['3_model']),
    )
    rc = shell_command(cmd)


def merge_samples(configs):
    cmd = '%s %s merge --input-dir %s --aligned-dir %s --model-dir %s --model %s --output-dir %s --output-mask-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        os.path.join(configs['1_source'], 'source_samples'),
        os.path.join(configs['f2merge'], 'merge_samples'),
        os.path.join(configs['3_model'], configs['model_type']),
        configs['model_type'],
        os.path.join(configs['4_merged'], 'samples'),
        os.path.join(configs['4_merged'], 'samples', 'mask'),
    )
    rc = shell_command(cmd)


def merge(configs):
    cmd = '%s %s merge --input-dir %s --aligned-dir %s --model-dir %s --model %s --output-dir %s --output-mask-dir %s' %(
        configs['python_exe'],
        configs['dfl_main'],
        configs['1_source'],
        configs['f2merge'],
        os.path.join(configs['3_model'], configs['model_type']),
        configs['model_type'],
        os.path.join(configs['4_merged'], configs['model_type']),
        os.path.join(configs['4_merged'], configs['model_type'], 'mask'),
    )
    rc = shell_command(cmd)


def get_loss(configs):
    """ Return the loss value from the saved model """

    model_name = "%s_%s" %(configs['model_label'], configs['model_type'])
    cmd = '%s %s %s %s' %(
        configs['python_exe'],
        os.path.join(configs['dfl_root'], 'utils', 'get-loss.py'),
        os.path.join(configs['3_model'], configs['model_type']),
        model_name
    )
    p_cmd = subprocess.Popen(   
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    stdout, stderr = p_cmd.communicate()
    return stdout


def video(configs):
    loss = get_loss(configs).strip()
    ffmpeg_path = os.path.join(configs['bindir'], 'ffmpeg', 'ffmpeg.exe')
    fps = configs['video_info']['fps']
    source_img_path = configs['1_source']
    #source_img_output = os.path.join(source_img_path, configs['title'] + r'_%5d.png')
    source_imgs = os.path.join(configs['4_merged'], configs['model_type'], configs['title'] + r'_%5d.png')
    ts = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
    video_filename = '%s-%s-%s-%s--LOSS--%s.mp4' %(
        configs['title'],
        configs['f2train_src_name'],
        configs['model_type'],
        ts,
        loss
    )
    output_video_file = os.path.join(configs['5_video'], video_filename)
    cmd = '%s -y -threads 11 -i "%s" -r %s -i "%s" -map 0:a? -map 1:v -r %s -c:v libx264 -b:v 8M -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 "%s"' %(
        ffmpeg_path,
        configs['input_video'],
        fps,
        source_imgs,
        fps,
        output_video_file
    )
    rc = shell_command(cmd)


if __name__ == "__main__":
    configs = get_configs()
    m = Menu(configs)
    configs['menu'] = m
    while True:
        #configs = get_configs()
        #options = menu_options()
        #display_menu(configs, options)
        m.display_menu()
        choice = input("Enter choice: ")
        #execute_option(configs, choice, options)
        execute_option(configs, m.options, choice)






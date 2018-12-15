import os
import sys
import time
import argparse
import multiprocessing
import subprocess
#from utils import Path_utils
from core import pathex
#from utils import os_utils
from pathlib import Path
from pprint import pprint
import pickle
import models
import shutil
import yaml

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    raise Exception("This program requires at least Python 3.6")

class fixPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def get_model_data(model_path, model_type, model_label):
    model_data_path = Path("%s\\%s_%s_data.dat" %(model_path, model_label, model_type))

    if not os.path.exists(model_data_path):
        print("Model file does not exist: %s" %model_data_path)
        return None

    model_data = pickle.loads( model_data_path.read_bytes() )

    #model_data['loss_history'] = []
    #model_data['sample_for_preview'] = []
    #pprint(model_data)

    #loss_history = model_data['loss_history'] if 'loss_history' in model_data.keys() else []
    #iter = model_data['iter'] if 'iter' in model_data.keys() else []
    #options = model_data['options'] if 'options' in model_data.keys() else []
    #pprint("Loss History: %s" %loss_history[-1])
    #pprint("Iteration: %s" %iter)
    #print("Options: ")
    #pprint(options)
    return model_data

def set_model_data(model_path, model_type, model_label, model_data):
    model_file = os.path.join(model_path, "%s_%s_data.dat" %(model_label, model_type))

    with open(model_file, 'wb') as f:
        f.write( pickle.dumps(model_data) )

    return

def restore_model(model_dir, last_good_save):
    backupdir = os.path.join(model_dir, 'backup', str(last_good_save))
    print("Restore to: %s" %model_dir)
    for filename in os.listdir(backupdir):
        filepath = os.path.join(backupdir, filename)
        if os.path.isfile(filepath):
            oldfilepath = os.path.join(model_dir, filename)
            if os.path.isfile(oldfilepath):
                os.remove(oldfilepath)
            print("Restoring from: %s" %filepath)
            shutil.copy(filepath, model_dir)


def save_model(model_dir, target_iter):
    newdir = os.path.join(model_dir, 'backup', str(target_iter))
    os.makedirs(newdir, exist_ok=True)
    for filename in os.listdir(model_dir):
        filepath = os.path.join(model_dir, filename)
        if os.path.isfile(filepath):
            shutil.copy(filepath, newdir)


def get_args():
    """ Parse command line arguments
        Separate args that will be passed to main.py from custom args
        used only in main-sequenced.py
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    p = subparsers.add_parser( "train", help="Trainer")
    p.add_argument('--training-data-src-dir', required=True, action=fixPathAction, dest="training_data_src_dir", help="Dir of src-set.")
    p.add_argument('--training-data-dst-dir', required=True, action=fixPathAction, dest="training_data_dst_dir", help="Dir of dst-set.")
    p.add_argument('--pretrained-model-dir', action=fixPathAction, dest="pretrained_model_dir", default=None, help="Optional dir of pretrain model files")
    p.add_argument('--model-dir', required=True, action=fixPathAction, dest="model_dir", help="Model dir.")
    p.add_argument('--model', required=True, dest="model_type", choices=pathex.get_all_dir_names_startswith ( Path(__file__).parent / 'models' , 'Model_'), help="Type of model")
    main_args, unknown = parser.parse_known_args()

    # Parse again, but this time leave extra args in
    #seq_parser = argparse.ArgumentParser()
    p.add_argument('--config', required=True, action=fixPathAction, dest="config_file", help="Path to yaml config file containing training_sequence")
    p.add_argument('--model-label', required=False, dest="model_label", help="Label of model (default=default)")
    args = parser.parse_args()

    # Filter out unknown args from all sysv args to pass back to main.py
    for item in unknown:
        sys.argv.remove(item)

    return args

if __name__ == "__main__":

    #$print("syargv: %s" %"\n  ".join(args))

    if sys.argv[1] != 'train':
        print("This script only works for training")
        sys.exit(1)

    arguments = get_args()
    src_dir = arguments.training_data_src_dir
    dst_dir = arguments.training_data_dst_dir
    model_dir = arguments.model_dir
    model_type = arguments.model_type
    model_label = arguments.model_label
    config_file = arguments.config_file

    # Load sequence settings from local+global config files
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
    yaml_configs = {**global_configs, **local_configs}

    try:
        seq_config = yaml_configs['training_sequence']
    except:
        print("training_sequence key not found in config file: %s" %config_file)
        sys.exit(1)
    if model_label is None:
        try:
            model_label = yaml_configs['model_label']
        except:
            print("model_label key not found in config file: %s" %config_file)
            sys.exit(1)

        
    args = sys.argv[1:] + ['--force-model-name', model_label, '--force-gpu-idxs', '0']
    last_good_save = None

    # Start interactive if no model data is found
    model_data = get_model_data(model_dir, model_type, model_label)
    if model_data is None:
        print("Starting training interactively")
        rc = subprocess.call(['python', r'G:\Temp\df\DeepFaceLabCUDA\_internal\DeepFaceLab\main.py'] + args)

    start_iter = 0
    for i, seq in enumerate(seq_config):
        print("Sequence: %s" %(i+1))
        model_data = get_model_data(model_dir, model_type, model_label)
        print("%-30s: %s" %("Current Iteration", model_data['iter']))
        target_iter = seq['target_iter']
        iter_step = seq['iter_step']
        if iter_step > 0:
            step_target_iter = start_iter + iter_step
            print("%-30s: %s" %("Final target iteration", target_iter))
            while model_data['iter'] > step_target_iter:
                step_target_iter += iter_step
                start_iter += iter_step
        else:
            step_target_iter = target_iter

        print("%-30s: %s" %("Setting target iteration to", step_target_iter))
        if model_data['iter'] > target_iter:
            continue

        while model_data['iter'] < target_iter:
            options = model_data['options']
            seq_options = seq['options']
            for key in seq_options.keys():
                if key in options:
                    print("%-30s: %-25s Old: %-10s -> New: %s" %("Setting option", key, options[key], seq_options[key]))
                    options[key] = seq_options[key]

            options['target_iter'] = step_target_iter
            model_data['options'] = options
            #model_data['target_iter'] = step_target_iter
            set_model_data(model_dir, model_type, model_label, model_data)
            rc = subprocess.call(['python', r'G:\Temp\df\DeepFaceLabCUDA\_internal\DeepFaceLab\main.py'] + args)
            if rc != 0:
                print("Bad return code: %s" %rc)
                sys.exit(1)
            # Refresh model data after training session is completed
            model_data = get_model_data(model_dir, model_type, model_label)
            if model_data['iter'] < step_target_iter:
                print("Step Target iteration not reached, exiting")
                sys.exit(0)
            # Check if loss has gone haywire due to artifacts
            last_loss = model_data['loss_history'][-1][0]
            print("%-30s: %s" %("Last loss", last_loss))
            if last_loss > seq['loss_threshold']:
                try_last = target_iter
                while last_good_save is None:
                    if os.path.isdir(os.path.join(model_dir, 'backup', str(try_last))):
                        last_good_save = try_last
                    try_last -= iter_step
                print("Model has collapsed, reverting to last good save: %s" %last_good_save)
                restore_model(model_dir, last_good_save)
                model_data = get_model_data(model_dir, model_type, model_label)
                start_iter = last_good_save
                if iter_step > 0:
                    step_target_iter = last_good_save + iter_step
                else:
                    step_target_iter = target_iter
            else:
                # save a copy of the model
                print("%-30s: %s" %("Saving model at iteration", model_data['iter']))
                save_model(model_dir, step_target_iter)
                last_good_save = step_target_iter

                # Reset starting point before incrementing the target iteration
                start_iter = step_target_iter
                if iter_step > 0:
                    step_target_iter = step_target_iter + iter_step
                else:
                    step_target_iter = target_iter

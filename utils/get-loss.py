import os
import sys
from pathlib import Path
import pickle

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 2):
    raise Exception("This program requires at least Python 3.2")

def get_loss(model_path, model_name):
    #print("Model path: %s" %model_path)
    #print("Model name: %s" %model_name)
    #model_data_path = Path("%s\\default_%s_data.dat" %(model_path, model_type))
    model_data_path = Path("%s\\%s_data.dat" %(model_path, model_name))
    #print("Model data path: %s" %model_data_path)
    model_data = pickle.loads( model_data_path.read_bytes() )
    loss_history = model_data['loss_history'] if 'loss_history' in model_data.keys() else []

    #print(loss_history[0])
    #print(loss_history[-1])
    print("S%.4f-D%.4f" %(loss_history[-1][0], loss_history[-1][1]))


if __name__ == "__main__":
    try:
        model_path = sys.argv[1]
        model_name = sys.argv[2]
    except:
        print("Usage: %s model_data_path model_name" %(sys.argv[0]))

    get_loss(model_path, model_name)

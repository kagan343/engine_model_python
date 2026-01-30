import os
import pickle
import inspect

# base functions from https://stackoverflow.com/questions/66271284/saving-and-reloading-variables-in-python-preserving-names

# Set directory, hard code fine for now not planning on chaning folder strct/name
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "Data_Storage")

def save(filename, *args):
    
    # Get global dictionary
    # glob = globals()
    glob = inspect.currentframe().f_back.f_globals # Needed for passing in variables from another script
    d = {}
    for v in args:
        # Copy over desired values
        d[v] = glob[v]

    # Set full_path
    full_path = os.path.join(data_dir, filename)

    with open(full_path, 'wb') as f:
        # Put them in the file 
        pickle.dump(d, f)
    print("Saved to:", full_path)

def load(filename):
    # Get global dictionary
    glob = inspect.currentframe().f_back.f_globals

    # Set full_path for loading
    full_path = os.path.join(data_dir, filename)

    with open(full_path, 'rb') as f:
        for k, v in pickle.load(f).items():
            # Set each global variable to the value from the file
            glob[k] = v

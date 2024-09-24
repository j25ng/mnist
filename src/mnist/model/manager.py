import os

def get_model_path():
    f = __file__
    path = os.path.abspath(f)
    dir_name = os.path.dirname(path)
    model_path = os.path.join(dir_name, "mnist240924.keras")
    return model_path


import yaml
import os.path
import pandas
import tempfile
import pandas as pd
from Orange.data.pandas_compat import table_from_frame

def load_env(env_file,name="ploomber_twinning"):
    with open(env_file, "r") as file:
        env = yaml.safe_load(file)        
    env["output_folder"] = os.path.join(tempfile.gettempdir(),name)
    return env

def env2table(env):
    return table_from_frame(pd.DataFrame.from_dict(env, orient="index", columns=["value"]))
# + tags=["parameters"]
upstream = ["read_templates"]
product = None
probe: None
root: None
crop_left: None
crop_right: None
# -

import pandas as pd
import os.path
from ramanchada2.spectrum import from_chada,from_local_file, Spectrum
from pathlib import Path

Path(product["data"]).mkdir(parents=True, exist_ok=True)

df = pd.read_excel(upstream["read_templates"]["data"])
ratios = pd.read_excel(upstream["read_templates"]["ratios"])

df.head()

ratios.head()

#reference = df.loc(df["source"]=='reference')
#twinned = df.loc(df["source"]=='twinned')
def findref_pair(id_twin,laser_power_percent):
    _tmp = ratios.loc[(ratios["id_twin"]==id_twin) & (ratios["laser_power_percent"]==laser_power_percent)]
    
    if _tmp.empty:
        return (None,None,None)
    else:
        row = _tmp.iloc[0]
        return (row["id_ref"],row["laser_power_mw_ratio"],row["integration_time_ms_ratio"])

def process(df, pair_normalize = False):
    #leds have no laser_power etc,  we want them as well
    id_groups = df.groupby(['id','sample','laser_power_percent','integration_time_ms','source','role'],dropna=False)

    # Iterate over each group
    for (id, sample,laser_power_percent,integration_time_ms,source,role), group in id_groups:
        print(id,sample,laser_power_percent,integration_time_ms,source,role,group.shape)
        spe = None
        # average spectra
        # these are replicates and should have the same grid (but better to check that)
        
        for index, row in group.iterrows():
            _tmp = from_local_file(os.path.join(root,row["path"],row["filename"]))
            spe = _tmp if spe is None else spe + _tmp
        spe /= group.shape[0]
        spe  = spe.trim_axes(method='x-axis',boundaries=(crop_left,max(spe.y) if crop_right is None else crop_right))

        if pair_normalize:
           idref,LP_ratio, T_ratio = findref_pair(id,laser_power_percent) 
           print(idref,LP_ratio, T_ratio)

        #spe.plot(label=f'{id} {sample} {laser_power_percent} {integration_time_ms}')
        
        #spe_calib.write_cha(file_path,dataset="/calibrated")
        #print(group["role"].unique())
        #source = group["source"].unique()
        #if "reference" in source:
        #    #laser_power_mw_ratio = ratios.loc[ratios['id_ref'] == id, 'laser_power_mw_ratio'].values
        #    #print(laser_power_mw_ratio)
  
#for index, row in ratios.iterrows():
#    id_ref = row["id_ref"]
#    id_twin = row["idtwin"]

#reference leds
process(df.loc[(df["source"]=="reference") & (df["role"]=="leds")])
#reference spectra
process(df.loc[(df["source"]=="reference") & (df["role"]=="spectra")])
#twinned leds
process(df.loc[(df["source"]=="twinned") & (df["role"]=="leds")])
#twinned spectra
process(df.loc[(df["source"]=="twinned") & (df["role"]=="spectra")] , pair_normalize = True)
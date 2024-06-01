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

df = pd.read_excel(upstream["read_templates"]["data"])
ratios = pd.read_excel(upstream["read_templates"]["ratios"])

df.head()

ratios.head()

#reference = df.loc(df["source"]=='reference')
#twinned = df.loc(df["source"]=='twinned')

#leds have no laser_power etc,  we want them as well
id_groups = df.groupby(['id','sample','laser_power_percent','integration_time_ms'],dropna=False)

# Iterate over each power group
for (id, sample,laser_power_percent,integration_time_ms), group in id_groups:
    print(id,sample,laser_power_percent,integration_time_ms,group.shape)
    spe = None
    # average spectra
    # these are replicates and should have the same grid (but better to check that)
    for index, row in group.iterrows():
        _tmp = from_local_file(os.path.join(root,row["path"],row["filename"]))
        spe = _tmp if spe is None else spe + _tmp
    spe /= group.shape[0]
    spe  = spe.trim_axes(method='x-axis',boundaries=(crop_left,max(spe.y) if crop_right is None else crop_right))
    spe.plot(label=f'{id} {sample} {laser_power_percent} {integration_time_ms}')
    
    #print(group["role"].unique())
    #source = group["source"].unique()
    #if "reference" in source:
    #    #laser_power_mw_ratio = ratios.loc[ratios['id_ref'] == id, 'laser_power_mw_ratio'].values
    #    #print(laser_power_mw_ratio)

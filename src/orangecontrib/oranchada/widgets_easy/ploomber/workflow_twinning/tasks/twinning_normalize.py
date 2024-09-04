# + tags=["parameters"]
upstream = ["load_spectra"]
product = None
probe: None
result_spectrum = "spectrum_normalized"

# -

import pandas as pd
import matplotlib.pyplot as plt

def score_laserpower(reference,twinned):
    # Merge the two DataFrames on "laser_power_percent"
    merged_df = twinned.merge(reference, on="laser_power_percent", suffixes=('', '_ref'))
    # Calculate the score and assign it to the "score" column
    merged_df['score'] = merged_df['laser_power_ref'] / merged_df['laser_power']
    # Update the original "twinned" DataFrame with the calculated scores
    #display(merged_df)
    return merged_df['score'].values



def normalize_spectra(row):
    return row["spectrum"] * row["score"]

devices_h5file= upstream["load_spectra"]["data"]
devices = pd.read_hdf(devices_h5file, key="devices")
devices.head()

leds = pd.read_hdf(devices_h5file, key="led")
leds.head()

def calculate_twinned_score(devices,reference_condition,twinned_condition):
    for group, group_df in devices.loc[reference_condition].groupby(['device', 'instrument', 'probe']):
        probe = group[2]
        #print("-{}-".format(probe))
        twinned = devices.loc[twinned_condition]
        score = score_laserpower(group_df,twinned)
        devices.loc[twinned_condition,"score"] = score
        #get_slope(group_df,twinned)

#score for the referencespectra
devices.loc[devices["reference"],"score"]  =1.0
#score for twinned spectra
twinned_condition = (~devices["reference"]) & (devices["probe"] == probe)
reference_condition = (devices["reference"]) & (devices["probe"] == probe)
calculate_twinned_score(devices,reference_condition,twinned_condition)

print(devices.columns)
# Assert that the DataFrame contains the expected columns
assert set(["score"]).issubset(devices.columns), "score column is missing"

#normalisation
twinned_condition = (~devices["reference"]) & pd.notna(devices["score"])
devices.loc[twinned_condition, result_spectrum] = devices.loc[twinned_condition].apply(normalize_spectra, axis=1)

devices.loc[reference_condition, result_spectrum] = devices.loc[reference_condition].apply(normalize_spectra, axis=1)

devices.loc[twinned_condition | reference_condition][["device","score","laser_power","laser_power_percent"]]

print(devices.columns)
# Assert that the DataFrame contains the expected columns
assert set([result_spectrum]).issubset(devices.columns), "a processed spectrum column is missing"


devices.to_hdf(product["data"], key='devices', mode='w')

leds.to_hdf(product["data"], key='led', mode='a')

pd.DataFrame({"original" : {"field" : "spectrum"}, "normalized" : {"field"  : result_spectrum}}).T.to_hdf(product["data"], key='processing', mode='a')

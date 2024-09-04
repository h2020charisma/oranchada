# + tags=["parameters"]
upstream = []
product = None
probe: None
root: None
reference_spectra: None
twinned_spectra: None 
reference_leds: None 
twinned_leds: None 
sample_spectra: None
sample_test: None
# -

import pandas as pd 
import os.path

def read_template(_path, source_tag = "reference", role_tag="spectra"):
    df = pd.read_excel(_path, sheet_name='Files')
    df.columns = ['sample', 'measurement', 'filename', 'optical_path', 'laser_power_percent', 'laser_power_mw', 'integration_time_ms',
              'humidity', 'temperature', 'date', 'time']
    df_meta = pd.read_excel(_path, sheet_name='Front sheet', skiprows=4)
    df_meta.columns = ['optical_path', 'instrument_make', 'instrument_model', 'wavelength','collection_optics','slit_size','grating','pin_hole_size','collection_fibre_diameter','notes','laser_power_max_mw']    
    df_merged = pd.merge(df, df_meta, on='optical_path', how='left')

    # Open the Excel file and read specific cells directly
    with pd.ExcelFile(_path) as xls:
        provider = xls.parse('Front sheet', usecols="B", nrows=1, header=None).iloc[0, 0]
        investigation = xls.parse('Front sheet', usecols="F", nrows=1, header=None).iloc[0, 0]
    df_merged["provider"] = provider
    df_merged["investigation"] = investigation
    df_merged["source"] = source_tag
    df_merged["role"] = role_tag
    return df_merged

#    df_merged["source"] = key
#    df_merged_list.append(df_merged)

df_spe_ref = read_template(os.path.join(root,reference_spectra),"reference","spectra")
df_spe_ref["path"] = os.path.dirname(reference_spectra)
df_spe_twin = read_template(os.path.join(root,twinned_spectra),"twinned","spectra")
df_spe_twin["path"] = os.path.dirname(twinned_spectra)
df_led_ref = read_template(os.path.join(root,reference_leds),"reference","leds")
df_led_ref["path"] = os.path.dirname(reference_leds)
df_led_twin = read_template(os.path.join(root,twinned_leds),"twinned","leds")
df_led_twin["path"] = os.path.dirname(twinned_leds)

df_merged_list = pd.concat([df_spe_ref, df_spe_twin, df_led_ref, df_led_twin], ignore_index=True)
df_merged_list['id'] = df_merged_list.apply(lambda row: f"{row['provider']}_{row['instrument_make']}_{row['instrument_model']}_{row['wavelength']}_{row['collection_optics']}_{row['investigation']}", axis=1)

df_merged_list.loc[df_merged_list['sample'] == sample_test, 'role'] = 'test'

df_merged_list.to_excel(product["data"],index=False)

#columns = ["instrument_make","instrument_model","wavelength","collection_optics","provider","role"]

#unique_combinations = df_merged_list.loc[df_merged_list["role"]=="spectra"][columns].drop_duplicates()
#unique_combinations

# Filter rows with role "reference"
# will calculate power ratio , we need spectra only, not the LEDs
df = df_merged_list.loc[df_merged_list["role"]=='spectra']
#reference spectra
references = df[df_merged_list['source'] == 'reference' ]
# Merge with rows having the same laser_power_percent and role "twinned"
merged = references.merge(df[df['source'] == 'twinned'], on='laser_power_percent', suffixes=('_ref', '_twin'))
# Calculate ratio
merged['laser_power_mw_ratio'] = merged['laser_power_mw_ref'] / merged['laser_power_mw_twin']
merged['integration_time_ms_ratio'] = merged['integration_time_ms_ref'] / merged['integration_time_ms_twin']

merged[["id_ref","id_twin","laser_power_percent","laser_power_mw_ratio","integration_time_ms_ratio"]].drop_duplicates().to_excel(product["ratios"],index=False)
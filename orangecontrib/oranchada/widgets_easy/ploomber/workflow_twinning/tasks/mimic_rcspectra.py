# + tags=["parameters"]
upstream = []
product = None
root_led_folder: None
root_data_folder: None
files_led_reference: None
files_led_twinned: None
files_spectra_reference: None
files_spectra_twinned: None
filter_probe: None
input_rcspectra: None
key_spectra: None
key_leds: None

# -

import pandas as pd
import ramanchada2 as rc2
import os.path

A =[]
for filename in os.listdir(os.path.join(root_data_folder,files_spectra_reference)):
    try:
        if filter_probe in filename:
            spea=rc2.spectrum.from_local_file(os.path.join(root_data_folder,files_spectra_reference,filename))
            A.append(spea)
    except:
        pass
B=[]
for filename in os.listdir(os.path.join(root_data_folder,files_spectra_twinned)):
    try:
        if filter_probe in filename:        
            speb=rc2.spectrum.from_local_file(os.path.join(root_data_folder,files_spectra_twinned,filename))
            B.append(speb)
    except:
        pass

dfA= pd.DataFrame(A,columns=["spectrum"])
dfA["reference"]= True
dfB= pd.DataFrame(B,columns=["spectrum"])
dfB["reference"]= False
df_spectra = pd.concat([dfA,dfB], ignore_index=True)

df_spectra.to_hdf(product["data"], key=key_spectra, mode='w')

A =[]
for filename in os.listdir(os.path.join(root_led_folder,files_led_reference)):
    try:
        if filter_probe in filename:
            spea=rc2.spectrum.from_local_file(os.path.join(root_led_folder,files_led_reference,filename))
            A.append(spea)
    except:
        pass
B=[]
for filename in os.listdir(os.path.join(root_led_folder,files_led_twinned)):
    try:
        if filter_probe in filename:
            speb=rc2.spectrum.from_local_file(os.path.join(root_led_folder,files_led_twinned,filename))
            B.append(speb)
    except:
        pass

dfA= pd.DataFrame(A,columns=["spectrum"])
dfA["reference"]= True
dfB= pd.DataFrame(B,columns=["spectrum"])
dfB["reference"]= False
df_leds = pd.concat([dfA,dfB], ignore_index=True)

df_leds.to_hdf(product["data"], key=key_leds, mode='a')
# + tags=["parameters"]
upstream = []
product = None
root_data_folder: None
files_spectra_reference: None
files_spectra_twinned: None

# -

import os
import ramanchada2 as rc2
import re
import pandas as pd



def load_spectra(root_data_folder=root_data_folder,folder_path=[files_spectra_reference,files_spectra_twinned]):
    devices = None
    reference = True
    for subset in folder_path:
        spectra = {}
        for filename in os.listdir(os.path.join(root_data_folder,subset)):
            #print(os.path.join(folder_path,filename))
            #print(filename.split("_"))
            
            result = re.split(r'[_().]+', filename)
            result = [s for s in result if s]
            laser_power = int(re.sub(r'\D', '',  result[6]))
            laser_power_percent = float(re.sub(r'\D', '',  result[5]))
            instrument = result[3]
            probe = result[4]
            acquisition_time =  result[7]
            #print(result)
            #tag =  '_'.join(result[:-3] + result[-3:-2])
            tag = "{}:{}:{}:{}:{}".format(subset,instrument,probe,laser_power,acquisition_time)
            spe = rc2.spectrum.from_local_file(os.path.join(root_data_folder,subset,filename))
            #print(tag)
            if not tag in spectra:
                spectra[tag] = {"laser_power" : laser_power, "laser_power_percent" :  laser_power_percent,  "acquisition_time" : acquisition_time,
                                "spectrum" : spe , "count" : 1 , "probe" : probe,
                                "instrument" : instrument}
            else:
                spectra[tag]["spectrum"] = spectra[tag]["spectrum"] + spe
                spectra[tag]["count"] = spectra[tag]["count"] + 1
        
        #average replicates
        for tag in spectra:
            spe = spectra[tag]["spectrum"]
            spe /= spectra[tag]["count"]
            #spe = spe - spe.moving_minimum(32)
            spectra[tag]["spectrum"] = spe
            #print(tag,spectra[tag]["count"],spectra[tag]["acquisition_time"],
            #        spectra[tag]["probe"],spectra[tag]["laser_power"],spectra[tag]["laser_power_percent"])
            
        tmp = pd.DataFrame(spectra).T
        tmp["device"] = subset
        tmp["reference"] = reference
        if devices is None:
            devices = tmp
        else:
            devices = pd.concat([devices, tmp], ignore_index=False)
        reference = False

        #devices[subset] = spectra
    return devices

devices=load_spectra(root_data_folder=root_data_folder,folder_path=[files_spectra_reference,files_spectra_twinned])
devices.head()

devices.to_hdf(product["data"], key='devices', mode='w')
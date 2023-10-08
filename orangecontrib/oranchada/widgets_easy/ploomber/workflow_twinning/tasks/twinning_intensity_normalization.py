# + tags=["parameters"]
upstream = ["twinning_normalize"]
product = None
probe: None
wavelength: None
moving_minimum_window: 10
spectrum_to_correct: None
spectrum_corrected_column: None 
baseline_after_ledcorrection: False
baseline_algorithm: None

# -
import matplotlib.pyplot as plt
import ramanchada2 as rc2
import numpy as np
import pandas as pd


def baseline_spectra(spe, algo="als", **kwargs):
    if algo == "snip":
        del kwargs["window"]
        kwargs["niter"]  = 1000
        return spe.subtract_baseline_rc1_snip(**kwargs)
    elif algo == "als":
        del kwargs["window"]
        kwargs["niter"]  = 1000
        kwargs["p"]  = 0.1
        kwargs["lam"]  = 1e3
        #lam: float = 1e5, p: float = 0.001, niter: PositiveInt = 100,#
        return spe.subtract_baseline_rc1_als(**kwargs)
    elif (algo == "none") or (algo is None):  # movingmin
        return spe     
    else:  # movingmin
        window = kwargs.get("window", 10)
        return spe - spe.moving_minimum(window)
    
def Y_532(x):
    A = 8.30752731e-01
    B = 2.54881472e-07
    x0 = 1.42483359e+3
    Y = A * np.exp(-B * (x - x0)**2)
    return Y

def Y_785(x):
    A0 = 5.90134423e-1
    A = 5.52032185e-1
    B = 5.72123096e-7
    x0 = 2.65628776e+3
    Y = A0 + A * np.exp(-B * (x - x0)**2)
    return Y

def Y(x,wavelength=785):
    if wavelength==785:
        return Y_785(x)
    elif wavelength==532:
        return Y_532(x)
    else:
        raise Exception("not supported wavelength {}".format(wavelength))


match_led={
    "reference" : "reference",
    "twinning": "twinning"
}
match_led


devices_h5file= upstream["twinning_normalize"]["data"]
print(devices_h5file)
devices = pd.read_hdf(devices_h5file, "devices")
devices.head()

led_frame = pd.read_hdf(devices_h5file, "led")
led_frame.head()

processing = pd.read_hdf(devices_h5file, "processing")
processing.head()

devices_h5file= product["data"]
devices.head()




def intensity_normalization(row,spectrum_to_correct):
    try:
        spe = row[spectrum_to_correct]        
        spe_y = spe.y
        spe_y[spe_y < 0] = 0
        _Y = Y(spe.x,wavelength)

        subset=row["device"]
        led_row = led_frame.loc[led_frame["device"]==subset]
        spe_dist =led_row["spe_dist"].values[0]
        #spe_led = led_row["spectrum"]
        #spe_dist = led_row["spe_dist"]
        area = led_row["area"].values[0]

        spe_led_sampled= spe_dist.pdf(spe.x)*area
        spe_corrected = _Y*spe_y/spe_led_sampled
        mask = (spe_led_sampled == 0)
        spe_corrected[mask] = 0
        return rc2.spectrum.Spectrum(spe.x, spe_corrected)
    except Exception as err:
        print(err)
        return None


baseline_column = "{}_baseline".format(spectrum_corrected_column)  if baseline_after_ledcorrection else "{}_baseline".format(spectrum_to_correct) 
twinned_condition = (~devices["reference"]) & (devices["probe"] == probe)
reference_condition = (devices["reference"]) & (devices["probe"] == probe)

kwargs= {"window" : moving_minimum_window}
if baseline_after_ledcorrection:
    devices.loc[twinned_condition, spectrum_corrected_column] = devices.loc[twinned_condition].apply(lambda row: intensity_normalization(row,spectrum_to_correct),axis=1)
    devices.loc[reference_condition, spectrum_corrected_column] = devices.loc[reference_condition].apply(lambda row: intensity_normalization(row,spectrum_to_correct),axis=1)
    devices.loc[twinned_condition, baseline_column] = devices.loc[twinned_condition][spectrum_corrected_column].apply(lambda spe : baseline_spectra(spe,baseline_algorithm,**kwargs)) 
    devices.loc[reference_condition, baseline_column] = devices.loc[reference_condition][spectrum_corrected_column].apply(lambda spe : baseline_spectra(spe,baseline_algorithm,**kwargs)) 
    devices.loc[reference_condition, "baseline_removed"] = "after LED correction"    
    devices.loc[twinned_condition, "baseline_removed"] = "after LED correction"    
    processing.loc["led_corrected"] = {"field" : spectrum_corrected_column}
    processing.loc["baseline"] = {"field" : baseline_column}    
else:
    devices.loc[twinned_condition, baseline_column] = devices.loc[twinned_condition][spectrum_to_correct].apply(lambda spe : baseline_spectra(spe,baseline_algorithm,**kwargs)) 
    devices.loc[reference_condition, baseline_column] = devices.loc[reference_condition][spectrum_to_correct].apply(lambda spe : baseline_spectra(spe,baseline_algorithm,**kwargs))     
    devices.loc[twinned_condition, spectrum_corrected_column] = devices.loc[twinned_condition].apply(lambda row: intensity_normalization(row,baseline_column),axis=1)
    devices.loc[reference_condition, spectrum_corrected_column] = devices.loc[reference_condition].apply(lambda row: intensity_normalization(row,baseline_column),axis=1)
    devices.loc[reference_condition, "baseline_removed"] = "before LED correction"    
    devices.loc[twinned_condition, "baseline_removed"] = "before LED correction" 
    processing.loc["baseline"] = {"field" : baseline_column}        
    processing.loc["led_corrected"] = {"field" : spectrum_corrected_column}
        
devices.columns

devices_h5file

devices.to_hdf(devices_h5file, key='devices', mode='w')

processing.to_hdf(devices_h5file, key='processing', mode='a')


led_frame.to_hdf(devices_h5file, key='led', mode='a')

led_frame.columns

# Assert that the DataFrame contains the expected columns
assert set([spectrum_corrected_column,baseline_column]).issubset(devices.columns), "a processed spectrum column is missing"


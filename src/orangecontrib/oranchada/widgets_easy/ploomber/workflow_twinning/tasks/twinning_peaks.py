# + tags=["parameters"]
upstream = ["twinning_intensity_normalization"]
product = None
probe: None
spectrum_corrected_column: None
baseline_after_ledcorrection: None
fit_peak: None

# -

import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import ramanchada2 as rc2
import numpy as np

peak_intensity="height"
spectra2process = "{}_baseline".format(spectrum_corrected_column)  if baseline_after_ledcorrection else spectrum_corrected_column
print(spectra2process)

def calc_peak_intensity(spe,peak=144,prominence=0.01):
    try:
        boundaries=(peak-50, peak+50)
        spe = spe.trim_axes(method='x-axis', boundaries=boundaries)
        candidates = spe.find_peak_multipeak(prominence=prominence)
        fig, ax = plt.subplots(figsize=(6,2))

        if fit_peak:
            fit_res = spe.fit_peak_multimodel(profile='Voigt', candidates=candidates)
            df = fit_res.to_dataframe_peaks()
            df["sorted"] = abs(df["center"] - peak) #closest peak to 144
            df_sorted = df.sort_values(by='sorted')
            index_left = np.searchsorted(spe.x, df_sorted["center"][0] , side='left', sorter=None)
            index_right = np.searchsorted(spe.x, df_sorted["center"][0] , side='right', sorter=None)
            intensity_val = (spe.y[index_right] + spe.y[index_left])/2.0
            _label = "intensity = {:.3f} {} ={:.3f} amplitude={:.3f} center={:.1f}".format(
                intensity_val,peak_intensity,df_sorted.iloc[0][peak_intensity],
                df_sorted.iloc[0]["amplitude"],df_sorted.iloc[0]["center"])
            spe.plot(ax=ax, fmt=':',label=_label)
            fit_res.plot(ax=ax)            
        else:
            _col = "amplitude"
            peak_list = []
            for c in candidates:
                for p in c.peaks:
                    peak_list.append({_col: p.amplitude, 'position': p.position})
            df_sorted = pd.DataFrame(peak_list)
            df_sorted["sorted"] = abs(df_sorted["position"] - peak) #closest peak to 144
            df_sorted = df_sorted.sort_values(by='sorted')
            intensity_val = df_sorted.iloc[0][_col]
            _label = "{}={:.3f} position={:.1f}".format(_col,intensity_val,df_sorted.iloc[0]["position"])            
            spe.plot(ax=ax, fmt=':',label=_label)
        #return df_sorted[peak_intensity][0]
        return intensity_val
    except Exception as err:
        print(err)
        return None

#slope
def calc_regression(x,y):
    model = LinearRegression().fit(x,y)
    #print("Intercept:", model.intercept_)
    #print("Slope (Coefficient):", model.coef_[0])    
    return  (model.intercept_,model.coef_[0])

devices_h5file= upstream["twinning_intensity_normalization"]["data"]
devices = pd.read_hdf(devices_h5file, "devices")
devices.head()

led_frame = pd.read_hdf(devices_h5file, "led")
led_frame.head()


processing = pd.read_hdf(devices_h5file, "processing")
processing.head()

devices_h5file =product["data"]

#peaks
reference_condition = (devices["reference"]) & (devices["probe"] == probe)
A = devices.loc[reference_condition]
A.head()

devices.loc[reference_condition,peak_intensity] = A[spectra2process].apply(calc_peak_intensity)

twinned_condition = (~devices["reference"]) & (devices["probe"] == probe)
B = devices.loc[twinned_condition]
B.head()

devices.loc[twinned_condition,peak_intensity] = B[spectra2process].apply(calc_peak_intensity)

devices.to_hdf(devices_h5file, key='devices', mode='w')

#regression
A= devices.loc[reference_condition,["device","reference","laser_power",peak_intensity]]
#.dropna()
A

(intercept_A,slope_A) = calc_regression(A[["laser_power"]],A[peak_intensity])

#regression
B= devices.loc[twinned_condition,["device","reference","laser_power",peak_intensity]]
#.dropna()
B

(intercept_B,slope_B) = calc_regression(B[["laser_power"]],B[peak_intensity])


#A = devices.loc[reference_condition]
#B = devices.loc[twinned_condition]

plt.plot(A["laser_power"],A[peak_intensity],'o',label=A["device"].unique())
plt.plot(B["laser_power"],B[peak_intensity],'+',label=B["device"].unique())
plt.legend()

#Factor correction (FC) is obtained by dividing the slope of the reference equipment (spectrometer A) 
# by the slope of the equipment to be twinned (spectrometer B).

factor_correction = slope_A/slope_B
print(slope_A,slope_B,factor_correction)



def harmonization(row):
    try:
        spe = row[spectra2process]       
        return rc2.spectrum.Spectrum(spe.x, spe.y *factor_correction)
    except Exception as err:
        print(err)
        return None
#only twinned is multiplied
devices.loc[twinned_condition,"spectrum_harmonized"] = devices.loc[twinned_condition].apply(harmonization,axis=1)
processing.loc["harmonized"] = {"field" : "spectrum_harmonized"}    
devices.to_hdf(devices_h5file, key='devices', mode='w')


def spe_area(spe):
    try:
        sc = spe.trim_axes(method='x-axis', boundaries=(100, 1750))  
        return np.sum(sc.y * np.diff(sc.x_bin_boundaries))
    except Exception as err:
        print(err)
        return None

devices.loc[reference_condition,"area"] = devices.loc[reference_condition][spectra2process].apply(spe_area)
devices.loc[reference_condition][["reference","device","laser_power","area"]]

devices.loc[twinned_condition,"area"] = devices.loc[twinned_condition][spectra2process].apply(spe_area)   
devices.loc[twinned_condition,"area_harmonized"] = devices.loc[twinned_condition]["spectrum_harmonized"].apply(spe_area)   
devices.loc[twinned_condition][["reference","device","laser_power","area","area_harmonized"]]

devices.to_hdf(devices_h5file, key='devices', mode='w')

processing.to_hdf(devices_h5file, key='processing', mode='a')

led_frame.to_hdf(devices_h5file, key='led', mode='a')

pd.DataFrame({"twinned" : {"slope"  : slope_B, "intercept" : intercept_B},
              "reference" : {"slope"  : slope_A, "intercept" : intercept_A}
              }).T.to_hdf(devices_h5file, key='regression', mode='a')

pd.DataFrame({"result" : {"factor_correction" :factor_correction}
              }).to_hdf(devices_h5file, key='factor_correction', mode='a')

import matplotlib.pyplot as plt
def plot_spectra(row,boundaries=(100, 1750)):
    try:
        sc =row[spectra2process]
        if boundaries:
            sc = sc.trim_axes(method='x-axis', boundaries=boundaries)        
        sc.plot(ax=axes[0],label="{}%".format(row["laser_power_percent"]))
    except:
        pass
    try:
        sc =row["spectrum_harmonized"]
        if boundaries:
            sc = sc.trim_axes(method='x-axis', boundaries=boundaries)
        sc.plot(ax=axes[1],label="{}%".format(row["laser_power_percent"]))
    except:
        pass    
    axes[0].set_title("{} {}".format(row["device"],row["probe"]))

fig, axes = plt.subplots(2, 1, figsize=(15, 6))      
axes[1].set_title("harmonized")
devices.loc[twinned_condition].apply(plot_spectra, axis=1)

fig, axes = plt.subplots(2, 1, figsize=(15, 6))      
axes[1].set_title("harmonized")
devices.loc[reference_condition].apply(plot_spectra, axis=1)
 
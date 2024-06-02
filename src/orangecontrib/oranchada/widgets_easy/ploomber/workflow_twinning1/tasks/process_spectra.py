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
import matplotlib.pyplot as plt
import numpy as np 
from sklearn.linear_model import LinearRegression

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

def calc_regression(x,y):
    model = LinearRegression().fit(x,y)
    #print("Intercept:", model.intercept_)
    #print("Slope (Coefficient):", model.coef_[0])    
    return  (model.intercept_,model.coef_[0])

def process(df, pair_normalize = False, baseline = False, ycalibration = False, peak =False):
    #leds have no laser_power etc,  we want them as well
    id_groups = df.groupby(['id','sample','laser_power_percent','integration_time_ms','source','role'],dropna=False)

    data4regression = []
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
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3))
            idref,LP_ratio, T_ratio = findref_pair(id,laser_power_percent) 
            spe.plot(ax1, label='average')
            if LP_ratio != None:
               spe = spe * LP_ratio
            if T_ratio != None:
                spe = spe * T_ratio
            spe.plot(ax1, label='normalized')
            plt.title(id)

        if baseline:
            kwargs = {"niter" : 40}            
            spe = spe.subtract_baseline_rc1_snip(**kwargs)
            #spe.plot(ax2,label='baseline')
            

        if ycalibration:
            #tbd
            pass

        if peak:
            intensity_val,_position = calc_peak_intensity(spe )
            print(intensity_val,_position)
            laser_power_mw = group["laser_power_mw"].unique()
            data4regression.append((id,laser_power_mw[0],intensity_val))

    return data4regression
  
def calc_peak_intensity(spe,peak=144,prominence=0.01,fit_peak= False,peak_intensity="height"):
    try:
        boundaries=(peak-50, peak+50)
        boundaries=(65,300)
        spe = spe.trim_axes(method='x-axis', boundaries=boundaries)
        candidates = spe.find_peak_multipeak(prominence=prominence)
        fig, ax = plt.subplots(figsize=(6,2))

        _position = None
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
            _position = df_sorted.iloc[0]["center"]
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
            _position = df_sorted.iloc[0]["position"]          
            spe.plot(ax=ax, fmt=':',label=_label)
        #return df_sorted[peak_intensity][0]
        return intensity_val, _position
    except Exception as err:
        print(err)
        return None

#reference leds
process(df.loc[(df["source"]=="reference") & (df["role"]=="leds")])
#reference spectra
data4regression_reference = process(df.loc[(df["source"]=="reference") & (df["role"]=="spectra")], pair_normalize= False, baseline= True,ycalibration= True, peak=True)
#twinned leds
process(df.loc[(df["source"]=="twinned") & (df["role"]=="leds")])
#twinned spectra
data4regression = process(df.loc[(df["source"]=="twinned") & (df["role"]=="spectra")] , pair_normalize = True,baseline= True, ycalibration= True, peak = True)


df = pd.DataFrame(data4regression_reference,columns=["id","laser_power_mw","peak_intensity"])
factor_correction = []
for id, group in df.groupby(['id']):

    _intercept,_slope = calc_regression(group[["laser_power_mw"]].values,group[["peak_intensity"]].values)
    factor_correction.append((id[0],_intercept[0],_slope[0]))
df_fc = pd.DataFrame(factor_correction,columns=["id","intercept","slope"])
with pd.ExcelWriter(os.path.join(product["data"],"data4regression_reference.xlsx"), engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='data4regression', index=False)
    df_fc.to_excel(writer, sheet_name='factor_correction', index=False)


df = pd.DataFrame(data4regression,columns=["id","laser_power_mw","peak_intensity"])
factor_correction = []
for id, group in df.groupby(['id']):
    _intercept,_slope = calc_regression(group[["laser_power_mw"]].values,group[["peak_intensity"]].values)
    factor_correction.append((id[0],_intercept[0],_slope[0]))
df_fc = pd.DataFrame(factor_correction,columns=["id","intercept","slope"])    
with pd.ExcelWriter(os.path.join(product["data"],"data4regression_twinned.xlsx"), engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='data4regression', index=False)
    df_fc.to_excel(writer, sheet_name='factor_correction', index=False)
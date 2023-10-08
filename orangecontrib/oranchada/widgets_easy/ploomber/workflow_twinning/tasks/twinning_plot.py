# + tags=["parameters"]
upstream = ["twinning_peaks"]
product = None
probe: None

# -

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


def plot_spectra(row, axes,column=0, reference=True,match_led= None,leds = None, cmap=None, norm = None, fc= None):
    peak= 144
    _left = peak - 50
    _right = peak + 50
    _right_long = 1750
    _color = cmap(norm(row["laser_power_percent"]))
    #_baseline_when = row["baseline_removed"]
    try:
        sc=row["spectrum"]
        sc.plot(ax=axes[0][column],label="{}%".format(row["laser_power_percent"]),c=_color)
        sc = sc.trim_axes(method='x-axis', boundaries=(_left, _right))        
        sc.plot(ax=axes[1][column],label="{}%".format(row["laser_power_percent"]),c=_color)
    except:
        pass


    index=2
    step = 1
    for _tag in ["spectrum_normalized","spectrum_normalized_baseline","spectrum_corrected","spectrum_corrected_baseline","spectrum_harmonized"]:
        try:
            #if _baseline_when=="before LED correction":
            sc=row[_tag]

            _fc = ""
            boundaries =  [(_left, _right)]
            if (_tag == "spectrum_harmonized") :
                _fc = "FC {:.3e}".format(fc)
                boundaries = [(_left, _right),(_left, _right_long)]
            if (_tag in ["spectrum_corrected_baseline"]) :
                boundaries = [(_left, _right),(_left, _right_long)]      
            if (_tag in ["spectrum_corrected"]) & reference :
                boundaries = [(_left, _right),(_left, _right_long)]                             
            for b in boundaries:
                sc1 = sc.trim_axes(method='x-axis', boundaries=b)
                sc1.plot(ax=axes[index][column],label="{}%".format( row["laser_power_percent"]),c=_color)
                axes[index][column].set_title("{}. {} {}".format(step,_tag.replace("_"," "),_fc))
                index =index+1  
            step = step+ 1          
        except Exception as err:
            print(err)
            pass    
       

    try:
        device=row["device"]
       
        led = match_led.loc[device]["led_spectra"]
        sc = leds.loc[led]["spectrum"]
        sc.plot(ax=axes[0][column],label='_nolegend_',c="gray")
        sc = sc.trim_axes(method='x-axis', boundaries=(_left, _right))        
        sc.plot(ax=axes[1][column],label='_nolegend_',c="gray")
        sc.plot(ax=axes[2][column],label='_nolegend_',c="gray")
    except Exception as err:
        print(err)
        pass   


    axes[0][column].set_title("0. {} {} {}".format(row["device"],row["probe"],"(reference)" if reference else ""))
    axes[1][column].set_title("0. (cropped)")

    #plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

devices_h5file= upstream["twinning_peaks"]["data"]
devices = pd.read_hdf(devices_h5file, "devices")
devices.head()

led_frame = pd.read_hdf(devices_h5file, "led")
led_frame.head()

processing = pd.read_hdf(devices_h5file, "processing")
processing.head()

regression = pd.read_hdf(devices_h5file, "regression")
factor_correction = pd.read_hdf(devices_h5file, "factor_correction")
regression,factor_correction

print(factor_correction.iloc[0,0])

leds = pd.read_hdf(devices_h5file, "led")
leds.head()

#match_led = pd.read_hdf(devices_h5file, "match")
#match_led.head()
match_led={
    "reference" : "reference",
    "twinning": "twinning"
}
match_led
    
print(processing.index,processing["field"])
 
cmap = plt.get_cmap('plasma')
norm = mcolors.Normalize(vmin=0, vmax=100)
reference_condition = (devices["reference"]) & (devices["probe"] == probe)
A=devices.loc[reference_condition].sort_values(by='laser_power_percent')
twinned_condition = (~devices["reference"]) & (devices["probe"] == probe)
B =devices.loc[twinned_condition].sort_values(by='laser_power_percent')

A

B

_figlen = 7 
print(processing.shape[0])
fig, axes = plt.subplots(_figlen,2 , figsize=(14,14)) 
A.apply(lambda row: plot_spectra(row,axes, 0, True,match_led,leds,cmap,norm), axis=1)
B.apply(lambda row: plot_spectra(row,axes, 1,False,match_led,leds,cmap,norm,fc=factor_correction.iloc[0,0]), axis=1)
plt.tight_layout()


fig, axes = plt.subplots(1,2, figsize=(10,4)) 
axes[0].plot(A["laser_power"],A["height"],'o',label=A["device"].unique())
A_regr=regression.loc["reference"]
A_pred = A["laser_power"]*A_regr["slope"] + A_regr["intercept"]
axes[0].plot(A["laser_power"],A_pred,'-',label="{:.2e} * LP + {:.2e}".format(A_regr["slope"],A_regr["intercept"]))
B_regr=regression.loc["twinned"]
axes[0].plot(B["laser_power"],B["height"],'+',label=B["device"].unique())
B_pred =B["laser_power"]*B_regr["slope"] + B_regr["intercept"]
axes[0].plot(B["laser_power"],B_pred,'-',label="{:.2e} * LP + {:.2e}".format(B_regr["slope"],B_regr["intercept"]))
#plt.plot(x_values, y_values, color='red', label="Linear Regression Line")
axes[0].set_ylabel("height of the (fitted) peak @ 144cm-1")
axes[0].set_xlabel("laser power, %")
axes[0].legend()
bar_width = 0.2  # Adjust this value to control the width of the groups
bar_positions = np.arange(len(A["laser_power_percent"].values))
axes[1].bar(bar_positions -bar_width,A["area"], width=bar_width,label=str(A["device"].unique()))
bar_positions = np.arange(len(B["laser_power_percent"].values))
axes[1].bar(bar_positions  ,B["area"],width=bar_width,label=str(B["device"].unique()))
axes[1].bar(bar_positions + bar_width,B["area_harmonized"],width=bar_width,label="{} harmonized FC={:.2e}".format(B["device"].unique(),factor_correction.iloc[0,0]))
axes[1].set_ylabel("spectrum area")
axes[1].set_xlabel("laser power, %")
# Set the x-axis positions and labels
plt.xticks(bar_positions, B["laser_power_percent"])
axes[1].legend()
plt.tight_layout()


show_leds = False
if show_leds:
    for index, led_spectra in leds.iterrows():
        fig, axes = plt.subplots(1, 3, figsize=(15, 2))   
        spe_led = led_spectra["spectrum"]   
        spe_led.plot(label=index,ax=axes[0])
        area = led_spectra["area"]
        spe_dist = led_spectra["spe_dist"]
        axes[1].plot(spe_led.x,spe_dist.pdf(spe_led.x))
        axes[2].plot(spe_led.x,spe_dist.pdf(spe_led.x)*area)
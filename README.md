# oranchada
[Orange](https://orangedatamining.com/) workflow add-on for processing [Raman spectra](https://en.wikipedia.org/wiki/Raman_spectroscopy). Based on [ramanchada2](https://github.com/h2020charisma/ramanchada2).

- [Poster: OPEN-SOURCE FOR RAMAN SPECTROSCOPY HARMONISATION](https://zenodo.org/record/8029032)
- [ORANCHADA visual guide (Widget usage examples)](https://zenodo.org/record/8232578)


## Installation

**UPDATE May 2024**: Orange 3.36 and later on Windows is affected by biolab/orange3#6744. Only use versions up to and including 3.35 ([download link](https://download.biolab.si/download/files/Orange3-3.35.0.zip)) and **do not** upgrade it until the bug is resolved. Oranchada can and still should be upgraded as usual when newer versions are available.

**UPDATE May 2023**: This guide used to suggest using the standalone installer of Orange. It is now recommended to use the portable version of Orange instead, which helps to avoid some possible incompatibilities.

1. Depending on your operating system:

    1. **Windows**: Download the *Portable Orange* ZIP from https://download.biolab.si/download/files/Orange3-3.35.0.zip and extract it to some place from which it will be convenient for you to start it. If you are not sure about the place, just extract it to your desktop (it will be possible to move it later if you change your mind). To run Portable Orange, open the shortcut. On the first run, there might be a security warning. In this case, unselect **Always ask before opening this file** and click **Open**.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/b91bbf52-d206-4a36-ad1f-a459723d92d1)

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/1545a7d9-c497-41b4-be97-7ac1e022a3f8)

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/0c45b2f2-62e0-4fc7-8056-8544a0fbf74f)

    2. **Linux**: Use the instructions in https://orangedatamining.com/download/#linux. However, we strongly recommend creating a separate environment (i.e. not the base one) if using Conda or a venv if using pip.

    1. **macOS**: Not tested; the instructions from https://orangedatamining.com/download/#macos should work. Feedback welcome.

1. Once it's installed and running, open **Options** ➡️ **Add-ons**. Note the "Orange Update Available" notification in the lower right corner that may show up at times. Do **not** click download. Refer to the [updating](#updating) section below for more information.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/cc51d79f-26dc-4740-b131-571a7d2ce230)

1. Click the **Add more...** button.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/20935c33-3f03-4e02-8125-34d28c98f426)

1. Type `oranchada` in the **Name** field, then click **Add**.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/6b34b124-3adc-4b1e-980c-958067813a94)

1. Scroll down the list until you find **oranchada**, then click the box next to it so that a check mark appears and *Install* is displayed in the **Action** column. Then click **OK**.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/62bfbea4-3019-41ec-862c-a9069d63abdd)

1. Orange will then proceed with the installation. When ready, it will suggest to restart itself. Click **OK**.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/2d300f92-559a-400f-b0ed-e5972feae3a0)

1. Once Orange restarts, you should see an **Oranchada Easy** and **Pro** categories in the left panel. Click them to reveal all widgets.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/e8fb0a68-9939-4371-a2e5-8486bd9a6d23)

1. To verify the Oranchada installation:

    1. Click the **Load Test Spectra** widget or drag it to the workflow area to the right.

        ![image](https://github.com/h2020charisma/oranchada/assets/1084155/da824cdd-d2c5-4a46-a067-f1139094c4df)
    
    2. Right-click on the widget in the workflow area and select **Open** or simply double click the widget.

        ![image](https://github.com/h2020charisma/oranchada/assets/1084155/64c8527b-b750-4444-b495-71a26f2dab5f)
    
    3. Scroll down the options on the left until you reach the **filenames** section and select an arbitrary filename from the list (e.g., the first one).

        ![image](https://github.com/h2020charisma/oranchada/assets/1084155/948d377e-0b6e-42c0-ac56-94826ccd9ba3)
    
    4. Scroll the options back to the top and click the **Plot** button. If Oranchada was installed correctly, you should see a spectrum visualization on the right.

        ![image](https://github.com/h2020charisma/oranchada/assets/1084155/9ecf6adb-0408-4a74-8f7c-d4b8d1bda2a2)


### Manual installation

If your network connection has very tight security that severely restricts what sites you can access, the usual installation method via **Options** ➡️ **Add-ons** might not work for you. It may be possible to circumvent the problem by installing *oranchada* manually:

1. Open https://pypi.org/project/oranchada/#files and download the "Built Distribution" `.whl` file.
1. Open **Options** ➡️ **Add-ons** then drag & drop the downloaded `.whl` file to the add-ons window.
1. Proceed with the general instructions above, starting from step 5 ("scroll down the list until you find **oranchada**").


## Updating

1. Open **Options** ➡️ **Add-ons**. If there's a new version of *oranchada* or *Orange* itself, they will be listed at the top, with your installed version and the latest available one indicated (e.g. you have `0.0.6` installed and `0.0.7` is the latest available version that you can update to).

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/d4f6281a-4513-4b29-ac79-c907c034b54e)

1. Click the box(es) next to the available updates so that a check mark appears and *Update* is displayed in the **Action** column, then click **OK**.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/1ca79c5e-d1d5-4f94-837f-5721d92e872e)

1. If *Orange* itself has an update in addition to *oranchada*, take note that:

    1. An additional warning will be displayed. Click **OK**.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/83e40eb7-fe70-45c9-82ce-7b42fd1a1edb)

    2. **IMPORTANT**: In case the upgrade fails, click **OK** and repeat the steps above—it should work on the second attempt. Do **NOT** close *Orange* here without repeating the steps! If you do this, you will most likely not be able to start *Orange* again and will have to install it anew from the beginning, possibly losing some of your settings.

    ![image](https://github.com/h2020charisma/oranchada/assets/1084155/78419dcc-73f7-4573-9c80-2cb738ee3f56)


## User guide

[ORANCHADA visual guide (Widget usage examples)](https://zenodo.org/record/8232578)


## Troubleshooting


### Windows cannot find 'Orange\pythonw.exe'

You may encounter the following error message when trying to start the portable Orange:

![image](https://github.com/h2020charisma/oranchada/assets/1084155/d2524a28-f57e-4575-b5f7-73cdbb1343cc)

A possible workaround is to open the `Orange` directory and then the `Scripts` one and start `orange-canvas.exe` from it. You may also need to restart *Orange* manually after installing or updating Oranchada or other add-ons.


### api-ms-win-core-path-l1-1-0.dll missing

You may encouter this or a similar error on Windows 7 and earlier. There are some workarounds, but since they require messing with important Windows components, we cannot recommend them to the casual user.


## For developers

Always use a virtual environment for better reproducibility. [Poetry](https://python-poetry.org/) may be introduced in the future, but currently it is recommended to use Conda.

Start by cloning the repo:

```
git clone https://github.com/h2020charisma/oranchada.git
```

or, if you have write access too:

```
git clone git@github.com:h2020charisma/oranchada.git
```


### Conda

[Miniforge](https://github.com/conda-forge/miniforge) is recommended.

Quick environment setup:

```
conda env create
```

This will create an environment named `oranchada` with Orange and oranchada installed in it. Oranchada will be installed in editable mode (a.k.a. `pip install -e`); restart Orange to have your local changes to the code picked up. To run Orange in the environment (don't forget to activate it first with `conda activate oranchada`) use `orange-canvas`.

If you need to also change the code of some of the dependencies, e.g. [ramanchada2](https://github.com/h2020charisma/ramanchada2), install them in editable mode as well (this should override the previously installed dependency from package). Again, don't forget to do this from within the activated environment.

```
pip install -e ../ramanchada2
```

The quick setup above uses the provided `environment.yml` file. You can create a basic environment yourself too:

```
conda create -n oranchada -c conda-forge -c default pyqt orange3
conda activate oranchada
pip install -e .
```


### Python venv

Make sure to use an appropriate Python version, typically what [Portable Orange](https://orangedatamining.com/download/) is bundled with (you can also check `environment.yml` in this repo). For POSIX systems, [pyenv](https://github.com/pyenv/pyenv) is convenient. For Windows, there's [pyenv-win](https://github.com/pyenv-win/pyenv-win).

```
cd oranchada
python -m venv .venv/oranchada
source .venv/oranchada/bin/activate
pip install -e .
```

For other POSIX shells and Windows, see https://docs.python.org/3/library/venv.html#how-venvs-work


## Acknowledgements

🇪🇺 This project has received funding from the European Union’s Horizon 2020 research and innovation program under [grant agreement No. 952921](https://cordis.europa.eu/project/id/952921).



import sys
import os

from quicklook_sma.utilities import read_config

# Additional QA plotting routines
from quicklook_sma import make_qa_tables, make_all_caltable_txt

# Info for SPW setup
# from lband_pipeline.spw_setup import (create_spw_dict)

# Quicklook imaging
from quicklook_sma.quicklook_imaging import quicklook_continuum_imaging


from casatools import logsink

casalog = logsink()


# Command line inputs.

config_filename = sys.argv[-1]

sma_config = read_config(config_filename)

casalog.post(f"Making quicklook products for: {sma_config['myvis']}")

# Created by hifv_exportdata. Must exist to run!
products_folder = "products"

if not os.path.exists(products_folder):
    os.mkdir(products_folder)

# --------------------------------
# Make quicklook images of targets
# --------------------------------
run_quicklook = True

# Run dirty imaging only for a quicklook
if run_quicklook:

    # Dirty images per sideband per target.
    quicklook_continuum_imaging(config_filename,
                                image_type='target',
                                niter=0, nsigma=5.,
                                output_folder="quicklook_imaging")


    # Gain and bandpass cals. No imaging of the flux cal by default.
    # It's helpful to clean for a few iterations on point source
    # calibrators.
    quicklook_continuum_imaging(config_filename,
                                image_type='calibrator',
                                niter=20, nsigma=5.,
                                output_folder="quicklook_calibrator_imaging")

    os.system("cp -r {0} {1}".format('quicklook_imaging', products_folder))
    os.system("cp -r {0} {1}".format('quicklook_calibrator_imaging', products_folder))

# ----------------------------
# Now make additional QA plots:
# -----------------------------

# Calibration table:
make_all_caltable_txt(config_filename)

# Per field outputs:
make_qa_tables(config_filename,
                output_folder='scan_plots_txt',
                outtype='txt',
                overwrite=False,
                chanavg=16384,)

# make_all_flagsummary_data(myvis, output_folder='perfield_flagfraction_txt')

# Move these folders to the products folder.
os.system("cp -r {0} {1}".format('final_caltable_txt', products_folder))
os.system("cp -r {0} {1}".format('scan_plots_txt', products_folder))
# os.system("cp -r {0} {1}".format('perfield_flagfraction_txt', products_folder))


casalog.post("Finished! To create interactive figures, run QAPlotter in the products"
             " directory.")

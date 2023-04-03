
from glob import glob
import os
import warnings

import numpy as np


from qaplotter.field_plots import target_scan_figure, calibrator_scan_figure

from qaplotter.target_summary_plots import (target_summary_ampfreq_figure,
                                            target_summary_amptime_figure)

from qaplotter.quicklook_target_imaging import make_quicklook_figures

from qaplotter.bp_plots import bp_amp_phase_figures

from qaplotter.amp_phase_cal_plots import (phase_gain_figures,
                                           amp_gain_time_figures,
                                           amp_gain_freq_figures)

from quicklook_sma.html_linking import (make_all_html_links, make_html_homepage,
                                        make_caltable_all_html_links,
                                        make_quicklook_html_links,
                                        make_html_casalog_page,
                                        make_html_manualflag_page)

from quicklook_sma.utilities import read_config, get_calfields, get_field_intents

from quicklook_sma.read_data_sma import (read_field_data_tables,
                                read_bpcal_data_tables,
                                read_BPinitialgain_data_tables,
                                read_phaseshortgaincal_data_tables,
                                read_ampgaincal_time_data_tables,
                                read_ampgaincal_freq_data_tables,
                                read_phasegaincal_data_tables,
                                read_blcal_freq_data_tables)


def make_all_cal_plots(folder, output_folder):

    fig_names = {}

    # Bandpass plots

    table_dict, meta_dict = read_bpcal_data_tables(folder)

    # Check if files exist. If not, skip.
    key0 = list(table_dict.keys())[0]
    if len(table_dict[key0]) > 0:

        meta_dict_0 = meta_dict['amp'][list(meta_dict['amp'].keys())[0]]

        figs = bp_amp_phase_figures(table_dict, meta_dict,
                                    nspw_per_figure=4)

        # Make output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        label = 'Bandpass'

        for i, fig in enumerate(figs):

            out_html_name = f"BP_amp_phase_plotly_interactive_{i}.html"
            fig.write_html(f"{output_folder}/{out_html_name}")

            fig_names[f"{label} {i+1}"] = out_html_name

    # Phase gain cal
    table_dict, meta_dict = read_phasegaincal_data_tables(folder)

    key0 = list(table_dict.keys())[0]
    if len(table_dict[key0]) > 0:

        label = 'Phase Gain Time'

        figs = phase_gain_figures(table_dict, meta_dict,
                                nant_per_figure=8,)

        for i, fig in enumerate(figs):

            out_html_name = f"phasegain_time_plotly_interactive_{i}.html"
            fig.write_html(f"{output_folder}/{out_html_name}")

            fig_names[f"{label} {i+1}"] = out_html_name

    # Amp gain cal time
    table_dict, meta_dict = read_ampgaincal_time_data_tables(folder)

    key0 = list(table_dict.keys())[0]
    if len(table_dict[key0]) > 0:

        label = 'Amp Gain Time'

        figs = amp_gain_time_figures(table_dict, meta_dict,
                                    nant_per_figure=8,)

        for i, fig in enumerate(figs):

            out_html_name = f"ampgain_time_plotly_interactive_{i}.html"
            fig.write_html(f"{output_folder}/{out_html_name}")

            fig_names[f"{label} {i+1}"] = out_html_name

    # Amp gain cal freq
    table_dict, meta_dict = read_ampgaincal_freq_data_tables(folder)

    key0 = list(table_dict.keys())[0]
    if len(table_dict[key0]) > 0:

        figs = amp_gain_freq_figures(table_dict, meta_dict,
                                    nant_per_figure=8,)
        label = 'Amp Gain Freq'

        for i, fig in enumerate(figs):

            out_html_name = f"ampgain_freq_plotly_interactive_{i}.html"
            fig.write_html(f"{output_folder}/{out_html_name}")

            fig_names[f"{label} {i+1}"] = out_html_name

    # BLcal
    # table_dict, meta_dict = read_blcal_freq_data_tables(folder)

    # # Check if files exist. If not, skip.
    # key0 = list(table_dict.keys())[0]
    # if len(table_dict[key0]) > 0:

    #     figs = amp_gain_freq_figures(table_dict, meta_dict,
    #                             nant_per_figure=8,)
    #     label = 'BLcal'

    #     for i, fig in enumerate(figs):

    #         out_html_name = f"blcal_plotly_interactive_{i}.html"
    #         fig.write_html(f"{output_folder}/{out_html_name}")

    #         fig_names[f"{label} {i+1}"] = out_html_name

    # phase short gain cal

    # Check if files exist. If not, skip.
    table_dict, meta_dict = read_phaseshortgaincal_data_tables(folder)

    key0 = list(table_dict.keys())[0]
    if len(table_dict[key0]) > 0:

        label = 'Phase (short) gain'

        figs = phase_gain_figures(table_dict, meta_dict,
                                nant_per_figure=8,)

        for i, fig in enumerate(figs):

            out_html_name = f"phaseshortgaincal_plotly_interactive_{i}.html"
            fig.write_html(f"{output_folder}/{out_html_name}")

            fig_names[f"{label} {i+1}"] = out_html_name

    # BP init phase
    table_dict, meta_dict = read_BPinitialgain_data_tables(folder)

    # Check if files exist. If not, skip.
    key0 = list(table_dict.keys())[0]
    if len(table_dict[key0]) > 0:

        figs = phase_gain_figures(table_dict, meta_dict,
                                nant_per_figure=8,)

        label = 'BP Initial Gain'

        for i, fig in enumerate(figs):

            out_html_name = f"BPinit_phase_plotly_interactive_{i}.html"
            fig.write_html(f"{output_folder}/{out_html_name}")

            fig_names[f"{label} {i+1}"] = out_html_name

    if len(fig_names) > 0:

        make_caltable_all_html_links(output_folder, fig_names, meta_dict_0)



def make_field_plots(config_filename, folder, output_folder,
                     save_fieldnames=False,
                     corrs=['XX', 'YY']):
    '''
    Make all scan plots into an HTML for each target.
    '''

    this_config = read_config(config_filename)

    # Grab all text files.
    txt_files = glob(f"{folder}/*.txt")

    # Make output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    def get_fieldname(filename):
        return "_".join(os.path.basename(filename).split("_")[1:-2])

    fieldnames = [get_fieldname(filename) for filename in txt_files]

    # Get unique names only
    fieldnames = sorted(list(set(fieldnames)))

    if save_fieldnames:
        field_txtfilename = f"{output_folder}/fieldnames.txt"

        if os.path.exists(field_txtfilename):
            os.remove(field_txtfilename)

        with open(field_txtfilename, 'w') as f:

            for field in fieldnames:
                f.write(f"{field}\n")

    meta_dict_0 = read_field_data_tables(fieldnames[0], folder)[1]['amp_time']

    field_intents = {}

    for i, field in enumerate(fieldnames):

        table_dict, meta_dict = read_field_data_tables(field, folder)

        try:
            field_intent = get_field_intents(field, this_config)
        except Exception as exc:
            warnings.warn(f"Unable to find field intent. Raise exception: {exc}")
            field_intent = ''

        meta_dict['intent'] = field_intent

        field_intents[field] = field_intent

        # Target
        if len(table_dict.keys()) == 3:

            fig = target_scan_figure(table_dict, meta_dict, show=False, corrs=corrs,
                                     spw_dict=None,
                                     show_linesonly=False)

        # 10 with amp/phase versus ant 1. 8 without.
        elif len(table_dict.keys()) == 10 or len(table_dict.keys()) == 8:

            fig = calibrator_scan_figure(table_dict, meta_dict, show=False, corrs=corrs,
                                         spw_dict=None)

        else:
            raise ValueError(f"Found {len(table_dict.keys())} tables for {field} instead of 3 or 10.")

        out_html_name = f"{field}_plotly_interactive.html"
        fig.write_html(f"{output_folder}/{out_html_name}")

    # Create summary tables using all target fields
    target_fields = []

    for i, field in enumerate(fieldnames):

        table_dict, meta_dict = read_field_data_tables(field, folder)

        try:
            field_intent = get_field_intents(field, this_config)
        except Exception as exc:
            warnings.warn(f"Unable to find field intent. Raise exception: {exc}")
            field_intent = ''

        if "target" in field_intent.lower():
            target_fields.append(field)

    # Create target field summary plots
    # First check that there were target fields.

    if len(target_fields) > 0:

        try:
            fig_summ_time = target_summary_amptime_figure(target_fields, folder,
                                                        corrs=corrs,
                                                        spw_dict=None,
                                                        show_linesonly=False,
                                                        telescope='sma')
            out_html_name = f"target_amptime_summary_plotly_interactive.html"
            fig_summ_time.write_html(f"{output_folder}/{out_html_name}")
        except Exception as exc:
            warnings.warn("Unable to make summary amp-time figure."
                          f" Raise exception {exc}")

        # Disabled for now. There's too many channels for this to be
        # efficient for viewing.

        # try:
        #     fig_summ_freq = target_summary_ampfreq_figure(target_fields, folder,
        #                                                 corrs=corrs,
        #                                                 spw_dict=None,
        #                                                 show_linesonly=False)
        #     out_html_name = f"target_ampfreq_summary_plotly_interactive.html"
        #     fig_summ_freq.write_html(f"{output_folder}/{out_html_name}")
        # except Exception as exc:
        #     warnings.warn("Unable to make summary amp-freq figure."
        #                   f" Raise exception {exc}")

    # Make the linking files into the same folder.
    make_all_html_links(output_folder, field_intents, meta_dict_0)


def make_all_quicklook_plots(folder="quicklook_imaging",
                             output_folder="quicklook_imaging_figures"):

    # Generate the quicklook plots.
    target_dict, summary_filenames = make_quicklook_figures(folder, output_folder)

    # Up this number as we're currently doing per sideband.
    # Only up to 4 images per field.
    fields_per_page = 10

    make_quicklook_html_links(output_folder, target_dict,
                              summary_filenames,
                              fields_per_page=fields_per_page)



def make_all_plots(config_filename=None,
                   folder_fields="scan_plots_txt",
                   output_folder_fields="scan_plots_QAplots",
                   folder_cals="final_caltable_txt",
                   output_folder_cals="final_caltable_QAplots",
                   folder_qlimg="quicklook_imaging",
                   output_folder_qlimg="quicklook_imaging_figures",
                   folder_cal_qlimg="quicklook_calibrator_imaging",
                   output_folder_cal_qlimg="quicklook_calibrator_imaging_figures",
                   save_fieldnames=True,
                   corrs=['XX', 'YY'],
                   logfile_name='casa_reduction.log',
                   flagfile_name='manual_flags.txt'
                   ):
    '''

    Parameters
    ----------
    folder_fields : str, optional
        Folder where the txt files per field are located.
    output_folder_fields : str, optional
        Output folder to place the interactive HTML figures per field.
    folder_BPs : str, optional
        Folder where the txt files for bandpass solutions per SPW are located.
    output_folder_BPs : str, optional
        Output folder to place the interactive HTML figures per bandpass SPW solution.
    corrs : list, optional
        Give which correlations to show in the plots. Default is ['XX', 'YY']. To show
        the cross terms, give: ['LL', 'RR', 'LR', 'RL'].
    '''

    ms_info_dict = {}

    if config_filename is None:
        # Search for a config filename in the folder we're working in
        from glob import glob
        config_filenames = list(glob("*.cfg"))
        if len(config_filenames) == 0:
            raise ValueError("Unable to find a config file. Specify manually.")
        elif len(config_filenames) > 1:
            print(f"Found multiple possible config filenames. Choosing the first one: {config_filenames[0]}")
            config_filename = config_filenames[0]
        else:
            config_filename = config_filenames[0]

    this_config = read_config(config_filename)
    msname = this_config['myvis']

    ms_info_dict['vis'] = msname

    make_html_homepage(".", ms_info_dict)

    make_html_casalog_page(".", logfile_name=logfile_name)

    make_html_manualflag_page(".", flagfile_name=flagfile_name)

    make_field_plots(config_filename, folder_fields, output_folder_fields,
                     save_fieldnames=save_fieldnames,
                     corrs=corrs)

    if os.path.exists(folder_cals):
        # Calibration plots
        make_all_cal_plots(folder_cals, output_folder_cals)

    else:
        print("No cal plot txt files were found. Skipping.")

    if os.path.exists(folder_qlimg):
        # Quicklook target images
        make_all_quicklook_plots(folder_qlimg,
                                 output_folder_qlimg)

    else:
        print("No quicklook images were found. Skipping.")

    if os.path.exists(folder_cal_qlimg):
        # Quicklook target images
        make_all_quicklook_plots(folder_cal_qlimg,
                                 output_folder_cal_qlimg)

    else:
        print("No quicklook calibrator images were found. Skipping.")

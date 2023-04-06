
'''

Routines for creating additional QA plots.

'''


import os
import numpy as np

import quicklook_sma.utilities as utils


def make_qa_tables(config_file,
                   output_folder='scan_plots_txt',
                   outtype='txt',
                   overwrite=True,
                   chanavg_vs_time=16384,
                   chanavg_vs_chan=1,
                   datacolumn='corrected'):

    '''
    Specifically for saving txt tables. Replace the scan loop in
    `make_qa_scan_figures` to make fewer but larger tables.

    '''

    from casatools import logsink

    casalog = logsink()

    from casatools import table
    tb = table()

    from casaplotms import plotms

    casalog.post("Running make_qa_tables to export txt files for QA.")
    print("Running make_qa_tables to export txt files for QA.")

    # Read in config settings:
    this_config = utils.read_config(config_file)

    ms_name = this_config['myvis']

    # Make folder for scan plots
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    else:
        if overwrite:
            casalog.post(message="Removing plot tables in {}".format(output_folder), origin='make_qa_tables')
            print("Removing plot tables in {}".format(output_folder))
            os.system("rm -r {}/*".format(output_folder))
        else:
            casalog.post("{} already exists. Will skip existing files.".format(output_folder))
            # raise ValueError("{} already exists. Enable overwrite=True to rerun.".format(output_folder))

    # Read the field names
    tb.open(os.path.join(ms_name, "FIELD"))
    names = tb.getcol('NAME')
    numFields = tb.nrows()
    tb.close()

    # Get calibrator names:
    cal_fields = utils.get_calfields(this_config)

    # This should always return all the science fields.
    science_fields = utils.get_mosaicfields(this_config)

    # Determine the fields that are calibrators.
    tb.open(ms_name)
    is_calibrator = np.zeros((numFields,), dtype='bool')

    has_data = np.ones((numFields,), dtype='bool')

    for ii in range(numFields):
        subtable = tb.query('FIELD_ID==%s' % ii)

        this_field = names[ii]

        # Is there any data for this field?
        has_data[ii] = subtable.nrows() > 0

        # Is the intent for calibration?
        if this_field in cal_fields.split(","):
            is_calibrator[ii] = True

        # Add a check here for skipping some sources
        # This is particularly needed as sources not identified in
        # the cfg file will not have been calibrated.
        if not is_calibrator[ii] and this_field not in science_fields.split(","):
            has_data[ii] = False

    tb.close()

    casalog.post(message="Fields are: {}".format(names), origin='make_qa_tables')
    casalog.post(message="Calibrator fields are: {}".format(names[is_calibrator]), origin='make_qa_tables')

    print("Fields are: {}".format(names))
    print("Calibrator fields are: {}".format(names[is_calibrator]))

    # Loop through fields. Make separate tables only for different targets.

    for ii in range(numFields):
        casalog.post(message="On field {}".format(names[ii]), origin='make_qa_plots')
        print("On field {}".format(names[ii]))

        # If field has data, continue. If not skip and log it.
        if not has_data[ii]:
            casalog.post(message='Field {} has no data in the table. Skipping.'.format(names[ii]),
                         origin='make_qa_plots')
            continue

        # Amp vs. time
        amptime_filename = os.path.join(output_folder,
                                        'field_{0}_amp_time.{1}'.format(names[ii], outtype))

        if not os.path.exists(amptime_filename):

            plotms(vis=ms_name,
                xaxis='time',
                yaxis='amp',
                ydatacolumn=datacolumn,
                selectdata=True,
                field=names[ii],
                scan="",
                spw="",
                avgchannel=str(chanavg_vs_time),
                correlation="",
                averagedata=True,
                avgbaseline=True,
                transform=False,
                extendflag=False,
                plotrange=[],
                # title='Amp vs Time: Field {0} Scan {1}'.format(names[ii], jj),
                xlabel='Time',
                ylabel='Amp',
                showmajorgrid=False,
                showminorgrid=False,
                plotfile=amptime_filename,
                overwrite=True,
                showgui=False)
        else:
            casalog.post(message="File {} already exists. Skipping".format(amptime_filename),
                         origin='make_qa_tables')

        # Amp vs. channel
        ampchan_filename = os.path.join(output_folder,
                                     'field_{0}_amp_chan.{1}'.format(names[ii], outtype))

        if not os.path.exists(ampchan_filename):

            plotms(vis=ms_name,
                xaxis='chan',
                yaxis='amp',
                ydatacolumn=datacolumn,
                selectdata=True,
                field=names[ii],
                scan="",
                spw="",
                avgchannel=str(chanavg_vs_chan),
                avgtime="1e8",
                correlation="",
                averagedata=True,
                avgbaseline=True,
                transform=False,
                extendflag=False,
                plotrange=[],
                # title='Amp vs Chan: Field {0} Scan {1}'.format(names[ii], jj),
                xlabel='Channel',
                ylabel='Amp',
                showmajorgrid=False,
                showminorgrid=False,
                plotfile=ampchan_filename,
                overwrite=True,
                showgui=False)
        else:
            casalog.post(message="File {0} already exists. Skipping".format(ampchan_filename),
                        origin='make_qa_tables')

        # Plot amp vs uvdist
        ampuvdist_filename = os.path.join(output_folder,
                                     'field_{0}_amp_uvdist.{1}'.format(names[ii], outtype))

        if not os.path.exists(ampuvdist_filename):

            plotms(vis=ms_name,
                xaxis='uvdist',
                yaxis='amp',
                ydatacolumn=datacolumn,
                selectdata=True,
                field=names[ii],
                scan="",
                spw="",
                avgchannel=str(chanavg_vs_time),
                avgtime='1e8',
                correlation="",
                averagedata=True,
                avgbaseline=False,
                transform=False,
                extendflag=False,
                plotrange=[],
                # title='Amp vs UVDist: Field {0} Scan {1}'.format(names[ii], jj),
                xlabel='uv-dist',
                ylabel='Amp',
                showmajorgrid=False,
                showminorgrid=False,
                plotfile=ampuvdist_filename,
                overwrite=True,
                showgui=False)
        else:
            casalog.post(message="File {} already exists. Skipping".format(ampuvdist_filename),
                         origin='make_qa_tables')

        # Make phase plots if a calibrator source.

        if is_calibrator[ii]:

            casalog.post("This is a calibrator. Exporting phase info, too.")
            print("This is a calibrator. Exporting phase info, too.")

            # Plot phase vs time

            phasetime_filename = os.path.join(output_folder,
                                         'field_{0}_phase_time.{1}'.format(names[ii], outtype))

            if not os.path.exists(phasetime_filename):

                plotms(vis=ms_name,
                    xaxis='time',
                    yaxis='phase',
                    ydatacolumn=datacolumn,
                    selectdata=True,
                    field=names[ii],
                    scan="",
                    spw="",
                    correlation="",
                    avgchannel=str(chanavg_vs_time),
                    averagedata=True,
                    avgbaseline=True,
                    transform=False,
                    extendflag=False,
                    plotrange=[],
                    # title='Phase vs Time: Field {0} Scan {1}'.format(names[ii], jj),
                    xlabel='Time',
                    ylabel='Phase',
                    showmajorgrid=False,
                    showminorgrid=False,
                    plotfile=phasetime_filename,
                    overwrite=True,
                    showgui=False)
            else:
                casalog.post(message="File {} already exists. Skipping".format(phasetime_filename),
                            origin='make_qa_tables')

            # Plot phase vs channel
            phasechan_filename = os.path.join(output_folder,
                                         'field_{0}_phase_chan.{1}'.format(names[ii], outtype))

            if not os.path.exists(phasechan_filename):

                plotms(vis=ms_name,
                    xaxis='chan',
                    yaxis='phase',
                    ydatacolumn=datacolumn,
                    selectdata=True,
                    field=names[ii],
                    scan="",
                    spw="",
                    avgchannel=str(chanavg_vs_chan),
                    avgtime="1e8",
                    correlation="",
                    averagedata=True,
                    avgbaseline=True,
                    transform=False,
                    extendflag=False,
                    plotrange=[],
                    # title='Phase vs Chan: Field {0} Scan {1}'.format(names[ii], jj),
                    xlabel='Chan',
                    ylabel='Phase',
                    showmajorgrid=False,
                    showminorgrid=False,
                    plotfile=phasechan_filename,
                    overwrite=True,
                    showgui=False)
            else:
                casalog.post(message="File {} already exists. Skipping".format(phasechan_filename),
                            origin='make_qa_tables')

            # Plot phase vs uvdist
            phaseuvdist_filename = os.path.join(output_folder,
                                         'field_{0}_phase_uvdist.{1}'.format(names[ii], outtype))

            if not os.path.exists(phaseuvdist_filename):

                plotms(vis=ms_name,
                    xaxis='uvdist',
                    yaxis='phase',
                    ydatacolumn=datacolumn,
                    selectdata=True,
                    field=names[ii],
                    scan="",
                    spw="",
                    correlation="",
                    avgchannel=str(chanavg_vs_time),
                    avgtime='1e8',
                    averagedata=True,
                    avgbaseline=False,
                    transform=False,
                    extendflag=False,
                    plotrange=[],
                    # title='Phase vs UVDist: Field {0} Scan {1}'.format(names[ii], jj),
                    xlabel='uv-dist',
                    ylabel='Phase',
                    showmajorgrid=False,
                    showminorgrid=False,
                    plotfile=phaseuvdist_filename,
                    overwrite=True,
                    showgui=False)

            else:
                casalog.post(message="File {} already exists. Skipping".format(phaseuvdist_filename),
                            origin='make_qa_tables')

            # Plot amp vs phase
            ampphase_filename = os.path.join(output_folder,
                                         'field_{0}_amp_phase.{1}'.format(names[ii], outtype))

            if not os.path.exists(ampphase_filename):

                plotms(vis=ms_name,
                    xaxis='amp',
                    yaxis='phase',
                    ydatacolumn=datacolumn,
                    selectdata=True,
                    field=names[ii],
                    scan="",
                    spw="",
                    correlation="",
                    avgchannel=str(chanavg_vs_time),
                    avgtime='1e8',
                    averagedata=True,
                    avgbaseline=False,
                    transform=False,
                    extendflag=False,
                    plotrange=[],
                    # title='Amp vs Phase: Field {0} Scan {1}'.format(names[ii], jj),
                    xlabel='Phase',
                    ylabel='Amp',
                    showmajorgrid=False,
                    showminorgrid=False,
                    plotfile=ampphase_filename,
                    overwrite=True,
                    showgui=False)
            else:
                casalog.post(message="File {} already exists. Skipping".format(ampphase_filename),
                            origin='make_qa_tables')

            # Plot uv-wave vs, amp - model residual
            # Check how good the point-source calibrator model is.

            ampresid_filename = os.path.join(output_folder,
                                         'field_{0}_ampresid_uvwave.{1}'.format(names[ii],
                                                                                outtype))

            if not os.path.exists(ampresid_filename):

                plotms(vis=ms_name,
                    xaxis='uvwave',
                    yaxis='amp',
                    ydatacolumn='corrected-model_scalar',
                    selectdata=True,
                    field=names[ii],
                    scan="",
                    spw="",
                    correlation="",
                    avgchannel=str(chanavg_vs_time),
                    avgtime='1e8',
                    averagedata=True,
                    avgbaseline=False,
                    transform=False,
                    extendflag=False,
                    plotrange=[],
                    xlabel='uv-dist',
                    ylabel='Phase',
                    showmajorgrid=False,
                    showminorgrid=False,
                    plotfile=ampresid_filename,
                    overwrite=True,
                    showgui=False)

            else:
                casalog.post(message="File {} already exists. Skipping".format(ampresid_filename),
                             origin='make_qa_tables')

            # Plot amplitude vs antenna 1.
            # Check for ant outliers

            ampant_filename = os.path.join(output_folder,
                                         'field_{0}_amp_ant1.{1}'.format(names[ii],
                                                                         outtype))

            if not os.path.exists(ampant_filename):

                plotms(vis=ms_name,
                    xaxis='antenna1',
                    yaxis='amp',
                    ydatacolumn=datacolumn,
                    selectdata=True,
                    field=names[ii],
                    scan="",
                    spw="",
                    correlation="",
                    avgchannel=str(chanavg_vs_time),
                    avgtime='1e8',
                    averagedata=True,
                    avgbaseline=False,
                    transform=False,
                    extendflag=False,
                    plotrange=[],
                    xlabel='antenna 1',
                    ylabel='Amp',
                    showmajorgrid=False,
                    showminorgrid=False,
                    plotfile=ampant_filename,
                    overwrite=True,
                    showgui=False)

            else:
                casalog.post(message="File {} already exists. Skipping".format(ampant_filename),
                             origin='make_qa_tables')


            # Plot phase vs antenna 1.
            # Check for ant outliers

            phaseant_filename = os.path.join(output_folder,
                                         'field_{0}_phase_ant1.{1}'.format(names[ii],
                                                                         outtype))

            if not os.path.exists(phaseant_filename):

                plotms(vis=ms_name,
                    xaxis='antenna1',
                    yaxis='phase',
                    ydatacolumn=datacolumn,
                    selectdata=True,
                    field=names[ii],
                    scan="",
                    spw="",
                    correlation="",
                    avgchannel=str(chanavg_vs_time),
                    avgtime='1e8',
                    averagedata=True,
                    avgbaseline=False,
                    transform=False,
                    extendflag=False,
                    plotrange=[],
                    xlabel='antenna 1',
                    ylabel='Phase',
                    showmajorgrid=False,
                    showminorgrid=False,
                    plotfile=phaseant_filename,
                    overwrite=True,
                    showgui=False)

            else:
                casalog.post(message="File {} already exists. Skipping".format(phaseant_filename),
                             origin='make_qa_tables')



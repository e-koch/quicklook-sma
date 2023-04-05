
import requests
from datetime import datetime
from glob import glob

import numpy as np
from astropy.table import Column, Table
from astropy.time import Time
import astropy.units as u


alt_name_mapping = {"ngc315": "0057+303",
                    "3c84": "0319+415",
                    "3c111": "0418+380",
                    "3c120": "0433+053",
                    "3c147": "0542+498",
                    "3c207": "0840+132",
                    "oj287": "0854+201",
                    "mrk421": "1104+382",
                    "3c273": "1229+020",
                    "3c274": "1230+123",
                    "3c279": "1256-057",
                    "cen a": "1325-430",
                    "3c286": "1331+305",
                    "3c309.1": "1459+716",
                    "nrao512": "1640+397",
                    "3c345": "1642+398",
                    "mrk501": "1653+397",
                    "nrao530": "1733-130",
                    "3c371": "1806+698",
                    "3c380": "1829+487",
                    "3c395": "1902+319",
                    "3c418": "2038+513",
                    "p2134+0": "2136+006",
                    "bllac": "2202+422",
                    "3c446": "2225-049",
                    "3c454.3": "2253+161"}


def get_flux_data(name='3c84', return_table=False,
                  write_table=True):

    # Check if an alternative name may be used:
    if name.lower() in alt_name_mapping:
        name_for_url = alt_name_mapping[name.lower()]
    else:
        name_for_url = name

    if "+" in name_for_url:
        url_name = name_for_url.replace("+", "%2B")
    else:
        url_name = name_for_url

    url = f"http://sma1.sma.hawaii.edu/callist/callist.html?data={url_name}"

    html = requests.get(url).content
    html_str = html.decode('utf-8')

    if "Data not found" in html_str:
        print(f"Cannot find flux data for given name {name}")
        print(f"Check whether this URL exists: {url}")
        return None

    html_tab = "BAND" + html_str.split('BAND')[-1]

    lines = []

    for ii, this_line in enumerate(html_tab.split("\n")):
        if ii == 0:
            header = this_line.split("  ")
            header = [val.strip(" ") for val in header if len(val) > 0]
            continue
        elif "end PAGE CONTENT" in this_line:
            break
        elif "</pre>" in this_line:
            break
        # Split out the values and format

        # Just brute force the extraction
        vals = this_line.split("  ")
        vals = [val.strip(" ") for val in vals if len(val) > 0]

        band = vals[0]
        date = vals[1][:-6]
        time = vals[1][-5:]
        obs = vals[2]
        freq = float(vals[3])
        flux = float(vals[4].split("+/-")[0])
        flux_err = float(vals[5])
        piname = vals[6]

        datetime_object = datetime.strptime(f"{date} {time}",
                                            '%d %b %Y %H:%M')

        this_time = Time(datetime_object)

        lines.append([band, date, time, obs,
                    freq, flux, flux_err, piname, this_time.mjd])

    header.append('MJD')

    cols = []
    for ii, colname in enumerate(header):
        vals = [line[ii] for line in lines]

        this_col = Column(vals, name=colname)

        cols.append(this_col)

    flux_table = Table(cols, names=header,)

    if write_table:
        flux_table.write(f"{name}_flux.csv", overwrite=True)

    if return_table:
        return flux_table


def interpolate_flux_to_date(tab_flux,
                             target_date_mjd,
                             fitted_flux=None,
                             fitted_fluxerr=None,
                             freq=230*u.GHz,
                             delta_freq=20*u.GHz,
                             min_pts_raise=5,
                             spline_type='pchip',
                             plot_spline=True,
                             plot_fileprefix="source"):
    '''
    Build an interpolation model from the give flux table
    and estimate the most likely flux for a given date.

    '''

    from scipy.interpolate import CubicSpline, PchipInterpolator

    if not isinstance(target_date_mjd, Time):
        time_mjd = Time(target_date_mjd, format='mjd')
    else:
        time_mjd = target_date_mjd

    # Find flux values within the set frequency range.
    freq_min = (freq - delta_freq/2).to(u.GHz)
    freq_max = (freq + delta_freq/2).to(u.GHz)
    mask_valid_bands = np.logical_and(tab_flux['F(GHz)'] >= freq_min.value,
                                      tab_flux['F(GHz)'] <= freq_max.value)

    if mask_valid_bands.sum() < min_pts_raise:
        # raise ValueError(f"Found less than {min_pts_raise} for the given frequency range {freq_min}-{freq_max}.")

        print(f"Found less than {min_pts_raise} for the given frequency range {freq_min}-{freq_max}.")
        print("Even more than normal: really don't trust the interpolation!")

    # https://docs.scipy.org/doc/scipy/tutorial/interpolate/1D.html#monotone-interpolants
    mjd_vals = np.array(tab_flux['MJD'][mask_valid_bands])

    incr_order = np.argsort(mjd_vals)

    # Force increasing order in time:
    mjd_vals = mjd_vals[incr_order]
    flux_vals = np.array(tab_flux['FLUX(JY)'][mask_valid_bands][incr_order])
    flux_errs = np.array(tab_flux['ERROR'][mask_valid_bands][incr_order])

    # The interpolation will also fail if there are 2 points at a single time.
    # e.g. 3c84 has two fluxes for the same time at the same frequency.
    # I'm going to pick the first on in these cases and consider it a corner case for now.
    while (np.diff(mjd_vals) == 0).any():
        mjd_rep_index = np.diff(mjd_vals).argmin()+1

        print(f"Deleting index {mjd_rep_index} due to multiple flux vals at same time")

        mjd_vals = np.delete(mjd_vals, [mjd_rep_index])
        flux_vals = np.delete(flux_vals, [mjd_rep_index])
        flux_errs = np.delete(flux_errs, [mjd_rep_index])

    if spline_type == 'pchip':
        interp = PchipInterpolator(mjd_vals, flux_vals)
    elif spline_type == 'cubics':
        interp = CubicSpline(mjd_vals, flux_vals)
    else:
        raise ValueError(f"spline_type must be 'pchip' or 'cubic'. Given {spline_type}.")

    if plot_spline:
        import matplotlib.pyplot as plt

        mjd_val_resamp = np.linspace(mjd_vals.min(), mjd_vals.max(),
                                     num=3*len(mjd_vals))

        ax = plt.subplot(211)
        # plt.errorbar(mjd_vals, flux_vals, yerr=flux_errs)
        plt.fill_between(mjd_vals, flux_vals-flux_errs,
                         y2=flux_vals+flux_errs,
                         alpha=0.5, facecolor='#40B0A6')
        plt.plot(mjd_vals, flux_vals, 'o--', color='#40B0A6')

        plt.plot(mjd_val_resamp, interp(mjd_val_resamp), color='#E1BE6A',
                 linewidth=2)

        # Show where our chosen time is located:
        plt.axvline(time_mjd.mjd, alpha=0.5, linewidth=4, color='gray')
        plt.plot(time_mjd.mjd, interp(time_mjd.mjd), 'D', markersize=10, color='gray')

        # If a pre-solved fit is given, plot it here:
        if fitted_flux is not None:
            plt.plot(time_mjd.mjd, fitted_flux, 'o', markersize=10, color='black')


        # Show location of zoom region in other subplots:
        plt.axvline(time_mjd.mjd - 50, alpha=0.5, linewidth=2, color='black',
                    linestyle='--')
        plt.axvline(time_mjd.mjd + 50, alpha=0.5, linewidth=2, color='black',
                    linestyle='--')

        ax.grid(True)
        ax.set_ylim(bottom=0)

        # Zoom in around requested date by \pm50 days.
        plt.subplot(212)

        zoom_samp_mask = np.logical_and(mjd_vals >= time_mjd.mjd - 50,
                                        mjd_vals <= time_mjd.mjd + 50)

        zoom_resamp_mask = np.logical_and(mjd_val_resamp >= time_mjd.mjd - 50,
                                          mjd_val_resamp <= time_mjd.mjd + 50)

        # plt.errorbar(mjd_vals[zoom_samp_mask],
        #              flux_vals[zoom_samp_mask],
        #              yerr=flux_errs[zoom_samp_mask])
        # plt.plot(mjd_val_resamp[zoom_resamp_mask],
        #          interp(mjd_val_resamp)[zoom_resamp_mask])

        plt.fill_between(mjd_vals[zoom_samp_mask],
                         (flux_vals-flux_errs)[zoom_samp_mask],
                         y2=(flux_vals+flux_errs)[zoom_samp_mask],
                         alpha=0.5, facecolor='#40B0A6')
        plt.plot(mjd_vals[zoom_samp_mask],
                 flux_vals[zoom_samp_mask], 'o--', color='#40B0A6')

        plt.plot(mjd_val_resamp[zoom_resamp_mask],
                 interp(mjd_val_resamp)[zoom_resamp_mask], color='#E1BE6A',
                 linewidth=2)

        # Show where our chosen time is located:
        plt.axvline(time_mjd.mjd, alpha=0.5, linewidth=4, color='gray')
        plt.plot(time_mjd.mjd, interp(time_mjd.mjd), 'D',
                 markersize=10, color='gray', drawstyle='steps-mid',
                 label='Interpolation')

        # If a pre-solved fit is given, plot it here:
        if fitted_flux is not None:
            if fitted_fluxerr is None:
                plt.plot(time_mjd.mjd, fitted_flux, 'o', markersize=5, color='black',
                         label='Fit from this obs')
            else:
                plt.errorbar(time_mjd.mjd, fitted_flux,
                             yerr=fitted_fluxerr,
                             fmt='o',
                             markersize=5, color='black',
                             label='Fit from this obs')

        plt.legend(loc='best', frameon=True)

        plt.savefig(f"{plot_fileprefix}_interp_flux_estimate_MJD{time_mjd.mjd:.1f}.png",
                    dpi=300)
        plt.close()

    return interp(time_mjd.mjd)


def plot_all_calfluxes(table_name, output_dir='fluxfit_plots'):
    '''
    Given an output csv table with the sources and flux fits, compare the fitted flux
    from the observation to the flux monitoring values.

    This is primarily meant to visually identify really bad fitted flux solutions.
    '''

    tab = Table.read(table_name)

    field_names = tab['field']

    ref_freq = (tab['fitRefFreq'][0] * u.Hz).to(u.GHz)
    ref_freq_label = f"{ref_freq:.0f}".replace(" ", "")

    # I'm running this in a larger pipeline that keeps the original
    # MIR filename when creating the MS and running the reduction in CASA
    # (that also sets the name of the fluxscale csv file).
    # We're just going to assume then that the name contains the date.
    # TODO: do something more robust here.
    date_and_time_str = table_name.split("_bin")[0]
    datetime_object = datetime.strptime(date_and_time_str,
                                        '%y%m%d_%H:%M:%S')
    this_mjd = Time(datetime_object).mjd

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    plotname_list = []

    for ii, this_field in enumerate(field_names):

        # Grab the flux data:
        tab_flux = get_flux_data(name=this_field,
                                 return_table=True,
                                 write_table=False)

        # Do the interpolation (for plotting purposes) and make the timeseries
        # plot with the fit point overlaid.
        val = interpolate_flux_to_date(tab_flux,
                             this_mjd,
                             fitted_flux=tab['fitFluxd'][ii],
                             fitted_fluxerr=tab['fitFluxdErr'][ii],
                             freq=ref_freq,
                             delta_freq=20*u.GHz,
                             min_pts_raise=5,
                             spline_type='pchip',
                             plot_spline=True,
                             plot_fileprefix=f"fluxfit_plots/{this_field}_{ref_freq_label}")

        # Gather the plot filenames.
        this_plot_filename = glob(f"fluxfit_plots/{this_field}_{ref_freq_label}*.png")
        if not len(this_plot_filename) == 1:
            raise ValueError("Unable to find flux plot file.")
        this_plot_filename = this_plot_filename[0]

        plotname_list.append(this_plot_filename)

    return plotname_list

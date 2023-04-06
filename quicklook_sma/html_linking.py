
'''
Function for embedding interactive plots and adding links, etc.
'''

from pathlib import Path
import numpy as np



def generate_webserver_track_link():
    '''
    Return a link to the home page for a given track.

    '''

    track_links = {}

    track_links["Track Home"] = "index.html"


    track_links['Calibration Plots'] = "final_caltable_QAplots/index.html"

    track_links['Field QA Plots'] = "scan_plots_QAplots/index.html"

    track_links['Sci Images'] = "quicklook_imaging_figures/index.html"
    track_links['Cal Images'] = "quicklook_calibrator_imaging_figures/index.html"

    track_links['Flux Scaling Plots'] = "flux_scaling.html"

    track_links['CASA Log'] = "casa_pipeline.html"

    track_links['Manual Flags'] = "casa_manualflags.html"

    track_links['CASA Script'] = "casa_script.html"

    track_links['Field Names'] = "scan_plots_QAplots/fieldnames.txt"


    return track_links


def make_index_html_homepage(config_filename, ms_info_dict,):
    '''
    Home page for the track with links to the weblogs, QA plots, etc.
    '''


    html_string = make_html_preamble()

    link_locations = generate_webserver_track_link()

    html_string += '<div class="navbar">\n'

    for linkname in link_locations:

        html_string += f'    <a href="{link_locations[linkname]}">{linkname}</a>\n'

    html_string += "</div>\n\n"

    # Add in MS info:
    html_string += '<div class="content" id="basic">\n'
    html_string += f'<h2>{ms_info_dict["vis"]}</h2>\n'


    # Embed the config file inputs into the main page.
    html_string += '\n'
    html_string += f'<iframe src="{config_filename}" height="100%" width=90%>\n'
    html_string += 'If you are seeing this, you need a browser understands IFrames.\n'
    html_string += '</iframe>\n'

    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_html_homepage(folder, config_filename, ms_info_dict,):

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "index.html"

    if index_file.exists():
        index_file.unlink()

    print(make_index_html_homepage(config_filename, ms_info_dict),
          file=open(index_file, 'a'))


def make_all_html_links(folder, field_dict, ms_info_dict):
    '''
    Make and save all html files for linking the interactive plots
    together.
    '''

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "index.html"

    if index_file.exists():
        index_file.unlink()

    print(make_index_html_page(field_dict,
                               ms_info_dict),
          file=open(index_file, 'a'))

    # Make linking files for the target summary plots:
    targsumm1_file = mypath / f"linker_target_amptime_summary_plotly_interactive.html"

    if targsumm1_file.exists():
        targsumm1_file.unlink()

    print(make_targsumm_html_page("target_amptime_summary", field_dict, active_idx=0),
            file=open(targsumm1_file, 'a'))

    targsumm2_file = mypath / f"linker_target_ampfreq_summary_plotly_interactive.html"

    if targsumm2_file.exists():
        targsumm2_file.unlink()

    print(make_targsumm_html_page("target_ampfreq_summary", field_dict, active_idx=1),
            file=open(targsumm2_file, 'a'))

    # Loop through the fields
    for i, field in enumerate(field_dict):

        field_file = mypath / f"linker_{field}.html"

        if field_file.exists():
            field_file.unlink()

        print(make_plot_html_page(field_dict, active_idx=i),
              file=open(field_file, 'a'))


def make_index_html_page(field_dict, ms_info_dict):

    html_string = make_html_preamble()

    field_list = list(field_dict.keys())

    # Add navigation bar with link to other QA products
    active_idx = 0
    html_string += make_next_previous_navbar(prev_field=None,
                                             next_field=field_list[min(active_idx + 1, len(field_list))],
                                             current_field=field_list[active_idx])

    html_string += make_sidebar(field_dict, active_idx=None)

    # Add in MS info:
    html_string += '<div class="content" id="basic">\n'
    html_string += f'<h2>{ms_info_dict["vis"]}</h2>\n'

    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_plot_html_page(field_dict, active_idx=0):

    html_string = make_html_preamble()

    field_list = list(field_dict.keys())

    prev_field = field_list[active_idx - 1] if active_idx != 0 else None
    next_field = field_list[active_idx + 1] if active_idx < len(field_list) - 1 else None

    html_string += make_next_previous_navbar(prev_field, next_field,
                                             current_field=field_list[active_idx])

    html_string += make_sidebar(field_dict, active_idx=active_idx+2)

    html_string += make_content_div(field_list[active_idx])

    html_string += make_html_suffix()

    return html_string

def make_targsumm_html_page(summary_name, field_dict, active_idx=0):

    html_string = make_html_preamble()

    field_list = list(field_dict.keys())

    prev_field = field_list[active_idx - 1] if active_idx != 0 else None
    next_field = field_list[active_idx + 1] if active_idx < len(field_list) - 1 else None

    html_string += make_next_previous_navbar(prev_field, next_field,
                                             current_field=field_list[active_idx])

    html_string += make_sidebar(field_dict, active_idx=active_idx)

    summ_name = ''

    html_string += f'<div class="content" id="{summary_name}">\n'

    html_string += f'    <iframe id="igraph" scrolling="yes" style="border:none;" seamless="seamless" src="{summary_name}_plotly_interactive.html" height="1000" width="100%"></iframe>\n'

    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def css_page_style():
    '''
    '''

    css_style_str = \
'''
body {
  margin: 0;
  font-family: "Lato", sans-serif;
}


 /* The navigation bar */
.navbar {
  overflow: auto;
  background-color: #f1f1f1;
  position: fixed; /* Set the navbar to fixed position */
  top: 0; /* Position the navbar at the top of the page */
  width: 100%; /* Full width */
  margin-left: 200px;
}

/* Links inside the navbar */
.navbar a {
  float: left;
  display: block;
  color: black;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
}

/* Change background on mouse-over */
.navbar a:hover {
  background: #555;
  color: white;
}

/* Main content */
.main {
  margin-top: 30px; /* Add a top margin to avoid content overlay */
}

.sidebar {
  margin: 0;
  padding: 0;
  width: 200px;
  background-color: #f1f1f1;
  position: fixed;
  height: 100%;
  overflow: auto;
}

.sidebar a {
  display: block;
  color: black;
  padding: 16px;
  text-decoration: none;
}

.sidebar a.active {
  background-color: #4CAF50;
  color: white;
}

.sidebar a:hover:not(.active) {
  background-color: #555;
  color: white;
}

div.content {
  margin-top: 45px;
  margin-left: 200px;
  padding: 1px 16px;
  height: 1000px;
}

@media screen and (max-width: 700px) {
  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
  }
  .sidebar a {float: left;}
  div.content {margin-left: 0;}
}

@media screen and (max-width: 400px) {
  .sidebar a {
    text-align: center;
    float: none;
  }
}

.box{
    float:left;
    margin-right:20px;
}
.clear{
    clear:both;
}

'''

    return css_style_str


def make_html_preamble():

    html_preamble_string = \
'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" type="text/css" href="qa_plot.css">
</head>
<body>\n\n
'''

    return html_preamble_string

def make_html_suffix():

    html_suffix_string = "</body>\n</html>\n"

    return html_suffix_string


def make_next_previous_navbar(prev_field=None, next_field=None,
                              current_field=None):
    '''
    Navbar links
    '''

    if prev_field is None and next_field is None:
        return ""

    navbar_string = '<div class="navbar">\n'

    if prev_field is not None:
        navbar_string += f'    <a href="linker_{prev_field}.html">{prev_field} (Previous)</a>\n'
    else:
        # If None, use current field
        navbar_string += f'    <a href="linker_{current_field}.html">{current_field} (Previous)</a>\n'

    if next_field is not None:
        navbar_string += f'    <a href="linker_{next_field}.html">{next_field} (Next)</a>\n'
    else:
        # If None, use current field
        navbar_string += f'    <a href="linker_{current_field}.html">{current_field} (Next)</a>\n'

    # Add in links to other QA products + home page
    link_locations = generate_webserver_track_link()

    for linkname in link_locations:

        navbar_string += f'    <a href="../{link_locations[linkname]}">{linkname}</a>\n'


    navbar_string += "</div>\n\n"

    return navbar_string


def make_sidebar(field_dict, active_idx=0):
    '''
    Persistent side bar with all field names. For quick switching.
    '''

    sidebar_string = '<div class="sidebar">\n'

    if active_idx is None:
        sidebar_string += '    <a class="active" href="index.html">Home</a>\n'
    else:
        sidebar_string += '    <a class="" href="index.html">Home</a>\n'

    targsumm1_name = "target_amptime_summary_plotly_interactive"

    class_is = "active" if active_idx == 0 else ""
    sidebar_string += f'    <a class="{class_is}" href="linker_{targsumm1_name}.html">Target Summary Amp-Time</a>\n'

    targsumm2_name = "target_ampfreq_summary_plotly_interactive"

    class_is = "active" if active_idx == 1 else ""
    sidebar_string += f'    <a class="{class_is}" href="linker_{targsumm2_name}.html">Target Summary Amp-Freq</a>\n'

    for i, field in enumerate(field_dict):

        # Set as active
        if active_idx is None:
            class_is = ""
        elif i == active_idx - 2:
            class_is = "active"
        else:
            class_is = ""

        sidebar_string += f'    <a class="{class_is}" href="linker_{field}.html">{i+1}. {field} <br><small>{field_dict[field]}</small> </a>\n'

    sidebar_string += '</div>\n\n'

    return sidebar_string


def make_content_div(field):

    content_string = f'<div class="content" id="{field}">\n'

    content_string += f'    <iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="{field}_plotly_interactive.html" height="1000" width="100%"></iframe>\n'

    content_string += '</div>\n\n'

    return content_string


#################################
# Functions for the calibration table plots, not the per field plots


def make_caltable_all_html_links(folder, cal_plots, ms_info_dict):
    '''
    Make and save all html files for linking the interactive plots
    together.
    '''

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "index.html"

    if index_file.exists():
        index_file.unlink()

    print(make_index_caltable_html_page(cal_plots, ms_info_dict),
          file=open(index_file, 'a'))

    # Loop through the fields
    for i, calplot in enumerate(cal_plots):

        field_file = mypath / f"linker_bp_{i}.html"

        if field_file.exists():
            field_file.unlink()

        print(make_plot_caltable_html_page(cal_plots,
                                           active_idx=i),
              file=open(field_file, 'a'))


def make_index_caltable_html_page(cal_plots, ms_info_dict):

    html_string = make_html_preamble()

    # Add links to other index files, etc.
    active_idx = 0
    next_field = active_idx + 1 if active_idx < len(cal_plots) - 1 else None

    html_string += make_next_previous_navbar_caltables(prev_field=None,
                                                       next_field=next_field,
                                                       next_field_name=list(cal_plots.keys())[next_field],
                                                       current_field=active_idx)

    html_string += make_sidebar_caltables(cal_plots, active_idx=None)

    # Add in MS info:
    html_string += '<div class="content" id="basic">\n'
    html_string += f'<h2>{ms_info_dict["vis"]}</h2>\n'


    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_plot_caltable_html_page(cal_plots, active_idx=0):

    html_string = make_html_preamble()

    prev_field = active_idx - 1 if active_idx != 0 else None
    next_field = active_idx + 1 if active_idx < len(cal_plots) - 1 else None

    cal_keys = list(cal_plots.keys())

    current_field_name = cal_keys[active_idx]
    prev_field_name = cal_keys[prev_field] if prev_field is not None else None
    next_field_name = cal_keys[next_field] if next_field is not None else None

    html_string += make_next_previous_navbar_caltables(prev_field=prev_field,
                                                       prev_field_name=prev_field_name,
                                                       next_field=next_field,
                                                       next_field_name=next_field_name,
                                                       current_field=active_idx,
                                                       current_field_name=current_field_name)

    html_string += make_sidebar_caltables(cal_plots, active_idx=active_idx)

    html_string += make_content_caltables_div(cal_plots[current_field_name])

    html_string += make_html_suffix()

    return html_string


def make_next_previous_navbar_caltables(prev_field=None, next_field=None,
                                        prev_field_name=None, next_field_name=None,
                                        current_field=None, current_field_name=None):
    '''
    Navbar links
    '''

    navbar_string = '<div class="navbar">\n'

    if prev_field is not None:
        navbar_string += f'    <a href="linker_bp_{prev_field}.html">{prev_field_name} (Previous)</a>\n'
    else:
        # If None, use current field
        navbar_string += f'    <a href="linker_bp_{current_field}.html">{current_field_name} (Previous)</a>\n'

    if next_field is not None:
        navbar_string += f'    <a href="linker_bp_{next_field}.html">{next_field_name} (Next)</a>\n'
    else:
        # If None, use current field
        navbar_string += f'    <a href="linker_bp_{current_field}.html">{current_field_name} (Next)</a>\n'

    link_locations = generate_webserver_track_link()

    for linkname in link_locations:

        navbar_string += f'    <a href="../{link_locations[linkname]}">{linkname}</a>\n'

    navbar_string += "</div>\n\n"

    return navbar_string


def make_sidebar_caltables(cal_plots, active_idx=0):
    '''
    Persistent side bar with all field names. For quick switching.
    '''

    sidebar_string = '<div class="sidebar">\n'

    if active_idx is None:
        sidebar_string += '    <a class="active" href="index.html">Home</a>\n'
    else:
        sidebar_string += '    <a class="" href="index.html">Home</a>\n'

    for i, cal_name in enumerate(cal_plots):

        # Set as active
        if i == active_idx:
            class_is = "active"
        else:
            class_is = ""

        sidebar_string += f'    <a class="{class_is}" href="linker_bp_{i}.html">{cal_name}</a>\n'

    sidebar_string += '</div>\n\n'

    return sidebar_string


def make_content_caltables_div(cal_plot):

    content_string = f'<div class="content" id="{cal_plot.rstrip(".html")[-1]}">\n'

    content_string += f'    <iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="{cal_plot}" height="1000" width="100%"></iframe>\n'

    content_string += '</div>\n\n'

    return content_string


# Functions for quicklook image figures:

def make_quicklook_html_links(folder, target_dict,
                              summary_filenames,
                              fields_per_page=5):

    # Number of pages to make
    num_targets = len(target_dict)
    num_pages = num_targets // fields_per_page
    if num_targets % fields_per_page > 0:
        num_pages += 1

    target_list = list(target_dict.keys())
    target_list.sort()
    target_list_split = np.array_split(target_list, num_pages)

    target_dict_split = []
    for these_targets in target_list_split:
        these_targets_dict = {}
        for target in these_targets:
            these_targets_dict[target] = target_dict[target]
        target_dict_split.append(these_targets_dict)

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "index.html"

    if index_file.exists():
        index_file.unlink()

    print(make_index_quicklook_html_page(target_list_split,
                                         summary_filenames),
          file=open(index_file, 'a'))

    # Loop through the fields
    for i, these_targets in enumerate(target_list_split):

        field_file = mypath / f"linker_ql_{i}.html"

        if field_file.exists():
            field_file.unlink()

        print(make_plot_quicklook_html_page(target_list_split,
                                            target_dict_split,
                                            active_idx=i),
              file=open(field_file, 'a'))


def make_index_quicklook_html_page(target_list_split, summary_filenames):

    html_string = make_html_preamble()

    # Add links to other index files, etc.
    active_idx = 0
    next_field = active_idx + 1 if active_idx < len(target_list_split) - 1 else None

    html_string += make_next_previous_navbar_quicklook(prev_field=None,
                                                       next_field=next_field,
                                                       next_field_name=f"({next_field})",
                                                       current_field=active_idx)

    html_string += make_sidebar_quicklook(target_list_split, active_idx=None)

    # Add in MS info:
    html_string += '<div class="content" id="basic">\n'

    # Include the summary plots
    html_string += f'    <iframe id="igraph" scrolling="yes" style="border:none;" seamless="seamless" src="{summary_filenames[0]}" height="1000" width="100%"></iframe>\n'
    html_string += f'    <iframe id="igraph" scrolling="yes" style="border:none;" seamless="seamless" src="{summary_filenames[1]}" height="1000" width="100%"></iframe>\n'

    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_next_previous_navbar_quicklook(prev_field=None, next_field=None,
                                        prev_field_name=None, next_field_name=None,
                                        current_field=None, current_field_name=None):
    '''
    Navbar links
    '''

    navbar_string = '<div class="navbar">\n'

    if prev_field is not None:
        navbar_string += f'    <a href="linker_ql_{prev_field}.html">{prev_field_name} (Previous)</a>\n'
    else:
        # If None, use current field
        navbar_string += f'    <a href="linker_ql_{current_field}.html">{current_field_name} (Previous)</a>\n'

    if next_field is not None:
        navbar_string += f'    <a href="linker_ql_{next_field}.html">{next_field_name} (Next)</a>\n'
    else:
        # If None, use current field
        navbar_string += f'    <a href="linker_ql_{current_field}.html">{current_field_name} (Next)</a>\n'

    link_locations = generate_webserver_track_link()

    for linkname in link_locations:

        navbar_string += f'    <a href="../{link_locations[linkname]}">{linkname}</a>\n'

    navbar_string += "</div>\n\n"

    return navbar_string


def make_sidebar_quicklook(target_list_split, active_idx=0):
    '''
    Persistent side bar with all field names. For quick switching.
    '''

    sidebar_string = '<div class="sidebar">\n'

    if active_idx is None:
        sidebar_string += '    <a class="active" href="index.html">Home</a>\n'
    else:
        sidebar_string += '    <a class="" href="index.html">Home</a>\n'

    for i, these_targets in enumerate(target_list_split):

        # Combine into a string of all targets
        these_targets_str = f"({active_idx}) " + "<br>".join(these_targets)

        # Set as active
        if i == active_idx:
            class_is = "active"
        else:
            class_is = ""

        sidebar_string += f'    <a class="{class_is}" href="linker_ql_{i}.html">{these_targets_str}</a>\n'

    sidebar_string += '</div>\n\n'

    return sidebar_string


def make_plot_quicklook_html_page(target_list_split,
                                  target_dict_split, active_idx=0):

    html_string = make_html_preamble()

    prev_field = active_idx - 1 if active_idx != 0 else None
    next_field = active_idx + 1 if active_idx < len(target_list_split) - 1 else None

    html_string += make_next_previous_navbar_quicklook(prev_field=prev_field,
                                                       prev_field_name=f"({prev_field})",
                                                       next_field=next_field,
                                                       next_field_name=f"({next_field})",
                                                       current_field=active_idx,
                                                       current_field_name=f"({active_idx})")

    html_string += make_sidebar_quicklook(target_list_split, active_idx=active_idx)

    html_string += make_content_quicklook_div(target_list_split[active_idx],
                                              target_dict_split[active_idx])

    html_string += make_html_suffix()

    return html_string


def make_content_quicklook_div(these_targets, these_targets_dict):

    content_string = ""

    for target in these_targets:

        content_string += f'<div class="content" id="{target}">\n'

        content_string += f'    <iframe id="igraph" scrolling="yes" style="border:none;" seamless="seamless" src="{these_targets_dict[target]}" height="1000" width="100%"></iframe>\n'

        content_string += '</div>\n\n'

    return content_string


def make_casalogfile_html_page(logfile_name='casa_reduction.log'):
    '''
    Home page for the track with links to the weblogs, QA plots, etc.
    '''

    html_string = make_html_preamble()

    link_locations = generate_webserver_track_link()

    html_string += '<div class="navbar">\n'

    for linkname in link_locations:

        html_string += f'    <a href="{link_locations[linkname]}">{linkname}</a>\n'

    html_string += "</div>\n\n"

    # Add in MS info:
    html_string += '<div class="content" id="basic">\n'
    html_string += f'<h2>CASA Log</h2>\n'


    # Embed the weblog into the main page.
    html_string += '\n'
    html_string += f'<iframe src="{logfile_name}" height="100%" width=90%>\n'
    html_string += 'If you are seeing this, you need a browser understands IFrames.\n'
    html_string += '</iframe>\n'

    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_html_casalog_page(folder, logfile_name='casa_reduction.log'):

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "casa_pipeline.html"

    if index_file.exists():
        index_file.unlink()

    print(make_casalogfile_html_page(logfile_name),
          file=open(index_file, 'a'))



def make_manualflag_html_page(flagfile_name='manual_flags.txt'):
    '''
    Home page for the track with links to the weblogs, QA plots, etc.
    '''

    html_string = make_html_preamble()

    link_locations = generate_webserver_track_link()

    html_string += '<div class="navbar">\n'

    for linkname in link_locations:

        html_string += f'    <a href="{link_locations[linkname]}">{linkname}</a>\n'

    html_string += "</div>\n\n"

    # Add in MS info:
    html_string += '<div class="content" id="basic">\n'
    html_string += f'<h2>Flags applied during reduction</h2>\n'


    # Embed the weblog into the main page.
    html_string += '\n'
    html_string += f'<iframe src="{flagfile_name}" height="100%" width=90%>\n'
    html_string += 'If you are seeing this, you need a browser understands IFrames.\n'
    html_string += '</iframe>\n'

    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_html_manualflag_page(folder, flagfile_name='manual_flags.txt'):

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "casa_manualflags.html"

    if index_file.exists():
        index_file.unlink()

    print(make_manualflag_html_page(flagfile_name),
          file=open(index_file, 'a'))


def make_reductionscript_html_page(script_name='casa_reduction_script.py'):
    '''
    Home page for the track with links to the weblogs, QA plots, etc.
    '''

    html_string = make_html_preamble()

    link_locations = generate_webserver_track_link()

    html_string += '<div class="navbar">\n'

    for linkname in link_locations:

        html_string += f'    <a href="{link_locations[linkname]}">{linkname}</a>\n'

    html_string += "</div>\n\n"

    # Add in MS info:
    html_string += '<div class="content" id="basic">\n'
    html_string += f'<h2>Script used for reduction</h2>\n'


    # Embed the weblog into the main page.
    html_string += '\n'
    html_string += f'<iframe src="{script_name}" height="100%" width=90%>\n'
    html_string += 'If you are seeing this, you need a browser understands IFrames.\n'
    html_string += '</iframe>\n'

    html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_html_reductionscript_page(folder, script_name='casa_reduction_script.py'):

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "casa_script.html"

    if index_file.exists():
        index_file.unlink()

    print(make_reductionscript_html_page(script_name),
          file=open(index_file, 'a'))


def make_fluxfit_html_page(folder_name='fluxfit_plots',
                           fluxcompare_plot_list=[]):
    '''
    Home page for the track with links to the weblogs, QA plots, etc.
    '''

    html_string = make_html_preamble()

    link_locations = generate_webserver_track_link()

    html_string += '<div class="navbar">\n'

    for linkname in link_locations:

        html_string += f'    <a href="{link_locations[linkname]}">{linkname}</a>\n'

    html_string += "</div>\n\n"

    # Loop through the plots and embed them here:
    from glob import glob

    all_plotfiles = glob(f"{folder_name}/*_fluxscale_fit.png")

    for plot_filename in all_plotfiles:

        print(plot_filename)

        this_filename = plot_filename.split("/")[1]

        field_name = this_filename.split("_")[0]

        html_string += '<div class="content" id="basic">\n'
        html_string += f'<h2>{field_name}</h2>\n'


        html_string += '<div class="box" id="basic">\n'
        html_string += f'<h3>Flux bootstrap and fit</h3>\n'

        html_string += '\n'
        html_string += f'<iframe src="{plot_filename}" frameborder="0" scrolling="no" width="100%" height="512" align="left"> >\n'
        html_string += 'If you are seeing this, you need a browser understands IFrames.\n'
        html_string += '</iframe>\n'

        html_string += '</div>\n\n'

        # See if the flux timeseries plot exists for this source:
        for fluxcomp_plot in fluxcompare_plot_list:
            if field_name not in fluxcomp_plot:
                continue

            html_string += '<div class="box" id="basic">\n'
            html_string += f'<h3>Avg. flux compared to flux monitoring</h3>\n'

            html_string += '\n'
            html_string += f'<iframe src="{fluxcomp_plot}" frameborder="0" scrolling="no" width="100%" height="512" align="right"> >\n'
            html_string += 'If you are seeing this, you need a browser understands IFrames.\n'
            html_string += '</iframe>\n'

            html_string += '</div>\n\n'

            break

        html_string += '</div>\n\n'

    html_string += make_html_suffix()

    return html_string


def make_html_fluxes_page(folder, folder_name='fluxfit_plots', fluxcompare_plot_list=[]):

    mypath = Path(folder)

    # CSS style
    css_file = mypath / "qa_plot.css"

    if css_file.exists():
        css_file.unlink()

    print(css_page_style(), file=open(css_file, 'a'))

    # index file
    index_file = mypath / "flux_scaling.html"

    if index_file.exists():
        index_file.unlink()

    print(make_fluxfit_html_page(folder_name, fluxcompare_plot_list=fluxcompare_plot_list),
          file=open(index_file, 'a'))

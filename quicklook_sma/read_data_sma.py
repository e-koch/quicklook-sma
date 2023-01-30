
import os
from glob import glob

osjoin = os.path.join

from qaplotter.utils.read_data import read_casa_txt


def read_bpcal_data_tables(inp_path, table_key='bcal_freq'):
    '''
    Read in the BP txt files for amp and phase.
    '''

    table_dict = dict()
    meta_dict = dict()

    # Table types:
    tab_types = ["amp", "phase"]

    for tab_type in tab_types:
        table_dict[tab_type] = {}
        meta_dict[tab_type] = {}

    amp_tab_names = glob(f"{inp_path}/*{table_key}_amp*.txt")
    phase_tab_names = glob(f"{inp_path}/*{table_key}_phase*.txt")

    if len(amp_tab_names) != len(phase_tab_names):
        raise ValueError("Number of BP amp tables does not match BP phase tables.: "
                         f"Num amp tables: {len(amp_tab_names)}. Num phase tables: {len(phase_tab_names)}")

    # Sort by SPW and create a text

    spw_nums = [int(tab.rstrip(".txt").split("spw")[1]) for tab in amp_tab_names]

    for spw in spw_nums:

        # There aren't many to loop through.
        for amp_name in amp_tab_names:

            if f"_spw{spw}.txt" in amp_name:
                break

        for phase_name in phase_tab_names:

            if f"_spw{spw}.txt" in phase_name:
                break

        amp_out = read_casa_txt(amp_name)
        phase_out = read_casa_txt(phase_name)

        table_dict['amp'][spw] = amp_out[0]
        table_dict['phase'][spw] = phase_out[0]

        meta_dict['amp'][spw] = amp_out[1]
        meta_dict['phase'][spw] = phase_out[1]

    return table_dict, meta_dict


def read_BPinitialgain_data_tables(inp_path, table_key="bpself.ap.gcal"):
    '''
    Read in the BP txt files for amp and phase.
    '''

    table_dict = dict()
    meta_dict = dict()

    # Table types:
    tab_types = ["phase"]

    for tab_type in tab_types:
        table_dict[tab_type] = {}
        meta_dict[tab_type] = {}

    bpinitial_tab_names = glob(f"{inp_path}/*{table_key}_time_phase*.txt")

    # Sort by SPW and create a text
    ant_nums = [int(tab.rstrip(".txt").split("ant")[1]) for tab in bpinitial_tab_names]

    for ant in ant_nums:

        # There aren't many to loop through.
        for ant_name in bpinitial_tab_names:

            if f"_ant{ant}.txt" in ant_name:
                break

        phase_out = read_casa_txt(ant_name)

        table_dict['phase'][ant] = phase_out[0]

        meta_dict['phase'][ant] = phase_out[1]

    return table_dict, meta_dict


def read_phaseshortgaincal_data_tables(inp_path, table_key="intphase_combinespw.gcal"):
    '''
    Read in the BP txt files for amp and phase.
    '''

    table_dict = dict()
    meta_dict = dict()

    # Table types:
    tab_types = ["phase"]

    for tab_type in tab_types:
        table_dict[tab_type] = {}
        meta_dict[tab_type] = {}

    phaseshort_tab_names = glob(f"{inp_path}/*{table_key}_time_phase*.txt")

    # Sort by SPW and create a text
    ant_nums = [int(tab.rstrip(".txt").split("ant")[1]) for tab in phaseshort_tab_names]

    for ant in ant_nums:

        # There aren't many to loop through.
        for ant_name in phaseshort_tab_names:

            if f"_ant{ant}.txt" in ant_name:
                break

        phase_out = read_casa_txt(ant_name)

        table_dict['phase'][ant] = phase_out[0]

        meta_dict['phase'][ant] = phase_out[1]

    return table_dict, meta_dict


def read_ampgaincal_time_data_tables(inp_path, table_key="amp.gcal"):
    '''
    Read in the BP txt files for amp and phase.
    '''

    table_dict = dict()
    meta_dict = dict()

    # Table types:
    tab_types = ["amp"]

    for tab_type in tab_types:
        table_dict[tab_type] = {}
        meta_dict[tab_type] = {}

    ampgaincal_tab_names = glob(f"{inp_path}/*{table_key}_time_amp*.txt")

    # Sort by SPW and create a text
    ant_nums = [int(tab.rstrip(".txt").split("ant")[1]) for tab in ampgaincal_tab_names]

    for ant in ant_nums:

        # There aren't many to loop through.
        for ant_name in ampgaincal_tab_names:

            if f"_ant{ant}.txt" in ant_name:
                break

        amp_out = read_casa_txt(ant_name)

        table_dict['amp'][ant] = amp_out[0]

        meta_dict['amp'][ant] = amp_out[1]

    return table_dict, meta_dict


def read_ampgaincal_freq_data_tables(inp_path, table_key="amp.gcal"):
    '''
    Read in the BP txt files for amp and phase.
    '''

    table_dict = dict()
    meta_dict = dict()

    # Table types:
    tab_types = ["amp"]

    for tab_type in tab_types:
        table_dict[tab_type] = {}
        meta_dict[tab_type] = {}

    ampgaincal_tab_names = glob(f"{inp_path}/*{table_key}_freq_amp*.txt")

    # Sort by SPW and create a text
    ant_nums = [int(tab.rstrip(".txt").split("ant")[1]) for tab in ampgaincal_tab_names]

    for ant in ant_nums:

        # There aren't many to loop through.
        for ant_name in ampgaincal_tab_names:

            if f"_ant{ant}.txt" in ant_name:
                break

        amp_out = read_casa_txt(ant_name)

        table_dict['amp'][ant] = amp_out[0]

        meta_dict['amp'][ant] = amp_out[1]

    return table_dict, meta_dict


def read_phasegaincal_data_tables(inp_path, table_key='scanphase_combinespw.gcal'):
    '''
    Read in the BP txt files for amp and phase.
    '''

    table_dict = dict()
    meta_dict = dict()

    # Table types:
    tab_types = ["phase"]

    for tab_type in tab_types:
        table_dict[tab_type] = {}
        meta_dict[tab_type] = {}

    phaseshort_tab_names = glob(f"{inp_path}/*{table_key}_time_phase*.txt")

    # Sort by SPW and create a text
    ant_nums = [int(tab.rstrip(".txt").split("ant")[1]) for tab in phaseshort_tab_names]

    for ant in ant_nums:

        # There aren't many to loop through.
        for ant_name in phaseshort_tab_names:

            if f"_ant{ant}.txt" in ant_name:
                break

        phase_out = read_casa_txt(ant_name)

        table_dict['phase'][ant] = phase_out[0]

        meta_dict['phase'][ant] = phase_out[1]

    return table_dict, meta_dict


def read_blcal_freq_data_tables(inp_path, table_key='blcal'):
    '''
    Read in the BP txt files for amp and phase.
    '''

    table_dict = dict()
    meta_dict = dict()

    # Table types:
    tab_types = ["amp"]

    for tab_type in tab_types:
        table_dict[tab_type] = {}
        meta_dict[tab_type] = {}

    ampgaincal_tab_names = glob(f"{inp_path}/*{table_key}_freq_amp*.txt")

    # Sort by SPW and create a text
    ant_nums = [int(tab.rstrip(".txt").split("ant")[1]) for tab in ampgaincal_tab_names]

    for ant in ant_nums:

        # There aren't many to loop through.
        for ant_name in ampgaincal_tab_names:

            if f"_ant{ant}.txt" in ant_name:
                break

        amp_out = read_casa_txt(ant_name)

        table_dict['amp'][ant] = amp_out[0]

        meta_dict['amp'][ant] = amp_out[1]

    return table_dict, meta_dict


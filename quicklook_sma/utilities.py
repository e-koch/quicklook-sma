

import configparser


def read_config(config_filename):
    '''
    '''

    config_parsed = configparser.ConfigParser()
    config_parsed.read(config_filename)


    sma_pipe_config = config_parsed['SMA-Pipe']

    # Verify config file
    verify_config(sma_pipe_config)

    return sma_pipe_config


def verify_config(config):
    '''
    Check expected keys exist.
    '''

    required_keys = ['myvis', 'manual_flag_file', 'restart_pipeline', 'interactive_on',
                     'flux', 'bpcal', 'pcal1', 'pcal2', 'science_fields', 'is_mosaic']

    missing_keys = []

    for key in required_keys:

        if not key in config:
            missing_keys.append(key)

    if len(missing_keys) > 0:
        raise KeyError(f"Missing the following required keys in the config file: {missing_keys}")


def get_fluxfield(config) -> str:
    return config['flux']


def get_bandpassfield(config) -> str:
    return config['bpcal']


def get_gainfield(config) -> str:

    gain_fields = [config['pcal1']]

    if config['pcal2'] is not None:
        gain_fields.append(config['pcal2'])

    return ",".join(gain_fields)


def get_calfields(config):

    return ",".join([get_fluxfield(config),
                    get_bandpassfield(config),
                    get_gainfield(config)])


def get_targetfield(config):
    return config['science_fields']


def is_mosaic(config):
    return config.getboolean('is_mosaic')


def get_mosaicfields(config):

    science_fields = get_targetfield(config)

    if not is_mosaic(config):
        return science_fields
    else:

        from casatools import table
        tb = table()

        tb.open("{0}/FIELD".format(config['myvis']))
        field_names = tb.getcol('NAME')
        tb.close()

        science_match = science_fields.strip("*")
        science_field_list = []

        for field in field_names:
            if science_match in field:
                science_field_list.append(field)

        return ",".join(science_field_list)


def get_field_intents(fieldname, config):

    field_intents = []

    if fieldname in get_bandpassfield(config):
        field_intents.append('bandpass')
    if fieldname in get_gainfield(config):
        field_intents.append('gain')
    if fieldname in get_fluxfield(config):
        field_intents.append('flux')
    # TODO: add pol cal

    if len(field_intents) == 0:
        return 'target'
    else:
        return ",".join(field_intents)

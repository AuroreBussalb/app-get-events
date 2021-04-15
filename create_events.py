#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings
import os
import shutil

def get_events(raw, param_create_events):
    """Extract existing events from a fif file or create new events.

    Parameters
    ----------
    raw: instance of mne.io.Raw
        Data from which the events will be extracted or created.
    param_create_events: bool
        If True, fixed length events will be created, else existing events from the fif file
        will be extracted.
   
    Returns
    -------
    events: .tsv file
        File containing the matrix of events (shape (n_events, 3)).
    """

    # Create fixed length events
    if param_create_events is True:
        events = mne.make_fixed_length_events(raw, duration=10)

    # Get events from raw file 
    else:
        events = mne.find_events(raw)

    # Save events matrix
    np.savetxt("out_dir_get_events/events.tsv", events, delimiter="\t")

    return events


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the MEG file and save it in out_dir_get_events
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)
    raw.save("out_dir_get_events/meg.fif", overwrite=True)

    # Read the crosstalk file
    cross_talk_file = config.pop('crosstalk')
    if os.path.exists(cross_talk_file) is True:
        shutil.copy2(cross_talk_file, 'out_dir_get_events/crosstalk_meg.fif')  # required to run a pipeline on BL

    # Read the calibration file
    calibration_file = config.pop('calibration')
    if os.path.exists(calibration_file) is True:
        shutil.copy2(calibration_file, 'out_dir_get_events/calibration_meg.dat')  # required to run a pipeline on BL

    # Read destination file 
    destination_file = config.pop('destination')
    if os.path.exists(destination_file) is True:
        shutil.copy2(destination_file, 'out_dir_get_events/destination.fif')  # required to run a pipeline on BL

    # Read head pos file
    head_pos = config.pop('headshape')
    if os.path.exists(head_pos) is True:
        shutil.copy2(head_pos, 'out_dir_get_events/headshape.pos')  # required to run a pipeline on BL

    # Test if the data contains events
    if raw.info['events'] is True and config['param_create_events'] is True:
        user_warning_message = f'Events already exist in this raw file. ' \
                               f'You are going to create a matrix of events ' \
                               f'different from those contained in the raw file.'
        warnings.warn(user_warning_message)
        dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message})
    
    # Create events
    create_events(raw, param_create_events)

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Events were successfully created.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()
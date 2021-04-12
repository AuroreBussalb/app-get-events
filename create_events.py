#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings

def create_events(raw):

    # create fixed length events
    array_events = mne.make_fixed_length_events(raw, duration=10)
    print(array_events)

    # Save events matrix
    np.savetxt("out_dir_create_events/events.tsv", array_events, delimiter="\t", fmt="%d")

    return array_events


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the files
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)

    # Test if the data contains events
    if raw.info['events'] is True:
        user_warning_message = f'Events already exist in this raw file.' 
        warnings.warn(user_warning_message)
        dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message})
    
    # Create events
    create_events(raw)

    # Success message in product.json    
    dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Events were successfully created.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()
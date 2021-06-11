#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings
import os
import shutil
from mne_bids import BIDSPath, write_raw_bids
import pandas as pd
from collections import Counter
from brainlife_apps_helper import helper


def get_events(raw, param_make_events, param_make_events_id, param_make_events_start,
               param_make_events_stop, param_make_events_duration, param_make_events_first_samp,
               param_make_events_overlap, param_find_events_stim_channels, param_find_events_output,
               param_find_events_consecutive, param_find_events_min_duration, param_find_events_shortest_event,
               param_find_events_mask, param_find_events_uint_cast, param_find_events_mask_type, 
               param_find_events_initial_event):
    """Extract existing events from a fif file or create new events.

    Parameters
    ----------
    raw: instance of mne.io.Raw
        Data from which the events will be extracted or created.
    param_make_events: bool
        If True, fixed length events will be created, else existing events from the fif file
        will be extracted.
    param_make_events_id: int
        The id to use. Default is 1.
    param_make_events_start: float
        Time of first event. Default is 0.
    param_make_events_stop: float or None
        Maximum time of last event. If None (default), events extend to the end of the recording.
    param_make_events_duration: float
        The duration in seconds to separate events by. Default is 1.
    param_make_events_first_samp: bool
        If True (default), times will have raw.first_samp added to them.
    param_make_events_overlap: float
        The overlap between events. Must be 0 <= overlap < duration.
        Default is 0.
    param_find_events_stim_channels: None or str or list of str
        Name of the stim channel or all the stim channels affected by triggers.
        If None (default), the config variables ‘MNE_STIM_CHANNEL’, ‘MNE_STIM_CHANNEL_1’, ‘MNE_STIM_CHANNEL_2’, etc. 
        are read. If these are not found, it will fall back to ‘STI 014’ if present, then fall back to the 
        first channel of type ‘stim’, if present. If multiple channels are provided then the returned events 
        are the union of all the events extracted from individual stim channels.
    param_find_events_output: str
        Whether to report when events start, when events end, or both.
        Either 'onset' (default), 'offset', or 'step'.
    param_find_events_consecutive: bool or str
        If True, consider instances where the value of the events channel changes without first returning 
        to zero as multiple events. If False, report only instances where the value of the events channel 
        changes from/to zero. If ‘increasing’ (default), report adjacent events only when the second event code 
        is greater than the first.
    param_find_events_min_duration: float
        The minimum duration of a change in the events channel required to consider it as an event (in seconds).
        Default is 0.
    param_find_events_shortest_event: int
        Minimum number of samples an event must last (default is 2). If the duration is less than 
        this an exception will be raised.
    param_find_events_mask: int or None
        The value of the digital mask to apply to the stim channel values. If None (default), no masking is performed.
    param_find_events_uint_cast: bool
        If True (default False), do a cast to uint16 on the channel data.
    param_find_events_mask_type: str
        The type of operation between the mask and the trigger. Either 'and' (default) or 'not_and'.
    param_find_events_initial_event: bool
        If True (default False), an event is created if the stim channel has a value different from 0 as its first sample.

    Returns
    -------
    events: .tsv file
        File containing the matrix of events (shape (n_events, 3)).
    """

    # Create fixed length events
    if param_make_events is True:
        events = mne.make_fixed_length_events(raw, id=param_make_events_id, start=param_make_events_start,
                                              stop=param_make_events_stop, duration=param_make_events_duration, 
                                              first_samp=param_make_events_first_samp, overlap=param_make_events_overlap)

    # Get events from raw file 
    else:
        events = mne.find_events(raw, stim_channel=param_find_events_stim_channels, output=param_find_events_output,
                                 consecutive=param_find_events_consecutive, min_duration=param_find_events_min_duration, 
                                 shortest_event=param_find_events_shortest_event, mask=param_find_events_mask, 
                                 uint_cast=param_find_events_uint_cast, mask_type=param_find_events_mask_type, 
                                 initial_event=param_find_events_initial_event)

    return events


def main():

    # Generate a json.product to display messages on Brainlife UI
    dict_json_product = {'brainlife': []}

    # Load inputs from config.json
    with open('config.json') as config_json:
        config = json.load(config_json)

    # Read the MEG file 
    data_file = config.pop('fif')
    raw = mne.io.read_raw_fif(data_file, allow_maxshield=True)

    # Read and save optional files
    config, cross_talk_file, calibration_file, events_file, head_pos_file, channels_file, destination = helper.read_optional_files(config, 'out_dir_get_events')
    
    # Convert empty strings values to None
    config = helper.convert_parameters_to_None(config)

    # Channels.tsv must be BIDS compliant
    if channels_file is not None:
        user_warning_message_channels = f'The channels file provided must be ' \
                                        f'BIDS compliant and the column "status" must be present. ' 
        warnings.warn(user_warning_message_channels)
        dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message_channels})
        # Udpate raw.info['bads'] with info contained in channels.tsv
        raw, user_warning_message_channels = helper.update_data_info_bads(raw, channels_file)
        if user_warning_message_channels is not None: 
            warnings.warn(user_warning_message_channels)
            dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message_channels})


    # Events file  
    if events_file is not None:    
        user_warning_message_events = f'The events.tsv file provided will be ' \
                                      f'overwritten with the new events obtained by this App.' 
        warnings.warn(user_warning_message_events)
        dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message_events})

    
    ## Convert parameters ## 

    # Deal with stim channels #
    # Convert it into a list of strings it is run on BL
    stim_channels = config['param_find_events_stim_channels']
    if isinstance(stim_channels, str) and stim_channels.find("[") != -1 and stim_channels is not None:
        stim_channels = stim_channels.replace('[', '')
        stim_channels = stim_channels.replace(']', '')
        config['param_find_events_stim_channels'] = list(map(str, stim_channels.split(', ')))   

    # Deal with param consecutive # 
    # Convert it into a bool if necessary
    if config['param_find_events_consecutive'] == "True":
        config['param_find_events_consecutive'] = True
    elif config['param_find_events_consecutive'] == "False":
        config['param_find_events_consecutive'] = False

    
    # Test if the data contains events
    if raw.info['events'] and config['param_make_events'] is True:
        user_warning_message = f'Events already exist in this raw file. ' \
                               f'You are going to create an events.tsv file with events ' \
                               f'different from those contained in the raw file.'
        warnings.warn(user_warning_message)
        dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message})
    elif not raw.info['events'] and config['param_make_events'] is False:
        error_value_message = f"You can't extract events from this raw file because it doesn't contain " \
                              f"any events. Please set param_make_events to 'True' so that fixed " \
                              f"length events will be created."
        raise ValueError(error_value_message)

    
    # Delete keys values in config.json when this app is executed on Brainlife
    kwargs = helper.define_kwargs(config)
    
    # Create or extract events
    events = get_events(raw, **kwargs)


    ## Create BIDS compliant events file ## 

    # Create a BIDSPath
    bids_path = BIDSPath(subject='subject',
                         session=None,
                         task='task',
                         run='01',
                         acquisition=None,
                         processing=None,
                         recording=None,
                         space=None,
                         suffix=None,
                         datatype='meg',
                         root='bids')

    # Extract event_id value #
    # When fixed length events were created
    if config['param_make_events'] is True:
        dict_event_id = {'event': config['param_make_events_id']}
    # When existing events were extracted    
    else: # to be tested
        event_id_value = list(events[:, 2])  # the third column of events corresponds to the value column of BIDS events.tsv
        id_values_occurrences = Counter(event_id_value)  # number of different events
        id_values_occurrences = list(id_values_occurrences.keys())
        trials_type = [f"events_{i}" for i in range(1, len(id_values_occurrences) + 1)]  # for trial type column of BIDS events.tsv 
        dict_event_id = dict((k, v) for k, v  in zip(trials_type, id_values_occurrences))

    # Write BIDS to create events.tsv BIDS compliant
    write_raw_bids(raw, bids_path, events_data=events, event_id=dict_event_id, overwrite=True)

    # Extract events.tsv from bids path
    events_file = 'bids/sub-subject/meg/sub-subject_task-task_run-01_events.tsv'

    # Copy events.tsv in outdir
    shutil.copy2(events_file, 'out_dir_get_events/events.tsv') 


    # Success message in product.json 
    if config['param_make_events'] is True:   
        dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Events were successfully created.'})
    else:
        dict_json_product['brainlife'].append({'type': 'success', 'msg': 'Events were successfully extracted.'})

    # Save the dict_json_product in a json file
    with open('product.json', 'w') as outfile:
        json.dump(dict_json_product, outfile)


if __name__ == '__main__':
    main()
#!/usr/local/bin/python3

import json
import mne
import numpy as np
import warnings
import os
import shutil

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


    ## Read the optional files

    # Read the crosstalk file
    cross_talk_file = config.pop('crosstalk')
    if cross_talk_file is not None:
        if os.path.exists(cross_talk_file) is True:
            shutil.copy2(cross_talk_file, 'out_dir_get_events/crosstalk_meg.fif')  # required to run a pipeline on BL

    # Read the calibration file
    calibration_file = config.pop('calibration')
    if calibration_file is not None:
        if os.path.exists(calibration_file) is True:
            shutil.copy2(calibration_file, 'out_dir_get_events/calibration_meg.dat')  # required to run a pipeline on BL

    # Read destination file 
    destination_file = config.pop('destination')
    if destination_file is not None:
        if os.path.exists(destination_file) is True:
            shutil.copy2(destination_file, 'out_dir_get_events/destination.fif')  # required to run a pipeline on BL

    # Read head pos file
    head_pos = config.pop('headshape')
    if head_pos is not None:
        if os.path.exists(head_pos) is True:
             shutil.copy2(head_pos, 'out_dir_get_events/headshape.pos')  # required to run a pipeline on BL

    # Read events file 
    events_file = config.pop('events')
    if events_file is not None:
        if os.path.exists(events_file) is True:
            shutil.copy2(events_file, 'out_dir_get_events/events.tsv') # required to run a pipeline on BL
        else:
            events_file = None

    # Read channels file 
    channels_file = config.pop('channels')
    if channels_file is not None:
        if os.path.exists(channels_file):
            shutil.copy2(channels_file, 'out_dir_get_events/channels.tsv')  # required to run a pipeline on BL


    # Convert all "" into None when the App runs on BL
    tmp = dict((k, None) for k, v in config.items() if v == "")
    config.update(tmp)

    
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
    if raw.info['events'] is True and config['param_make_events'] is True:
        user_warning_message = f'Events already exist in this raw file. ' \
                               f'You are going to create a matrix of events ' \
                               f'different from those contained in the raw file.'
        warnings.warn(user_warning_message)
        dict_json_product['brainlife'].append({'type': 'warning', 'msg': user_warning_message})

    
    ## Define kwargs ##

    # Delete keys values in config.json when this app is executed on Brainlife
    if '_app' and '_tid' and '_inputs' and '_outputs' in config.keys():
        del config['_app'], config['_tid'], config['_inputs'], config['_outputs'] 
    kwargs = config  

    
    # Create or extract events
    get_events(raw, **kwargs)

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
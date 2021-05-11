# app-get-events

This is the repository of a Brainlife App using MNE Python to extract existing events ([`mne.find_events`](https://mne.tools/stable/generated/mne.find_events.html?highlight=find_events#mne.find_events) or create events ([`mne.make_fixed_length_events`](https://mne.tools/stable/generated/mne.make_fixed_length_events.html?highlight=make_fixed_length_events#mne.make_fixed_length_events).

# app-get-events documentation

1) Extract or create existing events and store them in a .tsv file. 
2) This file can be used to make epochs or when the data is resampled.
3) Input files are:
    * a MEG file in `.fif` format,
    * an optional fine calibration file in `.dat`,
    * an optional crosstalk compensation file in `.fif`,
    * an optional head position file in `.pos`,
    * an optional destination file in `.fif`,
4) Input parameters are:
    * `param_make_events`: `bool`, if True, fixed length events will be created, else existing events from the fif file will be extracted.
    * `param_make_events_id`: `int`, the id to use. Default is 1.
    * `param_make_events_start`: `float`, time of first event. Default is 0.
    * `param_make_events_stop`: `float`, optional,  maximum time of last event. If None, events extend to the end of the recording. Default is None.
    * `param_make_events_duration`: `float`, the duration in seconds to separate events by. Default is 1.
    * `param_make_events_first_samp`: `str`, if True, times will have raw.first_samp added to them. Default is True.
    * `param_make_events_overlap`: `float`, the overlap between events. Must be 0 <= overlap < duration. Default is 0.
    * `param_find_events_stim_channels`: `str`, `list of str`, optional, name of the stim channel or all the stim channels affected by triggers. Default is None.
    * `param_find_events_output`: `str`, whether to report when events start, when events end, or both. Either 'onset', 'offset', or 'step'. Default is 'onset'.
    * `param_find_events_consecutive`: `bool` or `str`, if True, consider instances where the value of the events channel changes without first returning to zero as multiple events. If False, report only instances where the value of the events channel changes from/to zero. If ‘increasing’, report adjacent events only when the second event code is greater than the first. Default is 'increasing'.
    * `param_find_events_min_duration`: `float`, the minimum duration of a change in the events channel required to consider it as an event (in seconds). Default is 0.
    * `param_find_events_shortest_event`, `int`, minimum number of samples an event must last. Default is 2.
    * `param_find_events_mask`, `int`, optional, The value of the digital mask to apply to the stim channel values. If None, no masking is performed. Default is None.
    * `param_find_events_uint_cast`, `bool`, if True, do a cast to uint16 on the channel data. Default is False.
    * `param_find_events_mask_type`, `str`, The type of operation between the mask and the trigger. Either 'and' or 'not_and'. Default is 'and'.
    * `param_find_events_initial_event`: `bool`, if True, an event is created if the stim channel has a value different from 0 as its first sample. Default is False.
      
This list along with the default values correspond to the parameters of MNE Python version 0.22.0.

5) Ouput files are:
    * a `.tsv` file containing the matrix of events.

### Authors
- [Aurore Bussalb](aurore.bussalb@icm-institute.org)

### Contributors
- [Aurore Bussalb](aurore.bussalb@icm-institute.org)
- [Maximilien Chaumon](maximilien.chaumon@icm-institute.org)

### Funding Acknowledgement
brainlife.io is publicly funded and for the sustainability of the project it is helpful to Acknowledge the use of the platform. We kindly ask that you acknowledge the funding below in your code and publications. Copy and past the following lines into your repository when using this code.

[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
[![NSF-ACI-1916518](https://img.shields.io/badge/NSF_ACI-1916518-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1916518)
[![NSF-IIS-1912270](https://img.shields.io/badge/NSF_IIS-1912270-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1912270)
[![NIH-NIBIB-R01EB029272](https://img.shields.io/badge/NIH_NIBIB-R01EB029272-green.svg)](https://grantome.com/grant/NIH/R01-EB029272-01)

### Citations
1. Avesani, P., McPherson, B., Hayashi, S. et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. Sci Data 6, 69 (2019). [https://doi.org/10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)
2. Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A., & Jas, M. MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software, 4:1896 (2019). [https://doi.org/10.21105/joss.01896](https://doi.org/10.21105/joss.01896)

## Running the App 

### On Brainlife.io

This App is still private.

### Running Locally (on your machine)

1. git clone this repo
2. Inside the cloned directory, create `config.json` with the same keys as in `config.json.example` but with paths to your input 
   files and values of the input parameters. For instance:

```json
{
  "fif": "rest1-raw.fif"
}
```

3. Launch the App by executing `main`

```bash
./main
```

## Output

The output file is .tsv file.

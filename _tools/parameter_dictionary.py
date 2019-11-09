def parameter_dictionary():
    '''parameter dictionary with specified defaults'''
    
    return  {
              'registration': 'rigid',  # type of registration: 'rigid', 'translation' or None
              'diam_cell': 6.0,         # cell diameter (microns)
              'dir_ants': '',           # path to ANTs directory
              'dir_input': '',          # path to image directory
              'dir_output': '',         # path to output directory
              'ds': 2,                  # spatial coarse-graining in x-y dimension
              'dt': 1,                  # temporal downsampling for cell detection (ignored if 'timepoints' specified)
              'timepoints': None,       # timepoints to use in cell detection (computed from dt if not specified)
              'f_hipass': 0,            # frequency (Hz) for high-pass filtering of cell timeseries
              'f_volume': 2.0,          # imaging frequency (Hz)
              'n_cells_block': 100,     # number of cells in block
              'n_colors': 1,            # number of brain colors (2 in two-color images)
              'res_x': 0.40625,         # x resolution (microns)
              'res_y': 0.40625,         # y resolution (microns)
              'res_z': 5.0,             # z resolution (microns)
              't_baseline': 300,        # interval for baseline calculation (seconds)
              't_section': 0.01,        # exposure time (seconds): time of slice acquisition
              'thr_mask': 0.5,          # threshold for volume mask (0 to 1: least to most aggressive mask)
            }
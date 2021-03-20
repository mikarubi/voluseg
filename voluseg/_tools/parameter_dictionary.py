def parameter_dictionary():
    '''parameter dictionary with specified defaults'''
    
    return  {
              'registration': 'medium', # quality of registration: 'high', 'medium', 'low' or 'none'
              'diam_cell': 6.0,         # cell diameter (microns)
              'dir_ants': '',           # path to ANTs directory
              'dir_input': '',          # path to image directory
              'dir_output': '',         # path to output directory
              'ds': 2,                  # spatial coarse-graining in x-y dimension
              'planes_pad': 0,          # number of planes to pad the volume with (for robust registration)
              'planes_packed': False,   # packed planes in each volume (for single plane imaging with packed planes)
              'parallel_clean': True,   # parallelization of final cleaning (True is fast but memory intensive)
              'nt': 1000,               # number of timepoints to use for cell detection (use all points if nt = 0)
              'f_hipass': 0,            # frequency (Hz) for high-pass filtering of cell timeseries
              'f_volume': 2.0,          # imaging frequency (Hz)
              'n_cells_block': 100,     # number of cells in block
              'n_colors': 1,            # number of brain colors (2 in two-color images)
              'res_x': 0.40625,         # x resolution (microns)
              'res_y': 0.40625,         # y resolution (microns)
              'res_z': 5.0,             # z resolution (microns)
              't_baseline': 300,        # interval for baseline calculation (seconds)
              't_section': 0.01,        # exposure time (seconds): time of slice acquisition
              'thr_mask': 0.5,          # threshold for volume mask: 0 < thr <= 1 (probability) or thr > 1 (intensity)
            }

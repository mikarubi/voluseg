def parameter_dictionary():
    '''return parameter dictionary with some specified defaults'''
    
    return \
            {
                # type of registration: possible values -- 'rigid', 'translation', None
                'registration': 'rigid',
                # cell diameter (microns)
                'diam_cell': 6.0,
                # path to ANTs directory
                'dir_ants': '',
                # path to image directory
                'dir_input': '',
                # path to output directory
                'dir_output': '',
                # spatial coarse-graining in x-y
                'ds': 2,
                # temporal downsampling for cell detection (ignored if specified timepoints)
                'dt': 1,
                # timepoints to use in cell detection (computed from dt if empty)
                'timepoints': None,
                # frequency for high-pass filtering of cell timeseries (Hz)
                'f_hipass': 0,
                # frequency at which volumes are acquired (Hz)
                'f_volume': 2.66,
                # number of cells in block
                'n_cells_block': 100,
                # number of brain in each image (2 in two-color images)
                'n_colors': 1,
                # x resolution (microns)
                'res_x': 0.40625,
                # y resolution (microns)
                'res_y': 0.40625,
                # z resolution (microns)
                'res_z': 1.0,
                # time interval for baseline calculation (seconds)
                't_baseline': 300,
                # exposure time: time at which each slice is acquired (seconds)
                't_section': 0.01,
                # intensity threshold for masking volumes
                'thr_mask': 0.5,
            }
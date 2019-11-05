# INPUT VARIABLES:
# - dir_ants: path to ANTS directory
# - code_dir: directory in which the code resides
# - dir_input: input directory
# - dir_output: output directory
# - alignment_type: type of motion correction.
#     possible values:
#       translation: (translation only)
#       rigid: (translation and rotation)
# - dt: the range of timepoints to use for cell detection
#     can be a vector which specifies the precise point sequence
#     can be a scalar which specifies the downsampling factor
#     e.g.
#       dt = list(range(2000))      # first 2000 timepoints of recording
#       dt = 10;                    # every 10th point of recording
#       dt = 1, dt = 0, dt = []     # every point of recording
# - thr_mask: fluorescence threshold for brain masking the brain
#     typical values lie in the range of 100 to 110
#     if in doubt, set thr_mask=0 (this allows to choose it interactively later)
#     NB: cell detection is only performed on suprathreshold voxels
# - ds: spatial coarsegraining of in x-y dimensions:
#     typical value is 2 (leading to 4-fold reduction in size)
#     set value to 1 to maintain original dimensions
# - n_cells_block: number of cells in each detect_cellsion blok
#     larger values result in larger blocks and slower computation
# - diam_cell: approximate cell diameter
# - n_colors: number of brains in each image
#     typical value is 1.
#     value is 2 if two-color image
# - t_baseline; time intervals for baseline detection (in seconds)
#     typical values are 300-600 (5-10 minutes)
# - t_buffer: time intervals for censoring signal (in seconds)
#     t_buffer = 0                # apply no censoring
#     t_buffer = [300, 0]         # censor 300 seconds at start of recording
#     t_buffer = [0, 300]         # censor 300 seconds at end of recording
#     t_buffer = 300              # censor 300 seconds at beginning and end of recording
# - f_hipass: frequency cut-off for high-pass filtering
#     typical value is 0.001
#     set to 0 to disable high-pass filtering
# - nmf_algorithm: type of nmf algorithm for component detection
#     nmf_algorithm=0               # no nmf component detection
#     nmf_algorithm=1               # alternating least squares (custom implementation)
#     nmf_algorithm=2               # coordinate descent (sklearn implementation)
# - n_systems: number of components for nmf
#     could be a scalar or an array

parameters = {
            'alignment': None,
            'diam_cell': 6.0,
            'dir_ants': '',
            'dir_input': '',
            'dir_output': '',
            'ds': 2,
            'dt': 1,
            'f_hipass': 0,
            'f_volume': 2.66,
            'n_cells_block': 100,
            'n_colors': 1,
            'res_x': 0.40625,
            'res_y': 0.40625,
            'res_z': 1.0,
            't_baseline': 300,
            't_section': 0.01,
            'thr_mask': 0.5,
            'thr_similarity': 0.5
            }
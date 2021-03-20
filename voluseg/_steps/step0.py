def process_parameters(parameters0=None):
    '''process parameters and create parameter file'''
    
    import os
    import copy
    import pickle
    import numpy as np
    from voluseg._tools.load_image import load_image
    from voluseg._tools.plane_name import plane_name
    from voluseg._tools.parameter_dictionary import parameter_dictionary
    from voluseg._tools.evenly_parallelize import evenly_parallelize
    
    parameters = copy.deepcopy(parameters0)
    
    ## general checks
    
    # check that parameter input is a dictionary
    if not type(parameters) == dict:
        print('error: specify parameter dictionary as input.')
        return
    
    # check if any parameters are missing
    missing_parameters = set(parameter_dictionary()) - set(parameters)    
    if missing_parameters:
        print('error: missing parameters \'%s\'.'%('\', \''.join(missing_parameters)))
        return
    
    # get input and output directories, and parameter filename
    dir_input = parameters['dir_input']
    dir_output = parameters['dir_output']
    filename_parameters = os.path.join(dir_output, 'parameters.pickle')
    
    # load parameters from file, if it already exists
    if os.path.isfile(filename_parameters):
        print('exiting, parameter file exists: %s.'%(filename_parameters))
        return
    
    ## specific checks
    
    # check directory names
    for i in ['dir_ants', 'dir_input', 'dir_output', 'registration']:
        pi = parameters[i]
        if not (isinstance(pi, str) and (not ' ' in pi)):
            print('error: \'%s\' must be a string without spaces.'%(i))
            return
    
    # check booleans
    for i in ['parallel_clean', 'planes_packed']:
        pi = parameters[i]
        if not isinstance(pi, bool):
            print('error: \'%s\' must be a boolean.'%(i))
            return
    
    # check integers
    for i in ['ds', 'n_cells_block', 'n_colors', 'nt', 'planes_pad']:
        pi = parameters[i]
        if not (np.isscalar(pi) and (pi >= 0) and (pi == np.round(pi))):
            print('error: \'%s\' must be a nonnegative or positive integer.'%(i))
            return
    
    # check non-negative real numbers:
    for i in ['diam_cell', 'f_hipass', 'f_volume', 'res_x', 'res_y',
              'res_z', 't_baseline', 't_section', 'thr_mask']:
        pi = parameters[i]
        if not (np.isscalar(pi) and (pi >= 0) and np.isreal(pi)):
            print('error: \'%s\' must be a nonnegative or positive real number.'%(i))
            return
        
    # check registration
    if parameters['registration']:
        parameters['registration'] = parameters['registration'].lower()
        if parameters['registration']=='none':
            parameters['registration'] = None
        elif not parameters['registration'] in ['high', 'medium', 'low']:
            print('error: \'registration\' must be \'high\', \'medium\', \'low\', or \'none\'.')
            return
    
    # check plane padding
    if (not parameters['registration']) and not ((parameters['planes_pad'] == 0)):
            print('error: \'planes_pad\' must be 0 if \'registration\' is None.')
            return
    
    # get image extension, image names and number of segmentation timepoints
    file_names = [i.split('.', 1) for i in os.listdir(dir_input) if '.' in i]
    file_exts, counts = np.unique(list(zip(*file_names))[1], return_counts=True)
    ext = '.'+file_exts[np.argmax(counts)]
    volume_names = np.sort([i for i, j in file_names if '.'+j==ext])    
    lt = len(volume_names)
        
    # adjust parameters for packed planes data
    if parameters['planes_packed']:
        volume_names0 = copy.deepcopy(volume_names)
        parameters['volume_names0'] = volume_names0
        parameters['res_z'] = parameters['diam_cell']
        def volume_plane_names(tuple_name_volume):
            name_volume = tuple_name_volume[1]
            fullname_input = os.path.join(dir_input, name_volume+ext)
            lp = len(load_image(fullname_input, ext))
            return [plane_name(name_volume, pi) for pi in range(lp)]
        
        volume_names = evenly_parallelize(volume_names0).map(volume_plane_names).collect()
        volume_names = np.sort([pi for ni in volume_names for pi in ni])
        lt = len(volume_names)
    
    # affine matrix
    affine_mat = np.diag([  parameters['res_x'] * parameters['ds'], \
                            parameters['res_y'] * parameters['ds'], \
                            parameters['res_z'], \
                            1])
    
    # save parameters
    parameters['volume_names'] = volume_names
    parameters['ext'] = ext
    parameters['lt'] = lt
    parameters['affine_mat'] = affine_mat
        
    try:
        os.makedirs(dir_output, exist_ok=True)
        with open(filename_parameters, 'wb') as file_handle:
            pickle.dump(parameters, file_handle)        
            print('parameter file successfully saved.')
            
    except Exception as msg:
        print('parameter file not saved: %s.'%(msg))
                

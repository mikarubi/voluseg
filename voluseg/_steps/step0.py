def process_parameters(parameters0=None):
    '''process parameters and create parameter file'''
    
    import os
    import copy
    import pickle
    import numpy as np
    from voluseg._tools.parameter_dictionary import parameter_dictionary
    
    parameters = copy.deepcopy(parameters0)
    
    if not type(parameters) == dict:
        print('error: specify parameter dictionary as input.')
        return
        
    if not ('dir_input' in parameters) or not ('dir_output' in parameters):
        print('error: specify dir_input and dir_output dictionary keys.')
        return
    
    # get input and output directories, and parameter filename
    dir_input = parameters['dir_input']
    dir_output = parameters['dir_output']
    filename_parameters = os.path.join(dir_output, 'parameters.pickle')
    
    # load parameteres from file, if it already exists
    if os.path.isfile(filename_parameters):
        print('exiting, parameter file exists: %s.'%(filename_parameters))
        return
    
    # check if any parameters are missing
    missing_parameters = set(parameter_dictionary()) - set(parameters)    
    if missing_parameters:
        print('error: missing parameters %s.'%(', '.join(missing_parameters)))
        return
           
    # check registration
    if parameters['registration']:
        parameters['registration'] = parameters['registration'].lower()
        if parameters['registration']=='none':
            parameters['registration'] = None
        elif not parameters['registration'] in ['high', 'medium', 'low']:
            print('Error: \'registration\' must be either \'high\', \'medium\', \'low\', or None.')
            return
    
    # check plane padding
    if (not parameters['registration']) and not ((parameters['planes_pad'] == 0)):
            print('Error: planes_pad must be 0 in the absence of registration.')
        
    # get image extension, image names and number of segmentation timepoints
    file_names = [i.split('.', 1) for i in os.listdir(dir_input) if '.' in i]
    file_exts, counts = np.unique(list(zip(*file_names))[1], return_counts=True)
    ext = '.'+file_exts[np.argmax(counts)]
    volume_names = np.sort([i for i, j in file_names if '.'+j==ext])    
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
                
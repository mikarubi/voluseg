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
    if not parameters['registration'] in ['rigid', 'translation', None]:
        print('error: \'registration\' must be either \'rigid\', \'translation\' or None.')
        return
        
    # get image extension, image names and number of segmentation timepoints
    file_names = [i.split('.', 1) for i in os.listdir(dir_input) if '.' in i]
    file_exts, counts = np.unique(list(zip(*file_names))[1], return_counts=True)
    ext = '.'+file_exts[np.argmax(counts)]
    volume_names = np.sort([i for i, j in file_names if '.'+j==ext])    
    lt = len(volume_names)
    
#    # get segmentation segmentation timepoints
#    if parameters['timepoints']:
#        if parameters['dt']:
#            print('timepoints input is non-empty, ignoring value of dt.')
#        timepoints = parameters['timepoints']
#    else:
#        timepoints = np.r_[:lt:np.maximum(parameters['dt'], 1)]
        
    # affine matrix
    affine_mat = np.diag([  parameters['res_x'] * parameters['ds'], \
                            parameters['res_y'] * parameters['ds'], \
                            parameters['res_z'], \
                            1])
    
    # save parameters    
    parameters['volume_names'] = volume_names
    parameters['ext'] = ext
    parameters['lt'] = lt
#    parameters['timepoints'] = np.round(timepoints).astype(int)
    parameters['affine_mat'] = affine_mat
        
    try:
        os.makedirs(dir_output, exist_ok=True)
        with open(filename_parameters, 'wb') as file_handle:
            pickle.dump(parameters, file_handle)        
            print('parameter file successfully saved.')
            
    except Exception as msg:
        print('parameter file not saved: %s.'%(msg))
                
def preliminaries(parameters):
    import os
    import sys
    import pickle
    import numpy as np

    dir_input = parameters['dir_input']
    dir_output = parameters['dir_output']
            
    # configure only if prepro_parameters doesn't exist
    name_parameter_file = os.path.join(dir_output, 'parameters.pickle')
    if os.path.isfile(name_parameter_file):
        print('Parameter file already exists.')
        print('Delete file %s to overwrite.'%(name_parameter_file))
        return
        
    # check alignment
    if not parameters['alignment'] in ['rigid', 'translation', None]:
        raise Exception('\'alignment\' must be either \'rigid\', \'translation\' or None.') 
        
    # get image extension, image names and number of segmentation timepoints
    file_names = [i.split('.', 1) for i in os.listdir(dir_input) if '.' in i]
    file_exts, counts = np.unique(list(zip(*file_names))[1], return_counts=True)
    ext = '.'+file_exts[np.argmax(counts)]
    volume_names = np.sort([i for i, j in file_names if '.'+j==ext])    
    lt = len(volume_names)
    
    # get segmentation segmentation timepoints
    dt = np.array(parameters['dt'])
    if (dt.size > 2):
        timepoints = dt
    elif (dt.size == 2):
        timepoints = np.r_[:lt:np.maximum(lt/dt[1], 1)]
    elif (dt.size == 1):
        timepoints = np.r_[:lt:np.maximum(dt, 1)]
    else:
        timepoints = np.r_[:lt]
        
    # affine matrix
    affine_mat = np.diag([  parameters['res_x'] * parameters['ds'], \
                            parameters['res_y'] * parameters['ds'], \
                            parameters['res_z'], \
                            1])

    # save parameters    
    parameters['volume_names'] = volume_names
    parameters['ext'] = ext
    parameters['lt'] = lt
    parameters['timepoints'] = np.round(timepoints).astype(int)
    parameters['affine_mat'] = affine_mat
    
    try:
        os.makedirs(dir_output, exist_ok=True)
        with open(name_parameter_file, 'wb') as file_handle:
            pickle.dump(parameters, file_handle)
        
            print('Parameter file successfully saved.')        
            
    except:
        print('Error: Parameter file not saved.')
        
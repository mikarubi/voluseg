def z0():
    global input_dir, output_dir, code_dir, packed_planes, dt, lz, resn_z, freq_stack
    
    # configure only if prepro_parameters doesn't exist
    if os.path.isfile(output_dir + 'prepro_parameters.hdf5'):
        sys.exit('Imported modules and exiting')
        
    # pad directories
    code_dir = '/'.join(code_dir.split('/'))
    input_dir = '/'.join(input_dir.split('/'))
    output_dir = '/'.join(output_dir.split('/'))
        
    # output file formats
    data_type = 'float32'
    nii_ext   = '.nii.gz'
    
    while 1:
        # get image extension and image names
        file_names = [i.split('.', 1) for i in os.listdir(input_dir)]
        file_names = list(itertools.zip_longest(*file_names, fillvalue=''))
        file_exts, counts = np.unique(file_names[1], return_counts=True)
        image_ext = file_exts[np.argmax(counts)]
        
        image_names = [i.encode('utf8') for i, j in zip(*file_names) if j==image_ext]
        image_names.sort()
        def compute_match_szes(i):
            a, b = image_names[i], image_names[i+1]
            return difflib.SequenceMatcher(None,a,b).\
                    find_longest_match(0, len(a), 0, len(b)).size
        
        match_szes = sc.parallelize(np.r_[:len(image_names)-1]).map(compute_match_szes).collect()
        match_szes = np.max(np.array([np.r_[match_szes, 0], np.r_[0, match_szes]]), 0)    
        uniq_szes, counts = np.unique(match_szes, return_counts=True)
        assert(np.argmax(match_szes) == np.argmax(counts) and (np.max(uniq_szes) == uniq_szes[-1]))
        
        image_names = [j for i, j in enumerate(image_names) if match_szes[i] == uniq_szes[-1]]
        image_ext = ('.' + image_ext).encode('utf8')
        
        # unpack single planes
        if packed_planes:
            input_dir0 = input_dir
            input_dir1 = input_dir + 'pln/'
            os.system('mkdir ' + input_dir1)
            def volume_to_singleplane(image_name):
                try:
                    image_name = image_name.decode()
                except:
                    pass
                
                with h5py.File(input_dir0 + image_name + '.h5', 'r') as f:
                    vol = f['default'][()]
                    
                for i, vol_i in enumerate(vol):
                    with h5py.File(input_dir1 + image_name + '_PLN' + str(i).zfill(2) + '.h5', 'w') as g:
                        g['default'] = vol_i
            
            sc.parallelize(image_names).foreach(volume_to_singleplane)
            
            # change input directory and get new image names
            input_dir = input_dir1        
            packed_planes = 0
        else:
            break
    
    # get number of timepoints
    lt = len(image_names)
    
    # get dt_range
    dt = np.array(dt)
    if (dt.size > 2):
        dt_range = dt
    elif (dt.size == 2):
        dt_range = np.r_[:lt:np.maximum(lt/dt[1], 1)]
    elif (dt.size == 1):
        dt_range = np.r_[:lt:np.maximum(dt, 1)]
    else:
        dt_range = np.r_[:lt]
    
    # in case of packed planes, modify lz and freq_stack
    if packed_planes:
        freq_stack *= lz
        lz = 1;
        
    if alignment_type.lower() == 'rigid':
        reg_tip = 'r'
    elif alignment_type.lower() == 'translation':
        reg_tip = 't'
    else:
        raise Exception('alignment_type must be either \'rigid\' or \'translation\'.') 
    
    # if single plane, adjust resolution and padding
    if (lz==1) or (reg_tip=='t'):
        lpad = 0
    else:
        lpad = 4
        
    if (lz==1):
        resn_z = 1.0
    
    niiaffmat = np.diag([resn_x * ds, resn_y * ds, resn_z, 1])
    cell_ball_fine, cell_ball_midpoint_fine = get_ball(0.5 * cell_diam)
    cell_ball,      cell_ball_midpoint      = get_ball(1.0 * cell_diam)
    
    # get number of voxels in each cell
    if (lz == 1) or (resn_z >= cell_diam):
        cell_voxl_nmbr = np.pi * (np.square(cell_diam / 2.0)) / (resn_x * ds * resn_y * ds)
    else:
        cell_voxl_nmbr = \
            cell_diam * np.pi * (np.square(cell_diam / 2.0)) / (resn_x * ds * resn_y * ds * resn_z)
            
    
    # make directories and save  parameters
    os.system('mkdir -p ' + output_dir + '{brain_images,cell_series}')
    
    try:
        with h5py.File(output_dir + 'prepro_parameters.hdf5', 'w') as file_handle:
            file_handle['ants_dir']                = ants_dir
            file_handle['cell_ball']               = cell_ball
            file_handle['cell_ball_fine']          = cell_ball_fine
            file_handle['cell_ball_midpoint']      = cell_ball_midpoint
            file_handle['cell_ball_midpoint_fine'] = cell_ball_midpoint_fine
            file_handle['cell_diam']               = cell_diam
            file_handle['cell_voxl_nmbr']          = np.round(cell_voxl_nmbr).astype(int)
            file_handle['code_dir']                = code_dir
            file_handle['blok_cell_nmbr']          = np.round(blok_cell_nmbr).astype(int)
            file_handle['data_type']               = data_type
            file_handle['ds']                      = ds
            file_handle['dt_range']                = np.round(dt_range).astype(int)
            file_handle['freq_stack']              = freq_stack
            file_handle['freq_cutoff']             = freq_cutoff
            file_handle['image_ext']               = image_ext
            file_handle['image_names']             = image_names
            file_handle['imageframe_nmbr']         = imageframe_nmbr
            file_handle['input_dir']               = input_dir
            file_handle['lpad']                    = np.round(lpad).astype(int)
            file_handle['lt']                      = np.round(lt).astype(int)
            file_handle['lx']                      = np.round(lx).astype(int)
            file_handle['ly']                      = np.round(ly).astype(int)
            file_handle['lz']                      = np.round(lz).astype(int)
            file_handle['n_components']            = np.round(n_components).astype(int)
            file_handle['nmf_algorithm']           = np.round(nmf_algorithm).astype(int)
            file_handle['nii_ext']                 = nii_ext
            file_handle['niiaffmat']               = niiaffmat
            file_handle['output_dir']              = output_dir
            file_handle['reg_tip']                 = reg_tip
            file_handle['resn_x']                  = resn_x
            file_handle['resn_y']                  = resn_y
            file_handle['resn_z']                  = resn_z
            file_handle['t_exposure']              = t_exposure
            file_handle['thr_prob']                = thr_prob
        
        print('Parameter file successfully saved.')
        
        with h5py.File(output_dir + 'prepro_parameters.hdf5', 'r') as file_handle:
            for i in file_handle:
                if not 'cell' in i:
                    try:
                        len(file_handle[i])
                    except:
                        try: print("{} = {}".format(i,file_handle[i][()].decode()))
                        except: print("{} = {}".format(i,file_handle[i][()]))
            
    except:
        print('Error: Parameter file not saved.')
        
        os.remove(output_dir + 'prepro_parameters.hdf5')
        
z0()

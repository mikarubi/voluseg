def z4():
    for frame_i in range(imageframe_nmbr):
        if os.path.isfile(output_dir + 'Cells' + str(frame_i) + '.hdf5'):
            print('Cells' + str(frame_i) + '.hdf5 already exists, skipping.')
            break
        else:
            print('Creating Cells' + str(frame_i) + '.hdf5.')
            
        
        with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'r') as file_handle:
            blok_nmbr = file_handle['blok_nmbr'][()]
            blok_lidx = file_handle['blok_lidx'][()]
    
        cell_dir = output_dir + 'cell_series/' + str(frame_i)
        Cmpn_position = []
        Cmpn_spcesers = []
        Cmpn_timesers = []
        for blok_i in range(blok_nmbr):
            try:
                with h5py.File(cell_dir + '/Block' + str(blok_i).zfill(5) + '.hdf5', 'r') as file_handle:
                    for cmpn_i in file_handle['cmpn']:
                        Cmpn_position.append(file_handle['cmpn'][cmpn_i]['cmpn_position'][()])
                        Cmpn_spcesers.append(file_handle['cmpn'][cmpn_i]['cmpn_spcesers'][()])
                        Cmpn_timesers.append(file_handle['cmpn'][cmpn_i]['cmpn_timesers'][()])
            except KeyError:
                print('Block %d is empty.' %blok_i)
            except IOError:
                if blok_lidx[blok_i]:
                    print('Block %d does not exist.' %blok_i)
    
        cn = len(Cmpn_position)
        ln = np.max([len(i) for i in Cmpn_spcesers])
        Cmpn_position_array = np.full((cn, ln, 3), -1, dtype=int)
        Cmpn_spcesers_array = np.full((cn, ln   ), np.nan)
        for i in range(cn):
            j = len(Cmpn_spcesers[i])
            Cmpn_position_array[i, :j] = Cmpn_position[i]
            Cmpn_spcesers_array[i, :j] = Cmpn_spcesers[i]
        Cmpn_timesers_array = np.array(Cmpn_timesers)
    
        with h5py.File(output_dir + 'Cells' + str(frame_i) + '.hdf5', 'w-') as file_handle:
            file_handle['Cmpn_position'] = Cmpn_position_array
            file_handle['Cmpn_spcesers'] = Cmpn_spcesers_array
            file_handle['Cmpn_timesers'] = Cmpn_timesers_array
    
            file_handle['freq'] = freq_stack
            file_handle['resn'] = np.array([resn_x, resn_x, resn_y, ds])
            file_handle['dims'] = np.array([lx//ds, ly//ds, lz, lt])
    
z4()

for frame_i in range(imageframe_nmbr):
    with h5py.File(output_dir + 'brain_mask' + str(frame_i) + '.hdf5', 'r') as file_handle:
        blok_nmbr = file_handle['blok_nmbr'][()]
        blok_lidx = file_handle['blok_lidx'][()]

    cell_dir = output_dir + 'cell_series/' + str(frame_i)
    Cell_position = []
    Cell_spcesers = []
    Cell_timesers = []
    for blok_i in range(blok_nmbr):
        print(blok_i)
        try:
            with h5py.File(cell_dir + '/Block' + str(blok_i).zfill(5) + '.hdf5', 'r') as file_handle:
                for cell_i in file_handle['cell']:
                    Cell_position.append(file_handle['cell'][cell_i]['cell_position'][()])
                    Cell_spcesers.append(file_handle['cell'][cell_i]['cell_spcesers'][()])
                    Cell_timesers.append(file_handle['cell'][cell_i]['cell_timesers'][()])
        except KeyError:
            print('file is empty')
        except IOError:
            if blok_lidx[blok_i]:
                print('file does not exist')

    cn = len(Cell_position)
    ln = np.max([len(i) for i in Cell_spcesers])
    Cell_position_array = np.full((cn, ln, 3), np.nan)
    Cell_spcesers_array = np.full((cn, ln   ), np.nan)
    for i in range(cn):
        j = len(Cell_spcesers[i])
        Cell_position_array[i, :j] = Cell_position[i]
        Cell_spcesers_array[i, :j] = Cell_spcesers[i]
    Cell_timesers_array = np.array(Cell_timesers)

    with h5py.File(output_dir + 'Cells' + str(frame_i) + '.hdf5', 'w-') as file_handle:
        file_handle['Cell_position'] = Cell_position_array
        file_handle['Cell_spcesers'] = Cell_spcesers_array
        file_handle['Cell_timesers'] = Cell_timesers_array

        file_handle['freq'] = freq_stack
        file_handle['resn'] = np.array([resn_x, resn_x, resn_y, ds])
        file_handle['dims'] = np.array([lx//ds, ly//ds, lz, lt])


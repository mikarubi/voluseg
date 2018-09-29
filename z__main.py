import os, multiprocessing
os.environ['MKL_NUM_THREADS'] = str(multiprocessing.cpu_count())

# navigate to the output directory first before executing this block
try:
    import h5py
    with h5py.File('prepro_parameters.hdf5', 'r') as file_handle:
        for key in file_handle:
            var = file_handle[key][()]
            try:         var = var.decode()
            except:
                try:     var = [i.decode() for i in var]
                except:
                    pass
                    
            exec(key + '=var')
    print('Successfully imported from prepro_parameters.hdf5')
except:
    print('Warning: Did not import from prepro_parameters.hdf5')
    pass

# get_ipython().run_line_magic('matplotlib', 'inline')
from past.builtins import execfile
execfile(code_dir + 'zfun.py')
execfile(code_dir + 'zfun_cell.py')

## actual preprocessing begins here ##

# 1. alignment (motion correction)
execfile(code_dir + 'z1_alignment.py')

# 2. series conversion
execfile(code_dir + 'z2_brain_mask.py')

# 3. cell detection
execfile(code_dir + 'z3_cell_detect.py')

# 4. cell collection into a single file
execfile(code_dir + 'z4_cell_collect.py')

# 5. cell cleaning and baseline detection
execfile(code_dir + 'z5_cell_clean.py')

# 6. component detection
execfile(code_dir + 'z6_components.py')

# shutdown spark job
os.system('spark-janelia-lsf stopcluster -f')

# find . -name "image_aligned*" -delete
# find . -name "Block*hdf5" -delete

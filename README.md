# New version of segmentation pipeline to be posted soon #

# Dependencies
- Red Hat Enterprise Linux 3.10.0
- Python 3.5.2 and IPython 5.3.0
- Apache Spark 1.6.2
- Advanced Normalization Tools (ANTS) 2.1.0

# Installation
- Copy all files into a separate directory
- Within the python environment set the following variables:

  	`code_dir = path_to_code_directory`

  	`ants_dir = path_to_ants_directory`

# Instructions and Demo
- Download an example dataset folder: 

	https://www.dropbox.com/sh/psrj9lusohj7epu/AAAbj8Jbb3o__pyKTTDxPvIKa?dl=0

- Launch IPython with Spark.

- Configure processing parameters in file `z__parameters.py`

```
ants_dir        = '/groups/ahrens/home/rubinovm/ants-2.1.0-redhat/'
code_dir        = '/groups/ahrens/home/rubinovm/mycode/zfish_prepro/code/'
input_dir       = '/groups/ahrens/home/rubinovm/mycode/zfish_prepro/input/'
output_dir      = '/groups/ahrens/home/rubinovm/mycode/zfish_prepro/output/'
alignment_type  = 'rigid'
dt              = 1
thr_mask        = 105
ds              = 1
blok_cell_nmbr  = 100
cell_diam       = 6.0
imageframe_nmbr = 1


# manually specify imaging parameters
resn_x = 0.812
resn_y = 0.812
resn_z = 1.0
lx = 512
ly = 444
lz = 1
t_exposure = 9.7
freq_stack = 2.66
t_stack = 1000.0 / freq_stack

# packed planes: set to 1 when single plane stacks are packed into a 3d-volume
packed_planes = 0

# configure parameters, function, variable and path definitions
from past.builtins import execfile
execfile(code_dir + 'zfun.py')
execfile(code_dir + 'z0_preliminaries.py')
os.chdir(output_dir)
```

- Load variables from the output directory and load processing functions in file `z__main.py`

```
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
```

- Execute code sequentially to perform cell and component detection from file `z__main.py`

```
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
```

- This pipeline produces cell data located in the file `Cells0_clean.hdf5` and component data located in the file `Cells0_clust.hdf5`. The following code allows to visualize the resulting component results:

```
import h5py
import numpy as np
import matplotlib.pyplot as plt

# load spatial and temporal components
with h5py.File('Cells0_clust.hdf5', 'r') as file_handle:
    W1 = file_handle['W1'][()]
    H1 = file_handle['H1'][()]

# load cell position and number
with h5py.File('Cells0_clean.hdf5', 'r') as file_handle:
    X = file_handle['Cell_X'][()]
    Y = file_handle['Cell_Y'][()]
    Z = file_handle['Cell_Z'][()]
    x = file_handle['x'][()]
    y = file_handle['y'][()]
    z = file_handle['z'][()]
    n = file_handle['n'][()]

# loop over components
for h in range(W1.shape[1]):
    
    # construct component volumes
    S = np.zeros((x, y, z))
    for i in range(n):
        for j in range(np.count_nonzero(np.isfinite(X[i]))):
            xij, yij, zij = int(X[i, j]), int(Y[i, j]), int(Z[i, j])
            S[xij, yij, zij] = np.maximum(S[xij, yij, zij], W1[i, h])

    # visualize component maximal projections
    plt.imshow(S.max(2))
    plt.show()
    
    # visualize component timeseries
    plt.plot(H1[h])
    plt.show()
```


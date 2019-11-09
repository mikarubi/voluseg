## add package to path
# dir_code = 'path/to/package'
# import sys
# sys.path.append(dir_code)

# check for updates
import os
from voluseg import update
update()

# import package
import voluseg

# set parameters
parameters = voluseg.parameter_dictionary()
parameters['dir_ants'] = '/groups/rubinov/home/rubinovm/bin/ants/bin/'
parameters['dir_input'] = '/groups/rubinov/rubinovlab/input/'
parameters['dir_output'] = '/groups/rubinov/rubinovlab/output/'
parameters['registration'] = 'rigid'
parameters['ds'] = 2
parameters['dt'] = 1
parameters['thr_mask'] = 0.5
parameters['diam_cell'] = 5.0
parameters['f_volume'] = 2.66

# save parameters
print("save parameters."); voluseg.step0_process_parameters(parameters)
print("process images."); voluseg.step1_process_images(parameters)
print("align images."); voluseg.step2_align_images(parameters)
print("mask images."); voluseg.step3_mask_images(parameters)
print("detect cells."); voluseg.step4_detect_cells(parameters)
print("clean cells."); voluseg.step5_clean_cells(parameters)

# this step loads parameters as needed
filename_parameters = os.path.join(parameters['dir_output'], 'parameters.pickle')
print("load parameters."); parameters = voluseg.load_parameters(filename_parameters)

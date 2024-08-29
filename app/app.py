import os
import pprint
import voluseg


# set and save parameters
parameters0 = voluseg.parameter_dictionary()
parameters0["dir_ants"] = "/ants-2.5.3/bin/"
parameters0["dir_input"] = "/voluseg/data/"
parameters0["dir_output"] = "/voluseg/output/"
parameters0["registration"] = "high"
parameters0["diam_cell"] = 5.0
parameters0["f_volume"] = 2.0
voluseg.step0_process_parameters(parameters0)

# load and print parameters
filename_parameters = os.path.join(parameters0["dir_output"], "parameters.pickle")
parameters = voluseg.load_parameters(filename_parameters)
pprint.pprint(parameters)

print("process volumes.")
voluseg.step1_process_volumes(parameters)

print("align volumes.")
voluseg.step2_align_volumes(parameters)

print("mask volumes.")
voluseg.step3_mask_volumes(parameters)

print("detect cells.")
voluseg.step4_detect_cells(parameters)

print("clean cells.")
voluseg.step5_clean_cells(parameters)

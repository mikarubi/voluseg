# Volumetric segmentation pipeline #

# Dependencies
- Red Hat Enterprise Linux 3.10.0
- Python 3.5.2 and IPython 5.3.0
- Apache Spark 1.6.2
- Advanced Normalization Tools (ANTS) 2.1.0

# Installation
- Copy all initial volumes into a separate directory
- Within the python environment set the following variables:

# Instructions and Demo
- Download an example dataset folder: 

	https://www.dropbox.com/sh/psrj9lusohj7epu/AAAbj8Jbb3o__pyKTTDxPvIKa?dl=0

- Launch IPython with Spark.

- Import package and load default parameters:

```
import voluseg
parameters = voluseg.parameter_dictionary()

```

- Set parameters as required (see `voluseg.parameter_dictionary??` for details)

- Execute code sequentially to perform cell detection (see illustration below)

```
import os

# save parameters
print("save parameters."); voluseg.step0_save_parameters(parameters)

# this step allows to load parameters in from file
filename_parameters = os.path.join(parameters['dir_output'], 'parameters.pickle')
print("load parameters."); parameters = voluseg.load_parameters(filename_parameters)

# run pipeline
print("process images."); voluseg.step1_process_images(parameters)
print("align images."); voluseg.step2_align_images(parameters)
print("mask images."); voluseg.step3_mask_images(parameters)
print("detect cells."); voluseg.step4_detect_cells(parameters)
print("clean cells."); voluseg.step5_clean_cells(parameters)
```

- This pipeline produces cell data located in the file `cells0_clean.hdf5`.

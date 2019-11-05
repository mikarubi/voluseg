# import os as _os
# 
# _mods = sorted(_os.listdir(_os.path.dirname(__file__)))
# __all__ = [i.split('.')[0] for i in sorted(_mods) if i[0]=='z' and i[1]!='_']
# # print(__all__)

import os
import git 

dir_code = os.path.dirname(os.path.realpath(__file__))
g = git.cmd.Git(dir_code)
g.pull()

from ._steps.step0 import preliminaries as step0_preliminaries
from ._steps.step1 import process_images as step1_process_images
from ._steps.step2 import align_images as step2_align_images
from ._steps.step3 import mask_volume as step3_mask_volume
from ._steps.step4 import detect_cells as step4_detect_cells
from ._steps.step5 import clean_cells as step5_clean_cells
# from ._steps.step6 import detect_systems as step6_detect_systems

from ._tools.parameters import parameters as parameter_template
from ._tools.load_parameters import load_parameters as load_parameters

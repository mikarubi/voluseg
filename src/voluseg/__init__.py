"""initialization"""

from importlib.metadata import version as _version

try:
    __version__ = _version("voluseg")
except Exception:  # package not installed
    __version__ = "unknown"

from voluseg._steps.step0 import define_parameters as step0_define_parameters
from voluseg._steps.step1 import process_volumes as step1_process_volumes
from voluseg._steps.step2 import align_volumes as step2_align_volumes
from voluseg._steps.step3 import mask_volumes as step3_mask_volumes
from voluseg._steps.step4 import detect_cells as step4_detect_cells
from voluseg._steps.step5 import clean_cells as step5_clean_cells

from voluseg._tools.parameters import load_parameters, save_parameters

import os
import pprint
import voluseg
import pytest
from pathlib import Path


@pytest.fixture
def setup_parameters(tmp_path):
    # Define parameters and paths
    parameters0 = voluseg.parameter_dictionary()
    parameters0['dir_ants'] = "/home/luiz/Downloads/ants-2.5.2/bin"  # Change this to your actual ANTs bin path
    # parameters0['dir_input'] = str((Path(".").resolve().parent / "sample_data"))
    parameters0['dir_input'] = "/mnt/shared_storage/taufferconsulting/client_catalystneuro/project_voluseg/sample_data"
    parameters0['dir_output'] = str(tmp_path)  # Use pytest's tmp_path fixture for output
    parameters0['registration'] = 'high'
    parameters0['diam_cell'] = 5.0
    parameters0['f_volume'] = 2.0

    # Save parameters
    voluseg.step0_process_parameters(parameters0)

    # Return parameters for further use in tests
    return parameters0


def test_voluseg_pipeline_h5_dir(setup_parameters):
    parameters = setup_parameters
    filename_parameters = os.path.join(parameters['dir_output'], 'parameters.pickle')
    parameters = voluseg.load_parameters(filename_parameters)
    pprint.pprint(parameters)

    # Run the pipeline steps
    print("Process volumes.")
    voluseg.step1_process_volumes(parameters)

    print("Align volumes.")
    voluseg.step2_align_volumes(parameters)

    print("Mask volumes.")
    voluseg.step3_mask_volumes(parameters)

    print("Detect cells.")
    voluseg.step4_detect_cells(parameters)

    print("Clean cells.")
    voluseg.step5_clean_cells(parameters)

    # # Assert that expected output files exist (example assertions)
    # assert os.path.exists(os.path.join(parameters['dir_output'], 'step1_output_file.ext')), "Step 1 output file missing"
    # assert os.path.exists(os.path.join(parameters['dir_output'], 'step2_output_file.ext')), "Step 2 output file missing"
    # assert os.path.exists(os.path.join(parameters['dir_output'], 'step3_output_file.ext')), "Step 3 output file missing"
    # assert os.path.exists(os.path.join(parameters['dir_output'], 'step4_output_file.ext')), "Step 4 output file missing"
    # assert os.path.exists(os.path.join(parameters['dir_output'], 'step5_output_file.ext')), "Step 5 output file missing"


# if __name__ == "__main__":
#     pytest.main()

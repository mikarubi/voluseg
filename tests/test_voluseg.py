import os
import pprint
import voluseg
import pytest
from pathlib import Path

from voluseg._tools import download_sample_data


@pytest.fixture
def setup_parameters(tmp_path):
    # Define parameters and paths
    parameters = voluseg.parameter_dictionary()

    # Download sample data, only if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        data_path = download_sample_data()
    else:
        data_path = "/change_path_to/sample_data"
    parameters["dir_input"] = data_path
    parameters["dir_ants"] = os.environ.get("ANTS_PATH")
    parameters["dir_output"] = str(tmp_path)  # Use pytest's tmp_path fixture for output
    parameters["registration"] = "high"
    parameters["diam_cell"] = 5.0
    parameters["f_volume"] = 2.0

    # Save parameters
    parameters = voluseg.step0_process_parameters(parameters)

    # Return parameters for further use in tests
    return parameters


def test_load_parameters(setup_parameters):
    # Load parameters
    file_path = str(Path(setup_parameters["dir_output"]) / "parameters.pickle")
    file_parameters = voluseg.load_parameters(file_path)

    all_keys = set(setup_parameters.keys()).union(set(file_parameters.keys()))

    for key in all_keys:
        assert key in setup_parameters, f"Key '{key}' is missing in setup_parameters"
        assert key in file_parameters, f"Key '{key}' is missing in file_parameters"
        if key in setup_parameters and key in file_parameters:
            assert (
                setup_parameters[key] == file_parameters[key]
            ), f"Value differs for key '{key}': setup_parameters has {setup_parameters[key]}, file_parameters has {file_parameters[key]}"


def test_voluseg_pipeline_h5_dir(setup_parameters):
    # Test step 1 - process volumes
    print("Process volumes.")
    voluseg.step1_process_volumes(setup_parameters)
    n_files_input = len([p for p in Path(setup_parameters["dir_input"]).glob("*.h5")])
    n_files_output = len(
        [
            p
            for p in (Path(setup_parameters["dir_output"]) / "volumes/0/").glob(
                "*.nii.gz"
            )
        ]
    )
    assert (
        n_files_input == n_files_output
    ), f"Number of input files ({n_files_input}) does not match number of output files ({n_files_output})"

    # Test step 2 - align volumes
    print("Align volumes.")
    voluseg.step2_align_volumes(setup_parameters)
    n_files_transform = len(
        [
            p
            for p in (Path(setup_parameters["dir_output"]) / "transforms/0/").glob(
                "*.mat"
            )
        ]
    )
    assert (
        n_files_output == n_files_transform
    ), f"Number of output files ({n_files_output}) does not match number of transform files ({n_files_transform})"

    # Test step 3 - mask volumes
    print("Mask volumes.")
    voluseg.step3_mask_volumes(setup_parameters)
    assert (
        Path(setup_parameters["dir_output"]) / "masks_plots/0/histogram.png"
    ).exists(), "Histogram plot does not exist"
    assert (
        Path(setup_parameters["dir_output"]) / "masks_plots/0/mask_z000.png"
    ).exists(), "Mask plot does not exist"

    # print("Detect cells.")
    # voluseg.step4_detect_cells(setup_parameters)

    # print("Clean cells.")
    # voluseg.step5_clean_cells(setup_parameters)

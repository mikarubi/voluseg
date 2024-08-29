import os
import voluseg
from voluseg._tools import download_sample_data
import pytest
from pathlib import Path
import numpy as np


# # To run tests locally, set these environment variables:
# os.environ["GITHUB_ACTIONS"] = "false"
# os.environ["ANTS_PATH"] = "/home/luiz/Downloads/ants-2.5.2/bin/"
# os.environ["SAMPLE_DATA_PATH"] = "/mnt/shared_storage/taufferconsulting/client_catalystneuro/project_voluseg/sample_data"


@pytest.fixture(scope="module")
def setup_parameters(tmp_path_factory):
    # Define parameters and paths
    parameters = voluseg.parameter_dictionary()

    # Download sample data, only if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        data_path = download_sample_data()
    else:
        data_path = os.environ.get("SAMPLE_DATA_PATH")
    parameters["dir_input"] = data_path
    parameters["dir_ants"] = os.environ.get("ANTS_PATH")

    # Use pytest's tmp_path_factory fixture for output
    tmp_dir = str(tmp_path_factory.mktemp("output"))
    parameters["dir_output"] = tmp_dir

    # Other parameters
    parameters["registration"] = "high"
    parameters["diam_cell"] = 5.0
    parameters["f_volume"] = 2.0

    # Save parameters
    parameters = voluseg.step0_process_parameters(parameters)

    # Return parameters for further use in tests
    return parameters


@pytest.mark.order(1)
def test_load_parameters(setup_parameters):
    # Load parameters
    file_path = str(Path(setup_parameters["dir_output"]) / "parameters.pickle")
    file_parameters = voluseg.load_parameters(file_path)

    all_keys = set(setup_parameters.keys()).union(set(file_parameters.keys()))

    for key in all_keys:
        assert key in setup_parameters, f"Key '{key}' is missing in setup_parameters"
        assert key in file_parameters, f"Key '{key}' is missing in file_parameters"
        if key in setup_parameters and key in file_parameters:
            value_setup = setup_parameters[key]
            value_file = file_parameters[key]

            if isinstance(value_setup, np.ndarray) and isinstance(value_file, np.ndarray):
                assert np.array_equal(value_setup, value_file), (
                    f"Value differs for key '{key}': "
                    f"setup_parameters has {value_setup}, file_parameters has {value_file}"
                )
            else:
                assert value_setup == value_file, (
                    f"Value differs for key '{key}': "
                    f"setup_parameters has {value_setup}, file_parameters has {value_file}"
                )


@pytest.mark.order(2)
def test_voluseg_h5_dir_step_1(setup_parameters):
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


@pytest.mark.order(3)
def test_voluseg_h5_dir_step_2(setup_parameters):
    # Test step 2 - align volumes
    print("Align volumes.")
    voluseg.step2_align_volumes(setup_parameters)
    n_files_output = len(
        [
            p
            for p in (Path(setup_parameters["dir_output"]) / "volumes/0/").glob(
                "*.hdf5"
            )
        ]
    )
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


@pytest.mark.order(4)
def test_voluseg_h5_dir_step_3(setup_parameters):
    # Test step 3 - mask volumes
    print("Mask volumes.")
    voluseg.step3_mask_volumes(setup_parameters)
    assert (
        Path(setup_parameters["dir_output"]) / "mask_plots/0/histogram.png"
    ).exists(), "Histogram plot does not exist"
    assert (
        Path(setup_parameters["dir_output"]) / "mask_plots/0/mask_z000.png"
    ).exists(), "Mask plot does not exist"

    # print("Detect cells.")
    # voluseg.step4_detect_cells(setup_parameters)

    # print("Clean cells.")
    # voluseg.step5_clean_cells(setup_parameters)

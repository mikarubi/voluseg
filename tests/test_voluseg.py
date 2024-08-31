import os
import voluseg
from voluseg._tools import download_sample_data
import pytest
from pathlib import Path
import numpy as np
import h5py


# # To run tests locally, set these environment variables:
# os.environ["GITHUB_ACTIONS"] = "false"
# os.environ["ANTS_PATH"] = "/home/luiz/Downloads/ants-2.5.2/bin/"
# os.environ["SAMPLE_DATA_PATH"] = (
#     "/mnt/shared_storage/taufferconsulting/client_catalystneuro/project_voluseg/sample_data"
# )


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
    parameters["dir_output"] = data_path + "/output"

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

            if isinstance(value_setup, np.ndarray) and isinstance(
                value_file, np.ndarray
            ):
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
    output_files = [
        p
        for p in (Path(setup_parameters["dir_output"]) / "volumes/0/").glob("*.nii.gz")
    ]
    n_files_output = len(output_files)
    assert (
        n_files_input == n_files_output
    ), f"Number of input files ({n_files_input}) does not match number of output files ({n_files_output})"


@pytest.mark.order(3)
def test_voluseg_h5_dir_step_2(setup_parameters):
    # Test step 2 - align volumes
    print("Align volumes.")
    voluseg.step2_align_volumes(setup_parameters)

    files_output = [
        p for p in (Path(setup_parameters["dir_output"]) / "volumes/0/").glob("*.hdf5")
    ]
    n_files_output = len(files_output)
    files_transform = [
        p
        for p in (Path(setup_parameters["dir_output"]) / "transforms/0/").glob("*.mat")
    ]
    n_files_transform = len(files_transform)
    assert (
        n_files_output == n_files_transform
    ), f"Number of output files ({n_files_output}) does not match number of transform files ({n_files_transform})"
    assert (
        Path(setup_parameters["dir_output"]) / "volumes/0/reference.nii.gz"
    ).exists(), "Reference file does not exist"


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

    mean_timeseries_file = Path(setup_parameters["dir_output"]) / "mean_timeseries.hdf5"
    assert mean_timeseries_file.exists(), "Mean timeseries file does not exist"
    mean_timeseries_keys = [
        "mean_baseline",
        "mean_timeseries",
        "mean_timeseries_raw",
        "timepoints",
    ]
    with h5py.File(mean_timeseries_file, "r") as file_handle:
        for k in mean_timeseries_keys:
            assert (
                k in file_handle.keys()
            ), f"Key '{k}' is missing in mean timeseries file"

    volume0_file = Path(setup_parameters["dir_output"]) / "volume0.hdf5"
    assert volume0_file.exists(), "Volume file does not exist"
    volume0_keys = [
        "background",
        "thr_intensity",
        "thr_probability",
        "volume_mask",
        "volume_mean",
        "volume_peak",
    ]
    with h5py.File(volume0_file, "r") as file_handle:
        for k in volume0_keys:
            assert k in file_handle.keys(), f"Key '{k}' is missing in volume file"


@pytest.mark.order(5)
def test_voluseg_h5_dir_step_4(setup_parameters):
    print("Detect cells.")
    voluseg.step4_detect_cells(setup_parameters)
    assert Path(
        Path(setup_parameters["dir_output"]) / "cells"
    ).exists(), "Cells directory does not exist"
    assert Path(
        Path(setup_parameters["dir_output"]) / "cells/0/block00000.hdf5"
    ).exists(), "Block file 00000 does not exist"
    assert Path(
        Path(setup_parameters["dir_output"]) / "cells/0/block00001.hdf5"
    ).exists(), "Block file 00001 does not exist"
    assert Path(
        Path(setup_parameters["dir_output"]) / "cells/0/block00002.hdf5"
    ).exists(), "Block file 00002 does not exist"
    assert Path(
        Path(setup_parameters["dir_output"]) / "cells/0/block00003.hdf5"
    ).exists(), "Block file 00003 does not exist"


@pytest.mark.order(6)
def test_voluseg_h5_dir_step_5(setup_parameters):
    print("Clean cells.")
    voluseg.step5_clean_cells(setup_parameters)
    # TODO - add asserts

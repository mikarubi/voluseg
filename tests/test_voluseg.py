import os
import voluseg
from voluseg._tools import download_sample_data
import pytest
from pathlib import Path
import numpy as np
import h5py
import copy


# # To run tests locally, set these environment variables:
# os.environ["GITHUB_ACTIONS"] = "false"
# os.environ["ANTS_PATH"] = "/home/luiz/Downloads/ants-2.5.2/bin/"
# os.environ["SAMPLE_DATA_PATH_H5"] = (
#     "/mnt/shared_storage/taufferconsulting/client_catalystneuro/project_voluseg/sample_data"
# )
# os.environ["SAMPLE_DATA_PATH_NWB"] = (
#     "/mnt/shared_storage/taufferconsulting/client_catalystneuro/project_voluseg/sample_twophoton.nwb"
# )


def compare_dicts(
    dict1: dict,
    dict1_name: str,
    dict2: dict,
    dict2_name: str,
):
    all_keys = set(dict1.keys()).union(set(dict2.keys()))
    for key in all_keys:
        assert key in dict1, f"Key '{key}' is missing in {dict1_name}"
        assert key in dict2, f"Key '{key}' is missing in {dict2_name}"
        if key in dict1 and key in dict2:
            value_1 = dict1[key]
            value_2 = dict2[key]

            if isinstance(value_1, (np.ndarray, list)) and isinstance(
                value_2, (np.ndarray, list)
            ):
                assert np.array_equal(value_1, value_2), (
                    f"Value differs for key '{key}': "
                    f"{dict1_name} has {value_1}, {dict2_name} has {value_2}"
                )
            else:
                assert value_1 == value_2, (
                    f"Value differs for key '{key}': "
                    f"{dict1_name} has {value_1}, {dict2_name} has {value_2}"
                )


@pytest.fixture(scope="module")
def setup_parameters(tmp_path_factory):
    """
    Setup parameters for tests, using h5 sample data.
    """
    # Define parameters and paths
    parameters = voluseg.parameter_dictionary()

    # Download sample data, only if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        tmp_dir_input = str(tmp_path_factory.mktemp("input_h5"))
        data_path = download_sample_data(destination_folder=tmp_dir_input)
    else:
        data_path = os.environ.get("SAMPLE_DATA_PATH_H5")
    parameters["dir_input"] = data_path

    # Use pytest's tmp_path_factory fixture for output
    tmp_dir = str(tmp_path_factory.mktemp("output_h5"))
    parameters["dir_output"] = tmp_dir

    # Other parameters
    parameters["registration"] = "high"
    parameters["diam_cell"] = 5.0
    parameters["f_volume"] = 2.0

    # Save parameters
    parameters = voluseg.step0_process_parameters(parameters)

    # Return parameters for further use in tests
    return parameters


@pytest.fixture(scope="module")
def setup_parameters_nwb(tmp_path_factory):
    """
    Setup parameters for tests, using nwb sample data.
    """
    # Define parameters and paths
    parameters = voluseg.parameter_dictionary()

    # Download sample data, only if running in GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true":
        tmp_dir_input = str(tmp_path_factory.mktemp("input_nwb"))
        data_path = download_sample_data(
            destination_folder=tmp_dir_input,
            data_type="nwb_file",
        )
    else:
        data_path = os.environ.get("SAMPLE_DATA_PATH_NWB")
    parameters["dir_input"] = data_path

    # Use pytest's tmp_path_factory fixture for output
    tmp_dir = str(tmp_path_factory.mktemp("output_nwb"))
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
def test_parameters_json_pickle(setup_parameters, tmp_path):
    """
    Test saving and loading parameters as JSON and pickle.
    """
    temp_json = str((tmp_path / "parameters.json").resolve())
    voluseg.save_parameters(setup_parameters, temp_json)
    loaded_parameters_json = voluseg.load_parameters(temp_json)

    temp_pickle = str((tmp_path / "parameters.pickle").resolve())
    voluseg.save_parameters(setup_parameters, temp_pickle)
    loaded_parameters_pickle = voluseg.load_parameters(temp_pickle)

    compare_dicts(
        loaded_parameters_json,
        "loaded_parameters_json",
        loaded_parameters_pickle,
        "loaded_parameters_pickle",
    )


@pytest.mark.order(1)
def test_load_parameters(setup_parameters):
    """
    Test loading parameters from a JSON file.
    """
    # Load parameters
    file_path = str(Path(setup_parameters["dir_output"]) / "parameters.json")
    file_parameters = voluseg.load_parameters(file_path)

    # Compare parameters
    compare_dicts(
        setup_parameters,
        "setup_parameters",
        file_parameters,
        "file_parameters",
    )


@pytest.mark.order(2)
def test_voluseg_h5_dir_step_1(setup_parameters):
    """
    Test the first step of the pipeline - process volumes.
    """
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
    """
    Test the second step of the pipeline - align volumes.
    """
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
    """
    Test the third step of the pipeline - mask volumes.
    """
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
    """
    Test the fourth step of the pipeline - detect cells.
    """
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


@pytest.mark.order(7)
def test_voluseg_pipeline_nwbfile(setup_parameters_nwb):
    """
    Test the full pipeline with an NWB file as input.
    """
    print("Process volumes.")
    voluseg.step1_process_volumes(setup_parameters_nwb)

    print("Align volumes.")
    voluseg.step2_align_volumes(setup_parameters_nwb)

    print("Mask volumes.")
    voluseg.step3_mask_volumes(setup_parameters_nwb)

    print("Detect cells.")
    voluseg.step4_detect_cells(setup_parameters_nwb)

    # print("Clean cells.")
    # voluseg.step5_clean_cells(setup_parameters_nwb)


@pytest.mark.order(8)
def compare_results_nwb_and_h5_dir(
    setup_parameters,
    setup_parameters_nwb,
):
    """
    Compare segmentation results from the pipeline with h5 and nwb files.
    """
    result_nwb = Path(setup_parameters_nwb["dir_output"]) / "cells/0/block00000.hdf5"
    hdf_nwb = h5py.File(result_nwb, "r")

    result_h5 = Path(setup_parameters["dir_output"]) / "cells/0/block00000.hdf5"
    hdf_h5 = h5py.File(result_h5, "r")

    assert (
        hdf_nwb["n_cells"][()] == hdf_h5["n_cells"][()]
    ), "Different number of cells between NWB and h5 results"
    assert (
        hdf_nwb["completion"][()] == hdf_h5["completion"][()]
    ), "Different completion value between NWB and h5 results"
    assert np.array_equal(
        hdf_nwb["cell"]["00001"]["xyz"][:],
        hdf_h5["cell"]["00001"]["xyz"][:],
    ), "Different cell coordinates between NWB and h5 results"
    assert np.array_equal(
        hdf_nwb["cell"]["00001"]["weights"][:],
        hdf_h5["cell"]["00001"]["weights"][:],
    ), "Different cell weights between NWB and h5 results"
    assert np.array_equal(
        hdf_nwb["cell"]["00001"]["timeseries"][:],
        hdf_h5["cell"]["00001"]["timeseries"][:],
    ), "Different cell weights between NWB and h5 results"


@pytest.mark.order(9)
def test_voluseg_h5_dir_step_5(setup_parameters):
    """
    Test the fifth step of the pipeline - clean cells.
    """
    print("Clean cells.")
    voluseg.step5_clean_cells(setup_parameters)

    clean_cells_file = Path(setup_parameters["dir_output"]) / "cells0_clean.hdf5"
    assert clean_cells_file.exists(), "Cleaned cells file does not exist"

    hdf_h5 = h5py.File(clean_cells_file, "r")
    keys = [
        "background",
        "cell_baseline",
        "cell_block_id",
        "cell_timeseries",
        "cell_timeseries_raw",
        "cell_weights",
        "cell_x",
        "cell_y",
        "cell_z",
        "n",
        "t",
        "volume_id",
        "volume_weight",
        "x",
        "y",
        "z",
    ]
    for k in keys:
        assert k in hdf_h5.keys(), f"Key '{k}' is missing in cleaned cells file"


@pytest.mark.order(10)
def test_save_result_as_nwb(setup_parameters):
    """
    Test saving results as an NWB file.
    """
    from voluseg._tools.nwb import write_nwbfile

    clean_cells_file = Path(setup_parameters["dir_output"]) / "cells0_clean.hdf5"
    hdf_h5 = h5py.File(clean_cells_file, "r")
    write_nwbfile(
        output_path=str(Path(setup_parameters["dir_output"]) / "cells0_clean.nwb"),
        cell_x=hdf_h5["cell_x"][:],
        cell_y=hdf_h5["cell_y"][:],
        cell_z=hdf_h5["cell_z"][:],
        cell_weights=hdf_h5["cell_weights"][:],
        cell_timeseries=hdf_h5["cell_timeseries"][:],
    )
    # Check if the file was created
    assert (
        Path(setup_parameters["dir_output"]) / "cells0_clean.nwb"
    ).exists(), "NWB file was not created"


@pytest.mark.order(11)
def test_nwb_remote(tmp_path):
    """
    Test for remote NWB files.
    """
    # Define parameters and paths
    parameters = voluseg.parameter_dictionary()

    # Using this file: https://dandiarchive.org/dandiset/000350/0.240822.1759/files?location=sub-20161022-1&page=1
    parameters["dir_input"] = (
        "https://dandiarchive.s3.amazonaws.com/blobs/057/ecb/057ecbef-e732-4e94-8d99-40ebb74d346e"
    )

    # Use pytest's tmp_path fixture for output
    parameters["dir_output"] = str(tmp_path)

    # Other parameters
    parameters["registration"] = "high"
    parameters["diam_cell"] = 5.0
    parameters["f_volume"] = 2.0
    parameters["timepoints"] = 20

    print("Process parameters")
    parameters = voluseg.step0_process_parameters(parameters)

    print("Process volumes.")
    voluseg.step1_process_volumes(parameters)

    output_files = [
        p for p in (Path(parameters["dir_output"]) / "volumes/0/").glob("*.nii.gz")
    ]
    n_files_output = len(output_files)
    assert (
        n_files_output == parameters["timepoints"]
    ), f"Number of output files ({n_files_output}) does not match number of timepoints ({parameters['timepoints']})"

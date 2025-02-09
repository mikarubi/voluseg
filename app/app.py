import os
import typer
from typing_extensions import Annotated
import voluseg
from voluseg._tools.aws import export_to_s3


app = typer.Typer()


@app.command()
def run_pipeline(
    detrending: Annotated[str, typer.Option(envvar="VOLUSEG_DETRENDING")] = "standard",
    registration: Annotated[
        str, typer.Option(envvar="VOLUSEG_REGISTRATION")
    ] = "medium",
    registration_opts: Annotated[
        str, typer.Option(envvar="VOLUSEG_REGISTRATION_OPTS")
    ] = "",
    diam_cell: Annotated[float, typer.Option(envvar="VOLUSEG_DIAM_CELL")] = 6.0,
    ds: Annotated[int, typer.Option(envvar="VOLUSEG_DS")] = 2,
    planes_pad: Annotated[int, typer.Option(envvar="VOLUSEG_PLANES_PAD")] = 0,
    parallel_extra: Annotated[
        bool, typer.Option(envvar="VOLUSEG_PARALLEL_EXTRA")
    ] = False,
    save_volume: Annotated[bool, typer.Option(envvar="VOLUSEG_SAVE_VOLUME")] = False,
    type_timepoints: Annotated[
        str, typer.Option(envvar="VOLUSEG_TYPE_TIMEPOINTS")
    ] = "dff",
    type_mask: Annotated[str, typer.Option(envvar="VOLUSEG_TYPE_MASK")] = "geomean",
    timepoints: Annotated[int, typer.Option(envvar="VOLUSEG_TIMEPOINTS")] = 1000,
    f_hipass: Annotated[float, typer.Option(envvar="VOLUSEG_F_HIPASS")] = 0,
    f_volume: Annotated[float, typer.Option(envvar="VOLUSEG_F_VOLUME")] = 2.0,
    n_cells_block: Annotated[int, typer.Option(envvar="VOLUSEG_N_CELLS_BLOCK")] = 316,
    n_colors: Annotated[int, typer.Option(envvar="VOLUSEG_N_COLORS")] = 1,
    res_x: Annotated[float, typer.Option(envvar="VOLUSEG_RES_X")] = 0.40625,
    res_y: Annotated[float, typer.Option(envvar="VOLUSEG_RES_Y")] = 0.40625,
    res_z: Annotated[float, typer.Option(envvar="VOLUSEG_RES_Z")] = 5.0,
    t_baseline: Annotated[int, typer.Option(envvar="VOLUSEG_T_BASELINE")] = 300,
    t_section: Annotated[float, typer.Option(envvar="VOLUSEG_T_SECTION")] = 0.01,
    thr_mask: Annotated[float, typer.Option(envvar="VOLUSEG_THR_MASK")] = 0.5,
    dir_input: Annotated[
        str, typer.Option(envvar="VOLUSEG_DIR_INPUT")
    ] = "/voluseg/data/",
    dir_output: Annotated[
        str, typer.Option(envvar="VOLUSEG_DIR_OUTPUT")
    ] = "/tmp/voluseg_output",
):
    # set and save parameters
    parameters0 = voluseg.parameter_dictionary()
    parameters0["dir_input"] = dir_input
    parameters0["dir_output"] = dir_output

    # user-defined parameters
    parameters0["detrending"] = detrending
    parameters0["registration"] = registration
    parameters0["registration_opts"] = registration_opts
    parameters0["diam_cell"] = diam_cell
    parameters0["ds"] = ds
    parameters0["planes_pad"] = planes_pad
    parameters0["parallel_extra"] = parallel_extra
    parameters0["save_volume"] = save_volume
    parameters0["type_timepoints"] = type_timepoints
    parameters0["type_mask"] = type_mask
    parameters0["timepoints"] = timepoints
    parameters0["f_hipass"] = f_hipass
    parameters0["f_volume"] = f_volume
    parameters0["n_cells_block"] = n_cells_block
    parameters0["n_colors"] = n_colors
    parameters0["res_x"] = res_x
    parameters0["res_y"] = res_y
    parameters0["res_z"] = res_z
    parameters0["t_baseline"] = t_baseline
    parameters0["t_section"] = t_section
    parameters0["thr_mask"] = thr_mask

    voluseg.step0_process_parameters(parameters0)
    filename_parameters = str(
        os.path.join(parameters0["dir_output"], "parameters.json")
    )
    parameters = voluseg.load_parameters(filename_parameters)
    print("Parameters:\n", parameters)

    print("Process volumes...")
    voluseg.step1_process_volumes(parameters)

    print("Align volumes...")
    voluseg.step2_align_volumes(parameters)

    print("Mask volumes...")
    voluseg.step3_mask_volumes(parameters)

    print("Detect cells...")
    voluseg.step4_detect_cells(parameters)

    print("Clean cells...")
    voluseg.step5_clean_cells(parameters)

    print("Save results to S3...")
    stack_id = "VolusegBatchStack"
    bucket_name = f"{stack_id}-bucket".lower()
    job_id = os.environ.get("VOLUSEG_JOB_ID")
    local_file = str(os.path.join(dir_output, "cells0_clean.hdf5"))
    object_name = f"{job_id}/cells0_clean.hdf5"
    export_to_s3(
        local_path=local_file,
        bucket_name=bucket_name,
        object_name=object_name,
    )


if __name__ == "__main__":
    app()

import os
import typer
from typing_extensions import Annotated
import voluseg
from voluseg._tools.aws import export_to_s3

app = typer.Typer()

@app.command()
def run_pipeline(
    detrending: Annotated[str, typer.Option(envvar="VOLUSEG_DETRENDING")] = "standard",
    registration: Annotated[str, typer.Option(envvar="VOLUSEG_REGISTRATION")] = "medium",
    opts_ants: Annotated[str, typer.Option(envvar="OPTIONS_ANTS")] = "",
    diam_cell: Annotated[float, typer.Option(envvar="VOLUSEG_DIAM_CELL")] = 6.0,
    ds: Annotated[int, typer.Option(envvar="VOLUSEG_DS")] = 2,
    planes_pad: Annotated[int, typer.Option(envvar="VOLUSEG_PLANES_PAD")] = 0,
    parallel_extra: Annotated[bool, typer.Option(envvar="VOLUSEG_PARALLEL_EXTRA")] = False,
    save_volume: Annotated[bool, typer.Option(envvar="VOLUSEG_SAVE_VOLUME")] = False,
    type_timepoints: Annotated[str, typer.Option(envvar="VOLUSEG_TYPE_TIMEPOINTS")] = "dff",
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
    dir_input: Annotated[str, typer.Option(envvar="VOLUSEG_DIR_INPUT")] = "/voluseg/data/",
    dir_output: Annotated[str, typer.Option(envvar="VOLUSEG_DIR_OUTPUT")] = "/tmp/voluseg_output",
    # Dask configuration options
    dask_config_file: Annotated[str, typer.Option(envvar="VOLUSEG_DASK_CONFIG_FILE")] = "",
    dask_n_workers: Annotated[int, typer.Option(envvar="VOLUSEG_DASK_N_WORKERS")] = 0,
    dask_n_cores_per_worker: Annotated[int, typer.Option(envvar="VOLUSEG_DASK_N_CORES_PER_WORKER")] = 1,
    dask_memory_limit: Annotated[str, typer.Option(envvar="VOLUSEG_DASK_MEMORY_LIMIT")] = "2GB",
    dask_cluster_type: Annotated[str, typer.Option(envvar="VOLUSEG_DASK_CLUSTER_TYPE")] = "local",
):
    # set and save parameters
    filename_parameters = voluseg.step0_define_parameters(
        dir_input=dir_input,
        dir_output=dir_output,
        detrending=detrending,
        registration=registration,
        opts_ants=opts_ants,
        diam_cell=diam_cell,
        ds=ds,
        planes_pad=planes_pad,
        parallel_extra=parallel_extra,
        save_volume=save_volume,
        type_timepoints=type_timepoints,
        type_mask=type_mask,
        timepoints=timepoints,
        f_hipass=f_hipass,
        f_volume=f_volume,
        n_cells_block=n_cells_block,
        n_colors=n_colors,
        res_x=res_x,
        res_y=res_y,
        res_z=res_z,
        t_baseline=t_baseline,
        t_section=t_section,
        thr_mask=thr_mask,
    )

    parameters = voluseg.load_parameters(filename_parameters)
    
    # Configure Dask if options are provided
    dask_config = {}
    if dask_config_file:
        dask_config['config_file'] = dask_config_file
    if dask_n_workers > 0:
        dask_config['n_workers'] = dask_n_workers
    if dask_n_cores_per_worker > 0:
        dask_config['n_cores_per_worker'] = dask_n_cores_per_worker
    if dask_memory_limit:
        dask_config['memory_limit'] = dask_memory_limit
    if dask_cluster_type:
        dask_config['cluster_type'] = dask_cluster_type
    
    if dask_config:
        parameters['dask_config'] = dask_config
        # Configure Dask
        client = voluseg.configure_dask_from_parameters(parameters)
        print(f"Dask configured: {client.dashboard_link}")
    
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

"""Command-line interface for the Voluseg pipeline.

Installed as the ``voluseg`` console script; ``app/app.py`` keeps the
container entry point (``python3 /voluseg/app/app.py``) working.
"""

import json
from typing import Annotated, Optional

import typer

app = typer.Typer(add_completion=False)


def _version_callback(value: bool) -> None:
    if value:
        from importlib.metadata import version

        print(f"voluseg {version('voluseg')}")
        raise typer.Exit()


@app.command()
def run_pipeline(
    dir_input: Annotated[str, typer.Option(envvar="VOLUSEG_DIR_INPUT")] = "/voluseg/data/",
    dir_output: Annotated[str, typer.Option(envvar="VOLUSEG_DIR_OUTPUT")] = "/tmp/voluseg_output",
    detrending: Annotated[str, typer.Option(envvar="VOLUSEG_DETRENDING")] = "standard",
    registration: Annotated[str, typer.Option(envvar="VOLUSEG_REGISTRATION")] = "medium",
    opts_ants: Annotated[
        str,
        typer.Option(
            envvar="VOLUSEG_OPTS_ANTS",
            help="ANTs registration options as a JSON object, e.g. '{\"verbose\": \"1\"}'.",
        ),
    ] = "{}",
    registration_restrict: Annotated[
        str,
        typer.Option(
            envvar="VOLUSEG_REGISTRATION_RESTRICT",
            help="Restrict transform parameters, e.g. '1x1x1x1x1x0'.",
        ),
    ] = "",
    diam_cell: Annotated[float, typer.Option(envvar="VOLUSEG_DIAM_CELL")] = 6.0,
    dim_order: Annotated[str, typer.Option(envvar="VOLUSEG_DIM_ORDER")] = "zyx",
    dir_transform: Annotated[
        str,
        typer.Option(
            envvar="VOLUSEG_DIR_TRANSFORM",
            help="Directory of precomputed transforms (required for registration='transform').",
        ),
    ] = "",
    nwb_output: Annotated[bool, typer.Option(envvar="VOLUSEG_NWB_OUTPUT")] = False,
    ds: Annotated[int, typer.Option(envvar="VOLUSEG_DS")] = 2,
    planes_pad: Annotated[int, typer.Option(envvar="VOLUSEG_PLANES_PAD")] = 0,
    planes_packed: Annotated[
        bool,
        typer.Option(
            envvar="VOLUSEG_PLANES_PACKED",
            help="Input volumes contain packed planes (single-plane imaging).",
        ),
    ] = False,
    parallel_extra: Annotated[bool, typer.Option(envvar="VOLUSEG_PARALLEL_EXTRA")] = True,
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
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=_version_callback, is_eager=True),
    ] = None,
):
    """Run the full Voluseg pipeline (steps 0-5)."""
    import voluseg

    # parse ANTs options (ParametersModel expects a dict, not a string)
    opts_ants_dict = json.loads(opts_ants) if opts_ants.strip() else {}

    kwargs = dict(
        dir_input=dir_input,
        dir_output=dir_output,
        detrending=detrending,
        registration=registration,
        registration_restrict=registration_restrict,
        opts_ants=opts_ants_dict,
        diam_cell=diam_cell,
        dim_order=dim_order,
        nwb_output=nwb_output,
        ds=ds,
        planes_pad=planes_pad,
        planes_packed=planes_packed,
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
    # dir_transform is validated as a directory path; only pass it when set
    if dir_transform:
        kwargs["dir_transform"] = dir_transform

    filename_parameters = voluseg.step0_define_parameters(**kwargs)
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


if __name__ == "__main__":
    app()

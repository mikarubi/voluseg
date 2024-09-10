import os
import voluseg
import typer


app = typer.Typer()


@app.command()
def run_pipeline(
    detrending: str = "standard",
    registration: str = "medium",
    registration_restrict: str = "",
    diam_cell: float = 6.0,
    ds: int = 2,
    planes_pad: int = 0,
    planes_packed: bool = False,
    parallel_clean: bool = True,
    parallel_volume: bool = True,
    save_volume: bool = False,
    type_timepoints: str = "dff",
    type_mask: str = "geomean",
    timepoints: int = 1000,
    f_hipass: float = 0,
    f_volume: float = 2.0,
    n_cells_block: int = 316,
    n_colors: int = 1,
    res_x: float = 0.40625,
    res_y: float = 0.40625,
    res_z: float = 5.0,
    t_baseline: int = 300,
    t_section: float = 0.01,
    thr_mask: float = 0.5,
):
    # set and save parameters
    parameters0 = voluseg.parameter_dictionary()
    parameters0["dir_ants"] = "/ants-2.5.3/bin/"
    parameters0["dir_input"] = "/voluseg/data/"
    parameters0["dir_output"] = "/voluseg/output/"

    # user-defined parameters
    parameters0["detrending"] = detrending
    parameters0["registration"] = registration
    parameters0["registration_restrict"] = registration_restrict
    parameters0["diam_cell"] = diam_cell
    parameters0["ds"] = ds
    parameters0["planes_pad"] = planes_pad
    parameters0["planes_packed"] = planes_packed
    parameters0["parallel_clean"] = parallel_clean
    parameters0["parallel_volume"] = parallel_volume
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

    print("process volumes.")
    voluseg.step1_process_volumes(parameters)

    print("align volumes.")
    voluseg.step2_align_volumes(parameters)

    print("mask volumes.")
    voluseg.step3_mask_volumes(parameters)

    print("detect cells.")
    voluseg.step4_detect_cells(parameters)

    print("clean cells.")
    voluseg.step5_clean_cells(parameters)


if __name__ == "__main__":
    app()

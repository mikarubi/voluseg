import os
import h5py
import numpy as np
from types import SimpleNamespace
from typing import Tuple

from voluseg._tools.constants import hdf
from voluseg._tools.evenly_parallelize import evenly_parallelize


def collect_blocks(
    color_i: int,
    parameters: dict,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Collect cells across all blocks.

    Parameters
    ----------
    color_i : int
        Color index.
    parameters : dict
        Parameters dictionary.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        Tuple of cell block id, cell xyz, cell weights, cell timeseries, and cell lengths.
    """

    p = SimpleNamespace(**parameters)

    dir_cell = os.path.join(p.dir_output, "cells", str(color_i))

    fullname_volmean = os.path.join(p.dir_output, "volume%d" % (color_i))
    with h5py.File(fullname_volmean + hdf, "r") as file_handle:
        block_valids = file_handle["block_valids"][()]

    # define function to get data
    def get_data(ii):

        cell_block_id = []
        cell_xyz = []
        cell_weights = []
        cell_timeseries = []
        try:
            fullname_block = os.path.join(dir_cell, "block%05d" % (ii))
            with h5py.File(fullname_block + hdf, "r") as file_handle:
                for ci in range(file_handle["n_cells"][()]):
                    cell_xyz.append(file_handle["/cell/%05d/xyz" % (ci)][()])
                    cell_weights.append(file_handle["/cell/%05d/weights" % (ci)][()])
                    cell_timeseries.append(
                        file_handle["/cell/%05d/timeseries" % (ci)][()]
                    )
                    cell_block_id.append(ii)

        except KeyError:
            print("block %d is empty." % ii)
        except IOError:
            print("block %d does not exist." % ii)

        return [cell_block_id, cell_xyz, cell_weights, cell_timeseries]

    # define accumulator
    def accum_data(val1, val2):
        return [val1[i] + val2[i] for i in range(4)]

    # cumulate collected cells
    init_data = [[]] * 4
    idx_block_valids = np.argwhere(block_valids).T[0]
    if p.parallel_extra:
        block_validsRDD = evenly_parallelize(idx_block_valids)
        cell_dataRDD = block_validsRDD.map(get_data)
        cell_data = cell_dataRDD.fold(accum_data, initial=init_data).compute()
    else:
        cell_data = init_data
        for ii in idx_block_valids:
            cell_data = accum_data(cell_data, get_data(ii))

    # extract data
    cell_block_id, cell_xyz, cell_weights, cell_timeseries = cell_data
    cn = len(cell_xyz)
    cell_block_id = np.array(cell_block_id)
    cell_lengths = np.array([len(i) for i in cell_weights])
    cell_xyz_array = np.full((cn, np.max(cell_lengths), 3), -1, dtype=int)
    cell_weights_array = np.full((cn, np.max(cell_lengths)), np.nan)
    for ci, li in enumerate(cell_lengths):
        cell_xyz_array[ci, :li] = cell_xyz[ci]
        cell_weights_array[ci, :li] = cell_weights[ci]
    cell_timeseries_array = np.array(cell_timeseries)

    return (
        cell_block_id,
        cell_xyz_array,
        cell_weights_array,
        cell_timeseries_array,
        cell_lengths,
    )

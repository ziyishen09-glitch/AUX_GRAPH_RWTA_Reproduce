"""I/O related operations such as R/W data from disk and viz-related ops

"""

import os
import glob
import logging
from typing import List

import numpy as np
import matplotlib.pyplot as plt

__all__ = ('write_bp_to_disk', 'write_it_to_disk', 'plot_bp')

logger = logging.getLogger(__name__)


def write_bp_to_disk(result_dir: str,
                     filename: str, bplist: List[float]) -> None:
    """Writes blocking probabilities to text file

    Args:
        result_dir: directory to write files to
        filename: name of the file to be written
        itlist: list of blocking probability values, as percentages, to be
            dumped to file

    """
    if not os.path.isdir(result_dir):
        logger.info('Creating result dir in %s' % result_dir)
        os.mkdir(result_dir)

    filepath = os.path.join(result_dir, filename)
    logger.info('Writing blocking probability results to file "%s"' % filepath)
    with open(filepath, 'a') as f:
        for bp in bplist:
            f.write(' %7.3f' % bp)
        f.write('\n')


def write_it_to_disk(result_dir: str,
                     filename: str, itlist: List[float]) -> None:
    """Writes profiling time information to text file

    Args:
        result_dir: directory to write files to
        filename: name of the file to be written
        itlist: list of times, in seconds, to be dumped to file

    """
    if not os.path.isdir(result_dir):
        logger.info('Creating result dir in %s' % result_dir)
        os.mkdir(result_dir)

    filepath = os.path.join(result_dir, filename)
    logger.info('Writing simulation profiling times to file "%s"' % filepath)
    with open(filepath, 'a') as f:
        for it in itlist:
            f.write(' %7.7f' % it)
        # ensure each run ends with a newline so files contain one run per line
        f.write('\n')


def plot_bp(result_dir: str, load_min: int = 1, load_max: int | None = None, load_step: int = 1) -> None:
    """Reads blocking probabilities from `.bp` files and plot them.

    Each `.bp` file is expected to contain one simulation per line, where
    columns are blocking probabilities for increasing loads. This function
    will plot the mean across lines when multiple simulations are present,
    and the x-axis will correspond to loads starting at ``load_min``.

    Args:
        result_dir: directory that stores `*.bp` files to be read
        load_min: integer load value corresponding to the first column
            in the bp files (default: 1)
        load_max: optional integer upper bound for load; when provided the
            function will pad or truncate columns so the x-axis ranges from
            ``load_min`` to ``load_max`` inclusive.
    """
    filelist = []
    for f in glob.glob(os.path.join(result_dir, '*.bp')):
        filelist.append(os.path.basename(f))
        # read file line-by-line to tolerate ragged rows (different lengths)
        rows: list[list[float]] = []
        with open(f, 'r') as fh:
            for line in fh:
                parts = line.strip().split()
                if not parts:
                    continue
                try:
                    nums = [float(p) for p in parts]
                except ValueError:
                    # skip malformed lines
                    continue
                rows.append(nums)

        if not rows:
            continue

        # pad rows with NaN to make a rectangular array
        max_cols = max(len(r) for r in rows)
        data = np.full((len(rows), max_cols), np.nan)
        for i, r in enumerate(rows):
            data[i, :len(r)] = r


        # If user supplied load_max, align number of columns to expected
        if load_max is not None:
            if load_max < load_min:
                logger.warning('load_max < load_min, ignoring load_max')
            else:
                # number of expected columns given the step
                expected_cols = int((load_max - load_min) // load_step + 1)
                if expected_cols > data.shape[1]:
                    # pad additional columns with NaN
                    new_data = np.full((data.shape[0], expected_cols), np.nan)
                    new_data[:, : data.shape[1]] = data
                    data = new_data
                elif expected_cols < data.shape[1]:
                    # truncate extra columns
                    data = data[:, :expected_cols]

        ncols = data.shape[1]
        # construct x values starting at load_min stepping by load_step
        x = load_min + np.arange(ncols) * load_step

        if data.shape[0] == 1:
            y = data[0, :]
        else:
            # take nanmean across rows to ignore padding NaNs
            y = np.nanmean(data, axis=0)

        plt.plot(x, y, '--')

        # set x-limits to encompass half a step beyond first/last tick
        half = max(0.5, load_step / 2.0)
        plt.xlim(load_min - half, load_min + (ncols - 1) * load_step + half)
        if data.shape[0] < 10:
            logger.warning(
                'Remember you should simulate at least 10 times '
                '(found only %d in %s)' % (data.shape[0], f)
            )

    if not filelist:
        logger.warning('No .bp files found in %s' % result_dir)
        return

    plt.grid()
    plt.ylabel('Blocking probability (%)', fontsize=18)
    plt.xlabel('Load (Erlangs)', fontsize=18)
    plt.title('Average mean blocking probability', fontsize=20)
    plt.legend(filelist)
    plt.show(block=True)

#!/usr/bin/env python3

import numpy as np


def perturbative_beta(x, n, nf=12):
    # Eqs. (22), (24) of 1606.03756
    beta = np.asarray(
        [
            11 - 2 * nf / 3,
            102 - 38 * nf / 3,
        ]
    )
    return -((4 * np.pi) ** 2) * np.sum(
        (x / (4 * np.pi) ** 2) ** (np.arange(n)[:, np.newaxis] + 2)
        * beta[:n, np.newaxis],
        axis=0,
    )


def add_perturbative_lines(ax, xmin, xmax):
    analytic_range = np.linspace(xmin, xmax, 1000)
    for n_loops, dashes in [(1, (3, 1)), (2, (1, 1))]:
        ax.plot(
            analytic_range,
            perturbative_beta(analytic_range, n_loops),
            dashes=dashes,
            color="grey",
            label=f"{n_loops}-loop univ." if n_loops <= 2 else f"{n_loops}-loop GF",
        )

#!/usr/bin/env python3

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyerrors as pe

from fit_beta_against_g2 import interpolating_form
from plots import ColourRegistry, errorbar_pyerrors
from read import read_all_fit_results


def read_file(filename):
    read_data = pe.input.json.load_json_dict(filename, verbose=False)
    parsed_data = []
    for key, fit_parameters in read_data.items():
        beta_str, observable, time_str = key.split("|")
        for param in fit_parameters:
            param.gamma_method()
        parsed_data.append(
            {
                "beta": float(beta_str),
                "observable": observable,
                "time": float(time_str),
                "continuum": fit_parameters[0],
                "slope": fit_parameters[1],
            }
        )

    df = (
        pd.DataFrame(parsed_data)
        .pivot(columns=["observable"], index=["beta", "time"])
        .reset_index()
    )
    return df


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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("fit_filenames", nargs="+", metavar="beta_fit_filename")
    parser.add_argument("--plot_filename", default=None)
    parser.add_argument("--plot_styles", default="styles/paperdraft.mplstyle")
    return parser.parse_args()


def split_errors(series):
    return [datum.value for datum in series], [datum.dvalue for datum in series]


def output_fits(fit_results, filename):
    pe.input.json.dump_dict_to_json(fit_results, filename)


def plot_fit(x_values, fit_result, ax, colour=None):
    scan_x = np.linspace(min(x_values), max(x_values), 1000)
    scan_y = interpolating_form(np.asarray(fit_result, dtype=float), scan_x)
    scan_errors = pe.fits.error_band(scan_x, interpolating_form, fit_result)
    ax.fill_between(
        scan_x, scan_y + scan_errors, scan_y - scan_errors, color=colour, alpha=0.2
    )


def plot(fit_results, filename=None):
    fig, ax = plt.subplots()
    colours = ColourRegistry()

    ax.set_xlabel(r"$g_{\mathrm{GF}}^2(t; g_0^2)$")
    ax.set_ylabel(r"$\beta_{\mathrm{GF}}(t; g_0^2)$")

    for result in fit_results:
        data = read_all_fit_results(
            [source["filename"] for source in result["data_sources"]]
        )
        time = result["time"]
        gGF2 = [datum["gGF^2"][0] for datum in data]
        betaGF = [datum["betaGF"][0] for datum in data]
        errorbar_pyerrors(
            ax,
            gGF2,
            betaGF,
            label=f"$t / a^2 = {time}$",
            linestyle="none",
            color=colours[result["time"]],
        )

        plot_fit(
            [value.value for value in gGF2],
            result["beta_interpolation"],
            ax,
            colour=colours[result["time"]],
        )

    _, xmax = ax.get_xlim()
    analytic_range = np.linspace(0, xmax, 1000)
    for n_loops, dashes in [(1, (3, 1)), (2, (1, 1))]:
        ax.plot(
            analytic_range,
            perturbative_beta(analytic_range, n_loops),
            dashes=dashes,
            color="grey",
        )

    ax.set_xlim(0, xmax)
    ax.set_ylim(-2.4, 0.6)
    ax.legend(loc="best")

    if filename is None:
        plt.show()
    else:
        fig.savefig(filename)
        plt.close(fig)


def main():
    args = get_args()
    plt.style.use(args.plot_styles)
    fit_results = read_all_fit_results(args.fit_filenames)
    plot(fit_results, filename=args.plot_filename)


if __name__ == "__main__":
    main()

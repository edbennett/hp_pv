#!/usr/bin/env python

import argparse

import matplotlib.pyplot as plt
import numpy as np
import pyerrors as pe

from extrapolate_infinite_volume import get_scales_at_time, linear_fit
from plots import ColourRegistry, errorbar_pyerrors
from read import get_all_flows, read_all_fit_results


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("fit_filenames", metavar="fit_filename", nargs="+")
    parser.add_argument("--plot_styles", default="styles/paperdraft.mplstyle")
    parser.add_argument("--output_filename", default=None)
    return parser.parse_args()


def plot_fit(ax, fit_result, xmax, colour=None):
    scan_x = np.linspace(0, xmax, 1000)
    scan_y = linear_fit(np.asarray(fit_result, dtype=float), scan_x)
    scan_errors = pe.fits.error_band(scan_x, linear_fit, fit_result)
    ax.plot(scan_x, scan_y, dashes=(3, 2), color=colour)
    ax.fill_between(
        scan_x, scan_y + scan_errors, scan_y - scan_errors, color=colour, alpha=0.2
    )


def add_finite_L(ax_row, fit_result, colours):
    time = fit_result["time"]
    flows = get_all_flows(
        [ens["filename"] for ens in fit_result["ensembles"]],
        operator=fit_result["operator"],
        extra_metadata={"Nc": fit_result["Nc"]},
    )
    x_values = [1 / flow["NX"] ** 4 for flow in flows]
    gGF2_values = get_scales_at_time(flows, "gGF^2", time)
    betaGF_values = get_scales_at_time(flows, "betaGF", time)

    for ax, y_values in zip(ax_row, [gGF2_values, betaGF_values]):
        errorbar_pyerrors(
            ax, x_values, y_values, color=colours[time], ls="none", marker="x"
        )


def add_extrapolation_band(ax_row, fit_result, colours):
    for ax, scale in zip(ax_row, ["gGF^2", "betaGF"]):
        result = fit_result[scale]
        time = fit_result["time"]
        x_min, x_max = ax.get_xlim()
        plot_fit(ax, result, x_max, colour=colours[time])
        ax.set_xlim(x_min, x_max)


def group_betas(fit_results):
    betas = sorted(set(result["beta"] for result in fit_results))
    return {
        beta: [result for result in fit_results if result["beta"] == beta]
        for beta in betas
    }


def plot_g2_vs_L(fit_results, filename=None):
    grouped_results = group_betas(fit_results)
    num_rows = len(grouped_results)
    colours = ColourRegistry()
    L_values = set(
        [ens["NX"] for fit_result in fit_results for ens in fit_result["ensembles"]]
    )
    times = sorted(set([fit_result["time"] for fit_result in fit_results]))

    fig, axes = plt.subplots(
        nrows=num_rows,
        ncols=2,
        sharex=True,
        layout="constrained",
        figsize=(7, 1 + 2 * num_rows),
        squeeze=False,
    )
    for (beta, beta_results), ax_row in zip(grouped_results.items(), axes):
        ax_row[0].set_ylabel(r"$g_{\mathrm{GF}}^2$")
        ax_row[1].set_ylabel(r"$\beta_{\mathrm{GF}}$")
        for ax in ax_row:
            ax.text(
                0.05,
                0.95,
                f"$\\beta={beta}$",
                ha="left",
                va="top",
                transform=ax.transAxes,
            )

        for fit_result in beta_results:
            add_finite_L(ax_row, fit_result, colours)
            add_extrapolation_band(ax_row, fit_result, colours)

    xtick_positions = [0] + [1 / L**4 for L in L_values]
    xtick_labels = ["0"] + [f"$\\frac{{1}}{{{L}^4}}$" for L in L_values]

    for ax in axes[-1]:
        ax.set_xlim(0, None)
        ax.set_xlabel(r"$(a/L)^4$")
        ax.set_xticks(xtick_positions, xtick_labels)

    for ax in axes.ravel():
        for x in xtick_positions:
            ax.axvline(x, alpha=0.2)

    for time in times:
        axes[0][0].errorbar(
            [np.nan],
            [np.nan],
            yerr=[np.nan],
            color=colours[time],
            ls="none",
            marker="x",
            label=f"$t={time}$",
        )

    fig.legend(loc="outside lower center", ncols=4)
    if filename is None:
        plt.show()
    else:
        fig.savefig(filename)
        plt.close(fig)


def main():
    args = get_args()
    plt.style.use(args.plot_styles)

    fit_results = read_all_fit_results(args.fit_filenames)
    plot_g2_vs_L(fit_results, filename=args.output_filename)


if __name__ == "__main__":
    main()

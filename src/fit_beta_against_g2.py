#!/usr/bin/env python3

import argparse
import functools

import pyerrors as pe

from provenance import get_consistent_metadata
from read import read_all_fit_results


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filenames", metavar="input_filename", nargs="+")
    parser.add_argument("--order", type=int, default=4)
    parser.add_argument("--output_filename", default=None)
    return parser.parse_args()


def interpolating_form(a, x, n=4):
    # Eq. (10) of 2402.18038
    return x**2 * sum([a[i] * x**i for i in range(n)])


def fit_single(data, order=4):
    result = pe.fits.total_least_squares(
        [datum["gGF^2"][0] for datum in data],
        [datum["betaGF"][0] for datum in data],
        functools.partial(interpolating_form, n=order),
        silent=True,
    )
    for value in result.fit_parameters:
        value.gamma_method()

    return result.fit_parameters


def describe_inputs(data, **extra_metadata):
    specific_keys = ["filename", "beta"]
    consistent_keys = ["time", "Nc", "operator"]
    return {
        "_description": "Interpolating form for beta function at finite lattice spacing.",
        "data_sources": [{key: datum[key] for key in specific_keys} for datum in data],
        **{key: get_consistent_metadata(data, key) for key in consistent_keys},
        **extra_metadata,
    }


def main():
    args = get_args()
    data = read_all_fit_results(args.input_filenames)
    result = fit_single(data, order=args.order)
    if args.output_filename:
        pe.input.json.dump_dict_to_json(
            {"beta_interpolation": result},
            args.output_filename,
            description=describe_inputs(data, order=args.order),
        )
    else:
        print(f"beta(g^2) interpolation: {result}")


if __name__ == "__main__":
    main()

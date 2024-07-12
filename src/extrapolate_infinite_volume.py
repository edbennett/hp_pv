#!/usr/bin/env python3

import argparse

import pyerrors as pe

from read import get_all_flows
from stats import weighted_mean
from utils import zip_combinations


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_filenames", metavar="flow_filename", nargs="+")
    parser.add_argument("--reader", default="hp")
    parser.add_argument("--operator", default="sym")
    parser.add_argument("--observable", default="gGF^2")
    parser.add_argument("--output_filename", default=None)
    parser.add_argument("--time", required=True, type=float)
    return parser.parse_args()


def get_consistent_metadata(flows, key):
    values = set(flow[key] for flow in flows)
    if len(values) > 1:
        raise ValueError(
            f"Different {key} values {values} cannot be combined in one fit."
        )

    return values.pop() if values else None


def get_scales_at_time(flows, scale, time):
    result = []
    for flow in flows:
        index = int(time / flow["h"])
        result.append(flow[scale][index])

    return result


def linear_fit(a, x):
    return a[0] + a[1] * x


def fit_single(x_values, y_values):
    result = pe.fits.least_squares(x_values, y_values, linear_fit, silent=True)
    return result, result.chisquare_by_dof + 2 * len(result.fit_parameters)


def fit_scale(flows, scale, time):
    x_values = [1 / flow["NX"] ** 4 for flow in flows]
    scale_values = get_scales_at_time(flows, scale, time)
    fit_results = [
        fit_single(x_subset, scale_subset)
        for x_subset, scale_subset in zip_combinations(
            x_values, scale_values, min_count=3
        )
    ]
    return weighted_mean(fit_results)


def describe_flows(flows, **extra_metadata):
    ensemble_keys = ["filename", "NX", "NY", "NZ", "NT"]
    consistent_keys = ["beta", "Nc"]
    return {
        "_description": "Infinite volume extrapolation for gradient flow data.",
        "ensembles": [
            {key: ensemble[key] for key in ensemble_keys} for ensemble in flows
        ],
        **{key: get_consistent_metadata(flows, key) for key in consistent_keys},
        **extra_metadata,
    }


def main():
    args = get_args()
    flows = get_all_flows(
        args.flow_filenames,
        reader=args.reader,
        operator=args.operator,
        extra_metadata={"Nc": 3},
    )

    # Ensure a single consistent beta will be fit
    get_consistent_metadata(flows, "beta")

    result = {
        scale: fit_scale(flows, scale, args.time) for scale in ["gGF^2", "betaGF"]
    }

    if args.output_filename:
        pe.input.json.dump_dict_to_json(
            result,
            args.output_filename,
            description=describe_flows(flows, operator=args.operator, time=args.time),
        )
    else:
        print(f"{args.observable}: {result}")


if __name__ == "__main__":
    main()

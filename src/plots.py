#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pyerrors as pe


class ColourRegistry:
    def __init__(self, colours=None):
        if colours:
            self._colours = colours
        else:
            prop_cycle = plt.rcParams["axes.prop_cycle"]
            self._colours = prop_cycle.by_key()["color"]

        self._colour_dict = {}

    def __getitem__(self, key):
        if key not in self._colour_dict:
            self._colour_dict[key] = self._colours.pop(0)

        return self._colour_dict[key]


def errorbar_pyerrors(ax, x, y, *args, **kwargs):
    if isinstance(x[0], pe.Obs):
        x_values = [xi.value for xi in x]
        x_errors = [xi.dvalue for xi in x]
    else:
        x_values = x
        x_errors = None

    if isinstance(y[0], pe.Obs):
        y_values = [yi.value for yi in y]
        y_errors = [yi.dvalue for yi in y]
    else:
        y_values = y
        y_errors = None

    ax.errorbar(x_values, y_values, xerr=x_errors, yerr=y_errors, *args, **kwargs)

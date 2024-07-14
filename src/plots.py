#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pyerrors as pe


class PlotPropRegistry:
    def __init__(self, valid_props):
        self._potential_props = valid_props
        self._active_props = {}

    def __getitem__(self, key):
        if key not in self._active_props:
            self._active_props[key] = self._potential_props.pop(0)

        return self._active_props[key]

    def items(self):
        return self._active_props.items()

    @classmethod
    def colours(cls):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        return cls(prop_cycle.by_key()["color"])


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

    ax.errorbar(
        x_values,
        y_values,
        xerr=x_errors,
        yerr=y_errors,
        ls="none",
        *args,
        **kwargs,
    )


def save_or_show(fig, filename=None):
    if filename is not None:
        fig.savefig(filename)
        plt.close(fig)
    else:
        plt.show()

# Alternative analysis workflow for “Twelve flavor SU(3) gradient flow data for the continuous beta-function”

This workflow analyses
[the open data released by Anna Hasenfratz and Curtis Peterson][hp-data]
to reproduce their findings published in [arXiv:2402.18038][arxiv]
[(Phys.Rev.D 109 (2024) 11, 114507)][prd].

## Requirements

- Conda, for example, installed from [Miniforge][miniforge]
- [Snakemake][snakemake], which may be installed using Conda
- LaTeX, for example, from [TeX Live][texlive]

## Setup

1. Install the dependencies above.
2. Clone this repository
   (or download and `unzip` it)
   and `cd` into it:

   ```shellsession
   git clone https://github.com/edbennett/hp_pv
   cd hp_pv
   ```

3. Download all files from [Hasenfratz and Peterson's release][hp-data]
   and place them into the `data` subdirectory.

## Running the workflow

The workflow is run using Snakemake:

``` shellsession
snakemake --cores 1 --use-conda
```

where the number `1`
may be replaced by
the number of CPU cores you wish to allocate to the computation.

Snakemake will automatically download and install
all required Python packages.
This requires an Internet connection;
if you are running in an HPC environment where you would need
to run the workflow without Internet access,
details on how to preinstall the environment
can be found in the [Snakemake documentation][snakemake-conda].

Using `--cores 6` on a MacBook Pro with an M1 Pro processor,
the analysis takes around 17 minutes.

## Output

Output plots are placed in the `assets/plots` directory.

Intermediary data are placed in the `intermediary_data` directory.

## Extending the workflow

It is possible to add additional
values of $\beta$,
lattice volumes,
or operators,
by placing the relevant data files in the `data` directory
and updating the variables near the top of the file `workflow/Snakefile`.
(If additional operators are added,
an acronym will need to be defined for them
in the `operator_names` dict
in `src/names.py`.)

Other variables in `workflow/Snakefile`
control which parameter sets and ranges are included in each plot.
These will likely need to be changed
if this workflow is used to study other theories.

[arxiv]: https://doi.org/10.48550/arXiv.2402.18038
[hp-data]: https://doi.org/10.5281/zenodo.10719052
[miniforge]: https://github.com/conda-forge/miniforge
[prd]: https://doi.org/10.1103/PhysRevD.109.114507
[snakemake]: https://snakemake.github.io
[snakemake-conda]: https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html
[texlive]: https://tug.org/texlive/

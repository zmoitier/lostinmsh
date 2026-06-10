[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Doc formatter: docformatter](https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg)](https://github.com/PyCQA/docformatter)
[![Doc style: numpy](https://img.shields.io/badge/%20style-numpy-459db9.svg)](https://numpydoc.readthedocs.io/en/latest/format.html)

[![PyPI version](https://badge.fury.io/py/lostinmsh.svg)](https://badge.fury.io/py/lostinmsh)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7677383.svg)](https://doi.org/10.5281/zenodo.7677383)
[![Documentation](https://github.com/zmoitier/lostinmsh/actions/workflows/docs.yml/badge.svg)](https://zmoitier.github.io/lostinmsh)

# lostinmsh

The Python toolbox `lostinmsh` (_LOcally STructured polygonal INterface MeSH_), is a package using `GMSH` to construct locally structured triangular meshes of polygons which are useful for sign changing PDE problem.

## Installation

Using [`pip`](https://pip.pypa.io/en/stable/)

```bash
$ python -m pip install lostinmsh
$ python -m pip install lostinmsh[plot]  # with plotting dependencies
```

Using [`uv`](https://docs.astral.sh/uv/)

```bash
$ uv add lostinmsh
$ uv add lostinmsh --optional plot  # with plotting dependencies
```

## [Documentation](https://zmoitier.github.io/lostinmsh)

## Requirements

- Python ≥ 3.14
- [`GMSH`](https://gmsh.info) ≥ 4
- [`numpy`](https://github.com/numpy/numpy)
- [`scipy`](https://github.com/scipy/scipy)

## Optional requirements (only use for plotting)

- [`matplotlib`](https://github.com/matplotlib/matplotlib)
- [`meshio`](https://github.com/nschloe/meshio)

## Acknowledgements

This research was partially supported by the National Science Foundation Grant: DMS-2009366.

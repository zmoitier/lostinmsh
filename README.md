[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Doc formatter: docformatter](https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg)](https://github.com/PyCQA/docformatter)
[![Doc style: numpy](https://img.shields.io/badge/%20style-numpy-459db9.svg)](https://numpydoc.readthedocs.io/en/latest/format.html)

[![PyPI version](https://badge.fury.io/py/lostinmsh.svg)](https://badge.fury.io/py/lostinmsh)
[![DOI](https://zenodo.org/badge/602493619.svg)](https://zenodo.org/badge/latestdoi/602493619)
[![License: MIT](https://img.shields.io/github/license/zmoitier/lostinmsh)](https://github.com/zmoitier/lostinmsh/blob/main/LICENSE)
[![Documentation](https://github.com/zmoitier/lostinmsh/actions/workflows/docs.yaml/badge.svg)](https://zmoitier.github.io/lostinmsh)

# lostinmsh

The Python toolbox `lostinmsh` (_LOcally STructured polygonal INterface MeSH_), is a package using GMSH to construct locally structured triangular meshes of polygons which are useful for sign changing PDE problem.

## Installation

Use [`pip`](https://pip.pypa.io/en/stable/)

```bash
$ pip install lostinmsh
```

or clone the repository

```bash
$ git clone https://github.com/zmoitier/lostinmsh.git
```

and then you can locally install it via [`flit`](https://flit.pypa.io/en/stable/)

```bash
$ flit install --symlink
```

## [Documentation](https://zmoitier.github.io/lostinmsh)

## Requirements

- Python ≥ 3.10
- [GMSH](https://gmsh.info) ≥ 4 (and `import gmsh` must work)
- [numpy](https://github.com/numpy/numpy)

## Optional requirements

- [matplotlib](https://github.com/matplotlib/matplotlib) (only use for plotting)

## Acknowledgements

This research was partially supported by the National Science Foundation Grant: DMS-2009366.
